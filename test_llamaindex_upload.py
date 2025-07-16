#!/usr/bin/env python3
"""
Test script for LlamaIndex upload endpoint.
"""

import asyncio
import httpx
import json

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER_CREDENTIALS = {
    "identifier": "tester3@example.com",
    "password": "TestPassword123!"
}

async def authenticate() -> str:
    """Authenticate and get JWT token."""
    async with httpx.AsyncClient() as client:
        # First try to register the user
        register_data = {
            "email": "tester3@example.com",
            "username": "tester3",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
        
        try:
            response = await client.post(
                f"{API_BASE_URL}/auth/register",
                json=register_data
            )
            print(f"Register response: {response.status_code}")
        except Exception as e:
            print(f"Register error (expected if user exists): {e}")
        
        # Login
        response = await client.post(
            f"{API_BASE_URL}/auth/login",
            json=TEST_USER_CREDENTIALS
        )
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return None
        
        data = response.json()
        return data["access_token"]

async def test_llamaindex_upload(token: str):
    """Test the LlamaIndex upload endpoint."""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test data
        upload_data = {
            "project_id": "test-project-llamaindex",
            "file_content": "This is a test document for LlamaIndex processing. It contains information about machine learning and artificial intelligence.",
            "filename": "test_llamaindex.txt",
            "file_type": "text"
        }
        
        print("Testing LlamaIndex upload endpoint...")
        response = await client.post(
            f"{API_BASE_URL}/api/v1/documents/upload-llamaindex",
            headers=headers,
            json=upload_data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ LlamaIndex upload successful!")
        else:
            print("❌ LlamaIndex upload failed!")

async def main():
    """Main test function."""
    print("🔐 Authenticating...")
    token = await authenticate()
    
    if not token:
        print("❌ Authentication failed!")
        return
    
    print("✅ Authentication successful!")
    print(f"Token: {token[:50]}...")
    
    await test_llamaindex_upload(token)

if __name__ == "__main__":
    asyncio.run(main()) 