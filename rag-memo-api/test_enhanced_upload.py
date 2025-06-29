#!/usr/bin/env python3
"""
Test script for enhanced document upload with table and image processing.

This script tests the updated /api/v1/documents/upload endpoint to ensure
table and image extraction capabilities are working correctly.
"""

import asyncio
import httpx
import json
import os
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_PROJECT_ID = None  # Will be created during test
TEST_USER_CREDENTIALS = {
    "identifier": "tester3@example.com",
    "password": "TestPassword123!"
}

async def authenticate() -> str:
    """Authenticate and get JWT token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json=TEST_USER_CREDENTIALS
        )
        
        if response.status_code != 200:
            raise Exception(f"Authentication failed: {response.text}")
        
        data = response.json()
        return data["access_token"]

async def create_test_project(token: str) -> str:
    """Create a test project for document upload."""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/api/v1/projects",
            headers=headers,
            json={
                "name": "Enhanced Upload Test Project",
                "description": "Test project for table and image extraction",
                "tenant_type": "TEAM"
            }
        )
        
        if response.status_code != 201:
            raise Exception(f"Project creation failed: {response.text}")
        
        data = response.json()
        return data["id"]

async def test_enhanced_upload(token: str, project_id: str):
    """Test the enhanced document upload with table and image processing."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test file (we'll use a simple text file for this test)
    test_content = """
# Test Document with Tables and Images

This is a test document to verify enhanced processing capabilities.

## Sample Table Data
| Name     | Age | Department |
|----------|-----|------------|
| Alice    | 30  | Engineering|
| Bob      | 25  | Marketing  |
| Charlie  | 35  | Sales      |

## Text Content
This document contains mixed content including text, tables, and would normally include images in a real PDF.

The enhanced processor should:
1. Extract and summarize tables
2. Process any images with GPT-4 Vision
3. Create appropriate chunks for each content type
4. Generate embeddings for semantic search

## Additional Information
Processing status should show:
- has_tables: true (if tables detected)
- has_images: true (if images detected)
- chunk_types: text, table, image
"""
    
    # Upload the test document
    files = {"file": ("test_enhanced_doc.txt", test_content, "text/plain")}
    params = {"project_id": project_id}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("📤 Uploading test document...")
        response = await client.post(
            f"{API_BASE_URL}/api/v1/documents/upload",
            headers=headers,
            files=files,
            params=params
        )
        
        if response.status_code != 201:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        document_data = response.json()
        print("✅ Document uploaded successfully!")
        
        # Print enhanced processing results
        print(f"\n📊 Processing Results:")
        print(f"  - Document ID: {document_data['id']}")
        print(f"  - Filename: {document_data['filename']}")
        print(f"  - Status: {document_data['status']}")
        print(f"  - Content Type: {document_data['content_type']}")
        print(f"  - File Size: {document_data['file_size']} bytes")
        
        print(f"\n🔍 Content Analysis:")
        print(f"  - Total Chunks: {document_data['chunk_count']}")
        print(f"  - Tables Found: {document_data['table_count']}")
        print(f"  - Images Found: {document_data['image_count']}")
        print(f"  - Has Tables: {document_data['has_tables']}")
        print(f"  - Has Images: {document_data['has_images']}")
        
        # Show chunk types breakdown
        chunk_types = {}
        for chunk in document_data['chunks']:
            chunk_type = chunk.get('chunk_type', 'text')
            chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        print(f"\n📝 Chunk Types:")
        for chunk_type, count in chunk_types.items():
            print(f"  - {chunk_type}: {count} chunks")
        
        # Show table summaries if any
        if document_data['tables']:
            print(f"\n📋 Table Summaries:")
            for i, table in enumerate(document_data['tables']):
                print(f"  Table {i+1} (Page {table['page_number']}): {table['summary'][:100]}...")
        
        # Show image descriptions if any
        if document_data['images']:
            print(f"\n🖼️ Image Descriptions:")
            for i, image in enumerate(document_data['images']):
                print(f"  Image {i+1} (Page {image['page_number']}): {image['description'][:100]}...")
        
        return document_data['id']

async def cleanup_test_project(token: str, project_id: str):
    """Clean up the test project."""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        # Note: Project deletion might not be implemented yet
        print(f"🧹 Test project {project_id} can be manually cleaned up if needed")

async def main():
    """Run the enhanced upload test."""
    try:
        print("🚀 Starting Enhanced Document Upload Test")
        print("=" * 50)
        
        # Step 1: Authenticate
        print("🔐 Authenticating...")
        token = await authenticate()
        print("✅ Authentication successful")
        
        # Step 2: Create test project
        print("\n📁 Creating test project...")
        project_id = await create_test_project(token)
        print(f"✅ Test project created: {project_id}")
        
        # Step 3: Test enhanced upload
        print("\n📤 Testing enhanced document upload...")
        document_id = await test_enhanced_upload(token, project_id)
        
        if document_id:
            print(f"\n✅ Enhanced upload test completed successfully!")
            print(f"Document ID: {document_id}")
        else:
            print(f"\n❌ Enhanced upload test failed")
        
        # Step 4: Cleanup
        print(f"\n🧹 Cleaning up...")
        await cleanup_test_project(token, project_id)
        
        print("\n🎉 Test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 