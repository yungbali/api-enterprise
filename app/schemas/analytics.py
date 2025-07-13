"""
Analytics schema definitions
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date


class AnalyticsBase(BaseModel):
    """Base analytics schema"""
    metric_name: str = Field(..., description="Name of the metric")
    metric_value: float = Field(..., description="Value of the metric")
    metric_type: str = Field(..., description="Type of metric (plays, downloads, revenue, etc.)")
    date: date = Field(..., description="Date of the metric")
    
    
class AnalyticsCreate(AnalyticsBase):
    """Schema for creating analytics record"""
    release_id: Optional[str] = None
    partner_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AnalyticsUpdate(BaseModel):
    """Schema for updating analytics record"""
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    metric_type: Optional[str] = None
    date: Optional[date] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalyticsRecord(AnalyticsBase):
    """Schema for analytics record with ID"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    release_id: Optional[str] = None
    partner_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None


class AnalyticsSummary(BaseModel):
    """Schema for analytics summary"""
    model_config = ConfigDict(from_attributes=True)
    
    total_plays: int = 0
    total_downloads: int = 0
    total_streams: int = 0
    total_revenue: float = 0.0
    date_range: Optional[Dict[str, Any]] = None
    top_releases: List[Dict[str, Any]] = Field(default_factory=list)
    top_partners: List[Dict[str, Any]] = Field(default_factory=list)
