"""
Coding Tenant Element Insertion Script.

This script contains predefined elements for Coding tenant type, including
MCP configurations, agentic tools, and development-focused templates.
"""

import asyncio
from typing import List, Dict, Any

from models.enums import TenantType, TaskType, ElementType, ElementStatus
from .base_inserter import BaseElementInserter


class CodingElementInserter(BaseElementInserter):
    """Element inserter for Coding tenant type."""
    
    def get_elements_data(self) -> List[Dict[str, Any]]:
        """
        Get predefined Coding elements.
        
        Returns:
            List[Dict[str, Any]]: List of Coding element data
        """
        return [
            # Code Review Template
            {
                "name": "Code Review Template",
                "description": "Comprehensive template for conducting thorough code reviews",
                "task_type": TaskType.MCP,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Conduct a comprehensive code review for the following code:

**Code Information:**
- Language: {language}
- Component/Module: {component_name}
- Pull Request: {pr_number}
- Author: {author}

**Code to Review:**
```{language}
{code_content}
```

**Review Focus Areas:**
{focus_areas}

**Provide a detailed review covering:**

1. **Code Quality Assessment**
   - Code readability and maintainability
   - Naming conventions and standards compliance
   - Code structure and organization

2. **Functionality Analysis**
   - Logic correctness and edge cases
   - Error handling and input validation
   - Performance considerations

3. **Security Review**
   - Security vulnerabilities and risks
   - Input sanitization and validation
   - Authentication and authorization checks

4. **Best Practices Evaluation**
   - Design patterns usage
   - SOLID principles adherence
   - DRY (Don't Repeat Yourself) compliance

5. **Testing and Documentation**
   - Test coverage adequacy
   - Documentation completeness
   - Code comments quality

6. **Specific Recommendations**
   - Required changes (blocking issues)
   - Suggested improvements
   - Performance optimizations

**Provide constructive feedback with specific examples and actionable suggestions.**""",
                    variables=["language", "component_name", "pr_number", "author", "code_content", "focus_areas"],
                    execution_config={
                        "temperature": 0.2,
                        "max_tokens": 2500,
                        "model": "gpt-4o-mini"
                    }
                ),
                "tags": self.create_element_tags(["code_review", "quality", "security", "best_practices"])
            },
            
            # API Documentation Generator
            {
                "name": "API Documentation Generator",
                "description": "Template for generating comprehensive API documentation",
                "task_type": TaskType.MCP,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Generate comprehensive API documentation for the following endpoint:

**API Information:**
- Endpoint: {endpoint}
- Method: {http_method}
- Version: {api_version}
- Service: {service_name}

**Code Implementation:**
```{language}
{code_implementation}
```

**Additional Context:**
{additional_context}

**Generate documentation that includes:**

1. **Endpoint Overview**
   - Purpose and functionality
   - Use cases and scenarios
   - Integration guidelines

2. **Request Specification**
   - URL structure and parameters
   - Headers requirements
   - Request body schema (if applicable)
   - Authentication requirements

3. **Response Specification**
   - Success response format
   - HTTP status codes
   - Response headers
   - Error response formats

4. **Parameters Documentation**
   - Path parameters
   - Query parameters
   - Request body fields
   - Validation rules and constraints

5. **Examples**
   - Complete request examples
   - Response examples (success and error)
   - Code samples in multiple languages

6. **Error Handling**
   - Error codes and meanings
   - Troubleshooting guide
   - Common issues and solutions

7. **Rate Limiting and Usage**
   - Rate limiting information
   - Best practices for usage
   - Performance considerations

**Format the documentation in clear, developer-friendly structure with proper syntax highlighting.**""",
                    variables=["endpoint", "http_method", "api_version", "service_name", "language", "code_implementation", "additional_context"],
                    execution_config={
                        "temperature": 0.3,
                        "max_tokens": 3000,
                        "model": "gpt-4o-mini"
                    }
                ),
                "tags": self.create_element_tags(["api", "documentation", "integration", "reference"])
            },
            
            # Bug Report Analyzer
            {
                "name": "Bug Report Analyzer",
                "description": "Template for analyzing and categorizing bug reports",
                "task_type": TaskType.MCP,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Analyze the following bug report and provide a structured analysis:

**Bug Report Information:**
- Issue ID: {issue_id}
- Reporter: {reporter}
- Component: {component}
- Environment: {environment}

**Bug Description:**
{bug_description}

**Steps to Reproduce:**
{steps_to_reproduce}

**Expected Behavior:**
{expected_behavior}

**Actual Behavior:**
{actual_behavior}

**Error Logs/Screenshots:**
{error_logs}

**Provide a comprehensive analysis:**

1. **Bug Classification**
   - Severity level (Critical/High/Medium/Low)
   - Priority assessment
   - Bug category (UI, Backend, Performance, Security, etc.)

2. **Root Cause Analysis**
   - Potential root causes
   - Affected components and systems
   - Related dependencies

3. **Impact Assessment**
   - User impact and affected workflows
   - Business impact evaluation
   - Risk assessment

4. **Reproduction Analysis**
   - Reproducibility assessment
   - Missing information for reproduction
   - Environment-specific considerations

5. **Technical Investigation**
   - Code areas to investigate
   - Debugging strategies
   - Testing approaches

6. **Resolution Recommendations**
   - Immediate workarounds
   - Long-term solution approaches
   - Estimated effort and complexity

7. **Assignment Suggestions**
   - Recommended team/developer
   - Required expertise and skills
   - Dependencies and prerequisites

**Provide actionable insights to facilitate quick resolution.**""",
                    variables=["issue_id", "reporter", "component", "environment", "bug_description", "steps_to_reproduce", "expected_behavior", "actual_behavior", "error_logs"],
                    execution_config={
                        "temperature": 0.2,
                        "max_tokens": 2200,
                        "model": "gpt-4o-mini"
                    }
                ),
                "tags": self.create_element_tags(["bug_analysis", "debugging", "triage", "investigation"])
            },
            
            # MCP GitHub Integration Config
            {
                "name": "GitHub MCP Integration",
                "description": "MCP configuration for GitHub repository operations",
                "task_type": TaskType.MCP,
                "element_type": ElementType.MCP_CONFIG,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""MCP Configuration for GitHub Integration

This configuration enables seamless integration with GitHub repositories
for code analysis, pull request management, and repository operations.

**Connection Parameters:**
- GitHub API URL: {github_api_url}
- Authentication: {auth_method}
- Repository: {repository}
- Branch: {branch}

**Supported Operations:**
1. Repository Analysis
2. Pull Request Reviews
3. Issue Tracking
4. Code Search and Navigation
5. Commit History Analysis

**Configuration Schema:**
```json
{
  "provider": "github",
  "api_version": "v4",
  "base_url": "{github_api_url}",
  "authentication": {
    "type": "{auth_method}",
    "token": "{access_token}"
  },
  "repository": {
    "owner": "{repo_owner}",
    "name": "{repo_name}",
    "default_branch": "{branch}"
  },
  "capabilities": {
    "read_repository": true,
    "read_issues": true,
    "read_pull_requests": true,
    "write_comments": true,
    "create_issues": false
  }
}
```

**Usage Examples:**
- Fetch file content: GET /repos/{repo_owner}/{repo_name}/contents/{path}
- List pull requests: GET /repos/{repo_owner}/{repo_name}/pulls
- Create review comment: POST /repos/{repo_owner}/{repo_name}/pulls/{number}/reviews""",
                    variables=["github_api_url", "auth_method", "repository", "branch", "access_token", "repo_owner", "repo_name"],
                    execution_config={
                        "provider": "github",
                        "api_version": "v4",
                        "timeout": 30,
                        "retry_attempts": 3,
                        "rate_limit": 100
                    }
                ),
                "tags": self.create_element_tags(["mcp", "github", "integration", "repository"])
            },
            
            # Agentic Code Refactoring Tool
            {
                "name": "Agentic Code Refactoring Assistant",
                "description": "Intelligent agent for automated code refactoring suggestions",
                "task_type": TaskType.MCP,
                "element_type": ElementType.AGENTIC_TOOL,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Agentic Code Refactoring Assistant

An intelligent agent that analyzes code and provides automated refactoring suggestions
to improve code quality, performance, and maintainability.

**Agent Capabilities:**
1. **Pattern Recognition**
   - Identify code smells and anti-patterns
   - Detect duplicate code blocks
   - Find performance bottlenecks

2. **Refactoring Suggestions**
   - Extract methods and classes
   - Simplify complex expressions
   - Optimize data structures and algorithms

3. **Code Quality Improvements**
   - Naming convention fixes
   - Documentation generation
   - Test coverage enhancement

**Input Parameters:**
- Code Language: {language}
- File Path: {file_path}
- Refactoring Scope: {scope}
- Quality Metrics: {quality_metrics}

**Agent Workflow:**
1. Parse and analyze the provided code
2. Identify refactoring opportunities
3. Generate specific refactoring suggestions
4. Provide before/after code examples
5. Estimate impact and benefits

**Output Format:**
```json
{
  "analysis_summary": "...",
  "refactoring_suggestions": [
    {
      "type": "extract_method",
      "location": "lines 45-60",
      "suggestion": "...",
      "before_code": "...",
      "after_code": "...",
      "benefits": ["readability", "reusability"]
    }
  ],
  "quality_score": {
    "before": 6.5,
    "after": 8.2
  }
}
```

**Configuration:**
- Analysis depth: {analysis_depth}
- Suggestion confidence threshold: {confidence_threshold}
- Language-specific rules: {language_rules}""",
                    variables=["language", "file_path", "scope", "quality_metrics", "analysis_depth", "confidence_threshold", "language_rules"],
                    execution_config={
                        "agent_type": "refactoring_assistant",
                        "analysis_timeout": 60,
                        "max_suggestions": 10,
                        "confidence_threshold": 0.7
                    }
                ),
                "tags": self.create_element_tags(["agentic", "refactoring", "code_quality", "automation"])
            }
        ]


async def main():
    """Main function to run Coding element insertion."""
    inserter = CodingElementInserter(TenantType.CODING)
    result = await inserter.run()
    
    print("\n" + "="*50)
    print("CODING ELEMENT INSERTION SUMMARY")
    print("="*50)
    print(f"Tenant Type: {result.get('tenant_type', 'Unknown')}")
    print(f"Total Elements: {result.get('total_elements', 0)}")
    print(f"Successful: {result.get('successful', 0)}")
    print(f"Failed: {result.get('failed', 0)}")
    print(f"Skipped: {result.get('skipped', 0)}")
    print(f"Dry Run: {result.get('dry_run', False)}")
    
    if result.get('inserted_ids'):
        print(f"\nInserted Element IDs:")
        for element_id in result['inserted_ids']:
            print(f"  - {element_id}")
    
    if result.get('error'):
        print(f"\nError: {result['error']}")
    
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main()) 