"""
Authentication Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserLogin
from app.crud.user import user as crud_user
from app.core.security import create_access_token
from app.core.database import get_db

router = APIRouter()


@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = crud_user.authenticate(db, email=login_data.email, password=login_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout():
    """User logout endpoint."""
    return {"message": "Logout endpoint - implementation pending"}


@router.post("/refresh")
async def refresh_token():
    """Refresh JWT token."""
    return {"message": "Refresh token endpoint - implementation pending"}
