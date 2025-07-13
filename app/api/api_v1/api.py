"""
API Router Configuration
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    releases,
    partners,
    delivery,
    analytics,
    webhooks,
    auth,
    workflow,
    # musicbrainz,
)

api_router = APIRouter()

# Enable auth and releases routers for testing
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(releases.router, prefix="/releases", tags=["Releases"])
# api_router.include_router(partners.router, prefix="/delivery-partners", tags=["Delivery Partners"])
# api_router.include_router(delivery.router, prefix="/delivery", tags=["Delivery"])
# api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
# api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
# api_router.include_router(workflow.router, prefix="/workflow", tags=["Workflow"])
# api_router.include_router(musicbrainz.router, prefix="/musicbrainz", tags=["MusicBrainz"])
