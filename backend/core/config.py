from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Quflux"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Supabase (primary database and auth provider)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_DB_URL: str = ""  # Raw Supabase connection string
    
    # Database URLs (will be set after initialization)
    DATABASE_URL: str = ""
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convert Supabase connection string to different formats after loading env vars
        if self.SUPABASE_DB_URL and not self.DATABASE_URL:
            self.DATABASE_URL = self.SUPABASE_DB_URL.replace("postgresql://", "postgresql+asyncpg://")
        if self.SUPABASE_DB_URL and not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.SUPABASE_DB_URL.replace("postgresql://", "sqlalchemy+postgresql://")
        if self.SUPABASE_DB_URL and not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.SUPABASE_DB_URL.replace("postgresql://", "db+postgresql://")
    
    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""
    
    # External APIs
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_BEARER_TOKEN: str = ""
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    SENDGRID_API_KEY: str = ""
    
    # Strands SDK
    STRANDS_API_KEY: str = ""
    
    # Google Nano Banana
    GOOGLE_NANO_BANANA_API_KEY: str = ""
    
    # Security
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    ENCRYPTION_KEY: str = "your-encryption-key-change-in-production"
    
    class Config:
        env_file = ".env"  # Will look for .env in the current working directory
        case_sensitive = True


settings = Settings()