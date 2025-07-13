"""
Release Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.release import ReleaseStatus, Release
from app.schemas.release import ReleaseCreate, ReleaseUpdate, ReleaseOut

router = APIRouter()


@router.post("/", response_model=ReleaseOut, status_code=status.HTTP_201_CREATED)
async def create_release(
    release_in: ReleaseCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user),
):
    """Create new release."""
    release = crud.release.create(db=db, obj_in=release_in)
    return release


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
    return release


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
    return release


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
    return release
