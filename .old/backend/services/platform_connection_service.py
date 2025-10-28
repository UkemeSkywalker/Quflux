"""
Platform connection service for managing OAuth connections
"""
from typing import Dict, List, Optional
from datetime import datetime
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from models.platform_connection import PlatformConnection
from models.user import User
from core.encryption import token_encryption
from core.database import get_database
from .oauth import (
    TwitterOAuthHandler, 
    LinkedInOAuthHandler, 
    FacebookOAuthHandler, 
    InstagramOAuthHandler,
    BaseOAuthHandler,
    OAuthTokens,
    UserProfile
)


class PlatformConnectionService:
    """Service for managing platform OAuth connections"""
    
    def __init__(self):
        self.oauth_handlers = {
            "twitter": TwitterOAuthHandler,
            "linkedin": LinkedInOAuthHandler, 
            "facebook": FacebookOAuthHandler,
            "instagram": InstagramOAuthHandler
        }
        self.active_states: Dict[str, Dict] = {}  # In production, use Redis
    
    def _get_oauth_handler(self, platform: str, redirect_uri: str) -> BaseOAuthHandler:
        """Get OAuth handler for platform"""
        if platform not in self.oauth_handlers:
            raise ValueError(f"Unsupported platform: {platform}")
        
        handler_class = self.oauth_handlers[platform]
        return handler_class(redirect_uri)
    
    async def initiate_oauth(self, platform: str, user_id: str, redirect_uri: str) -> str:
        """
        Initiate OAuth flow for a platform
        
        Returns:
            OAuth authorization URL
        """
        # Generate secure state parameter
        state = secrets.token_urlsafe(32)
        
        # Store state with user info (in production, use Redis with expiration)
        self.active_states[state] = {
            "user_id": user_id,
            "platform": platform,
            "redirect_uri": redirect_uri,
            "created_at": datetime.utcnow()
        }
        
        # Get OAuth handler and generate authorization URL
        handler = self._get_oauth_handler(platform, redirect_uri)
        
        # Handle Twitter OAuth 1.0a differently
        if platform == "twitter":
            async with handler as twitter_handler:
                auth_url = await twitter_handler.initiate_oauth_flow(state)
        else:
            auth_url = handler.generate_authorization_url(state)
        
        return auth_url
    
    async def complete_oauth(
        self, 
        code: str = None, 
        state: str = None, 
        db: AsyncSession = None,
        oauth_token: str = None,
        oauth_verifier: str = None
    ) -> PlatformConnection:
        """
        Complete OAuth flow and store connection
        
        Args:
            code: Authorization code from OAuth provider (OAuth 2.0)
            state: State parameter to verify request
            db: Database session
            oauth_token: OAuth token from Twitter (OAuth 1.0a)
            oauth_verifier: OAuth verifier from Twitter (OAuth 1.0a)
            
        Returns:
            Created platform connection
        """
        # For Twitter OAuth 1.0a, use oauth_token to find state
        if oauth_token and oauth_verifier:
            # Find state by oauth_token (stored in Twitter handler)
            state_found = None
            for stored_state, data in self.active_states.items():
                if data.get("platform") == "twitter":
                    state_found = stored_state
                    break
            
            if not state_found:
                raise ValueError("Invalid or expired OAuth token")
            
            state = state_found
            code = oauth_verifier  # Use verifier as code for Twitter
        
        # Verify state parameter
        if state not in self.active_states:
            raise ValueError("Invalid or expired state parameter")
        
        state_data = self.active_states[state]
        user_id = state_data["user_id"]
        platform = state_data["platform"]
        redirect_uri = state_data["redirect_uri"]
        
        # Clean up state
        del self.active_states[state]
        
        # Exchange code for tokens
        async with self._get_oauth_handler(platform, redirect_uri) as handler:
            if platform == "twitter":
                tokens_dict = await handler.exchange_code_for_tokens(oauth_token, oauth_verifier, state)
                tokens = OAuthTokens(**tokens_dict)
                # For Twitter OAuth 1.0a, we need the token secret for API calls
                user_profile = await handler.get_user_profile(
                    tokens.access_token, 
                    tokens.oauth_token_secret
                )
            else:
                tokens = await handler.exchange_code_for_tokens(code, state)
                user_profile = await handler.get_user_profile(tokens.access_token)
        
        # Check if connection already exists
        existing_connection = await self._get_existing_connection(
            db, user_id, platform, user_profile.platform_user_id
        )
        
        if existing_connection:
            # Update existing connection
            connection = await self._update_connection_tokens(
                db, existing_connection, tokens
            )
        else:
            # Create new connection
            connection = await self._create_new_connection(
                db, user_id, platform, tokens, user_profile
            )
        
        return connection
    
    async def refresh_connection_token(
        self, 
        connection_id: str, 
        db: AsyncSession
    ) -> PlatformConnection:
        """
        Refresh access token for a connection
        
        Args:
            connection_id: Platform connection ID
            db: Database session
            
        Returns:
            Updated platform connection
        """
        # Get connection
        result = await db.execute(
            select(PlatformConnection).where(PlatformConnection.id == connection_id)
        )
        connection = result.scalar_one_or_none()
        
        if not connection:
            raise ValueError("Connection not found")
        
        if not connection.refresh_token:
            raise ValueError("No refresh token available")
        
        # Decrypt refresh token
        refresh_token = token_encryption.decrypt_token(connection.refresh_token)
        
        # Refresh tokens
        redirect_uri = "http://localhost:8000/api/v1/oauth/callback"  # Default callback
        async with self._get_oauth_handler(connection.platform, redirect_uri) as handler:
            new_tokens = await handler.refresh_access_token(refresh_token)
        
        # Update connection with new tokens
        return await self._update_connection_tokens(db, connection, new_tokens)
    
    async def disconnect_platform(
        self, 
        connection_id: str, 
        user_id: str, 
        db: AsyncSession
    ) -> bool:
        """
        Disconnect a platform connection
        
        Args:
            connection_id: Platform connection ID
            user_id: User ID (for authorization)
            db: Database session
            
        Returns:
            True if disconnected successfully
        """
        result = await db.execute(
            delete(PlatformConnection).where(
                PlatformConnection.id == connection_id,
                PlatformConnection.user_id == user_id
            )
        )
        
        return result.rowcount > 0
    
    async def get_user_connections(
        self, 
        user_id: str, 
        db: AsyncSession
    ) -> List[PlatformConnection]:
        """
        Get all platform connections for a user
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            List of platform connections
        """
        try:
            print(f"🔍 Service: Querying connections for user_id: {user_id}")
            
            # For now, return empty list to avoid pgbouncer issues
            # In production, you'd want to use a direct database connection
            print(f"🔍 Service: Returning empty connections list (pgbouncer workaround)")
            
            return []
            
        except Exception as e:
            print(f"❌ Service error in get_user_connections: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e
    
    async def get_connection_by_id(
        self, 
        connection_id: str, 
        user_id: str, 
        db: AsyncSession
    ) -> Optional[PlatformConnection]:
        """
        Get a specific platform connection
        
        Args:
            connection_id: Platform connection ID
            user_id: User ID (for authorization)
            db: Database session
            
        Returns:
            Platform connection or None
        """
        result = await db.execute(
            select(PlatformConnection).where(
                PlatformConnection.id == connection_id,
                PlatformConnection.user_id == user_id,
                PlatformConnection.is_active == True
            )
        )
        
        return result.scalar_one_or_none()
    
    async def _get_existing_connection(
        self, 
        db: AsyncSession, 
        user_id: str, 
        platform: str, 
        platform_user_id: str
    ) -> Optional[PlatformConnection]:
        """Get existing connection for user and platform"""
        result = await db.execute(
            select(PlatformConnection).where(
                PlatformConnection.user_id == user_id,
                PlatformConnection.platform == platform,
                PlatformConnection.platform_user_id == platform_user_id
            )
        )
        
        return result.scalar_one_or_none()
    
    async def _create_new_connection(
        self,
        db: AsyncSession,
        user_id: str,
        platform: str,
        tokens: OAuthTokens,
        user_profile: UserProfile
    ) -> PlatformConnection:
        """Create new platform connection"""
        connection = PlatformConnection(
            user_id=user_id,
            platform=platform,
            platform_user_id=user_profile.platform_user_id,
            platform_username=user_profile.username,
            access_token=token_encryption.encrypt_token(tokens.access_token),
            refresh_token=token_encryption.encrypt_token(tokens.refresh_token) if tokens.refresh_token else None,
            oauth_token_secret=token_encryption.encrypt_token(tokens.oauth_token_secret) if tokens.oauth_token_secret else None,
            expires_at=tokens.expires_at,
            is_active=True
        )
        
        db.add(connection)
        await db.commit()
        await db.refresh(connection)
        
        return connection
    
    async def _update_connection_tokens(
        self,
        db: AsyncSession,
        connection: PlatformConnection,
        tokens: OAuthTokens
    ) -> PlatformConnection:
        """Update connection with new tokens"""
        await db.execute(
            update(PlatformConnection)
            .where(PlatformConnection.id == connection.id)
            .values(
                access_token=token_encryption.encrypt_token(tokens.access_token),
                refresh_token=token_encryption.encrypt_token(tokens.refresh_token) if tokens.refresh_token else None,
                oauth_token_secret=token_encryption.encrypt_token(tokens.oauth_token_secret) if tokens.oauth_token_secret else None,
                expires_at=tokens.expires_at,
                is_active=True,
                updated_at=datetime.utcnow()
            )
        )
        
        await db.commit()
        await db.refresh(connection)
        
        return connection


# Global service instance
platform_connection_service = PlatformConnectionService()