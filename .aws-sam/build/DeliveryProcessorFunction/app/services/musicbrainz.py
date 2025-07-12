"""
MusicBrainz API Integration Service
"""
import asyncio
import aiohttp
from typing import Optional, Dict, List, Any
from urllib.parse import quote_plus
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class MusicBrainzService:
    """Service for interacting with MusicBrainz API"""
    
    BASE_URL = "https://musicbrainz.org/ws/2"
    
    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": f"{settings.APP_NAME}/{settings.APP_VERSION} (contact@yourdomain.com)",
            "Accept": "application/json"
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a request to MusicBrainz API with rate limiting"""
        if not self.session:
            raise RuntimeError("MusicBrainzService must be used as async context manager")
        
        url = f"{self.BASE_URL}/{endpoint}"
        params["fmt"] = "json"
        
        try:
            # MusicBrainz requires 1 request per second rate limiting
            await asyncio.sleep(1)
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 503:
                    # Rate limited, wait and retry once
                    logger.warning("Rate limited by MusicBrainz, retrying after delay")
                    await asyncio.sleep(2)
                    async with self.session.get(url, params=params) as retry_response:
                        if retry_response.status == 200:
                            return await retry_response.json()
                        else:
                            logger.error(f"MusicBrainz API error after retry: {retry_response.status}")
                            return None
                else:
                    logger.error(f"MusicBrainz API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error calling MusicBrainz API: {e}")
            return None
    
    # SEARCH METHODS
    async def search_artists(self, query: str, limit: int = 25) -> Optional[Dict[str, Any]]:
        """Search for artists by name"""
        params = {
            "query": query,
            "limit": limit
        }
        return await self._make_request("artist", params)
    
    async def search_releases(self, query: str, limit: int = 25) -> Optional[Dict[str, Any]]:
        """Search for releases (albums) by name"""
        params = {
            "query": query,
            "limit": limit
        }
        return await self._make_request("release", params)
    
    async def search_recordings(self, query: str, limit: int = 25) -> Optional[Dict[str, Any]]:
        """Search for recordings (tracks) by name"""
        params = {
            "query": query,
            "limit": limit
        }
        return await self._make_request("recording", params)
    
    async def search_release_groups(self, query: str, limit: int = 25) -> Optional[Dict[str, Any]]:
        """Search for release groups by name"""
        params = {
            "query": query,
            "limit": limit
        }
        return await self._make_request("release-group", params)
    
    # LOOKUP METHODS
    async def get_artist(self, mbid: str, inc: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get artist by MBID"""
        params = {}
        if inc:
            params["inc"] = "+".join(inc)
        return await self._make_request(f"artist/{mbid}", params)
    
    async def get_release(self, mbid: str, inc: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get release by MBID"""
        params = {}
        if inc:
            params["inc"] = "+".join(inc)
        return await self._make_request(f"release/{mbid}", params)
    
    async def get_recording(self, mbid: str, inc: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get recording by MBID"""
        params = {}
        if inc:
            params["inc"] = "+".join(inc)
        return await self._make_request(f"recording/{mbid}", params)
    
    async def get_release_group(self, mbid: str, inc: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get release group by MBID"""
        params = {}
        if inc:
            params["inc"] = "+".join(inc)
        return await self._make_request(f"release-group/{mbid}", params)
    
    # BROWSE METHODS
    async def browse_artist_releases(self, artist_mbid: str, limit: int = 50) -> Optional[Dict[str, Any]]:
        """Get all releases by an artist"""
        params = {
            "artist": artist_mbid,
            "limit": limit,
            "inc": "release-groups"
        }
        return await self._make_request("release", params)
    
    async def browse_artist_release_groups(self, artist_mbid: str, limit: int = 50) -> Optional[Dict[str, Any]]:
        """Get all release groups by an artist"""
        params = {
            "artist": artist_mbid,
            "limit": limit
        }
        return await self._make_request("release-group", params)
    
    async def browse_release_recordings(self, release_mbid: str) -> Optional[Dict[str, Any]]:
        """Get all recordings (tracks) in a release"""
        params = {
            "release": release_mbid,
            "inc": "artist-credits+isrcs"
        }
        return await self._make_request("recording", params)
    
    # ADVANCED SEARCH METHODS
    async def search_artist_by_name_exact(self, name: str) -> Optional[Dict[str, Any]]:
        """Search for artist with exact name match"""
        query = f'artist:"{name}"'
        return await self.search_artists(query, limit=10)
    
    async def search_release_by_artist_and_title(self, artist: str, title: str) -> Optional[Dict[str, Any]]:
        """Search for release by artist and title"""
        query = f'artist:"{artist}" AND release:"{title}"'
        return await self.search_releases(query, limit=10)
    
    async def search_recording_by_artist_and_title(self, artist: str, title: str) -> Optional[Dict[str, Any]]:
        """Search for recording by artist and title"""
        query = f'artist:"{artist}" AND recording:"{title}"'
        return await self.search_recordings(query, limit=10)
    
    # UTILITY METHODS
    async def get_artist_discography(self, artist_mbid: str) -> Dict[str, Any]:
        """Get complete artist discography with detailed information"""
        try:
            # Get artist info
            artist_data = await self.get_artist(artist_mbid, inc=["aliases", "tags", "genres"])
            
            # Get release groups (albums)
            release_groups_data = await self.browse_artist_release_groups(artist_mbid)
            
            # Get individual releases
            releases_data = await self.browse_artist_releases(artist_mbid)
            
            return {
                "artist": artist_data,
                "release_groups": release_groups_data,
                "releases": releases_data,
                "total_release_groups": release_groups_data.get("release-group-count", 0) if release_groups_data else 0,
                "total_releases": releases_data.get("release-count", 0) if releases_data else 0
            }
        except Exception as e:
            logger.error(f"Error getting artist discography: {e}")
            return {}
    
    async def get_release_details(self, release_mbid: str) -> Dict[str, Any]:
        """Get detailed release information including tracks"""
        try:
            # Get release info
            release_data = await self.get_release(
                release_mbid, 
                inc=["artists", "release-groups", "media", "recordings", "artist-credits", "labels"]
            )
            
            # Get recordings separately for more details
            recordings_data = await self.browse_release_recordings(release_mbid)
            
            return {
                "release": release_data,
                "recordings": recordings_data,
                "track_count": recordings_data.get("recording-count", 0) if recordings_data else 0
            }
        except Exception as e:
            logger.error(f"Error getting release details: {e}")
            return {}

# Singleton instance
musicbrainz_service = MusicBrainzService()
