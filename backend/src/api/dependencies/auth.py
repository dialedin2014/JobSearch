"""
Authentication dependency injection.

This module provides FastAPI dependencies for user authentication.
"""

from fastapi import Depends
from typing import Optional
from src.core.security import get_current_user, get_optional_user, UserContext


async def get_current_user_dependency(
    user: UserContext = Depends(get_current_user),
) -> UserContext:
    """
    Dependency for getting current authenticated user.
    
    Args:
        user: User context from security module
        
    Returns:
        UserContext: Current user
    """
    return user


async def get_optional_user_dependency(
    user: Optional[UserContext] = Depends(get_optional_user),
) -> Optional[UserContext]:
    """
    Dependency for getting optional user (endpoints that work with/without auth).
    
    Args:
        user: Optional user context
        
    Returns:
        Optional[UserContext]: Current user or None
    """
    return user
