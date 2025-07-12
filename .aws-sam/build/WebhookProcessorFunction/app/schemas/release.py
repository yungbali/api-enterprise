"""
Release Schemas
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.release import ReleaseStatus, ReleaseType, AssetType


class TrackCreate(BaseModel):
    """Schema for creating a track."""
    title: str = Field(..., max_length=500)
    artist: str = Field(..., max_length=500)
    featured_artists: Optional[List[str]] = None
    track_number: int = Field(..., ge=1)
    duration_ms: Optional[int] = Field(None, ge=0)
    isrc: Optional[str] = Field(None, max_length=12)
    composers: Optional[List[str]] = None
    publishers: Optional[List[str]] = None
    explicit: bool = False
    genre: Optional[str] = Field(None, max_length=100)
    language: Optional[str] = Field(None, max_length=10)
    audio_file_url: Optional[str] = Field(None, max_length=1000)
    audio_file_format: Optional[str] = Field(None, max_length=50)
    audio_file_size: Optional[int] = Field(None, ge=0)
    audio_bitrate: Optional[int] = Field(None, ge=0)
    audio_sample_rate: Optional[int] = Field(None, ge=0)


class Track(TrackCreate):
    """Schema for track response."""
    id: int
    release_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReleaseAssetCreate(BaseModel):
    """Schema for creating a release asset."""
    asset_type: AssetType
    file_name: str = Field(..., max_length=500)
    file_url: str = Field(..., max_length=1000)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    dimensions: Optional[str] = Field(None, max_length=50)


class ReleaseAsset(ReleaseAssetCreate):
    """Schema for release asset response."""
    id: int
    release_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReleaseCreate(BaseModel):
    """Schema for creating a release."""
    title: str = Field(..., max_length=500)
    artist: str = Field(..., max_length=500)
    label: Optional[str] = Field(None, max_length=500)
    release_type: ReleaseType = ReleaseType.SINGLE
    release_date: Optional[datetime] = None
    original_release_date: Optional[datetime] = None
    
    # DDEX Fields
    grid: Optional[str] = Field(None, max_length=50)
    upc: Optional[str] = Field(None, max_length=20)
    catalog_number: Optional[str] = Field(None, max_length=50)
    genre: Optional[str] = Field(None, max_length=100)
    subgenre: Optional[str] = Field(None, max_length=100)
    
    # Metadata
    description: Optional[str] = None
    copyright_text: Optional[str] = None
    producer_copyright_text: Optional[str] = None
    language: Optional[str] = Field(None, max_length=10)
    territory: Optional[str] = Field(None, max_length=10)
    
    # Related data
    tracks: List[TrackCreate] = Field(default_factory=list)
    assets: List[ReleaseAssetCreate] = Field(default_factory=list)


class ReleaseUpdate(BaseModel):
    """Schema for updating a release."""
    title: Optional[str] = Field(None, max_length=500)
    artist: Optional[str] = Field(None, max_length=500)
    label: Optional[str] = Field(None, max_length=500)
    release_type: Optional[ReleaseType] = None
    release_date: Optional[datetime] = None
    original_release_date: Optional[datetime] = None
    
    # DDEX Fields
    grid: Optional[str] = Field(None, max_length=50)
    upc: Optional[str] = Field(None, max_length=20)
    catalog_number: Optional[str] = Field(None, max_length=50)
    genre: Optional[str] = Field(None, max_length=100)
    subgenre: Optional[str] = Field(None, max_length=100)
    
    # Metadata
    description: Optional[str] = None
    copyright_text: Optional[str] = None
    producer_copyright_text: Optional[str] = None
    language: Optional[str] = Field(None, max_length=10)
    territory: Optional[str] = Field(None, max_length=10)
    
    # Status
    status: Optional[ReleaseStatus] = None


class Release(BaseModel):
    """Schema for release response."""
    id: int
    release_id: str
    title: str
    artist: str
    label: Optional[str] = None
    release_type: ReleaseType
    release_date: Optional[datetime] = None
    original_release_date: Optional[datetime] = None
    
    # DDEX Fields
    grid: Optional[str] = None
    upc: Optional[str] = None
    catalog_number: Optional[str] = None
    genre: Optional[str] = None
    subgenre: Optional[str] = None
    
    # Metadata
    description: Optional[str] = None
    copyright_text: Optional[str] = None
    producer_copyright_text: Optional[str] = None
    language: Optional[str] = None
    territory: Optional[str] = None
    
    # Status and tracking
    status: ReleaseStatus
    validation_status: str
    validation_errors: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # Related data
    tracks: List[Track] = Field(default_factory=list)
    assets: List[ReleaseAsset] = Field(default_factory=list)

    class Config:
        from_attributes = True
