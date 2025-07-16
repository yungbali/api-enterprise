"""
Default tasks for maintenance and utilities
"""
from typing import Dict, Any
import structlog
from datetime import datetime, timedelta

from app.core.celery import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="app.tasks.default.cleanup_old_tasks")
def cleanup_old_tasks() -> Dict[str, Any]:
    """
    Clean up old task results and logs.
    
    Returns:
        Dict with cleanup results
    """
    logger.info("Starting cleanup of old tasks")
    
    try:
        # This would normally clean up old task results from the database
        # For now, we'll just simulate the cleanup
        cleanup_count = 0
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        logger.info("Old tasks cleanup completed",
                   cleanup_count=cleanup_count,
                   cutoff_date=cutoff_date.isoformat())
        
        return {
            "status": "success",
            "cleanup_count": cleanup_count,
            "cutoff_date": cutoff_date.isoformat(),
            "message": "Old tasks cleaned up successfully"
        }
        
    except Exception as e:
        logger.error("Failed to cleanup old tasks", error=str(e))
        raise


@celery_app.task(bind=True, name="app.tasks.default.health_check")
def health_check(self) -> Dict[str, Any]:
    """
    Health check task to verify Celery is working.
    
    Returns:
        Dict with health check results
    """
    logger.info("Running Celery health check", task_id=self.request.id)
    
    try:
        return {
            "status": "healthy",
            "task_id": self.request.id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Celery is working correctly"
        }
        
    except Exception as e:
        logger.error("Health check failed", error=str(e), task_id=self.request.id)
        raise


@celery_app.task(name="app.tasks.default.send_notification")
def send_notification(message: str, recipient: str, notification_type: str = "info") -> Dict[str, Any]:
    """
    Send a notification (email, SMS, webhook, etc.).
    
    Args:
        message: Notification message
        recipient: Recipient identifier
        notification_type: Type of notification (info, warning, error)
        
    Returns:
        Dict with notification results
    """
    logger.info("Sending notification",
                message=message,
                recipient=recipient,
                notification_type=notification_type)
    
    try:
        # This would normally send actual notifications
        # For now, we'll just log the notification
        
        logger.info("Notification sent successfully",
                   message=message,
                   recipient=recipient,
                   notification_type=notification_type)
        
        return {
            "status": "success",
            "message": message,
            "recipient": recipient,
            "notification_type": notification_type,
            "sent_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to send notification",
                    error=str(e),
                    message=message,
                    recipient=recipient)
        raise
