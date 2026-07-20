"""
Redis-based rate limiting for API endpoints
"""
import time
from typing import Optional
from fastapi import Request, HTTPException, status
from app.core.cache import cache


class RateLimiter:
    """Redis-based rate limiter using sliding window algorithm"""

    def __init__(self):
        """Initialize rate limiter"""
        self.cache = cache

        # Rate limit configurations (requests per minute)
        self.limits = {
            'landing_submit': 10,      # 10 requests per minute for landing page submissions
            'api_default': 60,         # 60 requests per minute for general API
            'api_admin': 120,          # 120 requests per minute for admin API
            'api_client': 60,          # 60 requests per minute for client API
            'webhook': 30,             # 30 requests per minute for webhooks
        }

    def get_client_identifier(self, request: Request) -> str:
        """
        Get unique identifier for the client (IP or user)

        Args:
            request: FastAPI request object

        Returns:
            Client identifier string
        """
        # Try to get user from request state (if authenticated)
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.id}"

        # Fall back to IP address
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        client_host = request.client.host if request.client else 'unknown'
        return f"ip:{client_host}"

    def is_rate_limited(
        self,
        identifier: str,
        limit_type: str = 'api_default',
        custom_limit: Optional[int] = None
    ) -> tuple[bool, dict]:
        """
        Check if request should be rate limited

        Args:
            identifier: Client identifier
            limit_type: Type of rate limit to apply
            custom_limit: Custom limit (overrides default)

        Returns:
            Tuple of (is_limited: bool, info: dict)
        """
        # Get limit
        limit = custom_limit or self.limits.get(limit_type, self.limits['api_default'])

        # Create cache key
        cache_key = f"rate_limit:{limit_type}:{identifier}"

        # Get current count
        current_count = self.cache.get(cache_key) or 0

        # Check if limit exceeded
        if current_count >= limit:
            ttl = self.cache.redis_client.ttl(cache_key)
            return True, {
                'limited': True,
                'limit': limit,
                'remaining': 0,
                'reset_in': ttl if ttl > 0 else 60
            }

        # Increment counter
        new_count = current_count + 1
        self.cache.set(cache_key, new_count, ttl=60, cache_type='default')

        return False, {
            'limited': False,
            'limit': limit,
            'remaining': limit - new_count,
            'reset_in': 60
        }

    async def check_rate_limit(
        self,
        request: Request,
        limit_type: str = 'api_default',
        custom_limit: Optional[int] = None
    ):
        """
        Check rate limit and raise exception if exceeded

        Args:
            request: FastAPI request object
            limit_type: Type of rate limit to apply
            custom_limit: Custom limit (overrides default)

        Raises:
            HTTPException: If rate limit exceeded
        """
        identifier = self.get_client_identifier(request)
        is_limited, info = self.is_rate_limited(identifier, limit_type, custom_limit)

        # Add rate limit headers to response
        if hasattr(request.state, 'rate_limit_info'):
            request.state.rate_limit_info = info
        else:
            request.state.rate_limit_info = info

        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    'error': 'Rate limit exceeded',
                    'limit': info['limit'],
                    'reset_in': info['reset_in']
                },
                headers={
                    'X-RateLimit-Limit': str(info['limit']),
                    'X-RateLimit-Remaining': '0',
                    'X-RateLimit-Reset': str(info['reset_in']),
                    'Retry-After': str(info['reset_in'])
                }
            )

    def get_rate_limit_stats(self, identifier: str) -> dict:
        """
        Get rate limit statistics for an identifier

        Args:
            identifier: Client identifier

        Returns:
            Dictionary with rate limit stats
        """
        stats = {}
        for limit_type in self.limits.keys():
            cache_key = f"rate_limit:{limit_type}:{identifier}"
            count = self.cache.get(cache_key) or 0
            ttl = self.cache.redis_client.ttl(cache_key)

            stats[limit_type] = {
                'current': count,
                'limit': self.limits[limit_type],
                'remaining': max(0, self.limits[limit_type] - count),
                'reset_in': ttl if ttl > 0 else 0
            }

        return stats

    def reset_rate_limit(self, identifier: str, limit_type: Optional[str] = None):
        """
        Reset rate limit for an identifier

        Args:
            identifier: Client identifier
            limit_type: Specific limit type to reset (optional, resets all if not provided)
        """
        if limit_type:
            cache_key = f"rate_limit:{limit_type}:{identifier}"
            self.cache.delete(cache_key)
        else:
            # Reset all limit types for this identifier
            pattern = f"rate_limit:*:{identifier}"
            self.cache.delete_pattern(pattern)


# Global rate limiter instance
rate_limiter = RateLimiter()


# Middleware to add rate limit headers
async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to add rate limit headers to all responses
    """
    response = await call_next(request)

    # Add rate limit headers if available
    if hasattr(request.state, 'rate_limit_info'):
        info = request.state.rate_limit_info
        response.headers['X-RateLimit-Limit'] = str(info.get('limit', 0))
        response.headers['X-RateLimit-Remaining'] = str(info.get('remaining', 0))
        response.headers['X-RateLimit-Reset'] = str(info.get('reset_in', 0))

    return response
