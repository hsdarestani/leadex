"""
Redis caching utilities for performance optimization
"""
import json
import pickle
from typing import Optional, Any, Callable
from functools import wraps
import redis
from app.core.config import settings


class RedisCache:
    """Redis caching manager with TTL support"""

    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=False,  # We'll handle encoding ourselves
            socket_keepalive=True,
            socket_connect_timeout=5,
            max_connections=50
        )

        # Default TTL values (in seconds)
        self.ttl_config = {
            'clients': 300,          # 5 minutes
            'landing_pages': 600,    # 10 minutes
            'campaigns': 600,        # 10 minutes
            'tags': 1800,            # 30 minutes
            'custom_fields': 1800,   # 30 minutes
            'analytics': 60,         # 1 minute (real-time data)
            'lead_stats': 120,       # 2 minutes
            'default': 300           # 5 minutes
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = self.redis_client.get(key)
            if value:
                # Try to unpickle first (for complex objects)
                try:
                    return pickle.loads(value)
                except:
                    # If unpickling fails, try JSON
                    try:
                        return json.loads(value.decode('utf-8'))
                    except:
                        # Return raw value
                        return value.decode('utf-8')
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None, cache_type: str = 'default') -> bool:
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
            cache_type: Type of cache for default TTL

        Returns:
            True if successful, False otherwise
        """
        try:
            # Use provided TTL or get from config
            expiry = ttl or self.ttl_config.get(cache_type, self.ttl_config['default'])

            # Try to pickle complex objects
            try:
                serialized = pickle.dumps(value)
            except:
                # Fall back to JSON for simple types
                try:
                    serialized = json.dumps(value).encode('utf-8')
                except:
                    # Use string representation as last resort
                    serialized = str(value).encode('utf-8')

            self.redis_client.setex(key, expiry, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern

        Args:
            pattern: Redis key pattern (e.g., 'client:*')

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        try:
            info = self.redis_client.info('stats')
            return {
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(info),
                'total_keys': self.redis_client.dbsize(),
                'memory_used': self.redis_client.info('memory').get('used_memory_human', 'N/A')
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {}

    def _calculate_hit_rate(self, info: dict) -> float:
        """Calculate cache hit rate percentage"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return round((hits / total * 100) if total > 0 else 0, 2)

    def clear_all(self) -> bool:
        """
        Clear all cache (use with caution!)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False


# Global cache instance
cache = RedisCache()


def cached(ttl: Optional[int] = None, cache_type: str = 'default', key_prefix: str = ''):
    """
    Decorator for caching function results

    Args:
        ttl: Time to live in seconds
        cache_type: Type of cache for default TTL
        key_prefix: Prefix for cache key

    Usage:
        @cached(ttl=300, key_prefix='client')
        def get_client(client_id: str):
            # This result will be cached for 5 minutes
            return db.query(Client).filter(Client.id == client_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl=ttl, cache_type=cache_type)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl=ttl, cache_type=cache_type)

            return result

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
