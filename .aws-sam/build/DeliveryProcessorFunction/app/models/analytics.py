"""
Analytics Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class AnalyticsData(Base):
    """Analytics data model for storing normalized streaming and sales data."""
    __tablename__ = "analytics_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiers
    isrc = Column(String(12), index=True, nullable=False)
    release_id = Column(Integer, ForeignKey("releases.id"))
    partner_id = Column(Integer, ForeignKey("delivery_partners.id"))
    
    # Metadata
    track_title = Column(String(500))
    artist_name = Column(String(500))
    release_title = Column(String(500))
    partner_name = Column(String(200))
    
    # Metrics
    stream_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    revenue_usd = Column(Float, default=0.0)
    revenue_local = Column(Float, default=0.0)
    local_currency = Column(String(3))  # Currency code
    
    # Geographic data
    region = Column(String(10))  # Country/region code
    city = Column(String(100))
    
    # Temporal data
    report_date = Column(Date, nullable=False)
    period_start = Column(Date)
    period_end = Column(Date)
    
    # Raw data
    raw_data = Column(JSON)  # Original data from partner
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    release = relationship("Release")
    partner = relationship("DeliveryPartner")
    
    def __repr__(self):
        return f"<AnalyticsData(id={self.id}, isrc='{self.isrc}', streams={self.stream_count}, revenue={self.revenue_usd})>"


class ReportType(enum.Enum):
    """Report type enum."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ReportStatus(enum.Enum):
    """Report status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RevenueReport(Base):
    """Revenue report model for aggregated revenue data."""
    __tablename__ = "revenue_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Report info
    report_type = Column(Enum(ReportType), nullable=False)
    report_period = Column(String(20), nullable=False)  # e.g., "2024-01", "2024-Q1"
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    
    # Aggregated data
    total_streams = Column(Integer, default=0)
    total_downloads = Column(Integer, default=0)
    total_revenue_usd = Column(Float, default=0.0)
    unique_tracks = Column(Integer, default=0)
    unique_releases = Column(Integer, default=0)
    unique_partners = Column(Integer, default=0)
    
    # Breakdown data
    revenue_by_partner = Column(JSON)  # Partner-wise revenue breakdown
    revenue_by_territory = Column(JSON)  # Territory-wise revenue breakdown
    top_tracks = Column(JSON)  # Top performing tracks
    
    # File info
    report_file_url = Column(String(1000))
    report_file_size = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    generated_at = Column(DateTime)
    
    def __repr__(self):
        return f"<RevenueReport(id={self.id}, type='{self.report_type}', period='{self.report_period}')>"
