"""
Auth Routes — Registration, Login, Profile.

Uses bcrypt for password hashing and JWT (python-jose) for tokens.
"""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.capability import initialize_capability_matrix
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, username: str) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRY_HOURS)
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency: extract and validate JWT from Authorization header.
    Returns the authenticated User.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = auth_header[7:]  # Strip "Bearer "

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = int(payload.get("sub", 0))
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


@router.post("/register", response_model=TokenResponse)
async def register(
    body: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account."""
    # Check if username exists
    existing = await db.execute(
        select(User).where(User.username == body.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Check if email exists
    existing_email = await db.execute(
        select(User).where(User.email == body.email)
    )
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Initialize capability matrix from knowledge graph
    kg = request.app.state.knowledge_graph
    cap_matrix = initialize_capability_matrix(kg)

    user = User(
        username=body.username,
        email=body.email,
        password_hash=hash_password(body.password),
        capability_matrix=cap_matrix,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token(user.id, user.username)

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate and receive a JWT token."""
    result = await db.execute(
        select(User).where(User.username == body.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(user.id, user.username)

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return UserResponse.model_validate(current_user)
