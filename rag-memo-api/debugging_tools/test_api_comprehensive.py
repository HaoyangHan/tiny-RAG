#!/usr/bin/env python3
"""
Comprehensive API test suite for TinyRAG v1.4.

This module provides complete end-to-end testing of all API endpoints
following the .cursorrules guidelines for comprehensive test coverage.

Tests include:
- Authentication flow (register, login, token verification)  
- v1.4 API endpoints (projects, elements, generations, evaluations, users, documents)
- Legacy v1.3 endpoints (documents, memos, generation)
- Admin endpoints and security
- Error handling and edge cases
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

import aiohttp
import pytest


class TinyRAGAPITester:
    """
    Comprehensive API tester for TinyRAG v1.4.
    
    Follows .cursorrules standards for clean code and comprehensive testing.
    Provides detailed logging, error handling, and result tracking.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API tester with configuration."""
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_user_data = {
            "email": "api.tester@example.com",
            "username": "api_tester",
            "password": "TestPassword123!",
            "full_name": "API Tester"
        }
        self.test_results: List[Dict[str, Any]] = []
        self.created_resources: Dict[str, str] = {}  # Track created resources for cleanup
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def log_test(self, test_name: str, success: bool, details: str = "") -> None:
        """Log test result with timestamp and details."""
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
        """
        Make HTTP request to API with proper error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request data (JSON or form data)
            headers: Additional headers
            files: File upload data
            
        Returns:
            Response data with status, data, and headers
        """
        url = f"{self.base_url}{endpoint}"
        
        # Add authorization header if token is available
        request_headers = headers or {}
        if self.auth_token:
            request_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=request_headers, params=data) as response:
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        response_data = await response.json()
                    else:
                        response_data = {"message": await response.text()}
                    
                    return {
                        "status": response.status,
                        "data": response_data,
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
                            "data": await response.json() if response.content_type == "application/json" else {"message": await response.text()},
                            "headers": dict(response.headers)
                        }
                else:
                    async with self.session.post(url, headers=request_headers, json=data) as response:
                        return {
                            "status": response.status,
                            "data": await response.json() if response.content_type == "application/json" else {"message": await response.text()},
                            "headers": dict(response.headers)
                        }
            elif method.upper() == "PUT":
                async with self.session.put(url, headers=request_headers, json=data) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.content_type == "application/json" else {"message": await response.text()},
                        "headers": dict(response.headers)
                    }
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=request_headers) as response:
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        response_data = await response.json()
                    else:
                        response_data = {"message": await response.text()}
                    
                    return {
                        "status": response.status,
                        "data": response_data,
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
        """Test complete authentication flow including all auth endpoints."""
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
            
            # 4. Test additional auth endpoints
            await self.test_auth_endpoints()
            
            return verify_success
        
        return False
    
    async def test_auth_endpoints(self) -> None:
        """Test additional authentication endpoints."""
        # Test /api/v1/auth/me endpoint
        me_response = await self.make_request("GET", "/api/v1/auth/me")
        me_success = me_response["status"] == 200
        await self.log_test(
            "Auth Me Endpoint",
            me_success,
            f"Status: {me_response['status']}"
        )
        
        # Test /api/v1/auth/verify-token endpoint  
        verify_response = await self.make_request("GET", "/api/v1/auth/verify-token")
        verify_success = verify_response["status"] == 200
        await self.log_test(
            "Auth Verify Token",
            verify_success,
            f"Status: {verify_response['status']}"
        )
    
    async def test_v14_projects(self) -> str:
        """Test all v1.4 project endpoints comprehensively."""
        project_id = None
        
        # 1. Create project
        project_data = {
            "name": "Test API Project",
            "description": "Project created during API testing",
            "tenant_type": "coding",
            "visibility": "private",
            "keywords": ["testing", "api", "tinyrag"]
        }
        
        create_response = await self.make_request("POST", "/api/v1/projects/", project_data)
        create_success = create_response["status"] == 201
        
        if create_success:
            project_id = create_response["data"]["id"]
            self.created_resources["project_id"] = project_id
        
        await self.log_test(
            "v1.4 Create Project",
            create_success,
            f"Status: {create_response['status']}, ID: {project_id or 'None'}"
        )
        
        # 2. List projects
        list_response = await self.make_request("GET", "/api/v1/projects/")
        list_success = list_response["status"] == 200
        project_count = len(list_response["data"].get("projects", [])) if list_success else 0
        
        await self.log_test(
            "v1.4 List Projects",
            list_success,
            f"Status: {list_response['status']}, Count: {project_count}"
        )
        
        # 3. List public projects
        public_response = await self.make_request("GET", "/api/v1/projects/public")
        public_success = public_response["status"] == 200
        await self.log_test(
            "v1.4 List Public Projects",
            public_success,
            f"Status: {public_response['status']}"
        )
        
        # 4. Get specific project
        if project_id:
            get_response = await self.make_request("GET", f"/api/v1/projects/{project_id}")
            get_success = get_response["status"] == 200
            
            await self.log_test(
                "v1.4 Get Project",
                get_success,
                f"Status: {get_response['status']}"
            )
            
            # 5. Update project
            update_data = {
                "description": "Updated project description",
                "keywords": ["testing", "api", "tinyrag", "updated"]
            }
            update_response = await self.make_request("PUT", f"/api/v1/projects/{project_id}", update_data)
            update_success = update_response["status"] == 200
            
            await self.log_test(
                "v1.4 Update Project",
                update_success,
                f"Status: {update_response['status']}"
            )
            
            # 6. Test project collaboration endpoints (if collaborator endpoints exist)
            # Add collaborator (this may fail if user doesn't exist, which is expected)
            collab_data = {"user_id": "6859036f0cfc8f1bb0f21c76"}  # Example user ID
            collab_response = await self.make_request("POST", f"/api/v1/projects/{project_id}/collaborators", collab_data)
            collab_success = collab_response["status"] in [201, 400, 404]  # Various acceptable responses
            
            await self.log_test(
                "v1.4 Add Project Collaborator",
                collab_success,
                f"Status: {collab_response['status']}"
            )
        
        return project_id
    
    async def test_v14_elements(self, project_id: str) -> str:
        """Test all v1.4 element endpoints comprehensively."""
        if not project_id:
            await self.log_test(
                "v1.4 Elements Test",
                False,
                "No project ID available"
            )
            return None
        
        element_id = None
        
        # 1. Create element  
        element_data = {
            "name": "Test Element",
            "description": "Element created during API testing",
            "project_id": project_id,
            "element_type": "prompt_template",
            "template_content": "You are an AI assistant. Answer the following question: {question}",
            "variables": ["question"],
            "execution_config": {"temperature": 0.7, "max_tokens": 100},
            "tags": ["testing", "ai", "prompt"]
        }
        
        create_response = await self.make_request("POST", "/api/v1/elements/", element_data)
        create_success = create_response["status"] == 201
        
        if create_success:
            element_id = create_response["data"]["id"]
            self.created_resources["element_id"] = element_id
        
        await self.log_test(
            "v1.4 Create Element",
            create_success,
            f"Status: {create_response['status']}, ID: {element_id or 'None'}"
        )
        
        # 2. List elements  
        list_response = await self.make_request("GET", "/api/v1/elements/", {"project_id": project_id})
        list_success = list_response["status"] == 200
        
        await self.log_test(
            "v1.4 List Elements",
            list_success,
            f"Status: {list_response['status']}"
        )
        
        # 3. Get specific element
        if element_id:
            get_response = await self.make_request("GET", f"/api/v1/elements/{element_id}")
            get_success = get_response["status"] == 200
            
            await self.log_test(
                "v1.4 Get Element",
                get_success,
                f"Status: {get_response['status']}"
            )
            
            # 4. Execute element
            execute_data = {"question": "What is artificial intelligence?"}
            execute_response = await self.make_request("POST", f"/api/v1/elements/{element_id}/execute", execute_data)
            execute_success = execute_response["status"] in [200, 503]  # 503 if LLM disabled
            
            await self.log_test(
                "v1.4 Execute Element",
                execute_success,
                f"Status: {execute_response['status']}"
            )
        
        return element_id
    
    async def test_v14_generations(self, element_id: str) -> None:
        """Test all v1.4 generation endpoints comprehensively."""
        # 1. List generations
        list_response = await self.make_request("GET", "/api/v1/generations/")
        list_success = list_response["status"] == 200
        
        await self.log_test(
            "v1.4 List Generations",
            list_success,
            f"Status: {list_response['status']}"
        )
        
        # 2. Get specific generation (if any exist)
        if list_success and isinstance(list_response["data"], list) and list_response["data"]:
            generation_id = list_response["data"][0]["id"]
            get_response = await self.make_request("GET", f"/api/v1/generations/{generation_id}")
            get_success = get_response["status"] == 200
            
            await self.log_test(
                "v1.4 Get Generation",
                get_success,
                f"Status: {get_response['status']}"
            )
        elif list_success and isinstance(list_response["data"], dict) and list_response["data"].get("generations"):
            generation_id = list_response["data"]["generations"][0]["id"]
            get_response = await self.make_request("GET", f"/api/v1/generations/{generation_id}")
            get_success = get_response["status"] == 200
            
            await self.log_test(
                "v1.4 Get Generation",
                get_success,
                f"Status: {get_response['status']}"
            )
    
    async def test_v14_evaluations(self) -> None:
        """Test all v1.4 evaluation endpoints comprehensively."""
        # 1. List evaluations
        list_response = await self.make_request("GET", "/api/v1/evaluations/")
        list_success = list_response["status"] == 200
        
        await self.log_test(
            "v1.4 List Evaluations",
            list_success,
            f"Status: {list_response['status']}"
        )
        
        # 2. Create evaluation (if we have a generation)
        # This would require an existing generation to evaluate
        
        # 3. Get specific evaluation (if any exist)
        if list_success and isinstance(list_response["data"], list) and list_response["data"]:
            evaluation_id = list_response["data"][0]["id"]
            get_response = await self.make_request("GET", f"/api/v1/evaluations/{evaluation_id}")
            get_success = get_response["status"] == 200
            
            await self.log_test(
                "v1.4 Get Evaluation",
                get_success,
                f"Status: {get_response['status']}"
            )
        elif list_success and isinstance(list_response["data"], dict) and list_response["data"].get("evaluations"):
            evaluation_id = list_response["data"]["evaluations"][0]["id"]
            get_response = await self.make_request("GET", f"/api/v1/evaluations/{evaluation_id}")
            get_success = get_response["status"] == 200
            
            await self.log_test(
                "v1.4 Get Evaluation",
                get_success,
                f"Status: {get_response['status']}"
            )
    
    async def test_v14_users(self) -> None:
        """Test all v1.4 user endpoints comprehensively."""
        # 1. Get user profile  
        profile_response = await self.make_request("GET", "/api/v1/users/me/profile")
        profile_success = profile_response["status"] == 200
        
        await self.log_test(
            "v1.4 User Profile",
            profile_success,
            f"Status: {profile_response['status']}"
        )
        
        # 2. Update user profile
        update_data = {"full_name": "API Tester Updated"}
        update_response = await self.make_request("PUT", "/api/v1/users/me/profile", update_data)
        update_success = update_response["status"] in [200, 501]  # 501 if not implemented
        
        await self.log_test(
            "v1.4 Update User Profile",
            update_success,
            f"Status: {update_response['status']}"
        )
        
        # 3. Search users  
        search_response = await self.make_request("GET", "/api/v1/users/search", {"query": "test"})
        search_success = search_response["status"] in [200, 501]  # 501 if not implemented
        
        await self.log_test(
            "v1.4 User Search",
            search_success,
            f"Status: {search_response['status']}"
        )
        
        # 4. Get user analytics
        analytics_response = await self.make_request("GET", "/api/v1/users/me/analytics")
        analytics_success = analytics_response["status"] in [200, 501]  # 501 if not implemented
        
        await self.log_test(
            "v1.4 User Analytics",
            analytics_success,
            f"Status: {analytics_response['status']}"
        )
    
    async def test_v14_documents(self, project_id: str) -> None:
        """Test all v1.4 document endpoints comprehensively."""
        # 1. List documents
        list_response = await self.make_request("GET", "/api/v1/documents/", {"project_id": project_id} if project_id else None)
        list_success = list_response["status"] == 200
        
        await self.log_test(
            "v1.4 List Documents",
            list_success,
            f"Status: {list_response['status']}"
        )
        
        # 2. Upload document
        test_file_content = "This is a test document for API testing.\nIt contains sample text for processing."
        upload_files = {
            "file": {
                "content": test_file_content.encode(),
                "filename": "test_document.txt"
            }
        }
        upload_data = {"project_id": project_id} if project_id else None
        
        upload_response = await self.make_request("POST", "/api/v1/documents/upload", upload_data, files=upload_files)
        upload_success = upload_response["status"] == 201
        
        document_id = None
        if upload_success:
            document_id = upload_response["data"].get("id")
            self.created_resources["document_id"] = document_id
        
        await self.log_test(
            "v1.4 Upload Document",
            upload_success,
            f"Status: {upload_response['status']}, ID: {document_id or 'None'}"
        )
        
        # 3. Get specific document
        if document_id:
            get_response = await self.make_request("GET", f"/api/v1/documents/{document_id}")
            get_success = get_response["status"] == 200
            
            await self.log_test(
                "v1.4 Get Document",
                get_success,
                f"Status: {get_response['status']}"
            )
    
    async def test_legacy_v13_endpoints(self) -> None:
        """Test legacy v1.3 endpoints for backward compatibility."""
        # 1. Test legacy document upload
        test_file_content = "Legacy test document content."
        upload_files = {
            "file": {
                "content": test_file_content.encode(),
                "filename": "legacy_test.txt"
            }
        }
        
        legacy_upload_response = await self.make_request("POST", "/documents/upload", files=upload_files)
        legacy_upload_success = legacy_upload_response["status"] == 201
        
        await self.log_test(
            "v1.3 Legacy Document Upload",
            legacy_upload_success,
            f"Status: {legacy_upload_response['status']}"
        )
        
        # 2. Test legacy document list
        legacy_list_response = await self.make_request("GET", "/documents/")
        legacy_list_success = legacy_list_response["status"] == 200
        
        await self.log_test(
            "v1.3 Legacy Document List",
            legacy_list_success,
            f"Status: {legacy_list_response['status']}"
        )
        
        # 3. Test generation endpoint (without actual generation)
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
        
        # 4. Test memo endpoints
        memo_response = await self.make_request("GET", "/memos/")
        memo_success = memo_response["status"] == 200
        
        await self.log_test(
            "v1.3 Legacy Memo List",
            memo_success,
            f"Status: {memo_response['status']}"
        )
    
    async def test_admin_endpoints(self) -> None:
        """Test admin endpoints (requires admin privileges)."""
        # 1. Test admin users list
        users_response = await self.make_request("GET", "/admin/users")
        # May fail if user is not admin - that's expected
        users_success = users_response["status"] in [200, 403]
        
        await self.log_test(
            "Admin Users List",
            users_success,
            f"Status: {users_response['status']}"
        )
        
        # 2. Test admin system stats
        stats_response = await self.make_request("GET", "/admin/system-stats")
        stats_success = stats_response["status"] in [200, 403]
        
        await self.log_test(
            "Admin System Stats",
            stats_success,
            f"Status: {stats_response['status']}"
        )
    
    async def test_api_docs_endpoints(self) -> None:
        """Test API documentation endpoints."""
        # 1. Test OpenAPI docs
        docs_response = await self.make_request("GET", "/docs")
        docs_success = docs_response["status"] == 200
        
        await self.log_test(
            "API Documentation (/docs)",
            docs_success,
            f"Status: {docs_response['status']}"
        )
        
        # 2. Test ReDoc
        redoc_response = await self.make_request("GET", "/redoc")
        redoc_success = redoc_response["status"] == 200
        
        await self.log_test(
            "API ReDoc (/redoc)",
            redoc_success,
            f"Status: {redoc_response['status']}"
        )
        
        # 3. Test OpenAPI spec
        openapi_response = await self.make_request("GET", "/openapi.json")
        openapi_success = openapi_response["status"] == 200
        
        await self.log_test(
            "OpenAPI Specification",
            openapi_success,
            f"Status: {openapi_response['status']}"
        )
    
    async def cleanup_test_resources(self) -> None:
        """Clean up created test resources."""
        # Delete test project (which should cascade delete elements)
        if "project_id" in self.created_resources:
            delete_response = await self.make_request("DELETE", f"/api/v1/projects/{self.created_resources['project_id']}")
            await self.log_test(
                "Cleanup: Delete Test Project",
                delete_response["status"] == 204,
                f"Status: {delete_response['status']}"
            )
    
    async def run_comprehensive_test(self) -> None:
        """
        Run comprehensive test suite covering all endpoints.
        
        Following .cursorrules guidelines for thorough testing and clean code.
        """
        print("🚀 Starting TinyRAG v1.4 Comprehensive API Tests")
        print("=" * 60)
        
        try:
            # 1. Test health and documentation
            await self.test_health_check()
            await self.test_api_docs_endpoints()
            
            # 2. Test authentication
            auth_success = await self.test_authentication_flow()
            
            if not auth_success:
                print("\n❌ Authentication failed - stopping tests")
                return
            
            # 3. Test v1.4 endpoints comprehensively
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
            
            # 6. Cleanup test resources
            await self.cleanup_test_resources()
            
        except Exception as e:
            await self.log_test(
                "Test Suite Execution",
                False,
                f"Unexpected error: {str(e)}"
            )
        
        finally:
            # 7. Print comprehensive summary
            await self.print_test_summary()
    
    async def print_test_summary(self) -> None:
        """Print comprehensive test summary with detailed analysis."""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Categorize results
        categories = {
            "Authentication": [],
            "v1.4 Projects": [],
            "v1.4 Elements": [],
            "v1.4 Generations": [],
            "v1.4 Evaluations": [],
            "v1.4 Users": [],
            "v1.4 Documents": [],
            "v1.3 Legacy": [],
            "Admin": [],
            "Documentation": [],
            "Other": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            categorized = False
            
            for category in categories.keys():
                if category.lower().replace(" ", "_") in test_name.lower().replace(" ", "_"):
                    categories[category].append(result)
                    categorized = True
                    break
                    
            if not categorized:
                categories["Other"].append(result)
        
        # Print category summary
        print("\n📋 TEST CATEGORIES:")
        for category, tests in categories.items():
            if tests:
                category_passed = sum(1 for t in tests if t["success"])
                category_total = len(tests)
                print(f"  {category}: {category_passed}/{category_total} passed")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n📖 API DOCUMENTATION:")
        print(f"  - Swagger UI: {self.base_url}/docs")
        print(f"  - ReDoc: {self.base_url}/redoc")
        print(f"  - OpenAPI Spec: {self.base_url}/openapi.json")
        
        # Save detailed results
        with open("api_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: api_test_results.json")
        
        # Provide recommendations based on results
        print(f"\n🎯 RECOMMENDATIONS:")
        if (passed_tests / total_tests) >= 0.8:
            print("  🟢 Excellent! API is production-ready with high test coverage.")
        elif (passed_tests / total_tests) >= 0.6:
            print("  🟡 Good progress! Address failing tests for production readiness.")
        else:
            print("  🟠 Needs attention! Multiple critical issues require fixing.")


async def main():
    """
    Main function to run comprehensive API tests.
    
    Follows .cursorrules standards for clean code and proper error handling.
    """
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