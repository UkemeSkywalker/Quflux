#!/usr/bin/env python3
"""
Test Twitter OAuth 1.0a signature generation
"""
import hmac
import hashlib
import base64
import secrets
import time
from urllib.parse import quote

# Your Twitter credentials
TWITTER_API_KEY = "viF0sQmEOTfr60bWxVLDMepXX"
TWITTER_API_SECRET = "XgdZCpsR1hp5EVWvtPM4oXwTUiWrOhQXkRXG0gi23pJe9Nt8Nj"
CALLBACK_URL = "http://127.0.0.1:3000/dashboard/connections"

def generate_oauth_signature(method, url, params, consumer_secret, token_secret=""):
    """Generate OAuth 1.0a signature"""
    # Create parameter string
    sorted_params = sorted(params.items())
    param_string = "&".join([f"{quote(str(k), safe='')}={quote(str(v), safe='')}" for k, v in sorted_params])
    
    # Create signature base string
    base_string = f"{method.upper()}&{quote(url, safe='')}&{quote(param_string, safe='')}"
    
    # Create signing key
    signing_key = f"{quote(consumer_secret, safe='')}&{quote(token_secret, safe='')}"
    
    # Generate signature
    signature = hmac.new(
        signing_key.encode(),
        base_string.encode(),
        hashlib.sha1
    ).digest()
    
    return base64.b64encode(signature).decode()

def test_twitter_oauth():
    """Test Twitter OAuth signature generation"""
    print("🔍 Testing Twitter OAuth 1.0a signature generation...")
    
    # OAuth parameters
    oauth_params = {
        'oauth_callback': CALLBACK_URL,
        'oauth_consumer_key': TWITTER_API_KEY,
        'oauth_nonce': secrets.token_hex(16),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_version': '1.0'
    }
    
    print(f"🔍 OAuth params: {oauth_params}")
    
    # Generate signature
    signature = generate_oauth_signature(
        'POST', 
        'https://api.x.com/oauth/request_token', 
        oauth_params, 
        TWITTER_API_SECRET
    )
    
    oauth_params['oauth_signature'] = signature
    
    print(f"🔍 Generated signature: {signature}")
    
    # Create authorization header
    oauth_header_params = {k: v for k, v in oauth_params.items() if k.startswith('oauth_')}
    sorted_params = sorted(oauth_header_params.items())
    param_string = ", ".join([f'{k}="{quote(str(v), safe="")}"' for k, v in sorted_params])
    auth_header = f"OAuth {param_string}"
    
    print(f"🔍 Authorization header: {auth_header}")
    
    # Test with curl
    import subprocess
    
    curl_command = [
        'curl', '-s', '-X', 'POST',
        '-H', f'Authorization: {auth_header}',
        'https://api.x.com/oauth/request_token'
    ]
    
    print(f"🔍 Testing with curl...")
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=10)
        print(f"🔍 Response status: {result.returncode}")
        print(f"🔍 Response: {result.stdout}")
        
        if result.stderr:
            print(f"🔍 Error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Curl test failed: {e}")

if __name__ == "__main__":
    test_twitter_oauth()