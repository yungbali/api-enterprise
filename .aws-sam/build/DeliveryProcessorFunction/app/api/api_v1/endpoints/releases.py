"""
Release Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.release import ReleaseStatus, Release
from app.schemas.release import ReleaseCreate, ReleaseUpdate, ReleaseOut, TrackSummary, ReleaseAssetSummary

router = APIRouter()


@router.post("/", response_model=ReleaseOut, status_code=status.HTTP_201_CREATED)
async def create_release(
    release_in: ReleaseCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """Create new release."""
    release = crud.release.create(db=db, obj_in=release_in)
    return ReleaseOut(
        id=release.id,
        release_id=release.release_id,
        title=release.title,
        artist=release.artist,
        created_at=release.created_at,
        updated_at=release.updated_at,
        tracks=[
            TrackSummary(
                id=track.id,
                title=track.title,
                artist=track.artist,
                track_number=track.track_number
            ) for track in release.tracks
        ],
        assets=[
            ReleaseAssetSummary(
                id=asset.id,
                asset_type=str(asset.asset_type),
                file_name=asset.file_name
            ) for asset in release.assets
        ]
    )


@router.get("/{release_id}", response_model=ReleaseOut)
async def get_release(
    release_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """Get release by ID."""
    release = crud.release.get_by_release_id(db=db, release_id=release_id)
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found",
        )
    return ReleaseOut(
        id=release.id,
        release_id=release.release_id,
        title=release.title,
        artist=release.artist,
        created_at=release.created_at,
        updated_at=release.updated_at,
        tracks=[
            TrackSummary(
                id=track.id,
                title=track.title,
                artist=track.artist,
                track_number=track.track_number
            ) for track in release.tracks
        ],
        assets=[
            ReleaseAssetSummary(
                id=asset.id,
                asset_type=str(asset.asset_type),
                file_name=asset.file_name
            ) for asset in release.assets
        ]
    )


@router.put("/{release_id}", response_model=ReleaseOut)
async def update_release(
    release_id: str,
    release_in: ReleaseUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """Update existing release."""
    release = crud.release.get_by_release_id(db=db, release_id=release_id)
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found",
        )
    release = crud.release.update(db=db, db_obj=release, obj_in=release_in)
    return ReleaseOut(
        id=release.id,
        release_id=release.release_id,
        title=release.title,
        artist=release.artist,
        created_at=release.created_at,
        updated_at=release.updated_at,
        tracks=[
            TrackSummary(
                id=track.id,
                title=track.title,
                artist=track.artist,
                track_number=track.track_number
            ) for track in release.tracks
        ],
        assets=[
            ReleaseAssetSummary(
                id=asset.id,
                asset_type=str(asset.asset_type),
                file_name=asset.file_name
            ) for asset in release.assets
        ]
    )


@router.delete("/{release_id}", response_model=ReleaseOut)
async def delete_release(
    release_id: str,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """Delete release by ID."""
    release = crud.release.get_by_release_id(db=db, release_id=release_id)
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found",
        )
    release = crud.release.remove(db=db, id=release.id)
    return ReleaseOut(
        id=release.id,
        release_id=release.release_id,
        title=release.title,
        artist=release.artist,
        created_at=release.created_at,
        updated_at=release.updated_at,
        tracks=[
            TrackSummary(
                id=track.id,
                title=track.title,
                artist=track.artist,
                track_number=track.track_number
            ) for track in release.tracks
        ],
        assets=[
            ReleaseAssetSummary(
                id=asset.id,
                asset_type=str(asset.asset_type),
                file_name=asset.file_name
            ) for asset in release.assets
        ]
    )


@router.get("/", response_model=List[ReleaseOut])
def list_releases(db: Session = Depends(get_db)):
    return db.query(Release).all()
