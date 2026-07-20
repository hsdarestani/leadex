"""
Celery configuration for background task processing
"""
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    'leadex',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.workers.tasks']
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit

    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={'visibility_timeout': 3600},

    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,

    # Retry settings
    task_default_retry_delay=60,  # Retry after 60 seconds
    task_max_retries=3,

    # Beat schedule for periodic tasks
    beat_schedule={
        # Daily summary emails at 9 AM
        'send-daily-summaries': {
            'task': 'app.workers.tasks.send_daily_summaries',
            'schedule': crontab(hour=9, minute=0),
        },
        # Weekly summary emails on Monday at 9 AM
        'send-weekly-summaries': {
            'task': 'app.workers.tasks.send_weekly_summaries',
            'schedule': crontab(day_of_week=1, hour=9, minute=0),
        },
        # Cleanup old data every day at 2 AM
        'cleanup-old-data': {
            'task': 'app.workers.tasks.cleanup_old_data',
            'schedule': crontab(hour=2, minute=0),
        },
        # Process stored leads every minute
        'process-stored-leads': {
            'task': 'app.workers.tasks.process_stored_leads_task',
            'schedule': 60.0,  # Every 60 seconds
        },
    },
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    'app.workers.tasks.send_email_task': {'queue': 'email'},
    'app.workers.tasks.send_webhook_task': {'queue': 'webhook'},
    'app.workers.tasks.distribute_leads_task': {'queue': 'distribution'},
}
