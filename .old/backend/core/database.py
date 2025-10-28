"""
Database connection and session management using Supabase PostgreSQL
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from supabase import create_client, Client
from core.config import settings
import asyncio
from typing import AsyncGenerator

# SQLAlchemy setup for Supabase PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    # Fix for pgbouncer transaction pooling
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# Supabase client (optional for testing)
supabase: Client = None
if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
    supabase = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database():
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            # Import all models here to ensure they are registered
            from models import user, post, platform_connection, media_file, schedule, publication
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  Database initialization skipped: {e}")
        print("💡 Make sure to run the SQL script in Supabase or check your DATABASE_URL")


async def close_database():
    """Close database connections."""
    await engine.dispose()


class CacheService:
    """Service for key-value caching using Supabase."""
    
    def __init__(self):
        self.supabase = supabase
    
    async def get(self, key: str) -> dict | None:
        """Get value from cache."""
        if not self.supabase:
            print("⚠️  Cache service: Supabase client not available")
            return None
        try:
            result = self.supabase.table("cache_store").select("value").eq("key", key).execute()
            if result.data:
                print(f"✅ Cache get successful for key: {key}")
                return result.data[0]["value"]
            print(f"⚠️  Cache get: No data found for key: {key}")
            return None
        except Exception as e:
            print(f"❌ Cache get failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: dict, expires_at: str = None) -> bool:
        """Set value in cache."""
        if not self.supabase:
            print("⚠️  Cache service: Supabase client not available")
            return False
        try:
            data = {
                "key": key,
                "value": value,
                "expires_at": expires_at
            }
            result = self.supabase.table("cache_store").upsert(data).execute()
            print(f"✅ Cache set successful for key: {key}")
            return True
        except Exception as e:
            print(f"❌ Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.supabase:
            return False
        try:
            self.supabase.table("cache_store").delete().eq("key", key).execute()
            return True
        except Exception:
            return False


# Global cache service instance
cache_service = CacheService()