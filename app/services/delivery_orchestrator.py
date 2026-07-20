"""
Delivery Orchestrator Service
Coordinates delivery of leads to clients via multiple channels
"""
import logging
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models import Client, Asset, Delivery
from app.services.delivery import (
    WebhookDeliveryService,
    WhatsAppDeliveryService,
    EmailDeliveryService,
    SheetsDeliveryService
)
from app.services.credit_service import CreditService
from app.core.config import settings
from datetime import datetime
import time
from app.services.whatsiplus_registry import is_whatsapp_registered

logger = logging.getLogger(__name__)


class DeliveryOrchestrator:
    """Orchestrates delivery of leads to clients via multiple channels"""

    @staticmethod
    def deliver_lead(
        lead: Asset,
        client: Client,
        db: Session,
        attempt_number: int = 1
    ) -> Dict[str, any]:
        """
        Deliver a lead to a client via all enabled delivery methods

        Args:
            lead: Asset (Lead) object
            client: Client object
            db: Database session
            attempt_number: Current attempt number (1-3)

        Returns:
            Dictionary with delivery results
        """
        logger.info(f"Delivering lead {lead.id} to client {client.name} (attempt {attempt_number})")

        results = {
            "lead_id": str(lead.id),
            "client_id": str(client.id),
            "attempt_number": attempt_number,
            "deliveries": [],
            "overall_success": False
        }

        # Determine which delivery methods to use
        delivery_methods = []

        if client.accept_webhook and client.webhook_url:
            delivery_methods.append("webhook")

        if client.accept_sms and client.phone_number:
            delivery_methods.append("whatsapp")

        if client.accept_email and client.email:
            delivery_methods.append("email")

        if client.accept_sheets and client.google_sheet_id:
            delivery_methods.append("google_sheets")

        if not delivery_methods:
            logger.warning(f"No delivery methods enabled for client {client.name}")
            return results

        # WhatsApp registry check for the LEAD + (if true) send richtext to the LEAD
        try:
            if lead.has_whatsapp is None:
                lead.has_whatsapp = is_whatsapp_registered(settings.WHATSIPLUS_API_KEY, lead.mobile)
                lead.has_whatsapp_checked_at = datetime.utcnow()
                db.commit()

                # Only when we just checked AND result is True: send message to the LEAD
                if lead.has_whatsapp is True:
                    rich = (getattr(client, "whatsapp_details_richtext", None) or "").strip()
                    if rich:
                        wa_res = WhatsAppDeliveryService.deliver(
                            phone_number=lead.mobile,                 # <-- send to LEAD
                            message=rich,                             # <-- client's richtext
                            whatsapp_token=settings.WHATSIPLUS_API_KEY,
                            whatsapp_phone_id=getattr(settings, "WHATSAPP_PHONE_ID", "") or "",
                            timeout=30,
                        )
                        # optional: log result, but never break delivery
                        logger.info(
                            f"Lead WA richtext send result lead_id={lead.id} success={wa_res.get('success')} "
                            f"status={wa_res.get('status_code')} msgid={wa_res.get('message_id')}"
                        )
        except Exception:
            # Never break delivery because of registry check / lead message send
            pass


        # Deduct credits BEFORE delivery (on first attempt only)
        if attempt_number == 1:
            if not CreditService.has_sufficient_credits(client, 1):
                logger.warning(f"Client {client.name} has insufficient credits for lead {lead.id}")
                results["error"] = "Insufficient credits"
                return results

            # Deduct credits
            if not CreditService.deduct_credits(client, client.credit_cost_per_lead, db):
                logger.error(f"Failed to deduct credits for client {client.name}")
                results["error"] = "Credit deduction failed"
                return results

            logger.info(f"Deducted {client.credit_cost_per_lead} credits from client {client.name}")

        # Deliver via each method
        successful_deliveries = 0

        for method in delivery_methods:
            try:
                if method == "webhook":
                    result = DeliveryOrchestrator._deliver_webhook(lead, client)
                elif method == "whatsapp":
                    result = DeliveryOrchestrator._deliver_whatsapp(lead, client)
                elif method == "email":
                    result = DeliveryOrchestrator._deliver_email(lead, client)
                elif method == "google_sheets":
                    result = DeliveryOrchestrator._deliver_sheets(lead, client)
                else:
                    continue

                # Create delivery record
                delivery = Delivery(
                    asset_id=lead.id,
                    client_id=client.id,
                    delivery_method=method,
                    payload=WebhookDeliveryService.format_lead_data(lead, client) if method == "webhook" else None,
                    response_status=str(result.get("status_code", 0)),
                    response_body=result.get("response_body", "")[:1000],
                    attempt_number=attempt_number,
                    success=result.get("success", False),
                    credit_charged=client.credit_cost_per_lead if result.get("success") else 0.0
                )
                db.add(delivery)

                results["deliveries"].append({
                    "method": method,
                    "success": result.get("success", False),
                    "status_code": result.get("status_code", 0)
                })

                if result.get("success"):
                    successful_deliveries += 1
                    logger.info(f"✅ {method} delivery successful for lead {lead.id}")
                else:
                    logger.warning(f"❌ {method} detail: {result.get('response_body')}")

#                   logger.warning(f"❌ {method} delivery failed for lead {lead.id}")

            except Exception as e:
                logger.error(f"Error delivering via {method}: {str(e)}", exc_info=True)
                results["deliveries"].append({
                    "method": method,
                    "success": False,
                    "error": str(e)
                })

        # Overall success if at least one method succeeded
        results["overall_success"] = successful_deliveries > 0
        results["successful_count"] = successful_deliveries
        results["total_methods"] = len(delivery_methods)

        # Update lead status
        if results["overall_success"]:
            lead.status = "DELIVERED"
            logger.info(f"Lead {lead.id} delivered successfully ({successful_deliveries}/{len(delivery_methods)} methods)")
        else:
            if attempt_number >= settings.RETRY_ATTEMPTS:
                lead.status = "FAILED"
                # Refund credits on final failure
                CreditService.refund_credits(client, 1, db)
                logger.warning(f"Lead {lead.id} failed after {attempt_number} attempts - credits refunded")
            else:
                lead.status = "ASSIGNED"  # Keep as assigned for retry
                logger.info(f"Lead {lead.id} will be retried (attempt {attempt_number}/{settings.RETRY_ATTEMPTS})")

        lead.updated_at = datetime.utcnow()
        db.commit()

        return results

    @staticmethod
    def _deliver_webhook(lead: Asset, client: Client) -> Dict:
        """Deliver via webhook"""
        lead_data = WebhookDeliveryService.format_lead_data(lead, client)
        return WebhookDeliveryService.deliver(client.webhook_url, lead_data)

    @staticmethod
    def _deliver_whatsapp(lead: Asset, client: Client) -> Dict:
        """Deliver via WhatsApp"""
        message = WhatsAppDeliveryService.format_message(lead, client)
        return WhatsAppDeliveryService.deliver(
            phone_number=client.phone_number,
            message=message,
            whatsapp_token=settings.WHATSIPLUS_API_KEY,
            whatsapp_phone_id=""
        )

    @staticmethod
    def _deliver_email(lead: Asset, client: Client) -> Dict:
        """Deliver via email"""
        html_content = EmailDeliveryService.format_html_content(lead, client)
        return EmailDeliveryService.deliver(
            to_email=client.email,
            subject=f"New Lead: {lead.mobile}",
            html_content=html_content
        )

    @staticmethod
    def _deliver_sheets(lead: Asset, client: Client) -> Dict:
        """Deliver via Google Sheets"""
        row_data = SheetsDeliveryService.format_row_data(lead, client)
        return SheetsDeliveryService.deliver(
            spreadsheet_id=client.google_sheet_id,
            credentials_file=settings.GOOGLE_CREDENTIALS_FILE,
            lead_data=row_data
        )

