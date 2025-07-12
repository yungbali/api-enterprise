"""
Delivery tasks for background processing
"""
from typing import List, Dict, Any
import structlog
from celery import current_task

from app.core.celery import celery_app
from app.core.database import SessionLocal
from app.services.delivery_engine import DeliveryEngine

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True, name="app.tasks.delivery.process_delivery")
def process_delivery(self, release_id: str, partner_ids: List[str]) -> Dict[str, Any]:
    """
    Process delivery of a release to specified partners.
    
    Args:
        release_id: ID of the release to deliver
        partner_ids: List of partner IDs to deliver to
        
    Returns:
        Dict with delivery results
    """
    logger.info("Processing delivery task", 
                release_id=release_id, 
                partner_ids=partner_ids,
                task_id=self.request.id)
    
    try:
        with SessionLocal() as db:
            delivery_engine = DeliveryEngine(db)
            results = delivery_engine.process_delivery(release_id, partner_ids)
            
            logger.info("Delivery task completed successfully",
                       release_id=release_id,
                       results_count=len(results),
                       task_id=self.request.id)
            
            return {
                "status": "success",
                "release_id": release_id,
                "results": results,
                "task_id": self.request.id
            }
            
    except Exception as e:
        logger.error("Delivery task failed",
                    release_id=release_id,
                    error=str(e),
                    task_id=self.request.id)
        
        # Retry the task with exponential backoff
        raise self.retry(
            exc=e,
            countdown=60 * (2 ** self.request.retries),
            max_retries=3
        )


@celery_app.task(bind=True, name="app.tasks.delivery.retry_failed_delivery")
def retry_failed_delivery(self, release_id: str, partner_ids: List[str]) -> Dict[str, Any]:
    """
    Retry failed delivery for a release.
    
    Args:
        release_id: ID of the release to retry
        partner_ids: List of partner IDs to retry
        
    Returns:
        Dict with retry results
    """
    logger.info("Retrying failed delivery",
                release_id=release_id,
                partner_ids=partner_ids,
                task_id=self.request.id)
    
    try:
        with SessionLocal() as db:
            delivery_engine = DeliveryEngine(db)
            results = delivery_engine.retry_failed_deliveries(release_id, partner_ids)
            
            logger.info("Retry delivery task completed",
                       release_id=release_id,
                       results_count=len(results),
                       task_id=self.request.id)
            
            return {
                "status": "success",
                "release_id": release_id,
                "results": results,
                "task_id": self.request.id
            }
            
    except Exception as e:
        logger.error("Retry delivery task failed",
                    release_id=release_id,
                    error=str(e),
                    task_id=self.request.id)
        raise


@celery_app.task(name="app.tasks.delivery.process_scheduled_deliveries")
def process_scheduled_deliveries() -> Dict[str, Any]:
    """
    Process scheduled deliveries (called by Celery Beat).
    
    Returns:
        Dict with processing results
    """
    logger.info("Processing scheduled deliveries")
    
    try:
        # This would normally query the database for scheduled deliveries
        # For now, we'll just log that it's working
        processed_count = 0
        
        logger.info("Scheduled deliveries processed",
                   processed_count=processed_count)
        
        return {
            "status": "success",
            "processed_count": processed_count,
            "message": "Scheduled deliveries processed successfully"
        }
        
    except Exception as e:
        logger.error("Failed to process scheduled deliveries", error=str(e))
        raise


@celery_app.task(bind=True, name="app.tasks.delivery.process_takedown")
def process_takedown(self, release_id: str, partner_ids: List[str]) -> Dict[str, Any]:
    """
    Process takedown of a release from specified partners.
    
    Args:
        release_id: ID of the release to takedown
        partner_ids: List of partner IDs to takedown from
        
    Returns:
        Dict with takedown results
    """
    logger.info("Processing takedown task",
                release_id=release_id,
                partner_ids=partner_ids,
                task_id=self.request.id)
    
    try:
        with SessionLocal() as db:
            delivery_engine = DeliveryEngine(db)
            results = delivery_engine.process_takedown(release_id, partner_ids)
            
            logger.info("Takedown task completed",
                       release_id=release_id,
                       results_count=len(results),
                       task_id=self.request.id)
            
            return {
                "status": "success",
                "release_id": release_id,
                "results": results,
                "task_id": self.request.id
            }
            
    except Exception as e:
        logger.error("Takedown task failed",
                    release_id=release_id,
                    error=str(e),
                    task_id=self.request.id)
        
        raise self.retry(
            exc=e,
            countdown=30 * (2 ** self.request.retries),
            max_retries=2
        )
