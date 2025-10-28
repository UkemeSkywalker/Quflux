"""
Twitter/X OAuth 1.0a handler
"""
from typing import Dict, Any, Optional
import base64
import hashlib
import hmac
import secrets
import time
from urllib.parse import quote, urlencode
import httpx
from .base import UserProfile
from core.config import settings


class TwitterOAuth1Handler:
    """Twitter OAuth 1.0a handler"""
    
    def __init__(self, redirect_uri: str):
        self.client_id = settings.TWITTER_API_KEY
        self.client_secret = settings.TWITTER_API_SECRET
        self.redirect_uri = redirect_uri
        self.client = httpx.AsyncClient()
        
        # OAuth 1.0a URLs
        self.request_token_url = "https://api.x.com/oauth/request_token"
        self.authorize_url = "https://api.x.com/oauth/authenticate"
        self.access_token_url = "https://api.x.com/oauth/access_token"
        self.profile_url = "https://api.x.com/1.1/account/verify_credentials.json"
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _generate_oauth_signature(self, method: str, url: str, params: Dict[str, str], token_secret: str = "") -> str:
        """Generate OAuth 1.0a signature"""
        # Create parameter string with proper encoding
        sorted_params = sorted(params.items())
        param_string = "&".join([f"{quote(str(k), safe='')}={quote(str(v), safe='')}" for k, v in sorted_params])
        
        # Create signature base string
        base_string = f"{method.upper()}&{quote(url, safe='')}&{quote(param_string, safe='')}"
        
        print(f"🔍 Signature base string: {base_string}")
        
        # Create signing key
        signing_key = f"{quote(self.client_secret, safe='')}&{quote(token_secret, safe='')}"
        
        print(f"🔍 Signing key: {signing_key}")
        
        # Generate signature
        signature = hmac.new(
            signing_key.encode(),
            base_string.encode(),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode()
    
    def _create_oauth_header(self, params: Dict[str, str]) -> str:
        """Create OAuth authorization header"""
        oauth_params = {k: v for k, v in params.items() if k.startswith('oauth_')}
        sorted_params = sorted(oauth_params.items())
        param_string = ", ".join([f'{k}="{quote(str(v))}"' for k, v in sorted_params])
        return f"OAuth {param_string}"
    
    async def get_request_token(self) -> Dict[str, str]:
        """Step 1: Get request token"""
        print(f"🔍 Twitter OAuth: Getting request token")
        print(f"🔍 Redirect URI: {self.redirect_uri}")
        print(f"🔍 Client ID: {self.client_id}")
        
        oauth_params = {
            'oauth_callback': self.redirect_uri,
            'oauth_consumer_key': self.client_id,
            'oauth_nonce': secrets.token_hex(16),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_version': '1.0'
        }
        
        print(f"🔍 OAuth params before signature: {oauth_params}")
        
        # Generate signature
        oauth_params['oauth_signature'] = self._generate_oauth_signature(
            'POST', self.request_token_url, oauth_params
        )
        
        print(f"🔍 Generated signature: {oauth_params['oauth_signature']}")
        
        # Create authorization header
        auth_header = self._create_oauth_header(oauth_params)
        print(f"🔍 Authorization header: {auth_header}")
        
        response = await self.client.post(
            self.request_token_url,
            headers={'Authorization': auth_header}
        )
        
        print(f"🔍 Response status: {response.status_code}")
        print(f"🔍 Response text: {response.text}")
        
        if response.status_code != 200:
            raise Exception(f"Failed to get request token: {response.text}")
        
        # Parse response
        response_params = {}
        for param in response.text.split('&'):
            key, value = param.split('=')
            response_params[key] = value
        
        return response_params
    
    def generate_authorization_url(self, oauth_token: str) -> str:
        """Step 2: Generate authorization URL"""
        params = {
            'oauth_token': oauth_token
        }
        return f"{self.authorize_url}?{urlencode(params)}"
    
    async def get_access_token(self, oauth_token: str, oauth_verifier: str, oauth_token_secret: str) -> Dict[str, str]:
        """Step 3: Exchange request token for access token"""
        oauth_params = {
            'oauth_consumer_key': self.client_id,
            'oauth_nonce': secrets.token_hex(16),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_token': oauth_token,
            'oauth_verifier': oauth_verifier,
            'oauth_version': '1.0'
        }
        
        # Generate signature with token secret
        oauth_params['oauth_signature'] = self._generate_oauth_signature(
            'POST', self.access_token_url, oauth_params, oauth_token_secret
        )
        
        # Create authorization header
        auth_header = self._create_oauth_header(oauth_params)
        
        response = await self.client.post(
            self.access_token_url,
            headers={'Authorization': auth_header}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get access token: {response.text}")
        
        # Parse response
        response_params = {}
        for param in response.text.split('&'):
            key, value = param.split('=')
            response_params[key] = value
        
        return response_params
    
    async def get_user_profile(self, oauth_token: str, oauth_token_secret: str) -> UserProfile:
        """Get user profile using OAuth 1.0a"""
        oauth_params = {
            'oauth_consumer_key': self.client_id,
            'oauth_nonce': secrets.token_hex(16),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_token': oauth_token,
            'oauth_version': '1.0'
        }
        
        # Generate signature
        oauth_params['oauth_signature'] = self._generate_oauth_signature(
            'GET', self.profile_url, oauth_params, oauth_token_secret
        )
        
        # Create authorization header
        auth_header = self._create_oauth_header(oauth_params)
        
        response = await self.client.get(
            self.profile_url,
            headers={'Authorization': auth_header}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get user profile: {response.text}")
        
        profile_data = response.json()
        return UserProfile(
            platform_user_id=str(profile_data.get('id', '')),
            username=profile_data.get('screen_name', ''),
            display_name=profile_data.get('name'),
            profile_image_url=profile_data.get('profile_image_url_https')
        )
    
    @property
    def platform_name(self) -> str:
        return "twitter"


# For backward compatibility, create a wrapper that matches the base handler interface
class TwitterOAuthHandler:
    """Twitter OAuth handler wrapper for compatibility"""
    
    def __init__(self, redirect_uri: str):
        self.handler = TwitterOAuth1Handler(redirect_uri)
        self.redirect_uri = redirect_uri
        self._request_tokens = {}  # Store request tokens temporarily
    
    async def __aenter__(self):
        await self.handler.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.handler.__aexit__(exc_type, exc_val, exc_tb)
    
    def generate_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL - async wrapper needed"""
        # This needs to be called differently for OAuth 1.0a
        # We'll handle this in the service layer
        raise NotImplementedError("Use initiate_oauth_flow instead")
    
    async def initiate_oauth_flow(self, state: str) -> str:
        """Initiate OAuth 1.0a flow"""
        # Step 1: Get request token
        request_token_data = await self.handler.get_request_token()
        
        # Store request token data with state for later use
        self._request_tokens[state] = {
            'oauth_token': request_token_data['oauth_token'],
            'oauth_token_secret': request_token_data['oauth_token_secret']
        }
        
        # Step 2: Generate authorization URL
        auth_url = self.handler.generate_authorization_url(request_token_data['oauth_token'])
        
        return auth_url
    
    async def exchange_code_for_tokens(self, oauth_token: str, oauth_verifier: str, state: str) -> Dict[str, Any]:
        """Exchange OAuth verifier for access tokens"""
        # Get stored request token data
        if state not in self._request_tokens:
            raise Exception("Invalid state or expired request token")
        
        request_token_data = self._request_tokens[state]
        
        # Verify oauth_token matches
        if request_token_data['oauth_token'] != oauth_token:
            raise Exception("OAuth token mismatch")
        
        # Step 3: Get access token
        access_token_data = await self.handler.get_access_token(
            oauth_token,
            oauth_verifier,
            request_token_data['oauth_token_secret']
        )
        
        # Clean up stored request token
        del self._request_tokens[state]
        
        return {
            'access_token': access_token_data['oauth_token'],
            'refresh_token': None,  # OAuth 1.0a doesn't use refresh tokens
            'expires_in': None,
            'expires_at': None,
            'token_type': 'oauth1',
            'oauth_token_secret': access_token_data['oauth_token_secret']
        }
    
    async def get_user_profile(self, access_token: str, oauth_token_secret: str = None) -> UserProfile:
        """Get user profile"""
        if not oauth_token_secret:
            raise Exception("OAuth token secret required for Twitter OAuth 1.0a")
        
        return await self.handler.get_user_profile(access_token, oauth_token_secret)
    
    @property
    def platform_name(self) -> str:
        return "twitter"