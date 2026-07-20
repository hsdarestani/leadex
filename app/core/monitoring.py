"""
Performance monitoring and profiling utilities
"""
import time
import functools
from typing import Callable, Optional
from datetime import datetime
from fastapi import Request
from app.core.cache import cache


class PerformanceMonitor:
    """Monitor and track application performance metrics"""

    def __init__(self):
        self.cache = cache

    def record_request(
        self,
        endpoint: str,
        method: str,
        duration: float,
        status_code: int
    ):
        """
        Record API request metrics

        Args:
            endpoint: API endpoint path
            method: HTTP method
            duration: Request duration in milliseconds
            status_code: HTTP status code
        """
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
        key = f"metrics:request:{endpoint}:{method}:{timestamp}"

        # Store in Redis with 24-hour expiry
        metrics = self.cache.get(key) or {
            'count': 0,
            'total_duration': 0,
            'avg_duration': 0,
            'min_duration': float('inf'),
            'max_duration': 0,
            'status_codes': {}
        }

        metrics['count'] += 1
        metrics['total_duration'] += duration
        metrics['avg_duration'] = metrics['total_duration'] / metrics['count']
        metrics['min_duration'] = min(metrics['min_duration'], duration)
        metrics['max_duration'] = max(metrics['max_duration'], duration)

        # Count status codes
        status_key = str(status_code)
        metrics['status_codes'][status_key] = metrics['status_codes'].get(status_key, 0) + 1

        self.cache.set(key, metrics, ttl=86400)  # 24 hours

    def get_endpoint_stats(self, endpoint: str, method: str, hours: int = 24) -> dict:
        """
        Get statistics for a specific endpoint

        Args:
            endpoint: API endpoint path
            method: HTTP method
            hours: Number of hours to look back

        Returns:
            Dictionary with endpoint statistics
        """
        stats = {
            'total_requests': 0,
            'avg_duration': 0,
            'min_duration': float('inf'),
            'max_duration': 0,
            'status_codes': {},
            'hourly_breakdown': []
        }

        # Get data for each hour
        for hour_offset in range(hours):
            timestamp = datetime.utcnow()
            timestamp = timestamp.replace(minute=0, second=0, microsecond=0)
            timestamp = timestamp - timedelta(hours=hour_offset)
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M')

            key = f"metrics:request:{endpoint}:{method}:{timestamp_str}"
            metrics = self.cache.get(key)

            if metrics:
                stats['total_requests'] += metrics['count']
                stats['min_duration'] = min(stats['min_duration'], metrics['min_duration'])
                stats['max_duration'] = max(stats['max_duration'], metrics['max_duration'])

                # Merge status codes
                for status, count in metrics['status_codes'].items():
                    stats['status_codes'][status] = stats['status_codes'].get(status, 0) + count

                stats['hourly_breakdown'].append({
                    'hour': timestamp_str,
                    'requests': metrics['count'],
                    'avg_duration': metrics['avg_duration']
                })

        # Calculate overall average
        if stats['total_requests'] > 0:
            total_duration = sum(
                h['requests'] * h['avg_duration']
                for h in stats['hourly_breakdown']
            )
            stats['avg_duration'] = total_duration / stats['total_requests']

        return stats

    def get_system_stats(self) -> dict:
        """
        Get overall system statistics

        Returns:
            Dictionary with system-wide statistics
        """
        from app.core.database import engine

        # Database connection pool stats
        pool = engine.pool
        pool_stats = {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'total_connections': pool.checkedin() + pool.checkedout()
        }

        # Cache stats
        cache_stats = self.cache.get_stats()

        return {
            'database': pool_stats,
            'cache': cache_stats,
            'timestamp': datetime.utcnow().isoformat()
        }


# Global monitor instance
monitor = PerformanceMonitor()


def track_performance(endpoint_name: Optional[str] = None):
    """
    Decorator to track function performance

    Args:
        endpoint_name: Custom endpoint name (optional)

    Usage:
        @track_performance('get_clients')
        def get_clients():
            # Function code
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = (time.time() - start_time) * 1000  # Convert to ms
                name = endpoint_name or func.__name__
                monitor.record_request(name, 'FUNC', duration, 200)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = (time.time() - start_time) * 1000  # Convert to ms
                name = endpoint_name or func.__name__
                monitor.record_request(name, 'FUNC', duration, 200)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


async def performance_middleware(request: Request, call_next):
    """
    Middleware to track request performance
    """
    start_time = time.time()

    response = await call_next(request)

    duration = (time.time() - start_time) * 1000  # Convert to milliseconds

    # Record metrics
    monitor.record_request(
        endpoint=request.url.path,
        method=request.method,
        duration=duration,
        status_code=response.status_code
    )

    # Add performance headers
    response.headers['X-Response-Time'] = f"{duration:.2f}ms"

    return response


from datetime import timedelta
