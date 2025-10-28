"""
Encryption utilities for secure token storage
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Optional
from .config import settings


class TokenEncryption:
    """Handle encryption and decryption of OAuth tokens"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """Initialize with encryption key"""
        try:
            key = encryption_key or settings.ENCRYPTION_KEY
            if not key:
                # Use a default key for development (not secure for production)
                key = "quflux_dev_key_32_chars_long_12345"
                print("⚠️  Using default encryption key. Set ENCRYPTION_KEY in production!")
            
            if isinstance(key, str):
                # Derive a proper key from the string
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=b'quflux_salt',  # In production, use a random salt per user
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
            
            self.cipher_suite = Fernet(key)
        except Exception as e:
            print(f"❌ Encryption initialization failed: {e}")
            # Create a fallback cipher with a default key
            default_key = Fernet.generate_key()
            self.cipher_suite = Fernet(default_key)
            print("⚠️  Using fallback encryption key")
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token string"""
        if not token:
            return ""
        
        encrypted_token = self.cipher_suite.encrypt(token.encode())
        return base64.urlsafe_b64encode(encrypted_token).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token string"""
        if not encrypted_token:
            return ""
        
        try:
            decoded_token = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted_token = self.cipher_suite.decrypt(decoded_token)
            return decrypted_token.decode()
        except Exception:
            # If decryption fails, return empty string
            return ""


# Global instance
token_encryption = TokenEncryption()