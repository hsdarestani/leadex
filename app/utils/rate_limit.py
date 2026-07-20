"""
Rate limiting utility using Redis
"""
import redis
from app.core.config import settings
from typing import Tuple


# Initialize Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def check_rate_limit(key: str, max_attempts: int, window_seconds: int) -> Tuple[bool, int]:
    """
    Check if rate limit is exceeded
    
    Args:
        key: Rate limit key (e.g., "ip:192.168.1.1" or "mobile:+971501234567")
        max_attempts: Maximum attempts allowed in window
        window_seconds: Time window in seconds
    
    Returns:
        Tuple of (allowed: bool, remaining_attempts: int)
    """
    try:
        # Get current count
        current = redis_client.get(key)
        
        if current is None:
            # First attempt
            return True, max_attempts - 1
        
        current_count = int(current)
        
        if current_count >= max_attempts:
            # Rate limit exceeded
            return False, 0
        
        # Still within limit
        return True, max_attempts - current_count - 1
        
    except Exception as e:
        print(f"Rate limit check error: {e}")
        # On error, allow the request (fail open)
        return True, max_attempts


def record_submission(key: str, window_seconds: int) -> None:
    """
    Record a submission attempt
    
    Args:
        key: Rate limit key
        window_seconds: Time window in seconds
    """
    try:
        # Increment counter
        current = redis_client.incr(key)
        
        # Set expiry on first attempt
        if current == 1:
            redis_client.expire(key, window_seconds)
            
    except Exception as e:
        print(f"Rate limit record error: {e}")
