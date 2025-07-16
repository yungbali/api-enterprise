"""
User Schemas
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    """Schema for creating a user."""
    email: EmailStr
    username: Optional[str] = Field(None, max_length=100)
    full_name: Optional[str] = Field(None, max_length=200)
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.VIEWER
    company: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)
    timezone: str = "UTC"
    preferences: Optional[Dict[str, Any]] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = Field(None, max_length=100)
    full_name: Optional[str] = Field(None, max_length=200)
    role: Optional[UserRole] = None
    company: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class User(BaseModel):
    """Schema for user response."""
    id: int
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    role: UserRole
    company: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str
