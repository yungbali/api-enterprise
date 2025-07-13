"""
Delivery Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class DeliveryStatusEnum(enum.Enum):
    """Delivery status enum."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    LIVE = "live"
    FAILED = "failed"
    REJECTED = "rejected"
    TAKEDOWN = "takedown"
    SUSPENDED = "suspended"


class DeliveryStatus(Base):
    """Delivery status model for tracking release delivery to partners."""
    __tablename__ = "delivery_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("delivery_partners.id"), nullable=False)
    
    # Status tracking
    status = Column(Enum(DeliveryStatusEnum), default=DeliveryStatusEnum.PENDING)
    external_id = Column(String(200))  # Partner's internal ID for this release
    external_status = Column(String(100))  # Partner's status
    
    # Delivery metadata
    delivery_message = Column(Text)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    delivered_at = Column(DateTime)
    live_at = Column(DateTime)
    failed_at = Column(DateTime)
    next_retry_at = Column(DateTime)
    
    # Relationships
    release = relationship("Release", back_populates="delivery_statuses")
    partner = relationship("DeliveryPartner", back_populates="delivery_statuses")
    attempts = relationship("DeliveryAttempt", back_populates="delivery_status", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DeliveryStatus(id={self.id}, release_id={self.release_id}, partner_id={self.partner_id}, status='{self.status}')>"


class AttemptStatus(enum.Enum):
    """Delivery attempt status enum."""
    STARTED = "started"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RETRYING = "retrying"


class DeliveryAttempt(Base):
    """Delivery attempt model for tracking individual delivery attempts."""
    __tablename__ = "delivery_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    delivery_status_id = Column(Integer, ForeignKey("delivery_statuses.id"), nullable=False)
    
    # Attempt info
    attempt_number = Column(Integer, nullable=False)
    status = Column(Enum(AttemptStatus), default=AttemptStatus.STARTED)
    
    # Request/Response details
    request_payload = Column(JSON)
    response_payload = Column(JSON)
    http_status_code = Column(Integer)
    response_time_ms = Column(Float)
    
    # Error details
    error_type = Column(String(100))
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Timestamps
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    # Relationships
    delivery_status = relationship("DeliveryStatus", back_populates="attempts")
    
    def __repr__(self):
        return f"<DeliveryAttempt(id={self.id}, attempt_number={self.attempt_number}, status='{self.status}')>"
