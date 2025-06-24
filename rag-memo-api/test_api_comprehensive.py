#!/usr/bin/env python3
"""
Comprehensive API Testing Script for TinyRAG v1.4.

This script tests all API endpoints including:
- Legacy v1.3 endpoints (backward compatibility)
- New v1.4 project-based endpoints
- Authentication flows
- Error handling

Usage:
    python test_api_comprehensive.py

Requirements:
    - API server running on localhost:8000
    - Valid test credentials
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

import aiohttp
import pytest


class TinyRAGAPITester:
    """Comprehensive API tester for TinyRAG v1.4."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API tester."""
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_user_data = {
            "email": "api.tester@example.com",
            "username": "api_tester",
            "password": "TestPassword123!",
            "full_name": "API Tester"
        }
        self.test_results = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def log_test(self, test_name: str, success: bool, details: str = "") -> None:
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "status": status,
            "success": success,
            "details": details
        }
        
        self.test_results.append(result)
        print(f"[{timestamp}] {status} - {test_name}")
        if details:
            print(f"    Details: {details}")
    
    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        
        # Add authorization header if token is available
        request_headers = headers or {}
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=request_headers, params=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json(),
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "POST":
                if files:
                    form_data = aiohttp.FormData()
                    for key, value in (data or {}).items():
                        form_data.add_field(key, value)
                    for key, file_info in files.items():
                        form_data.add_field(key, file_info["content"], filename=file_info["filename"])
                    async with self.session.post(url, headers=request_headers, data=form_data) as response:
                        return {
                            "status": response.status,
                            "data": await response.json(),
                            "headers": dict(response.headers)
                        }
                else:
                    async with self.session.post(url, headers=request_headers, json=data) as response:
                        return {
                            "status": response.status,
                            "data": await response.json(),
                            "headers": dict(response.headers)
                        }
            elif method.upper() == "PUT":
                async with self.session.put(url, headers=request_headers, json=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json(),
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=request_headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else {},
                        "headers": dict(response.headers)
                    }
                    
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {}
            }
    
    async def test_health_check(self) -> None:
        """Test health check endpoint."""
        response = await self.make_request("GET", "/health")
        
        success = (
            response["status"] == 200 and
            response["data"].get("status") == "healthy" and
            response["data"].get("version") == "1.4.0"
        )
        
        await self.log_test(
            "Health Check",
            success,
            f"Status: {response['status']}, Version: {response['data'].get('version', 'unknown')}"
        )
    
    async def test_authentication_flow(self) -> bool:
        """Test complete authentication flow."""
        # 1. Register user
        register_response = await self.make_request("POST", "/auth/register", self.test_user_data)
        
        # If user already exists, that's OK for testing
        register_success = register_response["status"] in [200, 201, 400]
        await self.log_test(
            "User Registration",
            register_success,
            f"Status: {register_response['status']}"
        )
        
        # 2. Login user
        login_data = {
            "identifier": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        login_response = await self.make_request("POST", "/auth/login", login_data)
        login_success = login_response["status"] == 200 and "access_token" in login_response["data"]
        
        if login_success:
            self.auth_token = login_response["data"]["access_token"]
        
        await self.log_test(
            "User Login",
            login_success,
            f"Status: {login_response['status']}, Token: {'Yes' if self.auth_token else 'No'}"
        )
        
        # 3. Verify token by accessing user profile
        if self.auth_token:
            verify_response = await self.make_request("GET", "/api/v1/users/me/profile")
            verify_success = verify_response["status"] == 200
            
            await self.log_test(
                "Token Verification",
                verify_success,
                f"Status: {verify_response['status']}"
            )
            
            return verify_success
        
        return False
    
    async def test_v14_projects(self) -> str:
        """Test v1.4 project endpoints."""
        # Create project
        project_data = {
            "name": "Test API Project",
            "description": "Project created during API testing",
            "tenant_type": "coding",
            "visibility": "private"
        }
        
        create_response = await self.make_request("POST", "/api/v1/projects/", project_data)
        create_success = create_response["status"] == 201
        
        project_id = None
        if create_success:
            project_id = create_response["data"]["id"]
        
        await self.log_test(
            "v1.4 Create Project",
            create_success,
            f"Status: {create_response['status']}, ID: {project_id or 'None'}"
        )
        
        # List projects
        list_response = await self.make_request("GET", "/api/v1/projects/")
        list_success = list_response["status"] == 200 and isinstance(list_response["data"], list)
        
        await self.log_test(
            "v1.4 List Projects",
            list_success,
            f"Status: {list_response['status']}, Count: {len(list_response['data']) if list_success else 0}"
        )
        
        # Get specific project
        if project_id:
            get_response = await self.make_request("GET", f"/api/v1/projects/{project_id}")
            get_success = get_response["status"] == 200
            
            await self.log_test(
                "v1.4 Get Project",
                get_success,
                f"Status: {get_response['status']}"
            )
        
        return project_id
    
    async def test_v14_elements(self, project_id: str) -> str:
        """Test v1.4 element endpoints."""
        if not project_id:
            await self.log_test("v1.4 Elements Test", False, "No project ID available")
            return None
        
        # Create element
        element_data = {
            "name": "Test Prompt Template",
            "description": "A test prompt template for API testing",
            "project_id": project_id,
            "element_type": "PROMPT_TEMPLATE",
            "template_content": "You are a helpful assistant. Answer the following question: {question}",
            "variables": ["question"],
            "execution_config": {"temperature": 0.7, "max_tokens": 1000},
            "tags": ["test", "api"]
        }
        
        create_response = await self.make_request("POST", "/api/v1/elements/", element_data)
        create_success = create_response["status"] == 201
        
        element_id = None
        if create_success:
            element_id = create_response["data"]["id"]
        
        await self.log_test(
            "v1.4 Create Element",
            create_success,
            f"Status: {create_response['status']}, ID: {element_id or 'None'}"
        )
        
        # List elements
        list_response = await self.make_request("GET", "/api/v1/elements/", {"project_id": project_id})
        list_success = list_response["status"] == 200
        
        await self.log_test(
            "v1.4 List Elements",
            list_success,
            f"Status: {list_response['status']}"
        )
        
        # Execute element
        if element_id:
            execute_data = {"question": "What is artificial intelligence?"}
            execute_response = await self.make_request("POST", f"/api/v1/elements/{element_id}/execute", execute_data)
            execute_success = execute_response["status"] == 200
            
            await self.log_test(
                "v1.4 Execute Element",
                execute_success,
                f"Status: {execute_response['status']}"
            )
        
        return element_id
    
    async def test_v14_generations(self, element_id: str) -> None:
        """Test v1.4 generation endpoints."""
        # List generations
        list_response = await self.make_request("GET", "/api/v1/generations/")
        list_success = list_response["status"] == 200
        
        await self.log_test(
            "v1.4 List Generations",
            list_success,
            f"Status: {list_response['status']}"
        )
    
    async def test_v14_evaluations(self) -> None:
        """Test v1.4 evaluation endpoints."""
        # List evaluations
        list_response = await self.make_request("GET", "/api/v1/evaluations/")
        list_success = list_response["status"] == 200
        
        await self.log_test(
            "v1.4 List Evaluations",
            list_success,
            f"Status: {list_response['status']}"
        )
    
    async def test_v14_users(self) -> None:
        """Test v1.4 user endpoints."""
        # This will test when user routes are implemented
        pass
    
    async def test_v14_documents(self, project_id: str) -> None:
        """Test v1.4 document endpoints."""
        # List documents
        list_response = await self.make_request("GET", "/api/v1/documents/", {"project_id": project_id})
        list_success = list_response["status"] == 200
        
        await self.log_test(
            "v1.4 List Documents",
            list_success,
            f"Status: {list_response['status']}"
        )
    
    async def test_legacy_v13_endpoints(self) -> None:
        """Test legacy v1.3 endpoints for backward compatibility."""
        # Test generation endpoint (without actual generation)
        generation_data = {
            "query": "Test query for API testing",
            "max_tokens": 100,
            "temperature": 0.5
        }
        
        # Note: This will create a generation but may not complete due to LLM being disabled
        generation_response = await self.make_request("POST", "/generate", generation_data)
        generation_success = generation_response["status"] in [200, 503]  # 503 if LLM disabled
        
        await self.log_test(
            "v1.3 Legacy Generation",
            generation_success,
            f"Status: {generation_response['status']}"
        )
    
    async def test_admin_endpoints(self) -> None:
        """Test admin endpoints (requires admin privileges)."""
        # Test admin users list
        users_response = await self.make_request("GET", "/admin/users")
        # May fail if user is not admin - that's expected
        users_success = users_response["status"] in [200, 403]
        
        await self.log_test(
            "Admin Users List",
            users_success,
            f"Status: {users_response['status']}"
        )
        
        # Test admin system stats
        stats_response = await self.make_request("GET", "/admin/system-stats")
        stats_success = stats_response["status"] in [200, 403]
        
        await self.log_test(
            "Admin System Stats",
            stats_success,
            f"Status: {stats_response['status']}"
        )
    
    async def run_comprehensive_test(self) -> None:
        """Run comprehensive test suite."""
        print("🚀 Starting TinyRAG v1.4 Comprehensive API Tests")
        print("=" * 60)
        
        # 1. Test health check
        await self.test_health_check()
        
        # 2. Test authentication
        auth_success = await self.test_authentication_flow()
        
        if not auth_success:
            print("\n❌ Authentication failed - stopping tests")
            return
        
        # 3. Test v1.4 endpoints
        project_id = await self.test_v14_projects()
        element_id = await self.test_v14_elements(project_id)
        await self.test_v14_generations(element_id)
        await self.test_v14_evaluations()
        await self.test_v14_users()
        await self.test_v14_documents(project_id)
        
        # 4. Test legacy v1.3 endpoints
        await self.test_legacy_v13_endpoints()
        
        # 5. Test admin endpoints
        await self.test_admin_endpoints()
        
        # 6. Print summary
        await self.print_test_summary()
    
    async def print_test_summary(self) -> None:
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n📖 API Documentation Available at:")
        print(f"  - Swagger UI: {self.base_url}/docs")
        print(f"  - ReDoc: {self.base_url}/redoc")
        
        # Save detailed results
        with open("api_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: api_test_results.json")


async def main():
    """Main function to run comprehensive API tests."""
    print("Rules for AI loaded successfully!")
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status != 200:
                    print("❌ API server is not responding properly")
                    sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("🔧 Please ensure the API server is running on localhost:8000")
        sys.exit(1)
    
    # Run comprehensive tests
    async with TinyRAGAPITester() as tester:
        await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main()) 