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
    id: int
    release_id: str
    title: str
    artist: str
    created_at: datetime
    updated_at: datetime
    

class TrackSummary(BaseModel):
    id: int
    title: str
    artist: str
    track_number: int

    class Config:
        from_attributes = True

class ReleaseAssetSummary(BaseModel):
    id: int
    asset_type: str
    file_name: str

    class Config:
        from_attributes = True

# ---
# If you need to add recursive/self-referencing fields to this schema (e.g., sub_releases: List['ReleaseOut']),
# use a string type hint and call ReleaseOut.model_rebuild() after the class definition.
# Example:
#   sub_releases: List['ReleaseOut'] = []
#   ...
# ReleaseOut.model_rebuild()
# ---
class ReleaseOut(BaseModel):
    id: int
    release_id: str
    title: str
    artist: str
    created_at: datetime
    updated_at: datetime
    # tracks: List[TrackSummary] = []  # Temporarily commented out to test for RecursionError
    # assets: List[ReleaseAssetSummary] = []  # Temporarily commented out to test for RecursionError

    class Config:
        from_attributes = True
