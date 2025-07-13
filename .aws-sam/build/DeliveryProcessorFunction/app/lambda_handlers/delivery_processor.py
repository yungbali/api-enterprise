"""
Delivery Processor Lambda Handler
"""
import json
import boto3
from typing import Dict, Any
import structlog

from app.services.delivery_engine import DeliveryEngine
from app.core.database import SessionLocal
from app.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = structlog.get_logger("delivery_processor")

# Initialize AWS clients
eventbridge = boto3.client('events')
sns = boto3.client('sns')


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process delivery events from EventBridge.
    
    Event structure:
    {
        "source": "enterprise-suite",
        "detail-type": "Release Delivery",
        "detail": {
            "release_id": "RL123456",
            "partner_ids": ["partner1", "partner2"],
            "action": "deliver"
        }
    }
    """
    logger.info("Processing delivery event", event=event)
    
    try:
        # Extract event details
        detail = event.get('detail', {})
        release_id = detail.get('release_id')
        partner_ids = detail.get('partner_ids', [])
        action = detail.get('action', 'deliver')
        
        if not release_id:
            logger.error("Missing release_id in event", event=event)
            return {"statusCode": 400, "body": "Missing release_id"}
        
        # Process delivery
        with SessionLocal() as db:
            delivery_engine = DeliveryEngine(db)
            
            if action == "deliver":
                results = delivery_engine.process_delivery(release_id, partner_ids)
                logger.info("Delivery processed", release_id=release_id, results=results)
                
                # Send success notification
                for result in results:
                    if result.get('status') == 'success':
                        await send_delivery_notification(result)
                    
            elif action == "retry":
                results = delivery_engine.retry_failed_deliveries(release_id, partner_ids)
                logger.info("Retry processed", release_id=release_id, results=results)
                
            elif action == "takedown":
                results = delivery_engine.process_takedown(release_id, partner_ids)
                logger.info("Takedown processed", release_id=release_id, results=results)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Delivery processing completed",
                "release_id": release_id,
                "results": results
            })
        }
        
    except Exception as e:
        logger.error("Error processing delivery event", error=str(e), event=event)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }


async def send_delivery_notification(result: Dict[str, Any]):
    """Send delivery notification via SNS."""
    try:
        message = {
            "event_type": "delivery_complete",
            "release_id": result.get("release_id"),
            "partner_id": result.get("partner_id"),
            "partner_name": result.get("partner_name"),
            "status": result.get("status"),
            "external_id": result.get("external_id"),
            "timestamp": result.get("timestamp")
        }
        
        # Get SNS topic ARN from environment
        import os
        topic_arn = os.environ.get('DELIVERY_TOPIC_ARN')
        
        if topic_arn:
            sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message),
                Subject="Release Delivery Complete"
            )
            logger.info("Delivery notification sent", message=message)
        
    except Exception as e:
        logger.error("Error sending delivery notification", error=str(e), result=result)
