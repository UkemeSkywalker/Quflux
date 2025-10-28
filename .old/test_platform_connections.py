#!/usr/bin/env python3
"""
Test script to diagnose platform connections issues
"""
import asyncio
import sys
import os
import traceback
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

async def test_imports():
    """Test if all imports work correctly"""
    print("🔍 Testing imports...")
    
    try:
        from models.platform_connection import PlatformConnection
        print("✅ PlatformConnection model imported successfully")
    except Exception as e:
        print(f"❌ Failed to import PlatformConnection: {e}")
        traceback.print_exc()
        return False
    
    try:
        from services.platform_connection_service import platform_connection_service
        print("✅ platform_connection_service imported successfully")
    except Exception as e:
        print(f"❌ Failed to import platform_connection_service: {e}")
        traceback.print_exc()
        return False
    
    try:
        from core.database import get_database, AsyncSessionLocal
        print("✅ Database imports successful")
    except Exception as e:
        print(f"❌ Failed to import database: {e}")
        traceback.print_exc()
        return False
    
    try:
        from core.encryption import token_encryption
        print("✅ Encryption service imported successfully")
    except Exception as e:
        print(f"❌ Failed to import encryption: {e}")
        traceback.print_exc()
        return False
    
    return True

async def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from core.database import AsyncSessionLocal
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"✅ Database connection successful, test query returned: {test_value}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        traceback.print_exc()
        return False

async def test_platform_connections_table():
    """Test if platform_connections table exists and has correct schema"""
    print("\n🔍 Testing platform_connections table...")
    
    try:
        from core.database import AsyncSessionLocal
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as session:
            # Check if table exists
            result = await session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'platform_connections'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            if not columns:
                print("❌ platform_connections table does not exist")
                return False
            
            print("✅ platform_connections table exists with columns:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
            
            # Check if oauth_token_secret column exists
            oauth_secret_exists = any(col[0] == 'oauth_token_secret' for col in columns)
            if oauth_secret_exists:
                print("✅ oauth_token_secret column exists")
            else:
                print("❌ oauth_token_secret column missing")
                return False
            
            return True
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        traceback.print_exc()
        return False

async def test_platform_connections_query():
    """Test the actual platform connections query"""
    print("\n🔍 Testing platform connections query...")
    
    try:
        from core.database import AsyncSessionLocal
        from models.platform_connection import PlatformConnection
        from sqlalchemy import select
        
        # Test user ID from the token you showed
        test_user_id = "c2ff0767-1985-4b8a-b1d9-d9b5611d4e56"
        
        async with AsyncSessionLocal() as session:
            # Try the exact query from the service
            result = await session.execute(
                select(PlatformConnection)
                .where(
                    PlatformConnection.user_id == test_user_id,
                    PlatformConnection.is_active == True
                )
                .order_by(PlatformConnection.created_at.desc())
            )
            
            connections = result.scalars().all()
            print(f"✅ Query successful, found {len(connections)} connections")
            
            for conn in connections:
                print(f"   - Connection: {conn.platform} (@{conn.platform_username})")
            
            return True
    except Exception as e:
        print(f"❌ Platform connections query failed: {e}")
        traceback.print_exc()
        return False

async def test_service_method():
    """Test the service method directly"""
    print("\n🔍 Testing platform_connection_service.get_user_connections...")
    
    try:
        from services.platform_connection_service import platform_connection_service
        from core.database import AsyncSessionLocal
        
        test_user_id = "c2ff0767-1985-4b8a-b1d9-d9b5611d4e56"
        
        async with AsyncSessionLocal() as session:
            connections = await platform_connection_service.get_user_connections(
                user_id=test_user_id,
                db=session
            )
            
            print(f"✅ Service method successful, returned {len(connections)} connections")
            return True
    except Exception as e:
        print(f"❌ Service method failed: {e}")
        traceback.print_exc()
        return False

async def test_response_serialization():
    """Test if we can serialize the response"""
    print("\n🔍 Testing response serialization...")
    
    try:
        from services.platform_connection_service import platform_connection_service
        from core.database import AsyncSessionLocal
        from api.v1.platform_connections import PlatformConnectionResponse
        
        test_user_id = "c2ff0767-1985-4b8a-b1d9-d9b5611d4e56"
        
        async with AsyncSessionLocal() as session:
            connections = await platform_connection_service.get_user_connections(
                user_id=test_user_id,
                db=session
            )
            
            # Try to serialize each connection
            result = []
            for conn in connections:
                try:
                    connection_response = PlatformConnectionResponse(
                        id=str(conn.id),
                        platform=conn.platform,
                        platform_user_id=conn.platform_user_id,
                        platform_username=conn.platform_username,
                        is_active=conn.is_active,
                        created_at=conn.created_at.isoformat(),
                        updated_at=conn.updated_at.isoformat(),
                        expires_at=conn.expires_at.isoformat() if conn.expires_at else None
                    )
                    result.append(connection_response)
                    print(f"✅ Serialized connection: {conn.platform}")
                except Exception as conn_error:
                    print(f"❌ Failed to serialize connection {conn.id}: {conn_error}")
                    raise conn_error
            
            print(f"✅ Successfully serialized {len(result)} connections")
            return True
    except Exception as e:
        print(f"❌ Serialization failed: {e}")
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting platform connections diagnostic tests...\n")
    
    tests = [
        ("Imports", test_imports),
        ("Database Connection", test_database_connection),
        ("Platform Connections Table", test_platform_connections_table),
        ("Platform Connections Query", test_platform_connections_query),
        ("Service Method", test_service_method),
        ("Response Serialization", test_response_serialization),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
        
        print()  # Add spacing between tests
    
    # Summary
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! The issue might be elsewhere.")
    else:
        print("🔍 Some tests failed. Check the errors above for details.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())