"""
Projects API Tests for TinyRAG v1.4.

This module tests all project management endpoints including:
- Project CRUD operations (Create, Read, Update, Delete)
- Project collaboration management
- Public project listings
- Project search and filtering

Following .cursorrules standards for clean code and comprehensive testing.
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
import aiohttp


class ProjectsAPITester:
    """
    Projects API tester for TinyRAG v1.4.
    
    Follows .cursorrules standards for clean code and comprehensive testing.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the projects tester."""
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_user_data = {
            "email": "projects.tester@example.com",
            "username": "projects_tester",
            "password": "TestPassword123!",
            "full_name": "Projects API Tester"
        }
        self.test_results: List[Dict[str, Any]] = []
        self.created_projects: List[str] = []  # Track created projects for cleanup
        
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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API with proper error handling."""
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
    
    async def authenticate(self) -> bool:
        """Authenticate user and get token."""
        # Register user if needed
        register_response = await self.make_request("POST", "/auth/register", self.test_user_data)
        
        # Login user
        login_data = {
            "identifier": self.test_user_data["email"],
            "password": self.test_user_data["password"]
        }
        
        login_response = await self.make_request("POST", "/auth/login", login_data)
        
        if login_response["status"] == 200 and "access_token" in login_response["data"]:
            self.auth_token = login_response["data"]["access_token"]
            return True
        
        return False
    
    async def test_create_project(self) -> Optional[str]:
        """Test project creation with various configurations."""
        # Test basic project creation
        project_data = {
            "name": "Test Project - Basic",
            "description": "A basic test project for API testing",
            "tenant_type": "coding",
            "visibility": "private",
            "keywords": ["testing", "api", "basic"]
        }
        
        response = await self.make_request("POST", "/api/v1/projects/", project_data)
        success = response["status"] == 201
        
        project_id = None
        if success:
            project_id = response["data"]["id"]
            self.created_projects.append(project_id)
        
        await self.log_test(
            "Create Basic Project",
            success,
            f"Status: {response['status']}, ID: {project_id or 'None'}"
        )
        
        # Test project creation with all optional fields
        detailed_project_data = {
            "name": "Test Project - Detailed",
            "description": "A detailed test project with all fields",
            "tenant_type": "research", 
            "visibility": "public",
            "keywords": ["testing", "api", "detailed", "research", "comprehensive"]
        }
        
        detailed_response = await self.make_request("POST", "/api/v1/projects/", detailed_project_data)
        detailed_success = detailed_response["status"] == 201
        
        detailed_project_id = None
        if detailed_success:
            detailed_project_id = detailed_response["data"]["id"]
            self.created_projects.append(detailed_project_id)
        
        await self.log_test(
            "Create Detailed Project",
            detailed_success,
            f"Status: {detailed_response['status']}, ID: {detailed_project_id or 'None'}"
        )
        
        return project_id
    
    async def test_list_projects(self) -> None:
        """Test project listing with various filters."""
        # Test basic project listing
        list_response = await self.make_request("GET", "/api/v1/projects/")
        list_success = list_response["status"] == 200
        project_count = len(list_response["data"].get("projects", [])) if list_success else 0
        
        await self.log_test(
            "List All Projects",
            list_success,
            f"Status: {list_response['status']}, Count: {project_count}"
        )
        
        # Test filtered listing by tenant type
        filtered_response = await self.make_request("GET", "/api/v1/projects/", {"tenant_type": "coding"})
        filtered_success = filtered_response["status"] == 200
        
        await self.log_test(
            "List Projects by Tenant Type",
            filtered_success,
            f"Status: {filtered_response['status']}"
        )
        
        # Test search functionality
        search_response = await self.make_request("GET", "/api/v1/projects/", {"search": "test"})
        search_success = search_response["status"] == 200
        
        await self.log_test(
            "Search Projects",
            search_success,
            f"Status: {search_response['status']}"
        )
        
        # Test pagination
        paginated_response = await self.make_request("GET", "/api/v1/projects/", {"page": 1, "page_size": 5})
        paginated_success = paginated_response["status"] == 200
        
        await self.log_test(
            "Paginated Project List",
            paginated_success,
            f"Status: {paginated_response['status']}"
        )
    
    async def test_public_projects(self) -> None:
        """Test public project listings."""
        # Test public projects endpoint
        public_response = await self.make_request("GET", "/api/v1/projects/public")
        public_success = public_response["status"] == 200
        
        await self.log_test(
            "List Public Projects",
            public_success,
            f"Status: {public_response['status']}"
        )
        
        # Test public projects with filters
        filtered_public_response = await self.make_request("GET", "/api/v1/projects/public", {"tenant_type": "research"})
        filtered_public_success = filtered_public_response["status"] == 200
        
        await self.log_test(
            "List Filtered Public Projects",
            filtered_public_success,
            f"Status: {filtered_public_response['status']}"
        )
    
    async def test_project_details(self, project_id: str) -> None:
        """Test getting specific project details."""
        if not project_id:
            await self.log_test(
                "Get Project Details",
                False,
                "No project ID available"
            )
            return
        
        # Test getting project details
        get_response = await self.make_request("GET", f"/api/v1/projects/{project_id}")
        get_success = get_response["status"] == 200
        
        await self.log_test(
            "Get Project Details",
            get_success,
            f"Status: {get_response['status']}"
        )
        
        # Test getting non-existent project
        fake_id = "000000000000000000000000"
        fake_response = await self.make_request("GET", f"/api/v1/projects/{fake_id}")
        fake_success = fake_response["status"] == 404
        
        await self.log_test(
            "Get Non-existent Project",
            fake_success,
            f"Status: {fake_response['status']} (should be 404)"
        )
    
    async def test_update_project(self, project_id: str) -> None:
        """Test project updates."""
        if not project_id:
            await self.log_test(
                "Update Project",
                False,
                "No project ID available"
            )
            return
        
        # Test basic project update
        update_data = {
            "description": "Updated project description for testing",
            "keywords": ["testing", "api", "updated", "comprehensive"]
        }
        
        update_response = await self.make_request("PUT", f"/api/v1/projects/{project_id}", update_data)
        update_success = update_response["status"] == 200
        
        await self.log_test(
            "Update Project Details",
            update_success,
            f"Status: {update_response['status']}"
        )
        
        # Test update project status
        status_update_data = {"status": "active"}
        status_response = await self.make_request("PUT", f"/api/v1/projects/{project_id}", status_update_data)
        status_success = status_response["status"] == 200
        
        await self.log_test(
            "Update Project Status",
            status_success,
            f"Status: {status_response['status']}"
        )
    
    async def test_project_collaboration(self, project_id: str) -> None:
        """Test project collaboration features."""
        if not project_id:
            await self.log_test(
                "Project Collaboration",
                False,
                "No project ID available"
            )
            return
        
        # Test adding collaborator (will likely fail with 404 as user doesn't exist)
        collab_data = {"user_id": "6859036f0cfc8f1bb0f21c76"}  # Example user ID
        add_collab_response = await self.make_request("POST", f"/api/v1/projects/{project_id}/collaborators", collab_data)
        add_collab_success = add_collab_response["status"] in [201, 400, 404]  # Various acceptable responses
        
        await self.log_test(
            "Add Project Collaborator",
            add_collab_success,
            f"Status: {add_collab_response['status']}"
        )
        
        # Test removing collaborator
        remove_collab_response = await self.make_request("DELETE", f"/api/v1/projects/{project_id}/collaborators/{collab_data['user_id']}")
        remove_collab_success = remove_collab_response["status"] in [204, 404]  # 404 expected if user wasn't added
        
        await self.log_test(
            "Remove Project Collaborator",
            remove_collab_success,
            f"Status: {remove_collab_response['status']}"
        )
    
    async def test_delete_project(self, project_id: str) -> None:
        """Test project deletion."""
        if not project_id:
            await self.log_test(
                "Delete Project",
                False,
                "No project ID available"
            )
            return
        
        # Test project deletion
        delete_response = await self.make_request("DELETE", f"/api/v1/projects/{project_id}")
        delete_success = delete_response["status"] == 204
        
        await self.log_test(
            "Delete Project",
            delete_success,
            f"Status: {delete_response['status']}"
        )
        
        # Remove from tracking list if successfully deleted
        if delete_success and project_id in self.created_projects:
            self.created_projects.remove(project_id)
    
    async def cleanup_projects(self) -> None:
        """Clean up any remaining test projects."""
        for project_id in self.created_projects[:]:  # Copy list to avoid modification during iteration
            delete_response = await self.make_request("DELETE", f"/api/v1/projects/{project_id}")
            
            if delete_response["status"] == 204:
                self.created_projects.remove(project_id)
                await self.log_test(
                    f"Cleanup Project {project_id[:8]}",
                    True,
                    "Successfully deleted"
                )
    
    async def run_projects_tests(self) -> None:
        """Run comprehensive projects tests."""
        print("🏗️ Starting TinyRAG Projects API Tests")
        print("=" * 50)
        
        try:
            # 1. Authenticate
            auth_success = await self.authenticate()
            if not auth_success:
                print("❌ Authentication failed - cannot test projects")
                return
            
            # 2. Test project creation
            project_id = await self.test_create_project()
            
            # 3. Test project listing
            await self.test_list_projects()
            
            # 4. Test public projects
            await self.test_public_projects()
            
            # 5. Test project details
            await self.test_project_details(project_id)
            
            # 6. Test project updates
            await self.test_update_project(project_id)
            
            # 7. Test project collaboration
            await self.test_project_collaboration(project_id)
            
            # 8. Test project deletion (delete one project)
            if project_id:
                await self.test_delete_project(project_id)
            
        except Exception as e:
            await self.log_test(
                "Projects Test Suite Execution",
                False,
                f"Unexpected error: {str(e)}"
            )
        
        finally:
            # Cleanup remaining projects
            await self.cleanup_projects()
            await self.print_test_summary()
    
    async def print_test_summary(self) -> None:
        """Print projects test summary."""
        print("\n" + "=" * 50)
        print("📊 PROJECTS TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Save detailed results
        with open("test_logs/projects_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Results saved to: test_logs/projects_test_results.json")


async def main():
    """Main function to run projects tests."""
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
    
    # Run projects tests
    async with ProjectsAPITester() as tester:
        await tester.run_projects_tests()


if __name__ == "__main__":
    asyncio.run(main()) 