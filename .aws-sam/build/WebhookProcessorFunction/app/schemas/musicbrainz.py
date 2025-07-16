"""
MusicBrainz API Response Schemas
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import date

class MBIDArtist(BaseModel):
    """Artist reference with MBID"""
    id: str = Field(..., description="MusicBrainz ID")
    name: str = Field(..., description="Artist name")
    sort_name: Optional[str] = Field(None, description="Sort name")
    disambiguation: Optional[str] = Field(None, description="Disambiguation")

class MBIDArea(BaseModel):
    """Area (country/region) reference"""
    id: str = Field(..., description="Area MBID")
    name: str = Field(..., description="Area name")
    sort_name: Optional[str] = Field(None, description="Area sort name")

class MBIDLifeSpan(BaseModel):
    """Life span for artists or labels"""
    begin: Optional[str] = Field(None, description="Begin date")
    end: Optional[str] = Field(None, description="End date")
    ended: Optional[bool] = Field(None, description="Whether ended")

class MBIDAlias(BaseModel):
    """Alias for entities"""
    name: str = Field(..., description="Alias name")
    sort_name: Optional[str] = Field(None, description="Alias sort name")
    type: Optional[str] = Field(None, description="Alias type")
    primary: Optional[bool] = Field(None, description="Primary alias")

class MBIDTag(BaseModel):
    """Tag for entities"""
    count: int = Field(..., description="Tag count")
    name: str = Field(..., description="Tag name")

class MBIDArtistDetail(BaseModel):
    """Detailed artist information"""
    id: str = Field(..., description="MusicBrainz ID")
    name: str = Field(..., description="Artist name")
    sort_name: str = Field(..., description="Sort name")
    type: Optional[str] = Field(None, description="Artist type")
    type_id: Optional[str] = Field(None, description="Artist type ID")
    gender: Optional[str] = Field(None, description="Gender")
    gender_id: Optional[str] = Field(None, description="Gender ID")
    country: Optional[str] = Field(None, description="Country code")
    area: Optional[MBIDArea] = Field(None, description="Area information")
    begin_area: Optional[MBIDArea] = Field(None, description="Begin area")
    life_span: Optional[MBIDLifeSpan] = Field(None, description="Life span")
    aliases: Optional[List[MBIDAlias]] = Field(None, description="Aliases")
    tags: Optional[List[MBIDTag]] = Field(None, description="Tags")
    disambiguation: Optional[str] = Field(None, description="Disambiguation")
    score: Optional[int] = Field(None, description="Search score")

class MBIDReleaseGroup(BaseModel):
    """Release group information"""
    id: str = Field(..., description="Release group MBID")
    title: str = Field(..., description="Release group title")
    primary_type: Optional[str] = Field(None, description="Primary type")
    primary_type_id: Optional[str] = Field(None, description="Primary type ID")
    secondary_types: Optional[List[str]] = Field(None, description="Secondary types")
    first_release_date: Optional[str] = Field(None, description="First release date")
    disambiguation: Optional[str] = Field(None, description="Disambiguation")
    artist_credit: Optional[List[MBIDArtist]] = Field(None, description="Artist credits")

class MBIDTextRepresentation(BaseModel):
    """Text representation for releases"""
    language: Optional[str] = Field(None, description="Language")
    script: Optional[str] = Field(None, description="Script")

class MBIDLabel(BaseModel):
    """Label information"""
    id: str = Field(..., description="Label MBID")
    name: str = Field(..., description="Label name")
    catalog_number: Optional[str] = Field(None, description="Catalog number")

class MBIDCoverArtArchive(BaseModel):
    """Cover art archive information"""
    artwork: bool = Field(..., description="Has artwork")
    count: int = Field(..., description="Artwork count")
    front: bool = Field(..., description="Has front cover")
    back: bool = Field(..., description="Has back cover")

class MBIDRelease(BaseModel):
    """Release information"""
    id: str = Field(..., description="Release MBID")
    title: str = Field(..., description="Release title")
    status: Optional[str] = Field(None, description="Release status")
    status_id: Optional[str] = Field(None, description="Release status ID")
    packaging: Optional[str] = Field(None, description="Packaging")
    packaging_id: Optional[str] = Field(None, description="Packaging ID")
    text_representation: Optional[MBIDTextRepresentation] = Field(None, description="Text representation")
    artist_credit: Optional[List[MBIDArtist]] = Field(None, description="Artist credits")
    release_group: Optional[MBIDReleaseGroup] = Field(None, description="Release group")
    date: Optional[str] = Field(None, description="Release date")
    country: Optional[str] = Field(None, description="Country")
    barcode: Optional[str] = Field(None, description="Barcode")
    asin: Optional[str] = Field(None, description="ASIN")
    label_info: Optional[List[MBIDLabel]] = Field(None, description="Label information")
    track_count: Optional[int] = Field(None, description="Track count")
    media: Optional[List[Dict[str, Any]]] = Field(None, description="Media information")
    cover_art_archive: Optional[MBIDCoverArtArchive] = Field(None, description="Cover art archive")
    disambiguation: Optional[str] = Field(None, description="Disambiguation")
    score: Optional[int] = Field(None, description="Search score")

class MBIDRecording(BaseModel):
    """Recording information"""
    id: str = Field(..., description="Recording MBID")
    title: str = Field(..., description="Recording title")
    length: Optional[int] = Field(None, description="Length in milliseconds")
    disambiguation: Optional[str] = Field(None, description="Disambiguation")
    artist_credit: Optional[List[MBIDArtist]] = Field(None, description="Artist credits")
    isrcs: Optional[List[str]] = Field(None, description="ISRCs")
    tags: Optional[List[MBIDTag]] = Field(None, description="Tags")
    score: Optional[int] = Field(None, description="Search score")

# Search Response Schemas
class MBIDArtistSearchResponse(BaseModel):
    """Artist search response"""
    created: str = Field(..., description="Created timestamp")
    count: int = Field(..., description="Result count")
    offset: int = Field(..., description="Result offset")
    artists: List[MBIDArtistDetail] = Field(..., description="Artist results")

class MBIDReleaseSearchResponse(BaseModel):
    """Release search response"""
    created: str = Field(..., description="Created timestamp")
    count: int = Field(..., description="Result count")
    offset: int = Field(..., description="Result offset")
    releases: List[MBIDRelease] = Field(..., description="Release results")

class MBIDRecordingSearchResponse(BaseModel):
    """Recording search response"""
    created: str = Field(..., description="Created timestamp")
    count: int = Field(..., description="Result count")
    offset: int = Field(..., description="Result offset")
    recordings: List[MBIDRecording] = Field(..., description="Recording results")

class MBIDReleaseGroupSearchResponse(BaseModel):
    """Release group search response"""
    created: str = Field(..., description="Created timestamp")
    count: int = Field(..., description="Result count")
    offset: int = Field(..., description="Result offset")
    release_groups: List[MBIDReleaseGroup] = Field(alias="release-groups", description="Release group results")

# Discography Response Schema
class MBIDDiscographyResponse(BaseModel):
    """Artist discography response"""
    artist: Optional[MBIDArtistDetail] = Field(None, description="Artist information")
    release_groups: Optional[MBIDReleaseGroupSearchResponse] = Field(None, description="Release groups")
    releases: Optional[MBIDReleaseSearchResponse] = Field(None, description="Releases")
    total_release_groups: int = Field(0, description="Total release groups count")
    total_releases: int = Field(0, description="Total releases count")

# Release Details Response Schema
class MBIDReleaseDetailsResponse(BaseModel):
    """Release details response"""
    release: Optional[MBIDRelease] = Field(None, description="Release information")
    recordings: Optional[MBIDRecordingSearchResponse] = Field(None, description="Track recordings")
    track_count: int = Field(0, description="Track count")

# Simplified Response Schemas for API endpoints
class SimplifiedArtist(BaseModel):
    """Simplified artist for API responses"""
    mbid: str = Field(..., description="MusicBrainz ID")
    name: str = Field(..., description="Artist name")
    sort_name: Optional[str] = Field(None, description="Sort name")
    type: Optional[str] = Field(None, description="Artist type")
    country: Optional[str] = Field(None, description="Country")
    disambiguation: Optional[str] = Field(None, description="Disambiguation")
    score: Optional[int] = Field(None, description="Search relevance score")

class SimplifiedRelease(BaseModel):
    """Simplified release for API responses"""
    mbid: str = Field(..., description="MusicBrainz ID")
    title: str = Field(..., description="Release title")
    artist: str = Field(..., description="Primary artist name")
    date: Optional[str] = Field(None, description="Release date")
    country: Optional[str] = Field(None, description="Country")
    status: Optional[str] = Field(None, description="Release status")
    track_count: Optional[int] = Field(None, description="Track count")
    barcode: Optional[str] = Field(None, description="Barcode")
    score: Optional[int] = Field(None, description="Search relevance score")

class SimplifiedRecording(BaseModel):
    """Simplified recording for API responses"""
    mbid: str = Field(..., description="MusicBrainz ID")
    title: str = Field(..., description="Recording title")
    artist: str = Field(..., description="Primary artist name")
    length: Optional[int] = Field(None, description="Length in milliseconds")
    length_formatted: Optional[str] = Field(None, description="Formatted length (mm:ss)")
    disambiguation: Optional[str] = Field(None, description="Disambiguation")
    score: Optional[int] = Field(None, description="Search relevance score")

class MusicBrainzSearchResponse(BaseModel):
    """Generic MusicBrainz search response"""
    query: str = Field(..., description="Search query")
    results_type: str = Field(..., description="Type of results")
    count: int = Field(..., description="Number of results")
    artists: Optional[List[SimplifiedArtist]] = Field(None, description="Artist results")
    releases: Optional[List[SimplifiedRelease]] = Field(None, description="Release results")  
    recordings: Optional[List[SimplifiedRecording]] = Field(None, description="Recording results")
