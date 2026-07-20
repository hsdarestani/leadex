"""
Distribution Service - Core distribution logic (Round-Robin Cursor)
- NO priority_order
- NO percentage allocation
- NO "wait for 10 leads" batching logic (batching handled elsewhere)

Goal:
  For each incoming lead, assign to an eligible client:
    - client.status == "active"
    - client has enough credits for 1 lead
  Pick client in a deterministic round-robin order across eligible clients.

Important:
  - We persist the "cursor" in Redis cache so the next lead goes to the next client.
  - If eligibility changes (credits/status), cursor still works: it finds last id in current eligible list;
    if not found, it starts from the first eligible client in sorted order.
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models import Client, Asset, StoredLead, Delivery
from app.services.credit_service import CreditService
from app.core.cache import cache
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class DistributionService:
    """Service for distributing leads to clients using round-robin cursor over eligible clients"""

    # Cache key for round-robin cursor (stores last assigned client_id as string)
    CURSOR_KEY = "leadex:distribution:rr_cursor"

    @staticmethod
    def get_eligible_clients(db: Session) -> List[Client]:
        """
        Eligible = active + can afford at least 1 lead now.
        NOTE: We do credits check in Python because CreditService can contain logic beyond simple fields.
        """
        clients = db.query(Client).filter(Client.status == "active").all()

        eligible: List[Client] = []
        for c in clients:
            try:
                if CreditService.has_sufficient_credits(c, 1):
                    eligible.append(c)
            except Exception:
                continue

        return eligible

    @staticmethod
    def _stable_sort_clients(clients: List[Client]) -> List[Client]:
        """
        Deterministic order for RR.
        Use UUID string ordering to be stable across processes.
        """
        return sorted(clients, key=lambda c: str(c.id))

    @staticmethod
    def _get_cursor() -> Optional[str]:
        try:
            v = cache.get(DistributionService.CURSOR_KEY)
            return str(v) if v else None
        except Exception:
            return None

    @staticmethod
    def _set_cursor(client_id: str) -> None:
        try:
            # keep cursor for a long time (1 day); renewed each assignment
            cache.set(DistributionService.CURSOR_KEY, str(client_id), ttl=86400, cache_type="default")
        except Exception:
            # cursor persistence failure should NOT break assignment
            pass

    @staticmethod
    def pick_next_client(db: Session, eligible_clients: List[Client]) -> Optional[Client]:
        """
        Round-robin over current eligible clients using a persisted cursor.

        Steps:
          1) sort eligible clients deterministically
          2) read cursor (last assigned client_id)
          3) pick next after cursor; if cursor missing/not in list -> first
          4) update cursor to chosen client's id
        """
        if not eligible_clients:
            return None

        clients = DistributionService._stable_sort_clients(eligible_clients)
        last_id = DistributionService._get_cursor()

        chosen = None
        if last_id:
            try:
                idx = next(i for i, c in enumerate(clients) if str(c.id) == str(last_id))
                chosen = clients[(idx + 1) % len(clients)]
            except StopIteration:
                chosen = clients[0]
        else:
            chosen = clients[0]

        DistributionService._set_cursor(str(chosen.id))
        return chosen

    @staticmethod
    def assign_single_lead_to_client(lead_id: uuid.UUID, client: Client, db: Session) -> Dict[str, any]:
        """
        Assign a single lead to a chosen client:
          - verify lead exists
          - re-check credits at assignment time
          - reserve credits immediately for 1 lead
          - set lead.status = ASSIGNED
          - create a Delivery record placeholder (workers/orchestrator will update later)
        """
        lead = db.query(Asset).filter(Asset.id == lead_id).first()
        if not lead:
            return {"assigned": False, "reason": "lead_not_found", "lead_id": str(lead_id)}

        # Double-check credits at assignment time (race safety)
        if not CreditService.has_sufficient_credits(client, 1):
            return {
                "assigned": False,
                "reason": "insufficient_credits",
                "lead_id": str(lead_id),
                "client_id": str(client.id),
            }

        # Reserve credits (deduct now)
        if not CreditService.reserve_credits(client, 1, db):
            return {
                "assigned": False,
                "reason": "reserve_failed",
                "lead_id": str(lead_id),
                "client_id": str(client.id),
            }

        # Assign lead
        lead.status = "ASSIGNED"
        lead.updated_at = datetime.utcnow()

        # Create delivery record placeholder
        delivery = Delivery(
            asset_id=lead_id,
            client_id=client.id,
            success=False,
            delivery_method="multiple",  # will be updated by actual deliverers
            attempt_number=1,
        )
        db.add(delivery)

        db.commit()
        return {
            "assigned": True,
            "lead_id": str(lead_id),
            "client_id": str(client.id),
            "client_name": client.name,
        }

    @staticmethod
    def store_unassigned_lead(lead_id: uuid.UUID, db: Session, reason: str) -> None:
        """
        Mark lead STORED and create StoredLead record.
        """
        lead = db.query(Asset).filter(Asset.id == lead_id).first()
        if lead:
            lead.status = "STORED"
            lead.updated_at = datetime.utcnow()

        stored = StoredLead(
            asset_id=lead_id,
            reason=reason,
            retry_count=0,
        )
        db.add(stored)
        db.commit()

    @staticmethod
    def distribute_batch(lead_ids: List[uuid.UUID], db: Session) -> Dict[str, any]:
        """
        Distribute ANY number of leads immediately (no batching logic here).
        For each lead:
          - get eligible clients
          - pick next client (RR cursor)
          - assign
          - if no eligible client, store lead
        """
        logger.info(f"Starting RR distribution for {len(lead_ids)} leads")

        results = {
            "assigned": 0,
            "stored": 0,
            "assignments": [],
            "stored_lead_ids": [],
        }

        for lead_id in lead_ids:
            eligible = DistributionService.get_eligible_clients(db)

            if not eligible:
                logger.warning("No eligible clients (active+credits). Storing lead.")
                DistributionService.store_unassigned_lead(lead_id, db, reason="no_eligible_clients")
                results["stored"] += 1
                results["stored_lead_ids"].append(str(lead_id))
                continue

            client = DistributionService.pick_next_client(db, eligible)
            if not client:
                logger.warning("Eligible list empty after pick. Storing lead.")
                DistributionService.store_unassigned_lead(lead_id, db, reason="no_pickable_client")
                results["stored"] += 1
                results["stored_lead_ids"].append(str(lead_id))
                continue

            res = DistributionService.assign_single_lead_to_client(lead_id, client, db)
            if res.get("assigned"):
                results["assigned"] += 1
                results["assignments"].append(res)
                logger.info(f"Assigned lead {lead_id} to client {client.name}")
            else:
                logger.warning(f"Failed assign lead {lead_id}. reason={res.get('reason')}. storing.")
                DistributionService.store_unassigned_lead(lead_id, db, reason=res.get("reason") or "assign_failed")
                results["stored"] += 1
                results["stored_lead_ids"].append(str(lead_id))

        return results
