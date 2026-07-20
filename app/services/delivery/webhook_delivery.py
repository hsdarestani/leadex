"""
Webhook Delivery Service
Sends lead data to client webhook URLs via HTTP POST
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WebhookDeliveryService:
    """Service for delivering leads via webhook"""

    @staticmethod
    def deliver(
        webhook_url: str,
        lead_data: Dict,
        timeout: int = 30
    ) -> Dict[str, any]:
        """
        Deliver lead data to webhook URL

        Args:
            webhook_url: Client's webhook URL
            lead_data: Lead data to send
            timeout: Request timeout in seconds

        Returns:
            Dictionary with delivery result
        """
        try:
            logger.info(f"Sending webhook to: {webhook_url}")

            response = requests.post(
                webhook_url,
                json=lead_data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Leadex/1.0",
                    "X-Leadex-Timestamp": datetime.utcnow().isoformat()
                },
                timeout=timeout
            )

            success = response.status_code in [200, 201, 202, 204]

            result = {
                "success": success,
                "status_code": response.status_code,
                "response_body": response.text[:1000],  # Limit to 1000 chars
                "delivery_method": "webhook",
                "timestamp": datetime.utcnow().isoformat()
            }

            if success:
                logger.info(f"Webhook delivered successfully: {response.status_code}")
            else:
                logger.warning(f"Webhook delivery failed: {response.status_code}")

            return result

        except requests.Timeout as e:
            logger.error(f"Webhook timeout: {webhook_url} - {str(e)}")
            return {
                "success": False,
                "status_code": 0,
                "response_body": f"Timeout: {str(e)}",
                "delivery_method": "webhook",
                "timestamp": datetime.utcnow().isoformat()
            }

        except requests.RequestException as e:
            logger.error(f"Webhook request error: {webhook_url} - {str(e)}")
            return {
                "success": False,
                "status_code": 0,
                "response_body": f"Request error: {str(e)}",
                "delivery_method": "webhook",
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Webhook unexpected error: {webhook_url} - {str(e)}", exc_info=True)
            return {
                "success": False,
                "status_code": 0,
                "response_body": f"Error: {str(e)}",
                "delivery_method": "webhook",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def format_lead_data(lead, client) -> Dict:
        """
        Format lead data for webhook payload

        Sends only essential client-facing fields (7 fields total).
        Full data is still stored in database and visible in admin panel.

        Args:
            lead: Asset (Lead) object
            client: Client object

        Returns:
            Formatted lead data dictionary (simplified)
        """
        return {
            "lead_id": str(lead.id),
            "mobile": lead.mobile,
            "name": lead.name,
            "email": lead.email,
            "ip": lead.ip,
            "client": {
                "client_id": str(client.id),
                "client_name": client.name
            },
            "timestamp": lead.created_at.isoformat() if lead.created_at else None
        }

