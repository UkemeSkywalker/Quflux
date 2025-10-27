"""
Authentication middleware for FastAPI
"""
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import auth_service, AuthUser


# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> AuthUser:
    """
    Dependency to get the current authenticated user.
    Raises HTTPException if user is not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return await auth_service.validate_session(credentials.credentials)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[AuthUser]:
    """
    Dependency to get the current authenticated user.
    Returns None if user is not authenticated (doesn't raise exception).
    """
    if not credentials:
        return None
    
    try:
        return await auth_service.validate_session(credentials.credentials)
    except HTTPException:
        return None


def require_auth(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """
    Dependency that requires authentication.
    Use this for protected routes.
    """
    return user


def optional_auth(user: Optional[AuthUser] = Depends(get_current_user_optional)) -> Optional[AuthUser]:
    """
    Dependency that allows optional authentication.
    Use this for routes that work with or without authentication.
    """
    return user