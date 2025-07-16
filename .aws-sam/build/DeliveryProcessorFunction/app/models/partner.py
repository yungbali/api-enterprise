"""
Partner Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class PartnerStatus(enum.Enum):
    """Partner status enum."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class PartnerType(enum.Enum):
    """Partner type enum."""
    DSP = "dsp"  # Digital Service Provider
    AGGREGATOR = "aggregator"
    DISTRIBUTOR = "distributor"
    PLATFORM = "platform"


class AuthType(enum.Enum):
    """Authentication type enum."""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    CUSTOM = "custom"


class DeliveryPartner(Base):
    """Delivery partner model."""
    __tablename__ = "delivery_partners"
    
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    display_name = Column(String(200))
    
    # Partner info
    partner_type = Column(Enum(PartnerType), default=PartnerType.DSP)
    description = Column(Text)
    website = Column(String(500))
    contact_email = Column(String(200))
    
    # API Configuration
    api_base_url = Column(String(500), nullable=False)
    api_version = Column(String(20))
    auth_type = Column(Enum(AuthType), default=AuthType.API_KEY)
    
    # Delivery settings
    delivery_url = Column(String(500), nullable=False)
    callback_url = Column(String(500))
    supported_formats = Column(JSON)  # Array of supported audio formats
    supported_territories = Column(JSON)  # Array of supported territories
    
    # Status and configuration
    status = Column(Enum(PartnerStatus), default=PartnerStatus.ACTIVE)
    priority = Column(Integer, default=0)  # Higher number = higher priority
    auto_deliver = Column(Boolean, default=True)
    
    # Rate limiting
    rate_limit_requests = Column(Integer, default=100)
    rate_limit_window = Column(Integer, default=3600)  # in seconds
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_health_check = Column(DateTime)
    
    # Relationships
    configs = relationship("PartnerConfig", back_populates="partner", cascade="all, delete-orphan")
    delivery_statuses = relationship("DeliveryStatus", back_populates="partner")
    
    def __repr__(self):
        return f"<DeliveryPartner(id={self.id}, name='{self.name}', status='{self.status}')>"


class PartnerConfig(Base):
    """Partner configuration model for storing sensitive config data."""
    __tablename__ = "partner_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("delivery_partners.id"), nullable=False)
    
    # Configuration
    config_key = Column(String(100), nullable=False)
    config_value = Column(Text)  # Encrypted sensitive data
    config_type = Column(String(50), default="string")  # string, integer, boolean, json
    
    # Metadata
    description = Column(Text)
    is_sensitive = Column(Boolean, default=False)
    is_required = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    partner = relationship("DeliveryPartner", back_populates="configs")
    
    def __repr__(self):
        return f"<PartnerConfig(id={self.id}, key='{self.config_key}', partner_id={self.partner_id})>"
