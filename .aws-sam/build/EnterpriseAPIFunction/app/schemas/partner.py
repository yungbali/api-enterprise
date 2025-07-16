"""
Partner schema definitions
"""
from typing import Optional, Dict, Any, List
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


class DeliveryPartner(BaseModel):
    """Schema for partner with delivery info"""
    id: str
    name: str
    description: Optional[str] = None
    partner_type: str
    active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Remove any nested model fields (configs, delivery_statuses, config)

    class Config:
        from_attributes = True


class DeliverySummary(BaseModel):
    id: int
    status: str

    class Config:
        from_attributes = True

# ---
# If you need to add recursive/self-referencing fields to this schema (e.g., partners: List['PartnerOut']),
# use a string type hint and call PartnerOut.model_rebuild() after the class definition.
# Example:
#   partners: List['PartnerOut'] = []
#   ...
# PartnerOut.model_rebuild()
# ---
class PartnerOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    partner_type: str
    active: bool
    # deliveries: List[DeliverySummary] = []  # Temporarily commented out to test for RecursionError    
    class Config:
        from_attributes = True
