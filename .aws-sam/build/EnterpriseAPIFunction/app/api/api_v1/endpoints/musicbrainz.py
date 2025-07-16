"""
MusicBrainz API Endpoints
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from app.services.musicbrainz import musicbrainz_service
from app.schemas.musicbrainz import (
    MusicBrainzSearchResponse,
    SimplifiedArtist,
    SimplifiedRelease,
    SimplifiedRecording,
    MBIDDiscographyResponse,
    MBIDReleaseDetailsResponse
)

router = APIRouter()

def format_length(length_ms: Optional[int]) -> Optional[str]:
    """Format length from milliseconds to mm:ss"""
    if not length_ms:
        return None
    
    total_seconds = length_ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"

def extract_primary_artist(artist_credits: Optional[List[dict]]) -> str:
    """Extract primary artist name from artist credits"""
    if not artist_credits:
        return "Unknown Artist"
    
    return artist_credits[0].get("name", "Unknown Artist")

def transform_artist_data(artist_data: dict) -> SimplifiedArtist:
    """Transform MusicBrainz artist data to simplified format"""
    return SimplifiedArtist(
        mbid=artist_data["id"],
        name=artist_data["name"],
        sort_name=artist_data.get("sort-name"),
        type=artist_data.get("type"),
        country=artist_data.get("country"),
        disambiguation=artist_data.get("disambiguation"),
        score=artist_data.get("score")
    )

def transform_release_data(release_data: dict) -> SimplifiedRelease:
    """Transform MusicBrainz release data to simplified format"""
    return SimplifiedRelease(
        mbid=release_data["id"],
        title=release_data["title"],
        artist=extract_primary_artist(release_data.get("artist-credit")),
        date=release_data.get("date"),
        country=release_data.get("country"),
        status=release_data.get("status"),
        track_count=release_data.get("track-count"),
        barcode=release_data.get("barcode"),
        score=release_data.get("score")
    )

def transform_recording_data(recording_data: dict) -> SimplifiedRecording:
    """Transform MusicBrainz recording data to simplified format"""
    length = recording_data.get("length")
    return SimplifiedRecording(
        mbid=recording_data["id"],
        title=recording_data["title"],
        artist=extract_primary_artist(recording_data.get("artist-credit")),
        length=length,
        length_formatted=format_length(length),
        disambiguation=recording_data.get("disambiguation"),
        score=recording_data.get("score")
    )

@router.get("/search", response_model=MusicBrainzSearchResponse)
async def search_musicbrainz(
    query: str = Query(..., description="Search query"),
    type: str = Query("artist", description="Search type: artist, release, recording"),
    limit: int = Query(25, ge=1, le=100, description="Maximum number of results")
):
    """
    Search MusicBrainz database for artists, releases, or recordings
    """
    async with musicbrainz_service as mb:
        try:
            if type == "artist":
                data = await mb.search_artists(query, limit)
                if not data:
                    raise HTTPException(status_code=404, detail="No artists found")
                
                artists = [transform_artist_data(artist) for artist in data.get("artists", [])]
                return MusicBrainzSearchResponse(
                    query=query,
                    results_type="artists",
                    count=len(artists),
                    artists=artists
                )
            
            elif type == "release":
                data = await mb.search_releases(query, limit)
                if not data:
                    raise HTTPException(status_code=404, detail="No releases found")
                
                releases = [transform_release_data(release) for release in data.get("releases", [])]
                return MusicBrainzSearchResponse(
                    query=query,
                    results_type="releases",
                    count=len(releases),
                    releases=releases
                )
            
            elif type == "recording":
                data = await mb.search_recordings(query, limit)
                if not data:
                    raise HTTPException(status_code=404, detail="No recordings found")
                
                recordings = [transform_recording_data(recording) for recording in data.get("recordings", [])]
                return MusicBrainzSearchResponse(
                    query=query,
                    results_type="recordings",
                    count=len(recordings),
                    recordings=recordings
                )
            
            else:
                raise HTTPException(status_code=400, detail="Invalid search type. Must be: artist, release, or recording")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MusicBrainz search failed: {str(e)}")

@router.get("/search/artists", response_model=List[SimplifiedArtist])
async def search_artists(
    q: str = Query(..., description="Artist name to search"),
    limit: int = Query(25, ge=1, le=100, description="Maximum number of results")
):
    """
    Search for artists by name
    """
    async with musicbrainz_service as mb:
        try:
            data = await mb.search_artists(q, limit)
            if not data:
                return []
            
            return [transform_artist_data(artist) for artist in data.get("artists", [])]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Artist search failed: {str(e)}")

@router.get("/search/releases", response_model=List[SimplifiedRelease])
async def search_releases(
    q: str = Query(..., description="Release title to search"),
    artist: Optional[str] = Query(None, description="Filter by artist name"),
    limit: int = Query(25, ge=1, le=100, description="Maximum number of results")
):
    """
    Search for releases by title, optionally filtered by artist
    """
    async with musicbrainz_service as mb:
        try:
            if artist:
                data = await mb.search_release_by_artist_and_title(artist, q)
            else:
                data = await mb.search_releases(q, limit)
            
            if not data:
                return []
            
            return [transform_release_data(release) for release in data.get("releases", [])]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Release search failed: {str(e)}")

@router.get("/search/recordings", response_model=List[SimplifiedRecording])
async def search_recordings(
    q: str = Query(..., description="Recording title to search"),
    artist: Optional[str] = Query(None, description="Filter by artist name"),
    limit: int = Query(25, ge=1, le=100, description="Maximum number of results")
):
    """
    Search for recordings by title, optionally filtered by artist
    """
    async with musicbrainz_service as mb:
        try:
            if artist:
                data = await mb.search_recording_by_artist_and_title(artist, q)
            else:
                data = await mb.search_recordings(q, limit)
            
            if not data:
                return []
            
            return [transform_recording_data(recording) for recording in data.get("recordings", [])]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Recording search failed: {str(e)}")

@router.get("/artist/{mbid}")
async def get_artist_details(
    mbid: str = Path(..., description="MusicBrainz Artist ID")
):
    """
    Get detailed artist information by MBID
    """
    async with musicbrainz_service as mb:
        try:
            data = await mb.get_artist(mbid, inc=["aliases", "tags", "genres"])
            if not data:
                raise HTTPException(status_code=404, detail="Artist not found")
            
            return data
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get artist details: {str(e)}")

@router.get("/artist/{mbid}/discography")
async def get_artist_discography(
    mbid: str = Path(..., description="MusicBrainz Artist ID")
):
    """
    Get complete artist discography including release groups and releases
    """
    async with musicbrainz_service as mb:
        try:
            data = await mb.get_artist_discography(mbid)
            if not data:
                raise HTTPException(status_code=404, detail="Artist discography not found")
            
            return data
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get artist discography: {str(e)}")

@router.get("/artist/{mbid}/releases", response_model=List[SimplifiedRelease])
async def get_artist_releases(
    mbid: str = Path(..., description="MusicBrainz Artist ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results")
):
    """
    Get all releases by an artist
    """
    async with musicbrainz_service as mb:
        try:
            data = await mb.browse_artist_releases(mbid, limit)
            if not data:
                return []
            
            return [transform_release_data(release) for release in data.get("releases", [])]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get artist releases: {str(e)}")

@router.get("/release/{mbid}")
async def get_release_details(
    mbid: str = Path(..., description="MusicBrainz Release ID")
):
    """
    Get detailed release information by MBID
    """
    async with musicbrainz_service as mb:
        try:
            data = await mb.get_release_details(mbid)
            if not data:
                raise HTTPException(status_code=404, detail="Release not found")
            
            return data
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get release details: {str(e)}")

@router.get("/release/{mbid}/tracks", response_model=List[SimplifiedRecording])
async def get_release_tracks(
    mbid: str = Path(..., description="MusicBrainz Release ID")
):
    """
    Get all tracks (recordings) in a release
    """
    async with musicbrainz_service as mb:
        try:
            data = await mb.browse_release_recordings(mbid)
            if not data:
                return []
            
            return [transform_recording_data(recording) for recording in data.get("recordings", [])]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get release tracks: {str(e)}")

@router.get("/recording/{mbid}")
async def get_recording_details(
    mbid: str = Path(..., description="MusicBrainz Recording ID")
):
    """
    Get detailed recording information by MBID
    """
    async with musicbrainz_service as mb:
        try:
            data = await mb.get_recording(mbid, inc=["artists", "releases", "isrcs", "tags"])
            if not data:
                raise HTTPException(status_code=404, detail="Recording not found")
            
            return data
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get recording details: {str(e)}")

# Advanced search endpoints
@router.get("/advanced/search")
async def advanced_search(
    artist_name: Optional[str] = Query(None, description="Exact artist name"),
    release_title: Optional[str] = Query(None, description="Release title"),
    recording_title: Optional[str] = Query(None, description="Recording title"),
    country: Optional[str] = Query(None, description="Country code"),
    year: Optional[int] = Query(None, description="Release year"),
    limit: int = Query(25, ge=1, le=100, description="Maximum number of results")
):
    """
    Advanced search with multiple filters
    """
    if not any([artist_name, release_title, recording_title]):
        raise HTTPException(status_code=400, detail="At least one search parameter is required")
    
    async with musicbrainz_service as mb:
        try:
            results = {
                "artists": [],
                "releases": [],
                "recordings": []
            }
            
            # Search for exact artist name
            if artist_name:
                artist_data = await mb.search_artist_by_name_exact(artist_name)
                if artist_data and "artists" in artist_data:
                    results["artists"] = [transform_artist_data(artist) for artist in artist_data["artists"]]
            
            # Search for releases
            if release_title:
                if artist_name:
                    release_data = await mb.search_release_by_artist_and_title(artist_name, release_title)
                else:
                    release_data = await mb.search_releases(release_title, limit)
                
                if release_data and "releases" in release_data:
                    releases = [transform_release_data(release) for release in release_data["releases"]]
                    
                    # Filter by country and year if specified
                    if country or year:
                        filtered_releases = []
                        for release in releases:
                            include = True
                            if country and release.country != country:
                                include = False
                            if year and release.date and not release.date.startswith(str(year)):
                                include = False
                            if include:
                                filtered_releases.append(release)
                        results["releases"] = filtered_releases
                    else:
                        results["releases"] = releases
            
            # Search for recordings
            if recording_title:
                if artist_name:
                    recording_data = await mb.search_recording_by_artist_and_title(artist_name, recording_title)
                else:
                    recording_data = await mb.search_recordings(recording_title, limit)
                
                if recording_data and "recordings" in recording_data:
                    results["recordings"] = [transform_recording_data(recording) for recording in recording_data["recordings"]]
            
            return results
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Advanced search failed: {str(e)}")
