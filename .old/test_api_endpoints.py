#!/usr/bin/env python3
"""
Test script to test API endpoints directly
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Your access token from the browser console
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjMmZmMDc2Ny0xOTg1LTRiOGEtYjFkOS1kOWI1NjExZDRlNTYiLCJzZXNzaW9uX2lkIjoiNGY2NWQ1NWUtYTVmOC00ODNhLWFlYWMtYjdiMDM5YTk3ZmVjIiwiZXhwIjoxNzYxNjEyOTIxLCJpYXQiOjE3NjE2MDkzMjEsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.rG0ZKkYpEXutRr06QeBpzycmNhLhJUQOyk4DXdSJ3v4"

def test_endpoint(endpoint, description, use_auth=False):
    """Test a single endpoint"""
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {BASE_URL}{endpoint}")
    
    headers = {}
    if use_auth:
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Success: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"   ✅ Success: {response.text[:200]}...")
        else:
            print(f"   ❌ Error: {response.text}")
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False

def main():
    """Test all endpoints"""
    print("🚀 Testing API endpoints...\n")
    
    tests = [
        # Basic tests
        ("/", "Root endpoint", False),
        ("/status", "Status endpoint", False),
        
        # Auth tests
        ("/auth/test", "Auth service test", False),
        ("/auth/verify", "Auth verify (should fail without token)", False),
        ("/auth/verify", "Auth verify (with token)", True),
        
        # Platform connections tests
        ("/platform-connections/platforms/supported", "Supported platforms", False),
        ("/platform-connections/debug/test", "Debug test", False),
        ("/platform-connections/debug/auth-test", "Debug auth test", True),
        ("/platform-connections/debug/db-test", "Debug DB test", True),
        ("/platform-connections/", "Platform connections (the failing one)", True),
    ]
    
    results = {}
    
    for endpoint, description, use_auth in tests:
        results[description] = test_endpoint(endpoint, description, use_auth)
    
    # Summary
    print("\n📋 Test Results Summary:")
    print("=" * 60)
    
    for description, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {description}")
    
    print("=" * 60)
    
    # Check if the main issue is resolved
    if results.get("Platform connections (the failing one)", False):
        print("🎉 The platform connections endpoint is working!")
    else:
        print("🔍 The platform connections endpoint is still failing.")

if __name__ == "__main__":
    main()