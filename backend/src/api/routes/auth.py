"""
Authentication API routes for user registration, login, and token management.

This module handles user authentication flows including registration, login,
token refresh, and retrieving the current user profile.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import logging

from src.core.security import (
    hash_password,
    verify_password,
    generate_token,
    validate_token,
    get_current_user,
    UserContext,
    TokenResponse,
)
from src.core.database import get_db
from src.models.user_profile import UserProfile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    """User registration request model."""
    email: EmailStr
    password: str = Field(..., min_length=8,
                          description="Password must be at least 8 characters")


class LoginRequest(BaseModel):
    """User login request model."""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class UserResponse(BaseModel):
    """User profile response model."""
    user_id: str
    email: str

    class Config:
        from_attributes = True


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Creates a new user profile with hashed password and returns JWT tokens.

    Args:
        request: Registration request with email and password
        db: Database session

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        HTTPException 400: If email already exists
    """
    # Check if user already exists
    existing_user = db.query(UserProfile).filter(
        UserProfile.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(request.password)

    new_user = UserProfile(
        id=str(uuid.uuid4()),  # Convert UUID to string for SQLite
        user_id=user_id,
        email=request.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {request.email}")

    # Generate tokens
    access_token = generate_token(user_id, request.email, token_type="access")
    refresh_token = generate_token(
        user_id, request.email, token_type="refresh")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email and password.

    Validates credentials and returns JWT tokens.

    Args:
        request: Login request with email and password
        db: Database session

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Find user by email
    user = db.query(UserProfile).filter(
        UserProfile.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    logger.info(f"User logged in: {request.email}")

    # Generate tokens
    access_token = generate_token(
        user.user_id, user.email, token_type="access")
    refresh_token = generate_token(
        user.user_id, user.email, token_type="refresh")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.

    Validates refresh token and issues new access and refresh tokens.

    Args:
        request: Refresh token request

    Returns:
        TokenResponse with new access and refresh tokens

    Raises:
        HTTPException 401: If refresh token is invalid or expired
    """
    # Validate refresh token
    token_data = validate_token(request.refresh_token, expected_type="refresh")

    logger.info(f"Token refreshed for user: {token_data.email}")

    # Generate new tokens
    access_token = generate_token(
        token_data.user_id, token_data.email, token_type="access")
    refresh_token = generate_token(
        token_data.user_id, token_data.email, token_type="refresh")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserContext = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current authenticated user's profile.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        UserResponse with user profile data

    Raises:
        HTTPException 404: If user profile not found
    """
    user = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return UserResponse(
        user_id=user.user_id,
        email=user.email
    )
