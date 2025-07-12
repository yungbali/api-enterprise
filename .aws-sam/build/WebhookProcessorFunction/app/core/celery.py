"""
Celery configuration for Enterprise Suite API
"""
import os
from celery import Celery
from kombu import Queue

from app.core.config import settings

# Create Celery instance
celery_app = Celery("enterprise_suite")

# Configure Celery
celery_app.conf.update(
    broker_url=settings.CELERY_BROKER_URL,
    result_backend=settings.CELERY_RESULT_BACKEND,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_routes={
        "app.tasks.delivery.*": {"queue": "delivery"},
        "app.tasks.webhook.*": {"queue": "webhook"},
        "app.tasks.analytics.*": {"queue": "analytics"},
        "app.tasks.default.*": {"queue": "default"},
    },
    task_default_queue="default",
    task_queues=(
        Queue("default"),
        Queue("delivery"),
        Queue("webhook"),
        Queue("analytics"),
    ),
    beat_schedule={
        "process-scheduled-deliveries": {
            "task": "app.tasks.delivery.process_scheduled_deliveries",
            "schedule": 300.0,  # Every 5 minutes
        },
        "cleanup-old-tasks": {
            "task": "app.tasks.default.cleanup_old_tasks",
            "schedule": 3600.0,  # Every hour
        },
        "generate-analytics": {
            "task": "app.tasks.analytics.generate_daily_analytics",
            "schedule": 86400.0,  # Every day
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks([
    "app.tasks.delivery",
    "app.tasks.webhook", 
    "app.tasks.analytics",
    "app.tasks.default",
])


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f"Request: {self.request!r}")
    return "Debug task completed successfully"


if __name__ == "__main__":
    celery_app.start()
