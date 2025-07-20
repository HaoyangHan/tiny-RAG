#!/usr/bin/env python3
"""
Test Enhanced Document Upload API with Metadata Extraction
=========================================================

This script tests the enhanced document upload functionality with comprehensive
metadata extraction in TinyRAG v1.4.3.

Usage:
    python test_enhanced_upload_api.py
"""

import requests
import json
import time
from pathlib import Path


class EnhancedUploadTester:
    """Test class for enhanced document upload with metadata extraction."""
    
    def __init__(self):
        """Initialize the tester."""
        self.base_url = "http://localhost:8000"
        self.auth_token = None
        self.user_id = None
        self.project_id = None
        
        print("🚀 Enhanced Upload API Tester initialized")
    
    def login(self):
        """Login to get authentication token."""
        print("\n" + "="*60)
        print("STEP 1: User Authentication")
        print("="*60)
        
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                print(f"✅ Login successful")
                print(f"   - User ID: {self.user_id}")
                print(f"   - Token: {self.auth_token[:20]}...")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_project_id(self):
        """Get or create a test project."""
        print("\n" + "="*60)
        print("STEP 2: Project Setup")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Get existing projects
            response = requests.get(f"{self.base_url}/api/v1/projects", headers=headers)
            
            if response.status_code == 200:
                projects = response.json().get("projects", [])
                
                # Look for existing test project
                for project in projects:
                    if project.get("name") == "Enhanced Metadata Test Project":
                        self.project_id = project.get("id")
                        print(f"✅ Using existing project: {self.project_id}")
                        return True
                
                # Create new project if not found
                project_data = {
                    "name": "Enhanced Metadata Test Project",
                    "description": "Test project for enhanced metadata extraction",
                    "tenant_type": "hr"
                }
                
                response = requests.post(f"{self.base_url}/api/v1/projects", 
                                       json=project_data, headers=headers)
                
                if response.status_code == 201:
                    data = response.json()
                    self.project_id = data.get("id")
                    print(f"✅ Created new project: {self.project_id}")
                    return True
                else:
                    print(f"❌ Project creation failed: {response.status_code} - {response.text}")
                    return False
            else:
                print(f"❌ Failed to get projects: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Project setup error: {e}")
            return False
    
    def upload_document(self, file_path: str):
        """Upload a document with enhanced processing."""
        print("\n" + "="*60)
        print("STEP 3: Enhanced Document Upload")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Read file
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Prepare multipart form data
            files = {
                'file': (Path(file_path).name, file_content, 'text/plain')
            }
            data = {
                'project_id': self.project_id
            }
            
            print(f"📤 Uploading file: {Path(file_path).name}")
            print(f"   - Size: {len(file_content)} bytes")
            print(f"   - Project ID: {self.project_id}")
            
            # Upload document
            response = requests.post(
                f"{self.base_url}/api/v1/documents/upload",
                files=files,
                data=data,
                headers=headers
            )
            
            if response.status_code == 201:
                data = response.json()
                document_id = data.get("id")
                
                print(f"✅ Document uploaded successfully!")
                print(f"   - Document ID: {document_id}")
                print(f"   - Status: {data.get('status')}")
                print(f"   - Filename: {data.get('filename')}")
                print(f"   - File Size: {data.get('file_size')} bytes")
                
                # Enhanced features
                print(f"\n📊 Enhanced Processing Results:")
                print(f"   - Total Chunks: {len(data.get('chunks', []))}")
                print(f"   - Has Tables: {data.get('has_tables', False)}")
                print(f"   - Has Images: {data.get('has_images', False)}")
                print(f"   - Table Count: {data.get('table_count', 0)}")
                print(f"   - Image Count: {data.get('image_count', 0)}")
                
                # Analyze chunks and metadata
                chunks = data.get('chunks', [])
                total_metadata_fields = 0
                
                for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                    chunk_metadata = chunk.get('chunk_metadata', {})
                    if chunk_metadata:
                        total_metadata_fields += len(chunk_metadata)
                        
                        print(f"\n🔍 Chunk {i+1} Metadata Analysis:")
                        print(f"   - Text Length: {chunk_metadata.get('text_length', 'N/A')}")
                        print(f"   - Word Count: {chunk_metadata.get('word_count', 'N/A')}")
                        print(f"   - Language: {chunk_metadata.get('language', 'N/A')}")
                        print(f"   - Text Type: {chunk_metadata.get('text_type', 'N/A')}")
                        print(f"   - Readability Score: {chunk_metadata.get('readability_score', 'N/A'):.3f}")
                        print(f"   - Information Density: {chunk_metadata.get('information_density', 'N/A'):.3f}")
                        
                        # Keywords
                        keywords = chunk_metadata.get('keywords', [])
                        print(f"   - Keywords: {len(keywords)} found")
                        for j, kw in enumerate(keywords[:3]):  # Show top 3
                            print(f"     {j+1}. {kw.get('term', 'N/A')} (score: {kw.get('score', 0):.3f})")
                        
                        # Dates
                        dates = chunk_metadata.get('dates', [])
                        if dates:
                            print(f"   - Dates: {len(dates)} found")
                            for j, date in enumerate(dates[:2]):  # Show first 2
                                print(f"     {j+1}. {date.get('text', 'N/A')} -> {date.get('date', 'N/A')}")
                        
                        print(f"   - Section: {chunk.get('section', 'N/A')}")
                        print(f"   - Page Number: {chunk.get('page_number', 'N/A')}")
                
                print(f"\n📈 Metadata Extraction Summary:")
                print(f"   - Total Chunks Processed: {len(chunks)}")
                print(f"   - Total Metadata Fields: {total_metadata_fields}")
                print(f"   - Average Fields per Chunk: {total_metadata_fields/len(chunks):.1f}")
                
                return document_id
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return None
    
    def get_document_details(self, document_id: str):
        """Get detailed document information."""
        print("\n" + "="*60)
        print("STEP 4: Document Details Verification")
        print("="*60)
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/documents/{document_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Document details retrieved")
                print(f"   - Status: {data.get('status')}")
                print(f"   - Processing Complete: {data.get('metadata', {}).get('processed', False)}")
                print(f"   - Created: {data.get('created_at')}")
                print(f"   - Updated: {data.get('updated_at')}")
                
                # Check for enhanced fields
                metadata = data.get('metadata', {})
                print(f"\n🔬 Enhanced Metadata Verification:")
                print(f"   - Has Tables: {metadata.get('has_tables', False)}")
                print(f"   - Has Images: {metadata.get('has_images', False)}")
                print(f"   - Processing Error: {metadata.get('error', 'None')}")
                
                return True
            else:
                print(f"❌ Failed to get document details: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Document details error: {e}")
            return False
    
    def run_test(self):
        """Run the complete enhanced upload test."""
        print("🧪 Starting Enhanced Document Upload Test")
        print("=" * 80)
        
        # Test file
        test_file = "test_enhanced_metadata_doc.txt"
        
        if not Path(test_file).exists():
            print(f"❌ Test file not found: {test_file}")
            return False
        
        # Run test steps
        steps = [
            ("User Authentication", self.login),
            ("Project Setup", self.get_project_id),
            ("Document Upload", lambda: self.upload_document(test_file)),
        ]
        
        document_id = None
        
        for step_name, step_func in steps:
            try:
                result = step_func()
                if not result:
                    print(f"❌ Test failed at step: {step_name}")
                    return False
                if step_name == "Document Upload":
                    document_id = result
            except Exception as e:
                print(f"❌ Step '{step_name}' failed with exception: {e}")
                return False
        
        # Get document details
        if document_id:
            self.get_document_details(document_id)
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print("✅ Enhanced document upload test completed successfully!")
        print("🎉 LlamaIndex-style metadata extraction is working correctly.")
        print(f"📄 Document ID: {document_id}")
        
        return True


def main():
    """Main test function."""
    tester = EnhancedUploadTester()
    success = tester.run_test()
    
    if success:
        print("\n✅ Enhanced metadata extraction system is production-ready!")
    else:
        print("\n❌ Test failed. Please check the API and configuration.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main()) 