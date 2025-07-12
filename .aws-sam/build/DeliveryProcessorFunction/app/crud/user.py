"""
User CRUD Operations
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User."""
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create new user with hashed password."""
        user_data = obj_in.dict(exclude={"password"})
        user_data["hashed_password"] = get_password_hash(obj_in.password)
        
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user = CRUDUser(User)
