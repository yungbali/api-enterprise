"""
Simple test Lambda handler to test deployment
"""
from mangum import Mangum
from fastapi import FastAPI

# Create simple FastAPI app
test_app = FastAPI(title="Test API")

@test_app.get("/")
async def root():
    return {"message": "Test API Working", "status": "success"}

@test_app.get("/health")
async def health():
    return {"status": "healthy", "service": "test-api"}

@test_app.get("/musicbrainz/test")
async def test_musicbrainz():
    """Test MusicBrainz integration"""
    import aiohttp
    import asyncio
    
    async def search_artist(name: str):
        headers = {
            "User-Agent": "TestAPI/1.0 (test@example.com)",
            "Accept": "application/json"
        }
        
        url = "https://musicbrainz.org/ws/2/artist"
        params = {
            "query": name,
            "fmt": "json",
            "limit": 5
        }
        
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                await asyncio.sleep(1)  # Rate limiting
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "query": name,
                            "results_count": data.get("count", 0),
                            "artists": [{
                                "name": artist.get("name"),
                                "mbid": artist.get("id"),
                                "score": artist.get("score")
                            } for artist in data.get("artists", [])[:3]]
                        }
                    else:
                        return {"status": "error", "code": response.status}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # Test with "The Beatles"
    result = await search_artist("The Beatles")
    return result

# Create Lambda handler
handler = Mangum(test_app, lifespan="off")
