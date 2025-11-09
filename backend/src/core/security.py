"""
Authentication and security utilities for JWT token handling and password hashing.

This module provides JWT token generation/validation and bcrypt password hashing
following the constitution's security requirements.
"""

from datetime import datetime, timedelta
from typing import Optional
import os

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT security scheme
security = HTTPBearer()
# Optional security for routes that don't require auth
optional_security = HTTPBearer(auto_error=False)

# JWT Configuration from environment
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class TokenData(BaseModel):
    """Token payload data model."""
    user_id: str
    email: str
    token_type: str  # "access" or "refresh"
    exp: datetime


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserContext:
    """
    User context for authenticated requests.

    Attributes:
        user_id: Unique user identifier
        email: User email address
        is_authenticated: Whether user is authenticated
    """

    def __init__(self, user_id: str, email: str):
        """
        Initialize user context.

        Args:
            user_id: Unique user identifier
            email: User email address
        """
        self.user_id = user_id
        self.email = email
        self.is_authenticated = True


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_token(user_id: str, email: str, token_type: str = "access") -> str:
    """
    Generate a JWT token for authentication.

    Args:
        user_id: Unique user identifier
        email: User email address
        token_type: Type of token ("access" or "refresh")

    Returns:
        Encoded JWT token string
    """
    if token_type == "access":
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token_type == "refresh":
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        raise ValueError(f"Invalid token_type: {token_type}")

    payload = {
        "user_id": user_id,
        "email": email,
        "token_type": token_type,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def validate_token(token: str, expected_type: str = "access") -> TokenData:
    """
    Validate and decode a JWT token.

    Args:
        token: JWT token string to validate
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        TokenData object with decoded payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        token_type: str = payload.get("token_type")
        exp: datetime = datetime.fromtimestamp(payload.get("exp"))

        if not user_id or not email:
            raise HTTPException(
                status_code=401, detail="Invalid token payload")

        if token_type != expected_type:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token type. Expected {expected_type}, got {token_type}"
            )

        return TokenData(
            user_id=user_id,
            email=email,
            token_type=token_type,
            exp=exp
        )

    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> UserContext:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials with bearer token

    Returns:
        UserContext: Current user context

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = validate_token(token, expected_type="access")

    return UserContext(
        user_id=token_data.user_id,
        email=token_data.email,
    )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(
        optional_security),
) -> Optional[UserContext]:
    """
    Get current user if authenticated, None otherwise.

    Useful for endpoints that work with or without authentication.

    Args:
        credentials: Optional HTTP authorization credentials

    Returns:
        Optional[UserContext]: User context if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Extract and validate user_id from JWT token in Authorization header.

    This function is used as a FastAPI dependency to protect routes.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User ID string extracted from valid token

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    token_data = validate_token(token, expected_type="access")
    return token_data.user_id
