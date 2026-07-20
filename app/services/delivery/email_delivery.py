"""
Email Delivery Service
Sends lead data via email using SendGrid
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime
from app.core.config import settings
from app.utils.time import to_tehran_iso
logger = logging.getLogger(__name__)


class EmailDeliveryService:
    """Service for delivering leads via email"""
    
    SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"
    
    @staticmethod
    def deliver(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str = None,
        sendgrid_api_key: str = None,
        timeout: int = 30
    ) -> Dict[str, any]:
        """
        Send email via SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            from_email: Sender email (defaults to settings.SENDGRID_FROM_EMAIL)
            sendgrid_api_key: SendGrid API key (defaults to settings.SENDGRID_API_KEY)
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with delivery result
        """
        try:
            from_email = from_email or settings.SENDGRID_FROM_EMAIL
            sendgrid_api_key = sendgrid_api_key or settings.SENDGRID_API_KEY
            
            logger.info(f"Sending email to: {to_email}")
            
            payload = {
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "subject": subject
                    }
                ],
                "from": {"email": from_email},
                "content": [
                    {
                        "type": "text/html",
                        "value": html_content
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {sendgrid_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                EmailDeliveryService.SENDGRID_API_URL,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            
            success = response.status_code == 202
            
            result = {
                "success": success,
                "status_code": response.status_code,
                "response_body": response.text[:1000],
                "delivery_method": "email",
                "timestamp": to_tehran_iso(datetime.utcnow())
            }
            
            if success:
                logger.info(f"Email delivered successfully to: {to_email}")
            else:
                logger.warning(f"Email delivery failed: {response.status_code}")
            
            return result
            
        except requests.Timeout as e:
            logger.error(f"Email timeout: {to_email} - {str(e)}")
            return {
                "success": False,
                "status_code": 0,
                "response_body": f"Timeout: {str(e)}",
                "delivery_method": "email",
                "timestamp":to_tehran_iso(datetime.utcnow())
            }
            
        except Exception as e:
            logger.error(f"Email error: {to_email} - {str(e)}", exc_info=True)
            return {
                "success": False,
                "status_code": 0,
                "response_body": f"Error: {str(e)}",
                "delivery_method": "email",
                "timestamp": to_tehran_iso(datetime.utcnow())
            }
    
    @staticmethod
    def format_html_content(lead, client) -> str:
        """
        Format lead data as HTML email
        
        Args:
            lead: Asset (Lead) object
            client: Client object
            
        Returns:
            HTML email content
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #555; }}
                .value {{ color: #333; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🎯 New Lead for {client.name}</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">📱 Mobile:</span>
                        <span class="value">{lead.mobile}</span>
                    </div>
                    {f'<div class="field"><span class="label">👤 Name:</span> <span class="value">{lead.name}</span></div>' if lead.name else ''}
                    {f'<div class="field"><span class="label">📧 Email:</span> <span class="value">{lead.email}</span></div>' if lead.email else ''}
                    <div class="field">
                        <span class="label">🆔 Lead ID:</span>
                        <span class="value">{lead.id}</span>
                    </div>
                    <div class="field">
                        <span class="label">📅 Date:</span>
                        <span class="value">
{to_tehran_iso(lead.created_at) if lead.created_at else 'N/A'}
</span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

