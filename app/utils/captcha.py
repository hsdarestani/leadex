"""
reCAPTCHA v3 verification utility
"""
import httpx
from app.core.config import settings
from typing import Tuple


async def verify_recaptcha(token: str, remote_ip: str) -> Tuple[bool, float, str]:
    """
    Verify reCAPTCHA v3 token
    
    Args:
        token: reCAPTCHA token from frontend
        remote_ip: Client IP address
    
    Returns:
        Tuple of (success: bool, score: float, error_message: str)
    """
    if not token:
        return False, 0.0, "reCAPTCHA token is required"
    
    # For development/testing, allow bypass if secret key is placeholder
    if settings.RECAPTCHA_SECRET_KEY == "your_recaptcha_secret_key_here":
        return True, 0.9, ""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": token,
                    "remoteip": remote_ip
                },
                timeout=10.0
            )
            
            result = response.json()
            
            if not result.get("success", False):
                error_codes = result.get("error-codes", [])
                return False, 0.0, f"reCAPTCHA verification failed: {', '.join(error_codes)}"
            
            score = result.get("score", 0.0)
            
            # reCAPTCHA v3 score threshold (0.5 is recommended)
            if score < 0.5:
                return False, score, f"reCAPTCHA score too low: {score}"
            
            return True, score, ""
            
    except httpx.TimeoutException:
        return False, 0.0, "reCAPTCHA verification timeout"
    except Exception as e:
        return False, 0.0, f"reCAPTCHA verification error: {str(e)}"
