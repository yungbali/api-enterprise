"""
Enterprise Suite API - Simplified Main Application for Testing
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog
from contextlib import asynccontextmanager

# Simple settings for testing
class Settings:
    APP_NAME = "Enterprise Suite API"
    APP_VERSION = "1.0.0"
    API_V1_STR = "/api/v1"
    DEBUG = True
    CORS_ORIGINS = ["*"]

settings = Settings()

# Setup simple logging
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Enterprise Suite API")
    yield
    # Shutdown
    logger.info("Shutting down Enterprise Suite API")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API-first backend for automating music distribution workflows",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple API endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Enterprise Suite API",
        "version": settings.APP_VERSION,
        "status": "active",
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "services": {
            "api": "healthy",
        },
    }

# Basic API endpoints for testing
@app.get(f"{settings.API_V1_STR}/")
async def api_root():
    """API v1 root endpoint."""
    return {
        "message": "Enterprise Suite API v1",
        "version": settings.API_V1_STR,
        "endpoints": [
            "/auth",
            "/releases", 
            "/delivery-partners",
            "/delivery",
            "/analytics",
            "/webhooks",
            "/workflow",
            "/musicbrainz"
        ]
    }

@app.get(f"{settings.API_V1_STR}/releases")
async def list_releases():
    """List releases endpoint."""
    return {
        "message": "Releases endpoint",
        "releases": [],
        "total": 0
    }

@app.post(f"{settings.API_V1_STR}/releases")
async def create_release(request: Request):
    """Create release endpoint."""
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    return {
        "message": "Release created",
        "release_id": "test-123",
        "status": "created",
        "data": body
    }

@app.get(f"{settings.API_V1_STR}/delivery-partners")
async def list_partners():
    """List delivery partners endpoint."""
    return {
        "message": "Delivery partners endpoint",
        "partners": [
            {"id": "spotify", "name": "Spotify", "status": "active"},
            {"id": "apple-music", "name": "Apple Music", "status": "active"},
            {"id": "youtube-music", "name": "YouTube Music", "status": "active"},
        ]
    }

@app.get(f"{settings.API_V1_STR}/analytics")
async def analytics():
    """Analytics endpoint."""
    return {
        "message": "Analytics endpoint",
        "stats": {
            "total_releases": 42,
            "active_partners": 15,
            "successful_deliveries": 234
        }
    }

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
        },
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
