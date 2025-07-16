"""
Webhook Processor Lambda Handler
"""
import json
import requests
from typing import Dict, Any
import structlog

from app.core.database import SessionLocal
from app.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = structlog.get_logger("webhook_processor")

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process webhook events from SNS.

    Event structure:
    {
        "event_type": "delivery_complete",
        "release_id": "RL123456",
        "partner_id": "partner1",
        "partner_name": "Spotify",
        "status": "success",
        "external_id": "EXT123456",
        "timestamp": "2025-07-12T15:00:00Z",
        "url": "https://example.com/webhook"
    }
    """
    logger.info("Processing webhook event", event=event)

    try:
        # Extract event details
        url = event.get('url')
        payload = {
            "event_type": event.get("event_type"),
            "release_id": event.get("release_id"),
            "partner_id": event.get("partner_id"),
            "partner_name": event.get("partner_name"),
            "status": event.get("status"),
            "external_id": event.get("external_id"),
            "timestamp": event.get("timestamp")
        }

        if not url:
            logger.error("Missing webhook URL in event", event=event)
            return {"statusCode": 400, "body": "Missing webhook URL"}

        # Send webhook notification
        response = requests.post(url, json=payload)
        response.raise_for_status()

        logger.info("Webhook notification sent", url=url, payload=payload)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Webhook processed successfully",
                "response_status": response.status_code
            })
        }

    except requests.RequestException as e:
        logger.error("Error sending webhook notification", error=str(e), url=url)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Webhook processing error",
                "message": str(e)
            })
        }
