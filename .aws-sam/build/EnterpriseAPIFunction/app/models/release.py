"""
Release Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class ReleaseStatus(enum.Enum):
    """Release status enum."""
    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"
    DELIVERED = "delivered"
    LIVE = "live"
    FAILED = "failed"
    TAKEDOWN = "takedown"


class ReleaseType(enum.Enum):
    """Release type enum."""
    SINGLE = "single"
    ALBUM = "album"
    EP = "ep"
    COMPILATION = "compilation"


class Release(Base):
    """Release model."""
    __tablename__ = "releases"
    
    id = Column(Integer, primary_key=True, index=True)
    release_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(500), nullable=False)
    artist = Column(String(500), nullable=False)
    label = Column(String(500))
    release_type = Column(Enum(ReleaseType), default=ReleaseType.SINGLE)
    release_date = Column(DateTime)
    original_release_date = Column(DateTime)
    
    # DDEX Fields
    grid = Column(String(50))  # Global Release Identifier
    upc = Column(String(20))   # Universal Product Code
    catalog_number = Column(String(50))
    genre = Column(String(100))
    subgenre = Column(String(100))
    
    # Metadata
    description = Column(Text)
    copyright_text = Column(Text)
    producer_copyright_text = Column(Text)
    language = Column(String(10))
    territory = Column(String(10))
    
    # Status and tracking
    status = Column(Enum(ReleaseStatus), default=ReleaseStatus.DRAFT)
    validation_status = Column(String(50), default="pending")
    validation_errors = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    tracks = relationship("Track", back_populates="release", cascade="all, delete-orphan")
    assets = relationship("ReleaseAsset", back_populates="release", cascade="all, delete-orphan")
    delivery_statuses = relationship("DeliveryStatus", back_populates="release")
    
    def __repr__(self):
        return f"<Release(id={self.id}, title='{self.title}', artist='{self.artist}')>"


class Track(Base):
    """Track model."""
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=False)
    
    # Track info
    title = Column(String(500), nullable=False)
    artist = Column(String(500), nullable=False)
    featured_artists = Column(JSON)  # Array of featured artists
    track_number = Column(Integer, nullable=False)
    duration_ms = Column(Integer)  # Duration in milliseconds
    
    # Identifiers
    isrc = Column(String(12), unique=True, index=True)  # International Standard Recording Code
    
    # Metadata
    composers = Column(JSON)  # Array of composers
    publishers = Column(JSON)  # Array of publishers
    explicit = Column(Boolean, default=False)
    genre = Column(String(100))
    language = Column(String(10))
    
    # Audio file info
    audio_file_url = Column(String(1000))
    audio_file_format = Column(String(50))  # mp3, wav, flac, etc.
    audio_file_size = Column(Integer)
    audio_bitrate = Column(Integer)
    audio_sample_rate = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    release = relationship("Release", back_populates="tracks")
    
    def __repr__(self):
        return f"<Track(id={self.id}, title='{self.title}', isrc='{self.isrc}')>"


class AssetType(enum.Enum):
    """Asset type enum."""
    ARTWORK = "artwork"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


class ReleaseAsset(Base):
    """Release asset model for storing files related to releases."""
    __tablename__ = "release_assets"
    
    id = Column(Integer, primary_key=True, index=True)
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=False)
    
    # Asset info
    asset_type = Column(Enum(AssetType), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_url = Column(String(1000), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Metadata
    title = Column(String(500))
    description = Column(Text)
    dimensions = Column(String(50))  # For images/videos: "1400x1400"
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    release = relationship("Release", back_populates="assets")
    
    def __repr__(self):
        return f"<ReleaseAsset(id={self.id}, type='{self.asset_type}', file='{self.file_name}')>"
