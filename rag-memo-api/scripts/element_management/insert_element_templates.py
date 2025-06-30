#!/usr/bin/env python3
"""
Insert Element Templates - TinyRAG v1.4

This script inserts element templates into the database for automatic
provisioning to projects.
"""

import os
import sys
import asyncio
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import ElementTemplate, TenantConfiguration
from models.enums import TenantType, TaskType, ElementType, ElementStatus
from services.element_template_service import get_template_service
from database import get_database_url


class ElementTemplateInserter:
    """Service for inserting element templates into the database."""
    
    def __init__(self):
        """Initialize the template inserter."""
        self.logger = logging.getLogger(__name__)
        self.template_service = get_template_service()
        self.inserted_count = 0
        self.error_count = 0
        self.user_id = "6859036f0cfc8f1bb0f21c76"  # Default test user
    
    async def insert_all_tenant_templates(
        self,
        dry_run: bool = True,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """Insert templates for all tenant types."""
        self.logger.info("🚀 Inserting element templates for all tenants...")
        
        results = {}
        total_inserted = 0
        total_errors = 0
        
        for tenant_type in TenantType:
            try:
                result = await self.insert_tenant_templates(
                    tenant_type=tenant_type,
                    dry_run=dry_run,
                    force_update=force_update
                )
                results[tenant_type.value] = result
                total_inserted += result.get('inserted_count', 0)
                total_errors += result.get('error_count', 0)
                
            except Exception as e:
                self.logger.error(f"❌ Failed to insert templates for {tenant_type.value}: {e}")
                results[tenant_type.value] = {"error": str(e)}
                total_errors += 1
        
        return {
            "operation": "insert_all_templates",
            "dry_run": dry_run,
            "total_inserted": total_inserted,
            "total_errors": total_errors,
            "tenant_results": results
        }
    
    async def insert_tenant_templates(
        self,
        tenant_type: TenantType,
        dry_run: bool = True,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """Insert templates for a specific tenant type."""
        self.logger.info(f"📝 Inserting templates for tenant: {tenant_type.value}")
        
        # Get template definitions
        templates = self._get_tenant_template_definitions(tenant_type)
        
        if not templates:
            self.logger.info(f"✅ No templates defined for tenant: {tenant_type.value}")
            return {"message": "No templates defined", "inserted_count": 0}
        
        inserted_templates = []
        failed_templates = []
        
        for template_data in templates:
            try:
                if dry_run:
                    self.logger.info(f"🧪 DRY RUN: Would insert template '{template_data['name']}'")
                    inserted_templates.append(template_data['name'])
                else:
                    # Check if template already exists
                    existing = await ElementTemplate.find_one({
                        "name": template_data['name'],
                        "tenant_type": tenant_type
                    })
                    
                    if existing and not force_update:
                        self.logger.info(f"⏭️  Template '{template_data['name']}' already exists, skipping")
                        continue
                    elif existing and force_update:
                        self.logger.info(f"🔄 Updating existing template '{template_data['name']}'")
                        await self.template_service.update_template(
                            template_id=str(existing.id),
                            updates=template_data,
                            updated_by=self.user_id
                        )
                        inserted_templates.append(template_data['name'])
                    else:
                        # Create new template
                        template = await self.template_service.create_template(
                            template_data=template_data,
                            created_by=self.user_id,
                            generate_retrieval_prompt=True
                        )
                        inserted_templates.append(template.name)
                        self.logger.info(f"✅ Created template: {template.name}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to insert template '{template_data['name']}': {e}")
                failed_templates.append({
                    "name": template_data['name'],
                    "error": str(e)
                })
        
        return {
            "tenant_type": tenant_type.value,
            "total_templates": len(templates),
            "inserted_count": len(inserted_templates),
            "error_count": len(failed_templates),
            "inserted_templates": inserted_templates,
            "failed_templates": failed_templates
        }
    
    def _get_tenant_template_definitions(self, tenant_type: TenantType) -> List[Dict[str, Any]]:
        """Get template definitions for a tenant type."""
        # Template definitions based on the existing tenant scripts
        template_definitions = {
            TenantType.HR: [
                {
                    "name": "HR Policy Analyzer",
                    "description": "Analyzes HR policies and provides compliance insights",
                    "tenant_type": tenant_type,
                    "task_type": TaskType.RAG_QA,
                    "element_type": ElementType.PROMPT_TEMPLATE,
                    "generation_prompt": """You are an expert HR policy analyst. Analyze the provided HR policy document and provide comprehensive insights about compliance, potential risks, and recommendations for improvement.

**Analysis Framework:**
1. **Policy Overview**: Summarize the main purpose and scope of the policy
2. **Compliance Assessment**: Evaluate compliance with current labor laws and regulations
3. **Risk Analysis**: Identify potential legal, operational, or employee relations risks
4. **Best Practices**: Compare against industry best practices and standards
5. **Recommendations**: Provide specific, actionable recommendations for improvement

**Input Variables:**
- {policy_document}: The HR policy document to analyze
- {jurisdiction}: Legal jurisdiction for compliance requirements
- {company_size}: Company size category (startup, mid-size, enterprise)
- {industry}: Industry sector for context

**Analysis Requirements:**
- Focus on legal compliance and risk mitigation
- Provide specific citations and references where applicable
- Include severity ratings for identified risks (Low/Medium/High)
- Suggest implementation timelines for recommendations
- Consider both employee experience and business operations

**Output Format:**
Provide a structured analysis with clear sections, bullet points for key findings, and prioritized recommendations.""",
                    "variables": ["policy_document", "jurisdiction", "company_size", "industry"],
                    "execution_config": {
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "model": "gpt-4o-mini"
                    },
                    "tags": ["hr", "policy", "compliance", "analysis", "risk-assessment"]
                },
                {
                    "name": "Employee Onboarding Guide Generator",
                    "description": "Creates comprehensive onboarding guides for new employees",
                    "tenant_type": tenant_type,
                    "task_type": TaskType.STRUCTURED_GENERATION,
                    "element_type": ElementType.PROMPT_TEMPLATE,
                    "generation_prompt": """You are an expert HR specialist focused on employee onboarding and integration. Create a comprehensive, personalized onboarding guide for new employees based on their role, department, and company context.

**Onboarding Guide Structure:**
1. **Welcome Message**: Personalized welcome with company culture highlights
2. **First Day Schedule**: Detailed hour-by-hour schedule for the first day
3. **First Week Milestones**: Key activities, meetings, and learning objectives
4. **Role-Specific Training**: Customized training plan based on position
5. **Company Resources**: Essential tools, systems, and resources overview
6. **Team Introduction**: Team structure, key contacts, and collaboration methods
7. **Performance Expectations**: Clear goals and success metrics for first 30/60/90 days
8. **Cultural Integration**: Company values, traditions, and social activities

**Input Variables:**
- {employee_name}: New employee's name
- {position_title}: Job title and role description
- {department}: Department or team they're joining
- {start_date}: Official start date
- {manager_name}: Direct manager's name and contact
- {company_culture}: Key company values and culture elements
- {remote_hybrid_office}: Work arrangement (remote/hybrid/office)

**Guide Requirements:**
- Create engaging, welcoming tone throughout
- Include specific actionable items with deadlines
- Provide clear contact information for questions
- Reference company-specific tools and processes
- Include both formal requirements and informal cultural elements
- Ensure legal compliance requirements are covered

**Output Format:**
Create a well-structured, easy-to-follow guide with clear sections, checklists, and contact information.""",
                    "variables": ["employee_name", "position_title", "department", "start_date", "manager_name", "company_culture", "remote_hybrid_office"],
                    "execution_config": {
                        "temperature": 0.4,
                        "max_tokens": 2500,
                        "model": "gpt-4o-mini"
                    },
                    "tags": ["hr", "onboarding", "employee-experience", "training", "integration"]
                }
            ],
            TenantType.CODING: [
                {
                    "name": "Code Review Assistant",
                    "description": "Comprehensive code review with security, performance, and best practices analysis",
                    "tenant_type": tenant_type,
                    "task_type": TaskType.STRUCTURED_GENERATION,
                    "element_type": ElementType.PROMPT_TEMPLATE,
                    "generation_prompt": """You are an expert software engineer and code reviewer. Perform a comprehensive code review focusing on security, performance, maintainability, and best practices.

**Review Framework:**
1. **Code Quality**: Readability, organization, and structure
2. **Security Analysis**: Vulnerability assessment and security best practices
3. **Performance Review**: Efficiency, optimization opportunities, and scalability
4. **Best Practices**: Language-specific conventions and industry standards
5. **Architecture Assessment**: Design patterns and architectural decisions
6. **Testing Coverage**: Unit tests, integration tests, and test quality
7. **Documentation**: Code comments, README, and API documentation

**Input Variables:**
- {code_content}: The code to be reviewed
- {language}: Programming language (Python, JavaScript, Java, etc.)
- {project_type}: Type of project (web app, API, library, etc.)
- {review_focus}: Specific areas to emphasize (security, performance, etc.)
- {team_standards}: Team or company coding standards to follow

**Review Criteria:**
- Identify potential bugs and edge cases
- Suggest performance optimizations
- Check for security vulnerabilities (OWASP guidelines)
- Evaluate code maintainability and extensibility
- Ensure proper error handling and logging
- Verify adherence to coding standards and conventions

**Output Format:**
Provide structured feedback with:
- Overall assessment and rating
- Specific issues with line numbers and explanations
- Recommended improvements with code examples
- Priority levels for each finding (Critical/High/Medium/Low)
- Positive aspects and good practices identified""",
                    "variables": ["code_content", "language", "project_type", "review_focus", "team_standards"],
                    "execution_config": {
                        "temperature": 0.2,
                        "max_tokens": 2500,
                        "model": "gpt-4o-mini"
                    },
                    "tags": ["coding", "code-review", "security", "performance", "best-practices"]
                },
                {
                    "name": "API Documentation Generator",
                    "description": "Generates comprehensive API documentation from code and specifications",
                    "tenant_type": tenant_type,
                    "task_type": TaskType.STRUCTURED_GENERATION,
                    "element_type": ElementType.PROMPT_TEMPLATE,
                    "generation_prompt": """You are an expert technical writer specializing in API documentation. Create comprehensive, developer-friendly API documentation that follows industry best practices and standards.

**Documentation Structure:**
1. **API Overview**: Purpose, version, and key features
2. **Authentication**: Authentication methods and security requirements
3. **Base URL and Versioning**: Endpoint structure and versioning strategy
4. **Endpoints Documentation**: Detailed endpoint specifications
5. **Request/Response Examples**: Real-world usage examples
6. **Error Handling**: Error codes, messages, and troubleshooting
7. **Rate Limiting**: Usage limits and throttling policies
8. **SDKs and Libraries**: Available client libraries and tools
9. **Changelog**: Version history and breaking changes

**Input Variables:**
- {api_code}: API code or OpenAPI specification
- {api_title}: API name and title
- {api_version}: Current API version
- {base_url}: API base URL
- {authentication_type}: Auth method (OAuth, API key, JWT, etc.)
- {target_audience}: Primary users (developers, integrators, etc.)

**Documentation Requirements:**
- Follow OpenAPI 3.0 standards where applicable
- Include comprehensive request/response examples
- Provide clear parameter descriptions and validation rules
- Document all possible error scenarios
- Include code samples in multiple programming languages
- Ensure examples are functional and tested
- Use consistent formatting and terminology

**Output Format:**
Generate well-structured documentation with:
- Clear navigation and sections
- Interactive examples where possible
- Proper HTTP status code documentation
- Schema definitions for complex objects
- Getting started guide for new developers""",
                    "variables": ["api_code", "api_title", "api_version", "base_url", "authentication_type", "target_audience"],
                    "execution_config": {
                        "temperature": 0.3,
                        "max_tokens": 3000,
                        "model": "gpt-4o-mini"
                    },
                    "tags": ["coding", "api", "documentation", "technical-writing", "developer-tools"]
                }
            ],
            TenantType.FINANCIAL_REPORT: [
                {
                    "name": "Financial Statement Analyzer",
                    "description": "Comprehensive analysis of financial statements with insights and recommendations",
                    "tenant_type": tenant_type,
                    "task_type": TaskType.RAG_QA,
                    "element_type": ElementType.PROMPT_TEMPLATE,
                    "generation_prompt": """You are an expert financial analyst with deep expertise in financial statement analysis, ratio analysis, and business valuation. Perform a comprehensive analysis of the provided financial statements.

**Analysis Framework:**
1. **Financial Position**: Balance sheet analysis and capital structure
2. **Profitability Analysis**: Income statement trends and margin analysis
3. **Liquidity Assessment**: Working capital and cash flow analysis
4. **Efficiency Metrics**: Asset utilization and operational efficiency
5. **Leverage Analysis**: Debt levels, coverage ratios, and financial risk
6. **Growth Trends**: Revenue, profit, and asset growth patterns
7. **Industry Comparison**: Benchmarking against industry averages
8. **Risk Assessment**: Financial risks and sustainability factors

**Input Variables:**
- {financial_statements}: Complete financial statements (income statement, balance sheet, cash flow)
- {company_name}: Company name and basic information
- {industry}: Industry sector for benchmarking
- {analysis_period}: Time period for analysis (quarterly, annual, multi-year)
- {comparison_data}: Industry benchmarks or competitor data

**Analysis Requirements:**
- Calculate key financial ratios (liquidity, profitability, leverage, efficiency)
- Identify trends and patterns over time
- Highlight strengths and areas of concern
- Provide specific recommendations for improvement
- Consider industry context and business cycle factors
- Include forward-looking insights based on historical data

**Output Format:**
Provide structured analysis with:
- Executive summary of key findings
- Detailed ratio analysis with interpretations
- Trend analysis with visual indicators
- Peer comparison and industry context
- Risk factors and mitigation strategies
- Strategic recommendations for management""",
                    "variables": ["financial_statements", "company_name", "industry", "analysis_period", "comparison_data"],
                    "execution_config": {
                        "temperature": 0.2,
                        "max_tokens": 2500,
                        "model": "gpt-4o-mini"
                    },
                    "tags": ["financial", "analysis", "statements", "ratios", "business-intelligence"]
                }
            ]
        }
        
        return template_definitions.get(tenant_type, [])


async def main():
    """Main function to run the template inserter."""
    parser = argparse.ArgumentParser(
        description="Insert element templates into the database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run - show what would be inserted
  python insert_element_templates.py --dry-run

  # Insert all tenant templates
  python insert_element_templates.py

  # Insert templates for specific tenant
  python insert_element_templates.py --tenant hr

  # Force update existing templates
  python insert_element_templates.py --force-update
        """
    )
    
    parser.add_argument(
        "--tenant",
        type=str,
        choices=[t.value for t in TenantType],
        help="Insert templates for specific tenant type only"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be inserted without actually inserting"
    )
    
    parser.add_argument(
        "--force-update",
        action="store_true",
        help="Update existing templates"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize database
        logger.info("🔌 Connecting to database...")
        client = AsyncIOMotorClient(get_database_url())
        await init_beanie(
            database=client.tinyrag,
            document_models=[ElementTemplate, TenantConfiguration]
        )
        logger.info("✅ Database connected successfully")
        
        # Initialize inserter
        inserter = ElementTemplateInserter()
        
        # Execute based on arguments
        if args.tenant:
            tenant_type = TenantType(args.tenant)
            report = await inserter.insert_tenant_templates(
                tenant_type=tenant_type,
                dry_run=args.dry_run,
                force_update=args.force_update
            )
            print(f"\n✅ Template insertion complete for {args.tenant}: {report}")
        else:
            report = await inserter.insert_all_tenant_templates(
                dry_run=args.dry_run,
                force_update=args.force_update
            )
            print(f"\n✅ Template insertion complete: {report}")
        
    except KeyboardInterrupt:
        logger.info("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    asyncio.run(main()) 