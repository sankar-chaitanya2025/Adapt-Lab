"""Pydantic schemas for user-related API requests and responses."""

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Request body for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Request body for user login."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Public user profile response."""
    id: int
    username: str
    email: str
    capability_matrix: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token response after login."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
