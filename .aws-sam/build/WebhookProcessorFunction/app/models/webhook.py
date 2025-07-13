"""
Webhook Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class WebhookStatus(enum.Enum):
    """Webhook status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    SUSPENDED = "suspended"


class EventType(enum.Enum):
    """Event type enum."""
    RELEASE_CREATED = "release_created"
    RELEASE_UPDATED = "release_updated"
    RELEASE_DELIVERED = "release_delivered"
    RELEASE_LIVE = "release_live"
    RELEASE_FAILED = "release_failed"
    PARTNER_ADDED = "partner_added"
    PARTNER_UPDATED = "partner_updated"
    DELIVERY_COMPLETE = "delivery_complete"
    DELIVERY_FAILED = "delivery_failed"
    ROYALTY_REPORT_READY = "royalty_report_ready"
    TAKEDOWN_REQUESTED = "takedown_requested"
    WORKFLOW_TRIGGERED = "workflow_triggered"


class WebhookEndpoint(Base):
    """Webhook endpoint model."""
    __tablename__ = "webhook_endpoints"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Endpoint info
    name = Column(String(200), nullable=False)
    url = Column(String(1000), nullable=False)
    secret = Column(String(200))  # For signature verification
    
    # Configuration
    events = Column(JSON)  # Array of event types to listen for
    status = Column(Enum(WebhookStatus), default=WebhookStatus.ACTIVE)
    
    # Settings
    timeout_seconds = Column(Integer, default=30)
    retry_count = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=60)
    
    # Headers
    headers = Column(JSON)  # Additional headers to send
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_success = Column(DateTime)
    last_failure = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    events_sent = relationship("WebhookEvent", back_populates="endpoint", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WebhookEndpoint(id={self.id}, name='{self.name}', status='{self.status}')>"


class WebhookEventStatus(enum.Enum):
    """Webhook event status enum."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"
    ABANDONED = "abandoned"


class WebhookEvent(Base):
    """Webhook event model for tracking sent events."""
    __tablename__ = "webhook_events"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(Integer, ForeignKey("webhook_endpoints.id"), nullable=False)
    
    # Event info
    event_type = Column(Enum(EventType), nullable=False)
    event_id = Column(String(100), nullable=False)  # Unique event identifier
    payload = Column(JSON, nullable=False)
    
    # Status tracking
    status = Column(Enum(WebhookEventStatus), default=WebhookEventStatus.PENDING)
    attempt_count = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Response details
    http_status_code = Column(Integer)
    response_body = Column(Text)
    response_headers = Column(JSON)
    response_time_ms = Column(Integer)
    
    # Error details
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    sent_at = Column(DateTime)
    next_retry_at = Column(DateTime)
    
    # Relationships
    endpoint = relationship("WebhookEndpoint", back_populates="events_sent")
    
    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, event_type='{self.event_type}', status='{self.status}')>"
