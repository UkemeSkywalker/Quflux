"""
Meta (Facebook/Instagram) OAuth handler
"""
from typing import Dict, Any
from .base import BaseOAuthHandler, OAuthConfig, UserProfile
from core.config import settings


class MetaOAuthHandler(BaseOAuthHandler):
    """
    Meta (Facebook/Instagram) OAuth 2.0 handler
    
    Note: For Instagram, this uses the Instagram Basic Display API which allows
    access to basic profile information and media. For business features, you would
    need to use the Instagram API with Facebook Login for Business instead.
    """
    
    def __init__(self, redirect_uri: str, platform_type: str = "facebook"):
        """
        Initialize Meta OAuth handler
        
        Args:
            redirect_uri: OAuth redirect URI
            platform_type: Either 'facebook' or 'instagram'
        """
        self.platform_type = platform_type
        
        # Different endpoints and scopes based on platform
        if platform_type == "instagram":
            # Instagram Basic Display API uses these endpoints
            authorization_url = "https://api.instagram.com/oauth/authorize"
            token_url = "https://api.instagram.com/oauth/access_token"
            scope = "instagram_basic"  # Basic scope for Instagram Basic Display API
        else:
            authorization_url = "https://www.facebook.com/v18.0/dialog/oauth"
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            scope = "pages_manage_posts,pages_read_engagement,pages_show_list"
        
        config = OAuthConfig(
            client_id=settings.META_APP_ID,
            client_secret=settings.META_APP_SECRET,
            authorization_url=authorization_url,
            token_url=token_url,
            scope=scope,
            redirect_uri=redirect_uri
        )
        super().__init__(config)
    
    def get_authorization_params(self) -> Dict[str, str]:
        """Meta-specific authorization parameters"""
        return {}
    
    def get_token_exchange_params(self, code: str, state: str) -> Dict[str, str]:
        """Meta-specific token exchange parameters"""
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
        """Meta user profile endpoint"""
        if self.platform_type == "instagram":
            # Instagram Basic Display API endpoint
            return "https://graph.instagram.com/me?fields=id,username"
        else:
            return "https://graph.facebook.com/v18.0/me?fields=id,name,picture"
    
    def parse_user_profile(self, profile_data: Dict[str, Any]) -> UserProfile:
        """Parse Meta user profile"""
        if self.platform_type == "instagram":
            return UserProfile(
                platform_user_id=profile_data.get('id', ''),
                username=profile_data.get('username', ''),
                display_name=profile_data.get('username')
            )
        else:
            # Facebook
            profile_image_url = None
            picture_data = profile_data.get('picture', {})
            if isinstance(picture_data, dict) and 'data' in picture_data:
                profile_image_url = picture_data['data'].get('url')
            
            return UserProfile(
                platform_user_id=profile_data.get('id', ''),
                username=profile_data.get('name', ''),  # Facebook uses name as display
                display_name=profile_data.get('name'),
                profile_image_url=profile_image_url
            )
    
    @property
    def platform_name(self) -> str:
        return self.platform_type


class FacebookOAuthHandler(MetaOAuthHandler):
    """Facebook-specific OAuth handler"""
    
    def __init__(self, redirect_uri: str):
        super().__init__(redirect_uri, "facebook")


class InstagramOAuthHandler(MetaOAuthHandler):
    """Instagram-specific OAuth handler"""
    
    def __init__(self, redirect_uri: str):
        super().__init__(redirect_uri, "instagram")