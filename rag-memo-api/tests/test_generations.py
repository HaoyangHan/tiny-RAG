#!/usr/bin/env python3
"""
TinyRAG v1.4 Generations API Test Suite

Testing all generation-related endpoints for TinyRAG v1.4 API.
Following .cursorrules standards for clean, maintainable code.
"""

import asyncio
import json
import aiohttp
import time
from datetime import datetime
from typing import Dict, Any, List


class GenerationAPITester:
    """Test suite for Generation API endpoints."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_base = f"{self.base_url}/api/v1"
        self.test_results = []
        self.session = None
        self.user_token = None
        self.test_element_id = None
        self.test_generation_id = None
        
    async def setup_session(self):
        """Setup aiohttp session for testing."""
        self.session = aiohttp.ClientSession()
        print("🔧 Session initialized for Generation API testing")
        
    async def cleanup_session(self):
        """Cleanup aiohttp session."""
        if self.session:
            await self.session.close()
            print("🔧 Session cleaned up")
    
    def log_result(self, test_name: str, endpoint: str, success: bool, 
                   status_code: int, response_data: Any = None, error: str = None):
        """Log test result with timestamp and details."""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        result = {
            "timestamp": timestamp,
            "test_name": test_name,
            "endpoint": endpoint,
            "status_code": status_code,
            "success": success,
            "response_data": response_data,
            "error": error
        }
        
        self.test_results.append(result)
        
        print(f"[{timestamp}] {status} {test_name}")
        print(f"    📍 Endpoint: {endpoint}")
        print(f"    📊 Status: {status_code}")
        
        if error:
            print(f"    ❌ Error: {error}")
        elif response_data:
            print(f"    📄 Response: {str(response_data)[:100]}...")
        print()
    
    async def login_test_user(self):
        """Login with test user to get JWT token."""
        login_data = {
            "identifier": "tester3",
            "password": "TestPassword123!"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.user_token = data.get("access_token")
                    print(f"🔑 Login successful. Token acquired.")
                    return True
                else:
                    print(f"❌ Login failed with status: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    async def setup_test_element(self):
        """Create a test element for generation testing."""
        endpoint = f"{self.api_base}/elements"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        element_data = {
            "name": "Test Generation Element",
            "type": "template",
            "content": "Generate a summary about: {{topic}}",
            "category": "testing",
            "tags": ["test", "generation"],
            "is_public": True
        }
        
        try:
            async with self.session.post(endpoint, headers=headers, json=element_data) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    self.test_element_id = data.get("id")
                    print(f"🔧 Test element created: {self.test_element_id}")
                    return True
                else:
                    print(f"❌ Failed to create test element: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error creating test element: {str(e)}")
            return False
    
    async def test_create_generation(self):
        """Test POST /api/v1/generations - Create new generation."""
        endpoint = f"{self.api_base}/generations"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        generation_data = {
            "element_id": self.test_element_id,
            "inputs": {
                "topic": "artificial intelligence"
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 500
            }
        }
        
        try:
            async with self.session.post(endpoint, headers=headers, json=generation_data) as response:
                data = await response.json()
                success = response.status in [200, 201]
                
                if success and data.get("id"):
                    self.test_generation_id = data.get("id")
                
                self.log_result(
                    "Create Generation",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Create Generation",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_get_generations(self):
        """Test GET /api/v1/generations - Get user's generations."""
        endpoint = f"{self.api_base}/generations"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        params = {
            "limit": 10,
            "offset": 0
        }
        
        try:
            async with self.session.get(endpoint, headers=headers, params=params) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Get Generations",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Get Generations",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_get_generation_details(self):
        """Test GET /api/v1/generations/{id} - Get generation details."""
        if not self.test_generation_id:
            print("⚠️ Skipping generation details test - no test generation available")
            return False, None
            
        endpoint = f"{self.api_base}/generations/{self.test_generation_id}"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            async with self.session.get(endpoint, headers=headers) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Get Generation Details",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Get Generation Details",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_delete_generation(self):
        """Test DELETE /api/v1/generations/{id} - Delete generation."""
        if not self.test_generation_id:
            print("⚠️ Skipping generation deletion test - no test generation available")
            return False, None
            
        endpoint = f"{self.api_base}/generations/{self.test_generation_id}"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            async with self.session.delete(endpoint, headers=headers) as response:
                if response.status == 204:
                    data = {"message": "Generation deleted successfully"}
                else:
                    data = await response.json()
                
                success = response.status == 204
                
                self.log_result(
                    "Delete Generation",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Delete Generation",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_generation_analytics(self):
        """Test GET /api/v1/generations/analytics - Get generation analytics."""
        endpoint = f"{self.api_base}/generations/analytics"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            async with self.session.get(endpoint, headers=headers) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Get Generation Analytics",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Get Generation Analytics",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def cleanup_test_element(self):
        """Clean up test element."""
        if self.test_element_id:
            endpoint = f"{self.api_base}/elements/{self.test_element_id}"
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            try:
                async with self.session.delete(endpoint, headers=headers) as response:
                    if response.status == 204:
                        print(f"🔧 Test element cleaned up: {self.test_element_id}")
            except Exception as e:
                print(f"⚠️ Failed to cleanup test element: {str(e)}")
    
    async def run_all_tests(self):
        """Run all generation API tests."""
        print("🚀 Starting TinyRAG v1.4 Generations API Test Suite")
        print("=" * 60)
        
        await self.setup_session()
        
        # Login first
        if not await self.login_test_user():
            print("❌ Cannot proceed without authentication")
            await self.cleanup_session()
            return
        
        # Setup test element
        if not await self.setup_test_element():
            print("❌ Cannot proceed without test element")
            await self.cleanup_session()
            return
        
        # Run all tests
        tests = [
            self.test_create_generation(),
            self.test_get_generations(),
            self.test_get_generation_details(),
            self.test_generation_analytics(),
            self.test_delete_generation()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Cleanup
        await self.cleanup_test_element()
        
        # Calculate summary
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("=" * 60)
        print(f"📊 Generations API Test Summary:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {total - passed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        with open("test_logs/generations_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Results saved to: test_logs/generations_test_results.json")
        
        await self.cleanup_session()


if __name__ == "__main__":
    tester = GenerationAPITester()
    asyncio.run(tester.run_all_tests()) 