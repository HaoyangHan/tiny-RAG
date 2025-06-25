#!/usr/bin/env python3
"""
TinyRAG v1.4 Evaluations API Test Suite

Testing all evaluation-related endpoints for TinyRAG v1.4 API.
Following .cursorrules standards for clean, maintainable code.
"""

import asyncio
import json
import aiohttp
import time
from datetime import datetime
from typing import Dict, Any, List


class EvaluationAPITester:
    """Test suite for Evaluation API endpoints."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_base = f"{self.base_url}/api/v1"
        self.test_results = []
        self.session = None
        self.user_token = None
        self.test_evaluation_id = None
        self.test_generation_id = None
        
    async def setup_session(self):
        """Setup aiohttp session for testing."""
        self.session = aiohttp.ClientSession()
        print("🔧 Session initialized for Evaluation API testing")
        
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
    
    async def test_create_evaluation(self):
        """Test POST /api/v1/evaluations - Create new evaluation."""
        endpoint = f"{self.api_base}/evaluations"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        evaluation_data = {
            "type": "quality",
            "target_type": "generation",
            "target_id": "test_generation_id_123",
            "criteria": {
                "accuracy": {"weight": 0.4, "description": "Factual correctness"},
                "clarity": {"weight": 0.3, "description": "Clear and understandable"},
                "relevance": {"weight": 0.3, "description": "Relevant to the request"}
            },
            "inputs": {
                "content": "This is a test generation to evaluate",
                "prompt": "Generate a summary about AI",
                "expected_output": "AI summary"
            }
        }
        
        try:
            async with self.session.post(endpoint, headers=headers, json=evaluation_data) as response:
                data = await response.json()
                success = response.status in [200, 201]
                
                if success and data.get("id"):
                    self.test_evaluation_id = data.get("id")
                
                self.log_result(
                    "Create Evaluation",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Create Evaluation",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_get_evaluations(self):
        """Test GET /api/v1/evaluations - Get user's evaluations."""
        endpoint = f"{self.api_base}/evaluations"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        params = {
            "limit": 10,
            "offset": 0,
            "type": "quality"
        }
        
        try:
            async with self.session.get(endpoint, headers=headers, params=params) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Get Evaluations",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Get Evaluations",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_get_evaluation_details(self):
        """Test GET /api/v1/evaluations/{id} - Get evaluation details."""
        if not self.test_evaluation_id:
            print("⚠️ Skipping evaluation details test - no test evaluation available")
            return False, None
            
        endpoint = f"{self.api_base}/evaluations/{self.test_evaluation_id}"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            async with self.session.get(endpoint, headers=headers) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Get Evaluation Details",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Get Evaluation Details",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_update_evaluation(self):
        """Test PUT /api/v1/evaluations/{id} - Update evaluation."""
        if not self.test_evaluation_id:
            print("⚠️ Skipping evaluation update test - no test evaluation available")
            return False, None
            
        endpoint = f"{self.api_base}/evaluations/{self.test_evaluation_id}"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        update_data = {
            "status": "completed",
            "scores": {
                "accuracy": 8.5,
                "clarity": 9.0,
                "relevance": 7.5
            },
            "overall_score": 8.3,
            "feedback": "Good quality generation with minor improvements needed"
        }
        
        try:
            async with self.session.put(endpoint, headers=headers, json=update_data) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Update Evaluation",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Update Evaluation",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_delete_evaluation(self):
        """Test DELETE /api/v1/evaluations/{id} - Delete evaluation."""
        if not self.test_evaluation_id:
            print("⚠️ Skipping evaluation deletion test - no test evaluation available")
            return False, None
            
        endpoint = f"{self.api_base}/evaluations/{self.test_evaluation_id}"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            async with self.session.delete(endpoint, headers=headers) as response:
                if response.status == 204:
                    data = {"message": "Evaluation deleted successfully"}
                else:
                    data = await response.json()
                
                success = response.status == 204
                
                self.log_result(
                    "Delete Evaluation",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Delete Evaluation",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_evaluation_analytics(self):
        """Test GET /api/v1/evaluations/analytics - Get evaluation analytics."""
        endpoint = f"{self.api_base}/evaluations/analytics"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            async with self.session.get(endpoint, headers=headers) as response:
                data = await response.json()
                success = response.status == 200
                
                self.log_result(
                    "Get Evaluation Analytics",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Get Evaluation Analytics",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def test_run_batch_evaluation(self):
        """Test POST /api/v1/evaluations/batch - Run batch evaluation."""
        endpoint = f"{self.api_base}/evaluations/batch"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        batch_data = {
            "evaluation_type": "quality",
            "targets": [
                {
                    "target_type": "generation",
                    "target_id": "gen_1",
                    "content": "Test generation 1"
                },
                {
                    "target_type": "generation", 
                    "target_id": "gen_2",
                    "content": "Test generation 2"
                }
            ],
            "criteria": {
                "accuracy": {"weight": 0.5},
                "clarity": {"weight": 0.5}
            }
        }
        
        try:
            async with self.session.post(endpoint, headers=headers, json=batch_data) as response:
                data = await response.json()
                success = response.status in [200, 201]
                
                self.log_result(
                    "Run Batch Evaluation",
                    endpoint,
                    success,
                    response.status,
                    data if success else None,
                    data.get("detail") if not success else None
                )
                
                return success, data
                
        except Exception as e:
            self.log_result(
                "Run Batch Evaluation",
                endpoint,
                False,
                0,
                None,
                str(e)
            )
            return False, None
    
    async def run_all_tests(self):
        """Run all evaluation API tests."""
        print("🚀 Starting TinyRAG v1.4 Evaluations API Test Suite")
        print("=" * 60)
        
        await self.setup_session()
        
        # Login first
        if not await self.login_test_user():
            print("❌ Cannot proceed without authentication")
            await self.cleanup_session()
            return
        
        # Run all tests
        tests = [
            self.test_create_evaluation(),
            self.test_get_evaluations(),
            self.test_get_evaluation_details(),
            self.test_update_evaluation(),
            self.test_evaluation_analytics(),
            self.test_run_batch_evaluation(),
            self.test_delete_evaluation()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Calculate summary
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("=" * 60)
        print(f"📊 Evaluations API Test Summary:")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {total - passed}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        with open("test_logs/evaluations_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Results saved to: test_logs/evaluations_test_results.json")
        
        await self.cleanup_session()


if __name__ == "__main__":
    tester = EvaluationAPITester()
    asyncio.run(tester.run_all_tests()) 