"""
Partner schema definitions
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PartnerConfig(BaseModel):
    """Partner configuration schema"""
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    auth_method: Optional[str] = "api_key"
    metadata_format: Optional[str] = "json"
    supported_formats: Optional[list] = []
    
    class Config:
        from_attributes = True


class PartnerBase(BaseModel):
    """Base partner schema"""
    name: str = Field(..., description="Partner name")
    description: Optional[str] = None
    partner_type: str = Field(..., description="Type of partner (dsp, aggregator, etc.)")
    active: bool = True
    config: Optional[PartnerConfig] = None


class PartnerCreate(PartnerBase):
    """Schema for creating a partner"""
    pass


class PartnerUpdate(BaseModel):
    """Schema for updating a partner"""
    name: Optional[str] = None
    description: Optional[str] = None
    partner_type: Optional[str] = None
    active: Optional[bool] = None
    config: Optional[PartnerConfig] = None


class DeliveryPartner(PartnerBase):
    """Schema for partner with delivery info"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        # Exclude relationships that could cause circular references
        exclude = {"configs", "delivery_statuses"}
