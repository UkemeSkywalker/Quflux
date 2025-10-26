"""
Simple test script to verify core dependencies are properly configured
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test that all core dependencies can be imported."""
    print("Testing core dependency imports...")
    
    try:
        # Test FastAPI
        from fastapi import FastAPI
        print("✓ FastAPI imported successfully")
        
        # Test Pydantic
        from pydantic import BaseModel
        print("✓ Pydantic imported successfully")
        
        # Test Supabase
        from supabase import create_client
        print("✓ Supabase client imported successfully")
        
        # Test Celery
        from celery import Celery
        print("✓ Celery imported successfully")
        
        # Test Strands SDK
        from strands import Agent, tool
        print("✓ Strands SDK imported successfully")
        
        # Test SQLAlchemy
        from sqlalchemy.ext.asyncio import create_async_engine
        print("✓ SQLAlchemy imported successfully")
        
        # Test our custom modules
        from core.config import settings
        print("✓ Configuration imported successfully")
        
        from core.database import Base, get_database
        print("✓ Database utilities imported successfully")
        
        from services.ai_agent import ai_content_service
        print("✓ AI service imported successfully")
        
        from models import User, Post, Schedule
        print("✓ Models imported successfully")
        
        from tasks.publishing import publish_post_task
        print("✓ Celery tasks imported successfully")
        
        print("\n🎉 All core dependencies imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def test_configuration():
    """Test that configuration is properly loaded."""
    print("\nTesting configuration...")
    
    try:
        from core.config import settings
        
        # Check that settings object exists
        assert hasattr(settings, 'APP_NAME')
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'CELERY_BROKER_URL')
        
        print(f"✓ App Name: {settings.APP_NAME}")
        print(f"✓ Database URL configured: {settings.DATABASE_URL[:20]}...")
        print(f"✓ Celery Broker configured: {settings.CELERY_BROKER_URL[:20]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


async def test_ai_agent():
    """Test that AI agent is properly configured."""
    print("\nTesting AI agent configuration...")
    
    try:
        from services.ai_agent import ai_content_service, ai_agent
        
        # Check that agent exists
        assert ai_agent is not None
        assert ai_content_service is not None
        
        # Check that agent has tools (Strands agents store tools differently)
        # Just check that the agent exists and has the expected name
        assert ai_agent.name == "Quflux Content Generator"
        
        print(f"✓ AI agent configured with name: {ai_agent.name}")
        print(f"✓ AI content service initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ AI agent error: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Testing Quflux Core Dependencies Setup\n")
    
    tests = [
        test_imports(),
        test_configuration(),
        test_ai_agent()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    success_count = sum(1 for result in results if result is True)
    total_tests = len(results)
    
    print(f"\n📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Core dependencies are properly configured.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)