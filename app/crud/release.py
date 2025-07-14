"""
Release CRUD Operations
"""
from typing import Optional
from sqlalchemy.orm import Session
import uuid

from app.crud.base import CRUDBase
from app.models.release import Release
from app.schemas.release import ReleaseCreate, ReleaseUpdate


class CRUDRelease(CRUDBase[Release, ReleaseCreate, ReleaseUpdate]):
    """CRUD operations for Release."""
    
    def create(self, db: Session, *, obj_in: ReleaseCreate) -> Release:
        """Create new release with auto-generated release_id."""
        # Generate unique release ID
        release_id = f"RL{uuid.uuid4().hex[:8].upper()}"
        
        # Create release data
        release_data = obj_in.dict()
        release_data["release_id"] = release_id
        
        # Create release
        db_release = Release(**release_data)
        db.add(db_release)
        db.commit()
        db.refresh(db_release)
        return db_release
    
    def get_by_release_id(self, db: Session, *, release_id: str) -> Optional[Release]:
        """Get release by release_id."""
        return db.query(Release).filter(Release.release_id == release_id).first()


release = CRUDRelease(Release)
