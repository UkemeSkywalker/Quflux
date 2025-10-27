"""
Authentication API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from services.auth_service import (
    auth_service, 
    UserRegistration, 
    UserLogin, 
    AuthToken,
    AuthUser
)
from middleware.auth import get_current_user, security
from fastapi.security import HTTPAuthorizationCredentials
from typing import Optional


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthToken)
async def register(user_data: UserRegistration):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Password (minimum 6 characters)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    """
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=AuthToken)
async def login(login_data: UserLogin):
    """
    Authenticate user with email and password.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns access token for authenticated requests.
    """
    return await auth_service.authenticate_user(login_data)


@router.post("/logout")
async def logout(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Logout current user by invalidating the session.
    """
    if credentials:
        await auth_service.logout_user(credentials.credentials)
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=AuthUser)
async def get_current_user_info(current_user: AuthUser = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Requires valid authentication token.
    """
    return current_user


@router.get("/verify")
async def verify_token(current_user: AuthUser = Depends(get_current_user)):
    """
    Verify if the current token is valid.
    
    Returns user information if token is valid.
    """
    return {
        "valid": True,
        "user": current_user,
        "message": "Token is valid"
    }


@router.get("/test")
async def test_auth_service():
    """
    Test endpoint to check if auth service is working.
    """
    try:
        from services.auth_service import auth_service
        return {
            "status": "ok",
            "supabase_connected": auth_service.supabase is not None,
            "message": "Auth service is working"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Auth service has issues"
        }