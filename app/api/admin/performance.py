"""
Performance monitoring and cache management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.cache import cache
from app.core.monitoring import monitor
from app.core.rate_limiter import rate_limiter
from app.api.dependencies import get_current_admin
from app.models.admin_user import AdminUser

router = APIRouter(tags=["Performance"])


@router.get("/cache/stats")
async def get_cache_stats(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get cache statistics

    Returns cache hit/miss rates, memory usage, and total keys
    """
    try:
        stats = cache.get_stats()
        return {
            'success': True,
            'data': stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching cache stats: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Clear cache entries

    Args:
        pattern: Redis key pattern to clear (e.g., 'client:*'), or None to clear all
    """
    try:
        if pattern:
            deleted = cache.delete_pattern(pattern)
            return {
                'success': True,
                'message': f'Cleared {deleted} cache entries matching pattern: {pattern}'
            }
        else:
            cache.clear_all()
            return {
                'success': True,
                'message': 'All cache cleared'
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )


@router.get("/system/stats")
async def get_system_stats(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get system-wide performance statistics

    Returns database connection pool stats and cache stats
    """
    try:
        stats = monitor.get_system_stats()
        return {
            'success': True,
            'data': stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching system stats: {str(e)}"
        )


@router.get("/endpoint/stats")
async def get_endpoint_stats(
    endpoint: str,
    method: str = 'GET',
    hours: int = 24,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get statistics for a specific API endpoint

    Args:
        endpoint: API endpoint path (e.g., '/api/admin/leads')
        method: HTTP method (GET, POST, etc.)
        hours: Number of hours to look back (default: 24)
    """
    try:
        stats = monitor.get_endpoint_stats(endpoint, method, hours)
        return {
            'success': True,
            'endpoint': endpoint,
            'method': method,
            'data': stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching endpoint stats: {str(e)}"
        )


@router.get("/rate-limit/stats")
async def get_rate_limit_stats(
    identifier: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get rate limit statistics

    Args:
        identifier: Specific identifier to check (optional)
    """
    try:
        if identifier:
            stats = rate_limiter.get_rate_limit_stats(identifier)
            return {
                'success': True,
                'identifier': identifier,
                'data': stats
            }
        else:
            # Return general rate limit configuration
            return {
                'success': True,
                'limits': rate_limiter.limits
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching rate limit stats: {str(e)}"
        )


@router.post("/rate-limit/reset")
async def reset_rate_limit(
    identifier: str,
    limit_type: Optional[str] = None,
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Reset rate limit for a specific identifier

    Args:
        identifier: Identifier to reset (e.g., 'user:123' or 'ip:1.2.3.4')
        limit_type: Specific limit type to reset (optional, resets all if not provided)
    """
    try:
        rate_limiter.reset_rate_limit(identifier, limit_type)
        return {
            'success': True,
            'message': f'Rate limit reset for {identifier}' + (f' ({limit_type})' if limit_type else '')
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting rate limit: {str(e)}"
        )


@router.get("/database/stats")
async def get_database_stats(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get database statistics including table sizes and index usage
    """
    try:
        # Query database statistics
        table_stats_query = """
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
                pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10;
        """

        result = db.execute(table_stats_query)
        tables = []
        for row in result:
            tables.append({
                'schema': row[0],
                'table': row[1],
                'total_size': row[2],
                'table_size': row[3],
                'index_size': row[4]
            })

        return {
            'success': True,
            'tables': tables
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching database stats: {str(e)}"
        )


@router.get("/celery/stats")
async def get_celery_stats(
    current_admin: AdminUser = Depends(get_current_admin)
):
    """
    Get Celery task queue statistics
    """
    try:
        from app.core.celery_app import celery_app

        # Get active tasks
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        scheduled_tasks = inspect.scheduled()
        registered_tasks = inspect.registered()

        stats = {
            'active_tasks': active_tasks or {},
            'scheduled_tasks': scheduled_tasks or {},
            'registered_tasks': registered_tasks or {},
            'workers': list(active_tasks.keys()) if active_tasks else []
        }

        return {
            'success': True,
            'data': stats
        }
    except Exception as e:
        # Celery might not be running
        return {
            'success': False,
            'message': 'Celery not available',
            'error': str(e)
        }
