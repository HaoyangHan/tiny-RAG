#!/usr/bin/env python3
"""
TinyRAG v1.4 Users API Test Suite

Testing all user-related endpoints for TinyRAG v1.4 API.
Following .cursorrules standards for clean, maintainable code.
"""

import asyncio
import json
import aiohttp
import time
from datetime import datetime
from typing import Dict, Any, List


class UserAPITester:
    """Test suite for User API endpoints."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_base = f"{self.base_url}/api/v1"
        self.test_results = []
        self.session = None
        self.user_token = None
        self.test_user_id = None
        
    async def setup_session(self):
        """Setup aiohttp session for testing."""
        self.session = aiohttp.ClientSession()
        print("🔧 Session initialized for User API testing")
        
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
                    self.test_user_id = data.get("user", {}).get("id", "6859036f0cfc8f1bb0f21c76")
                    print(f"🔑 Login successful. Token acquired for user: {self.test_user_id}")
                    return True
                else:
                    print(f"❌ Login failed with status: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    async def test_get_user_profile(self):
        """Test GET /api/v1/users/profile - Get current user profile."""
        endpoint = f"{self.api_base}/users/profile"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            async with self.session.get(endpoint, headers=headers) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Get User Profile",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Get User Profile",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_update_user_profile(self):
        """Test PUT /api/v1/users/profile - Update user profile."""
        endpoint = f"{self.api_base}/users/profile"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        update_data = {
            "full_name": "Updated Test User",
            "bio": "Updated bio for testing",
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        try:
            async with self.session.put(endpoint, headers=headers, json=update_data) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Update User Profile",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Update User Profile",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_search_users(self):
        """Test GET /api/v1/users/search - Search users."""
        endpoint = f"{self.api_base}/users/search"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        params = {
            "query": "test",
            "limit": 10
        }
        
        try:
            async with self.session.get(endpoint, headers=headers, params=params) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Search Users",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Search Users",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_get_user_analytics(self):
        """Test GET /api/v1/users/analytics - Get user analytics."""
        endpoint = f"{self.api_base}/users/analytics"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            async with self.session.get(endpoint, headers=headers) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Get User Analytics",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Get User Analytics",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def run_all_tests(self):
        """Run all user API tests."""
        print("🚀 Starting TinyRAG v1.4 Users API Test Suite")
        print("=" * 60)
        
        await self.setup_session()
        
        # Login first
        if not await self.login_test_user():
            print("❌ Cannot proceed without authentication")
            await self.cleanup_session()
            return
        
        # Run all tests
        tests = [
            self.test_get_user_profile(),
            self.test_update_user_profile(),
            self.test_search_users(),
            self.test_get_user_analytics()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Calculate summary
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("=" * 60)
        print(f"📊 Users API Test Summary:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {total - passed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        with open("test_logs/users_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Results saved to: test_logs/users_test_results.json")
        
        await self.cleanup_session()


if __name__ == "__main__":
    tester = UserAPITester()
    asyncio.run(tester.run_all_tests()) 