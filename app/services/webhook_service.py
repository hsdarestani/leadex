from app.models.client import Client
from app.models.webhook_log import WebhookLog
"""
Advanced Webhook Service
"""
import hmac
import hashlib
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.integration import WebhookSubscription, WebhookDeliveryLog
import time
import uuid


class WebhookService:
    """Service for advanced webhook management"""

    EVENT_LEAD_CREATED = 'lead.created'
    EVENT_LEAD_ASSIGNED = 'lead.assigned'

    def __init__(self, db: Session):
        self.db = db

    def generate_hmac_signature(self, payload: str, secret_key: str, algorithm: str = 'sha256') -> str:
        """Generate HMAC signature"""
        if algorithm == 'sha256':
            return hmac.new(secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.new(secret_key.encode(), payload.encode(), hashlib.sha512).hexdigest()

    def trigger_webhook(self, event_type: str, event_data: Dict[str, Any], client_id: Optional[str] = None) -> List:
        """Trigger webhooks for event"""
        query = self.db.query(WebhookSubscription).filter(WebhookSubscription.is_active == True)
        if client_id:
            query = query.filter((WebhookSubscription.client_id == client_id) | (WebhookSubscription.client_id == None))
        
        subscriptions = query.all()
        results = []
        
        for sub in subscriptions:
            if event_type in sub.events:
                results.append(self.deliver_webhook(sub, event_type, event_data))
        
        return results

    def deliver_webhook(self, subscription: WebhookSubscription, event_type: str, event_data: Dict, attempt: int = 1) -> Dict:
        """Deliver webhook"""
        log = WebhookDeliveryLog(
            subscription_id=subscription.id,
            event_type=event_type,
            event_data=event_data,
            attempt_number=attempt,
            status='pending'
        )
        self.db.add(log)
        self.db.commit()

        try:
            payload = {'event': event_type, 'data': event_data, 'timestamp': datetime.utcnow().isoformat()}
            payload_str = json.dumps(payload, sort_keys=True)
            
            headers = {'Content-Type': 'application/json', 'X-Webhook-Event': event_type}
            
            if subscription.use_hmac:
                sig = self.generate_hmac_signature(payload_str, subscription.secret_key, subscription.hmac_algorithm)
                headers[f'X-Webhook-Signature-{subscription.hmac_algorithm.upper()}'] = sig
            
            response = requests.post(subscription.endpoint_url, data=payload_str, headers=headers, timeout=30)
            
            log.http_status_code = response.status_code
            log.responded_at = datetime.utcnow()
            
            if 200 <= response.status_code < 300:
                log.status = 'delivered'
                subscription.successful_deliveries += 1
                self.db.commit()
                return {'success': True, 'delivery_id': str(log.id)}
            else:
                log.status = 'failed'
                subscription.failed_deliveries += 1
                self.db.commit()
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        except Exception as e:
            log.status = 'failed'
            log.error_message = str(e)
            self.db.commit()
            return {'success': False, 'error': str(e)}
    @staticmethod
    def test_webhook(
        db: Session,
        client_id: uuid.UUID,
        webhook_url: str,
        test_payload: Optional[Dict[str, Any]] = None,
        method: str = "POST",
    ) -> Dict[str, Any]:
        """
        Test a webhook endpoint, store a WebhookLog row, and return a dict
        compatible with WebhookTestResponse in admin API.

        Router expects:
          - on invalid client: result.get("success")==False and result.get("error")=="Client not found"
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {
                "success": False,
                "log_id": "",
                "status_code": None,
                "response_time_ms": 0.0,
                "response_body": None,
                "error_message": "Client not found",
                "error": "Client not found",
            }

        payload = test_payload or {
            "event": "webhook.test",
            "timestamp": datetime.utcnow().isoformat(),
            "client_id": str(client_id),
        }

        method_upper = (method or "POST").upper().strip()
        if method_upper not in {"POST", "PUT", "PATCH", "GET", "DELETE"}:
            method_upper = "POST"

        request_headers = {
            "Content-Type": "application/json",
            "X-Webhook-Test": "true",
        }

        # Create log row first (so even network errors are logged)
        log = WebhookLog(
            client_id=client_id,
            webhook_url=str(webhook_url),
            method=method_upper,
            request_headers=request_headers,
            request_payload=payload,
            response_status_code=None,
            response_headers=None,
            response_body=None,
            response_time_ms=None,
            success=False,
            error_message=None,
            attempt_number=1,
            is_retry=False,
            is_test=True,
            created_at=datetime.utcnow(),
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        start = time.perf_counter()
        try:
            # For GET/DELETE: usually no body is sent
            if method_upper in {"GET", "DELETE"}:
                resp = requests.request(
                    method_upper,
                    str(webhook_url),
                    headers=request_headers,
                    timeout=30,
                )
            else:
                resp = requests.request(
                    method_upper,
                    str(webhook_url),
                    json=payload,
                    headers=request_headers,
                    timeout=30,
                )

            elapsed_ms = (time.perf_counter() - start) * 1000.0

            log.response_status_code = resp.status_code
            log.response_headers = dict(resp.headers) if resp.headers else None

            body_text = resp.text
            # Avoid huge DB writes
            if body_text and len(body_text) > 20000:
                body_text = body_text[:20000] + "\n...TRUNCATED..."
            log.response_body = body_text

            log.response_time_ms = float(elapsed_ms)
            log.success = 200 <= resp.status_code < 300
            log.error_message = None if log.success else f"HTTP {resp.status_code}"
            db.commit()

            return {
                "success": log.success,
                "log_id": str(log.id),
                "status_code": log.response_status_code,
                "response_time_ms": float(elapsed_ms),
                "response_body": log.response_body,
                "error_message": log.error_message,
            }

        except requests.RequestException as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            log.response_time_ms = float(elapsed_ms)
            log.success = False
            log.error_message = str(e)
            db.commit()

            return {
                "success": False,
                "log_id": str(log.id),
                "status_code": None,
                "response_time_ms": float(elapsed_ms),
                "response_body": None,
                "error_message": str(e),
            }

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            log.response_time_ms = float(elapsed_ms)
            log.success = False
            log.error_message = str(e)
            db.commit()

            return {
                "success": False,
                "log_id": str(log.id),
                "status_code": None,
                "response_time_ms": float(elapsed_ms),
                "response_body": None,
                "error_message": str(e),
            }

    @staticmethod
    def get_webhook_logs(
        db: Session,
        client_id: Optional[uuid.UUID] = None,
        is_test: Optional[bool] = None,
        success: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[WebhookLog]:
        """
        Get webhook logs with filtering, newest first.
        """
        q = db.query(WebhookLog)

        if client_id is not None:
            q = q.filter(WebhookLog.client_id == client_id)
        if is_test is not None:
            q = q.filter(WebhookLog.is_test == is_test)
        if success is not None:
            q = q.filter(WebhookLog.success == success)

        q = q.order_by(WebhookLog.created_at.desc())

        return q.offset(offset).limit(limit).all()

