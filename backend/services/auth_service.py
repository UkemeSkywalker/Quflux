"""
Authentication service using Supabase
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from supabase import Client
from pydantic import BaseModel, EmailStr
from core.config import settings
from core.database import cache_service, supabase
import jwt
import uuid


class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class AuthUser(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    is_active: bool = True


class AuthService:
    """Authentication service using database."""
    
    def __init__(self):
        self.supabase: Client = supabase
        if not self.supabase:
            print("⚠️  Warning: Supabase client not initialized")
            raise RuntimeError("Supabase client not initialized")
    
    async def register_user(self, user_data: UserRegistration) -> AuthToken:
        """Register a new user."""
        try:
            from passlib.context import CryptContext
            
            # Initialize password hashing
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # Check if user already exists
            existing_user = self.supabase.table("users").select("*").eq("email", user_data.email).execute()
            if existing_user.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            
            # Create new user ID
            user_id = str(uuid.uuid4())
            
            # Validate password length (bcrypt has a 72 byte limit)
            if len(user_data.password.encode('utf-8')) > 72:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password is too long. Please use a shorter password."
                )
            
            # Hash password
            hashed_password = pwd_context.hash(user_data.password)
            
            # Create user record
            user_record = {
                "id": user_id,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "password_hash": hashed_password,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            
            # Insert into users table
            result = self.supabase.table("users").insert(user_record).execute()
            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user"
                )
            
            # Remove password hash from response
            user_record.pop("password_hash", None)
            
            # Create session token
            session_token = await self._create_session_token(user_id, user_record)
            
            return AuthToken(
                access_token=session_token,
                expires_in=3600,  # 1 hour
                user=user_record
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def authenticate_user(self, login_data: UserLogin) -> AuthToken:
        """Authenticate user with email and password."""
        try:
            from passlib.context import CryptContext
            
            # Initialize password hashing
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # Get user from database
            user_result = self.supabase.table("users").select("*").eq("email", login_data.email).execute()
            
            if not user_result.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            user_record = user_result.data[0]
            
            # Verify password
            if not pwd_context.verify(login_data.password, user_record.get("password_hash", "")):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Check if user is active
            if not user_record.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated"
                )
            
            # Remove password hash from response
            user_record.pop("password_hash", None)
            
            # Create session token
            session_token = await self._create_session_token(user_record["id"], user_record)
            
            return AuthToken(
                access_token=session_token,
                expires_in=3600,  # 1 hour
                user=user_record
            )
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Authentication error: {e}")  # Debug logging
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    async def validate_session(self, token: str) -> AuthUser:
        """Validate session token and return user."""
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            
            user_id = payload.get("sub")
            session_id = payload.get("session_id")
            
            if not user_id or not session_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Check session in cache
            session_data = await cache_service.get(f"session:{session_id}")
            if not session_data or session_data.get("user_id") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired or invalid"
                )
            
            # Get user from database
            user_result = self.supabase.table("users").select("*").eq("id", user_id).execute()
            
            if not user_result.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            user_data = user_result.data[0]
            
            if not user_data.get("is_active", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated"
                )
            
            return AuthUser(
                id=user_data["id"],
                email=user_data["email"],
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                created_at=datetime.fromisoformat(user_data["created_at"].replace("Z", "+00:00")),
                is_active=user_data.get("is_active", True)
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed"
            )
    
    async def logout_user(self, token: str) -> bool:
        """Logout user by invalidating session."""
        try:
            # Decode token to get session ID
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
            
            session_id = payload.get("session_id")
            if session_id:
                # Remove session from cache
                await cache_service.delete(f"session:{session_id}")
            
            return True
            
        except Exception:
            # Even if token is invalid, consider logout successful
            return True
    
    async def _create_session_token(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """Create a JWT session token."""
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Store session in cache
        session_data = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await cache_service.set(
            f"session:{session_id}",
            session_data,
            expires_at.isoformat()
        )
        
        # Create JWT token
        payload = {
            "sub": user_id,
            "session_id": session_id,
            "exp": expires_at,
            "iat": datetime.utcnow(),
            "type": "access_token"
        }
        
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        return token


# Global auth service instance
auth_service = AuthService()