"""
User management API endpoints
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_database
from repositories.user_repository import (
    UserRepository, 
    UserUpdate, 
    UserResponse
)
from middleware.auth import get_current_user, AuthUser


router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get current user's profile information.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return UserResponse.model_validate(user)


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Update current user's profile information.
    
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    """
    user_repo = UserRepository(db)
    
    # Only allow updating first_name and last_name for profile updates
    profile_data = UserUpdate(
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    try:
        updated_user = await user_repo.update_user(current_user.id, profile_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.model_validate(updated_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/profile")
async def deactivate_user_account(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Deactivate current user's account (soft delete).
    This will set the account to inactive but preserve data.
    """
    user_repo = UserRepository(db)
    
    success = await user_repo.delete_user(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Account deactivated successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_details(
    current_user: AuthUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get detailed information about the current authenticated user.
    This endpoint provides the same information as /profile but with a different path.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)