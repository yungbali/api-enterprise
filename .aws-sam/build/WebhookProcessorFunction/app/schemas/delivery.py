"""
Delivery schema definitions
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DeliveryStatusEnum(str, Enum):
    """Delivery status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class DeliveryBase(BaseModel):
    """Base delivery schema"""
    release_id: str = Field(..., description="ID of the release being delivered")
    partner_id: str = Field(..., description="ID of the delivery partner")
    delivery_type: str = Field(default="standard", description="Type of delivery")
    priority: int = Field(default=1, description="Delivery priority (1=highest)")
    metadata: Optional[Dict[str, Any]] = {}


class DeliveryCreate(DeliveryBase):
    """Schema for creating delivery"""
    scheduled_at: Optional[datetime] = None


class DeliveryUpdate(BaseModel):
    """Schema for updating delivery"""
    status: Optional[DeliveryStatusEnum] = None
    priority: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class Delivery(BaseModel):
    """Schema for delivery with tracking info"""
    id: str
    status: DeliveryStatusEnum = DeliveryStatusEnum.PENDING
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    external_id: Optional[str] = None
    # Remove any nested model fields (release, partner, attempts)
    
    class Config:
        from_attributes = True


class DeliveryBatch(BaseModel):
    """Schema for batch delivery request"""
    release_id: str
    partner_ids: List[str]
    delivery_type: str = "standard"
    priority: int = 1
    scheduled_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = {}


class DeliveryBatchResult(BaseModel):
    """Schema for batch delivery result"""
    batch_id: str
    release_id: str
    total_deliveries: int
    created_deliveries: List[str] = []
    failed_deliveries: List[Dict[str, str]] = []
    
    class Config:
        from_attributes = True


class DeliveryStats(BaseModel):
    """Schema for delivery statistics"""
    total_deliveries: int = 0
    pending_deliveries: int = 0
    processing_deliveries: int = 0
    completed_deliveries: int = 0
    failed_deliveries: int = 0
    success_rate: float = 0.0
    average_delivery_time: Optional[float] = None  # in minutes
    
    class Config:
        from_attributes = True
