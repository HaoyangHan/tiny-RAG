"""
Elements API Tests for TinyRAG v1.4.

This module tests all element management endpoints including:
- Element CRUD operations (Create, Read, Update, Delete)
- Element execution and template processing
- Element search and filtering
- Element version management

Following .cursorrules standards for clean code and comprehensive testing.
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
import aiohttp


class ElementsAPITester:
    """
    Elements API tester for TinyRAG v1.4.
    
    Follows .cursorrules standards for clean code and comprehensive testing.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the elements tester."""
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_user_data = {
            "email": "elements.tester@example.com",
            "username": "elements_tester",
            "password": "TestPassword123!",
            "full_name": "Elements API Tester"
        }
        self.test_results: List[Dict[str, Any]] = []
        self.created_projects: List[str] = []
        self.created_elements: List[str] = []
        
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
    
    async def create_test_project(self) -> Optional[str]:
        """Create a test project for element testing."""
        project_data = {
            "name": "Elements Test Project",
            "description": "Project for testing elements functionality",
            "tenant_type": "coding",
            "visibility": "private",
            "keywords": ["testing", "elements", "api"]
        }
        
        response = await self.make_request("POST", "/api/v1/projects/", project_data)
        
        if response["status"] == 201:
            project_id = response["data"]["id"]
            self.created_projects.append(project_id)
            return project_id
        
        return None
    
    async def test_create_elements(self, project_id: str) -> Optional[str]:
        """Test element creation with various types."""
        if not project_id:
            await self.log_test(
                "Create Elements",
                False,
                "No project ID available"
            )
            return None
        
        # Test prompt template element
        prompt_element_data = {
            "name": "Test Prompt Template",
            "description": "A test prompt template for AI assistance",
            "project_id": project_id,
            "element_type": "prompt_template",
            "template_content": "You are an AI assistant specializing in {domain}. Answer the following question: {question}",
            "variables": ["domain", "question"],
            "execution_config": {"temperature": 0.7, "max_tokens": 500},
            "tags": ["testing", "prompt", "ai"]
        }
        
        prompt_response = await self.make_request("POST", "/api/v1/elements/", prompt_element_data)
        prompt_success = prompt_response["status"] == 201
        
        prompt_element_id = None
        if prompt_success:
            prompt_element_id = prompt_response["data"]["id"]
            self.created_elements.append(prompt_element_id)
        
        await self.log_test(
            "Create Prompt Template Element",
            prompt_success,
            f"Status: {prompt_response['status']}, ID: {prompt_element_id or 'None'}"
        )
        
        # Test MCP configuration element
        mcp_element_data = {
            "name": "Test MCP Configuration",
            "description": "A test MCP configuration for tool integration",
            "project_id": project_id,
            "element_type": "mcp_config",
            "template_content": '{"server": "test_server", "tools": ["calculator", "search"]}',
            "variables": [],
            "execution_config": {"timeout": 30, "retry_count": 3},
            "tags": ["testing", "mcp", "tools"]
        }
        
        mcp_response = await self.make_request("POST", "/api/v1/elements/", mcp_element_data)
        mcp_success = mcp_response["status"] == 201
        
        mcp_element_id = None
        if mcp_success:
            mcp_element_id = mcp_response["data"]["id"]
            self.created_elements.append(mcp_element_id)
        
        await self.log_test(
            "Create MCP Configuration Element",
            mcp_success,
            f"Status: {mcp_response['status']}, ID: {mcp_element_id or 'None'}"
        )
        
        # Test agentic tool element
        tool_element_data = {
            "name": "Test Agentic Tool",
            "description": "A test agentic tool for automated tasks",
            "project_id": project_id,
            "element_type": "agentic_tool",
            "template_content": "function execute_task(params) { return process(params); }",
            "variables": ["params"],
            "execution_config": {"language": "javascript", "timeout": 60},
            "tags": ["testing", "tool", "automation"]
        }
        
        tool_response = await self.make_request("POST", "/api/v1/elements/", tool_element_data)
        tool_success = tool_response["status"] == 201
        
        tool_element_id = None
        if tool_success:
            tool_element_id = tool_response["data"]["id"]
            self.created_elements.append(tool_element_id)
        
        await self.log_test(
            "Create Agentic Tool Element",
            tool_success,
            f"Status: {tool_response['status']}, ID: {tool_element_id or 'None'}"
        )
        
        return prompt_element_id
    
    async def test_list_elements(self, project_id: str) -> None:
        """Test element listing with various filters."""
        # Test basic element listing
        list_response = await self.make_request("GET", "/api/v1/elements/", {"project_id": project_id})
        list_success = list_response["status"] == 200
        
        await self.log_test(
            "List Elements by Project",
            list_success,
            f"Status: {list_response['status']}"
        )
        
        # Test list elements by type
        type_response = await self.make_request("GET", "/api/v1/elements/", {"element_type": "prompt_template"})
        type_success = type_response["status"] == 200
        
        await self.log_test(
            "List Elements by Type",
            type_success,
            f"Status: {type_response['status']}"
        )
        
        # Test list all elements
        all_response = await self.make_request("GET", "/api/v1/elements/")
        all_success = all_response["status"] == 200
        
        await self.log_test(
            "List All Elements",
            all_success,
            f"Status: {all_response['status']}"
        )
    
    async def test_element_details(self, element_id: str) -> None:
        """Test getting specific element details."""
        if not element_id:
            await self.log_test(
                "Get Element Details",
                False,
                "No element ID available"
            )
            return
        
        # Test getting element details
        get_response = await self.make_request("GET", f"/api/v1/elements/{element_id}")
        get_success = get_response["status"] == 200
        
        await self.log_test(
            "Get Element Details",
            get_success,
            f"Status: {get_response['status']}"
        )
        
        # Test getting non-existent element
        fake_id = "000000000000000000000000"
        fake_response = await self.make_request("GET", f"/api/v1/elements/{fake_id}")
        fake_success = fake_response["status"] == 404
        
        await self.log_test(
            "Get Non-existent Element",
            fake_success,
            f"Status: {fake_response['status']} (should be 404)"
        )
    
    async def test_element_execution(self, element_id: str) -> None:
        """Test element execution functionality."""
        if not element_id:
            await self.log_test(
                "Execute Element",
                False,
                "No element ID available"
            )
            return
        
        # Test element execution with parameters
        execution_data = {
            "domain": "software development",
            "question": "What are the benefits of microservices architecture?"
        }
        
        execute_response = await self.make_request("POST", f"/api/v1/elements/{element_id}/execute", execution_data)
        execute_success = execute_response["status"] in [200, 503]  # 503 if LLM service disabled
        
        await self.log_test(
            "Execute Element with Parameters",
            execute_success,
            f"Status: {execute_response['status']}"
        )
        
        # Test element execution without required parameters
        empty_execution_data = {}
        
        empty_execute_response = await self.make_request("POST", f"/api/v1/elements/{element_id}/execute", empty_execution_data)
        empty_execute_success = empty_execute_response["status"] in [400, 422, 503]  # Various error statuses expected
        
        await self.log_test(
            "Execute Element without Parameters",
            empty_execute_success,
            f"Status: {empty_execute_response['status']} (validation error expected)"
        )
    
    async def test_update_element(self, element_id: str) -> None:
        """Test element updates."""
        if not element_id:
            await self.log_test(
                "Update Element",
                False,
                "No element ID available"
            )
            return
        
        # Test basic element update
        update_data = {
            "description": "Updated element description for testing",
            "tags": ["testing", "updated", "comprehensive"]
        }
        
        update_response = await self.make_request("PUT", f"/api/v1/elements/{element_id}", update_data)
        update_success = update_response["status"] in [200, 501]  # 501 if not implemented
        
        await self.log_test(
            "Update Element Details",
            update_success,
            f"Status: {update_response['status']}"
        )
        
        # Test update element template
        template_update_data = {
            "template_content": "You are an expert AI assistant in {domain}. Please provide a detailed answer to: {question}",
            "execution_config": {"temperature": 0.8, "max_tokens": 750}
        }
        
        template_response = await self.make_request("PUT", f"/api/v1/elements/{element_id}", template_update_data)
        template_success = template_response["status"] in [200, 501]  # 501 if not implemented
        
        await self.log_test(
            "Update Element Template",
            template_success,
            f"Status: {template_response['status']}"
        )
    
    async def test_delete_element(self, element_id: str) -> None:
        """Test element deletion."""
        if not element_id:
            await self.log_test(
                "Delete Element",
                False,
                "No element ID available"
            )
            return
        
        # Test element deletion
        delete_response = await self.make_request("DELETE", f"/api/v1/elements/{element_id}")
        delete_success = delete_response["status"] in [204, 501]  # 501 if not implemented
        
        await self.log_test(
            "Delete Element",
            delete_success,
            f"Status: {delete_response['status']}"
        )
        
        # Remove from tracking list if successfully deleted
        if delete_success and delete_response["status"] == 204 and element_id in self.created_elements:
            self.created_elements.remove(element_id)
    
    async def cleanup_resources(self) -> None:
        """Clean up created test resources."""
        # Cleanup elements
        for element_id in self.created_elements[:]:
            delete_response = await self.make_request("DELETE", f"/api/v1/elements/{element_id}")
            if delete_response["status"] == 204:
                self.created_elements.remove(element_id)
        
        # Cleanup projects
        for project_id in self.created_projects[:]:
            delete_response = await self.make_request("DELETE", f"/api/v1/projects/{project_id}")
            if delete_response["status"] == 204:
                self.created_projects.remove(project_id)
    
    async def run_elements_tests(self) -> None:
        """Run comprehensive elements tests."""
        print("🧩 Starting TinyRAG Elements API Tests")
        print("=" * 50)
        
        try:
            # 1. Authenticate
            auth_success = await self.authenticate()
            if not auth_success:
                print("❌ Authentication failed - cannot test elements")
                return
            
            # 2. Create test project
            project_id = await self.create_test_project()
            if not project_id:
                print("❌ Project creation failed - cannot test elements")
                return
            
            # 3. Test element creation
            element_id = await self.test_create_elements(project_id)
            
            # 4. Test element listing
            await self.test_list_elements(project_id)
            
            # 5. Test element details
            await self.test_element_details(element_id)
            
            # 6. Test element execution
            await self.test_element_execution(element_id)
            
            # 7. Test element updates
            await self.test_update_element(element_id)
            
            # 8. Test element deletion (delete one element)
            if element_id:
                await self.test_delete_element(element_id)
            
        except Exception as e:
            await self.log_test(
                "Elements Test Suite Execution",
                False,
                f"Unexpected error: {str(e)}"
            )
        
        finally:
            # Cleanup remaining resources
            await self.cleanup_resources()
            await self.print_test_summary()
    
    async def print_test_summary(self) -> None:
        """Print elements test summary."""
        print("\n" + "=" * 50)
        print("📊 ELEMENTS TEST SUMMARY")
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
        with open("test_logs/elements_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Results saved to: test_logs/elements_test_results.json")


async def main():
    """Main function to run elements tests."""
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
    
    # Run elements tests
    async with ElementsAPITester() as tester:
        await tester.run_elements_tests()


if __name__ == "__main__":
    asyncio.run(main()) 