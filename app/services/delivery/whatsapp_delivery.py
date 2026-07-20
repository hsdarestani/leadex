"""
WhatsApp Delivery Service
Sends lead data via WhatsApp using WhatsiPlus API (replacing Meta Business API)
IMPORTANT:
- Keep the same class/method names & signature to avoid breaking existing callers.
- whatsapp_token is re-used as WhatsiPlus API Key.
- whatsapp_phone_id is ignored (kept only for backward compatibility).
"""
import os
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils.time import to_tehran_iso
logger = logging.getLogger(__name__)


class WhatsAppDeliveryService:
    """Service for delivering leads via WhatsApp (WhatsiPlus transport)"""

    # Set this in env as needed (do NOT hardcode secrets here)
    # Example: https://api.whatsiplus.com  (adjust if your panel provides a different base)
    BASE_URL = os.getenv("WHATSIPLUS_BASE_URL", "https://api.whatsiplus.com")

    @staticmethod
    def deliver(phone_number: str, message: str, whatsapp_token: str, whatsapp_phone_id: str, timeout: int = 30):
        api_key = (whatsapp_token or "").strip()
        if not api_key:
            return {"success": False, "status_code": 0, "response_body": "Missing WHATSIPLUS API key", "message_id": None,
                    "delivery_method": "whatsiplus", "timestamp": datetime.utcnow().isoformat()}

        # WhatsiPlus expects digits (examples show no '+')
        normalized_phone = "".join(ch for ch in phone_number if ch.isdigit())

        url = f"{WhatsAppDeliveryService.BASE_URL}/sendMsg/{api_key}"

        payload = {
            "phonenumber": normalized_phone,
            "message": message,
            # "schedule": "1724160037"  # اگر خواستی زمان‌بندی کنی (UNIX)
        }

        try:
            resp = requests.post(url, data=payload, timeout=timeout)

            try:
                data = resp.json()
            except Exception:
                data = {"raw": (resp.text or "")[:4000]}

            # WhatsiPlus: success is string "true"/"false"
            api_success = False
            message_id = None
            if isinstance(data, dict):
                api_success = str(data.get("success", "")).lower() == "true"
                message_id = data.get("messageId") or data.get("message_id") or data.get("id")

            success = (200 <= resp.status_code < 300) and api_success and (message_id is not None)

            return {
                "success": success,
                "status_code": resp.status_code,
                "response_body": str(data)[:1000],
                "message_id": message_id,
                "delivery_method": "whatsiplus",
                "timestamp": datetime.utcnow().isoformat()
            }

        except requests.Timeout as e:
            return {"success": False, "status_code": 0, "response_body": f"Timeout: {e}", "message_id": None,
                    "delivery_method": "whatsiplus", "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            return {"success": False, "status_code": 0, "response_body": f"Error: {e}", "message_id": None,
                    "delivery_method": "whatsiplus", "timestamp": datetime.utcnow().isoformat()}

    @staticmethod
    def format_message(lead, client) -> str:
        """
        Format lead data as WhatsApp message (unchanged)
        """
        message_parts = [
            f"🎯 *New Lead for {client.name}*",
            "",
            f"📱 Mobile: {lead.mobile}"
        ]

        has_wa = getattr(lead, "has_whatsapp", None)
        if has_wa is True:
            message_parts.append("✅ Lead WhatsApp: Yes")
        elif has_wa is False:
            message_parts.append("❌ Lead WhatsApp: No")
        else:
            message_parts.append("❓ Lead WhatsApp: Unknown")

        if getattr(lead, "name", None):
            message_parts.append(f"👤 Name: {lead.name}")

        if getattr(lead, "email", None):
            message_parts.append(f"📧 Email: {lead.email}")

        created_at = getattr(lead, "created_at", None)
        message_parts.extend([
            "",
            f"🆔 Lead ID: {getattr(lead, 'id', 'N/A')}",
            f"📅 Date: {to_tehran_iso(created_at) if created_at else 'N/A'}"
        ])

        return "\n".join(message_parts)

