"""
User repository for database operations
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from models.user import User
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid


class UserCreate(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UserRepository:
    """Repository for user database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate, user_id: Optional[str] = None) -> User:
        """Create a new user."""
        try:
            user = User(
                id=uuid.UUID(user_id) if user_id else uuid.uuid4(),
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
            
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("User with this email already exists")
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            user_uuid = uuid.UUID(user_id)
            result = await self.db.execute(
                select(User).where(User.id == user_uuid)
            )
            return result.scalar_one_or_none()
        except ValueError:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        try:
            user_uuid = uuid.UUID(user_id)
            
            # Build update data, excluding None values
            update_data = {
                k: v for k, v in user_data.model_dump().items() 
                if v is not None
            }
            
            if not update_data:
                # No data to update, return current user
                return await self.get_user_by_id(user_id)
            
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.db.execute(
                update(User)
                .where(User.id == user_uuid)
                .values(**update_data)
                .returning(User)
            )
            
            updated_user = result.scalar_one_or_none()
            if updated_user:
                await self.db.commit()
                await self.db.refresh(updated_user)
            else:
                await self.db.rollback()
            
            return updated_user
            
        except ValueError:
            return None
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Update failed due to constraint violation")
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by setting is_active to False)."""
        try:
            user_uuid = uuid.UUID(user_id)
            
            result = await self.db.execute(
                update(User)
                .where(User.id == user_uuid)
                .values(is_active=False, updated_at=datetime.utcnow())
                .returning(User.id)
            )
            
            deleted_user_id = result.scalar_one_or_none()
            if deleted_user_id:
                await self.db.commit()
                return True
            else:
                await self.db.rollback()
                return False
                
        except ValueError:
            return False
    
    async def list_users(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[User]:
        """List users with pagination."""
        query = select(User)
        
        if active_only:
            query = query.where(User.is_active == True)
        
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count_users(self, active_only: bool = True) -> int:
        """Count total users."""
        from sqlalchemy import func
        
        query = select(func.count(User.id))
        
        if active_only:
            query = query.where(User.is_active == True)
        
        result = await self.db.execute(query)
        return result.scalar() or 0