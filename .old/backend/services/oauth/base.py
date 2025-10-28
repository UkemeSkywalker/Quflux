"""
Base OAuth handler class with common functionality
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import httpx
from urllib.parse import urlencode, parse_qs, urlparse
from pydantic import BaseModel


class OAuthConfig(BaseModel):
    """OAuth configuration for a platform"""
    client_id: str
    client_secret: str
    authorization_url: str
    token_url: str
    scope: str
    redirect_uri: str


class OAuthTokens(BaseModel):
    """OAuth token response"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    expires_at: Optional[datetime] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None
    oauth_token_secret: Optional[str] = None  # For OAuth 1.0a (Twitter)


class UserProfile(BaseModel):
    """User profile information from OAuth provider"""
    platform_user_id: str
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    profile_image_url: Optional[str] = None


class BaseOAuthHandler(ABC):
    """Base class for OAuth handlers"""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
        self.client = httpx.AsyncClient()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def generate_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        params = {
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'scope': self.config.scope,
            'response_type': 'code',
            'state': state,
        }
        
        # Add platform-specific parameters
        platform_params = self.get_authorization_params()
        params.update(platform_params)
        
        return f"{self.config.authorization_url}?{urlencode(params)}"
    
    async def exchange_code_for_tokens(self, code: str, state: str) -> OAuthTokens:
        """Exchange authorization code for access tokens"""
        data = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'code': code,
            'redirect_uri': self.config.redirect_uri,
            'grant_type': 'authorization_code',
        }
        
        # Add platform-specific parameters
        platform_data = self.get_token_exchange_params(code, state)
        data.update(platform_data)
        
        headers = self.get_token_exchange_headers()
        
        response = await self.client.post(
            self.config.token_url,
            data=data,
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Token exchange failed: {response.text}")
        
        token_data = response.json()
        return self.parse_token_response(token_data)
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokens:
        """Refresh access token using refresh token"""
        if not refresh_token:
            raise Exception("No refresh token available")
        
        data = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        headers = self.get_token_exchange_headers()
        
        response = await self.client.post(
            self.config.token_url,
            data=data,
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception(f"Token refresh failed: {response.text}")
        
        token_data = response.json()
        return self.parse_token_response(token_data)
    
    async def get_user_profile(self, access_token: str) -> UserProfile:
        """Get user profile information"""
        headers = {
            'Authorization': f'Bearer {access_token}',
            **self.get_api_headers()
        }
        
        profile_url = self.get_profile_url()
        response = await self.client.get(profile_url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user profile: {response.text}")
        
        profile_data = response.json()
        return self.parse_user_profile(profile_data)
    
    def parse_token_response(self, token_data: Dict[str, Any]) -> OAuthTokens:
        """Parse token response from OAuth provider"""
        expires_at = None
        if 'expires_in' in token_data:
            expires_at = datetime.utcnow() + timedelta(seconds=token_data['expires_in'])
        
        return OAuthTokens(
            access_token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            expires_in=token_data.get('expires_in'),
            expires_at=expires_at,
            token_type=token_data.get('token_type', 'Bearer'),
            scope=token_data.get('scope')
        )
    
    # Abstract methods that must be implemented by platform-specific handlers
    
    @abstractmethod
    def get_authorization_params(self) -> Dict[str, str]:
        """Get platform-specific authorization parameters"""
        pass
    
    @abstractmethod
    def get_token_exchange_params(self, code: str, state: str) -> Dict[str, str]:
        """Get platform-specific token exchange parameters"""
        pass
    
    @abstractmethod
    def get_token_exchange_headers(self) -> Dict[str, str]:
        """Get headers for token exchange request"""
        pass
    
    @abstractmethod
    def get_api_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        pass
    
    @abstractmethod
    def get_profile_url(self) -> str:
        """Get URL for user profile endpoint"""
        pass
    
    @abstractmethod
    def parse_user_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """Parse user profile data from platform response"""
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Platform name identifier"""
        pass