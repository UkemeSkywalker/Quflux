"""
LinkedIn OAuth handler
"""
from typing import Dict, Any
from .base import BaseOAuthHandler, OAuthConfig, UserProfile
from core.config import settings


class LinkedInOAuthHandler(BaseOAuthHandler):
    """LinkedIn OAuth 2.0 handler"""
    
    def __init__(self, redirect_uri: str):
        config = OAuthConfig(
            client_id=settings.LINKEDIN_CLIENT_ID,
            client_secret=settings.LINKEDIN_CLIENT_SECRET,
            authorization_url="https://www.linkedin.com/oauth/v2/authorization",
            token_url="https://www.linkedin.com/oauth/v2/accessToken",
            scope="profile email w_member_social",
            redirect_uri=redirect_uri
        )
        super().__init__(config)
    
    def get_authorization_params(self) -> Dict[str, str]:
        """LinkedIn-specific authorization parameters"""
        return {}
    
    def get_token_exchange_params(self, code: str, state: str) -> Dict[str, str]:
        """LinkedIn-specific token exchange parameters"""
        return {}
    
    def get_token_exchange_headers(self) -> Dict[str, str]:
        """Headers for token exchange"""
        return {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    def get_api_headers(self) -> Dict[str, str]:
        """Headers for API requests"""
        return {
            'Content-Type': 'application/json'
        }
    
    def get_profile_url(self) -> str:
        """LinkedIn user profile endpoint"""
        return "https://api.linkedin.com/v2/userinfo"
    
    def parse_user_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """Parse LinkedIn user profile"""
        # The userinfo endpoint returns a simpler format
        display_name = profile_data.get('name', '')
        
        return UserProfile(
            platform_user_id=profile_data.get('sub', ''),  # 'sub' is the user ID in userinfo
            username=profile_data.get('email', '').split('@')[0] if profile_data.get('email') else profile_data.get('sub', ''),
            display_name=display_name or None,
            email=profile_data.get('email'),
            profile_image_url=profile_data.get('picture')
        )
    
    @property
    def platform_name(self) -> str:
        return "linkedin"