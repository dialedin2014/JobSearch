"""
Authentication middleware for route protection.

This middleware automatically validates JWT tokens for protected routes
and injects user_id into request state.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging

from src.core.security import validate_token

logger = logging.getLogger(__name__)


# Routes that don't require authentication
PUBLIC_ROUTES = [
    "/",
    "/api/v1/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
    "/docs",
    "/redoc",
    "/openapi.json",
]


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate JWT tokens and protect routes.
    
    This middleware:
    1. Checks if the route requires authentication
    2. Validates JWT token from Authorization header
    3. Injects user_id into request.state for use in route handlers
    4. Returns 401 Unauthorized if auth is required but token is invalid
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process each request through authentication middleware.
        
        Args:
            request: HTTP request
            call_next: Next middleware or route handler
            
        Returns:
            Response from next handler or 401 error
        """
        path = request.url.path
        
        # Check if route is public
        is_public = any(path.startswith(public_route) for public_route in PUBLIC_ROUTES)
        
        if is_public:
            # Public route - no auth required
            return await call_next(request)
        
        # Protected route - validate JWT token
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            logger.warning(f"Missing Authorization header for protected route: {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing Authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract token from "Bearer <token>" format
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            logger.warning(f"Invalid Authorization header format for route: {path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid Authorization header format. Use: Bearer <token>"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate token
        try:
            token_data = validate_token(token, expected_type="access")
            
            # Inject user_id into request state
            request.state.user_id = token_data.user_id
            request.state.email = token_data.email
            
            logger.debug(f"Authenticated request for user: {token_data.email}")
            
        except HTTPException as e:
            logger.warning(f"Token validation failed for route {path}: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Continue to route handler
        response = await call_next(request)
        return response
