#!/usr/bin/env python3
"""
Sample Financial Project Creation Script for TinyRAG v1.4.2

Creates a Nike financial analysis project with keyword-based company targeting.
Demonstrates company-based financial report generation using project keywords.
"""

import asyncio
import os
from typing import List, Dict, Any
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models.enums import TenantType, ProjectStatus, VisibilityType, ElementStatus
from models.project import Project, ProjectConfiguration
from models.element_template import ElementTemplate
from models.element import Element, ElementTemplate as ElementTemplateNested
from auth.models import User


async def create_sample_financial_project():
    """Create a sample financial project with Nike as the target company."""
    
    # Connect to database using environment variable
    mongodb_url = os.getenv('MONGODB_URL')
    print(f"🔗 Connecting to MongoDB: {mongodb_url}")
    
    client = AsyncIOMotorClient(mongodb_url)
    
    # Initialize Beanie with required models
    await init_beanie(
        database=client.tinyrag,
        document_models=[Project, ElementTemplate, Element, User]
    )
    
    print('🚀 Creating Sample Financial Project...')
    
    # Check if project already exists
    existing_project = await Project.find_one(
        Project.name == "Nike Financial Analysis"
    )
    
    if existing_project:
        print(f'⚠️  Project "Nike Financial Analysis" already exists (ID: {existing_project.id})')
        
        # Provision elements for the existing project
        await provision_financial_elements(existing_project)
        
        client.close()
        return {
            "project_id": str(existing_project.id),
            "status": "existing_project_updated"
        }
    
    # Create project configuration for financial analysis
    project_config = ProjectConfiguration(
        default_model="gpt-4-turbo",
        temperature=0.2,
        max_tokens=2000,
        retrieval_top_k=8,
        similarity_threshold=0.75,
        custom_settings={
            "company_focus": "Nike, Inc.",
            "analysis_type": "investment_memo",
            "report_sections": ["client_overview", "financial_analysis", "liquidity", "risk_factors", "esg"]
        }
    )
    
    # Create the financial project
    financial_project = Project(
        name="Nike Financial Analysis",
        description="Comprehensive financial analysis and investment memo generation for Nike, Inc. using RAG-based element templates.",
        keywords=["Nike", "NKE", "Athletic Footwear", "Sportswear", "Consumer Discretionary"],  # Company as keywords
        tenant_type=TenantType.FINANCIAL_REPORT,
        owner_id="system",  # Default system user
        collaborators=[],
        visibility=VisibilityType.SHARED,
        status=ProjectStatus.ACTIVE,
        configuration=project_config,
        statistics={
            "target_company": "Nike, Inc.",
            "ticker_symbol": "NKE",
            "sector": "Consumer Discretionary",
            "industry": "Athletic Footwear & Apparel"
        }
    )
    
    # Insert the project
    await financial_project.insert()
    print(f'✅ Created financial project: {financial_project.name} (ID: {financial_project.id})')
    
    # Provision financial elements for this project
    await provision_financial_elements(financial_project)
    
    client.close()
    return {
        "project_id": str(financial_project.id),
        "status": "new_project_created"
    }


async def provision_financial_elements(project: Project):
    """Provision financial element templates as project-specific elements."""
    
    print(f'📋 Provisioning financial elements for project: {project.name}')
    
    # Get all financial element templates V2
    financial_templates = await ElementTemplate.find(
        ElementTemplate.tenant_type == TenantType.FINANCIAL_REPORT
    ).to_list()
    
    # Filter for V2 templates by version instead of name suffix
    v2_templates = [t for t in financial_templates if t.version == "2.0.0"]
    
    if not v2_templates:
        print('⚠️  No financial element templates V2 found!')
        print(f'📋 Found {len(financial_templates)} templates total. Available templates:')
        for t in financial_templates[:5]:  # Show first 5 for debugging
            print(f'  - {t.name} (v{t.version})')
        return
    
    print(f'✅ Found {len(v2_templates)} V2 templates to provision')
    
    provisioned_count = 0
    
    for template in v2_templates:
        try:
            # Check if element already exists for this project
            existing_element = await Element.find_one(
                Element.project_id == str(project.id),
                Element.name == f"{template.name}_Nike"  # Customize for Nike
            )
            
            if existing_element:
                print(f'⚠️  Element {template.name}_Nike already provisioned for this project')
                continue
            
            # Create element from template
            element_name = f"{template.name}_Nike"
            
            # Customize the generation prompt with Nike-specific context
            customized_prompt = template.generation_prompt.replace(
                "**Retrieved Document Chunks:**\n{retrieved_chunks}",
                f"**Company:** Nike, Inc. (NKE)\n**Retrieved Document Chunks:**\n{{retrieved_chunks}}"
            )
            
            # Customize the additional instructions template for Nike
            nike_instructions = "Nike-specific focus areas: [e.g., emphasis on athletic footwear market, focus on DTC strategy, highlight sustainability initiatives, etc.]"
            
            # Create the element template object
            element_template = ElementTemplateNested(
                content=customized_prompt,  # Legacy content field
                generation_prompt=customized_prompt,
                retrieval_prompt=template.retrieval_prompt.replace(
                    "the company", "Nike, Inc."
                ) if "the company" in template.retrieval_prompt else template.retrieval_prompt,
                additional_instructions_template=nike_instructions,
                execution_config=template.execution_config,
                version=template.version
            )
            
            # Create the project element
            project_element = Element(
                name=element_name,
                description=f"Nike-specific {template.description.lower()}",
                project_id=str(project.id),
                tenant_type=template.tenant_type,
                task_type=template.task_type,
                element_type=template.element_type,
                status=ElementStatus.ACTIVE,
                template=element_template,
                tags=template.tags + ["nike", "nke", "project_specific"],
                owner_id="system",  # Required field
                is_default_element=True,
                template_id=str(template.id)
            )
            
            await project_element.insert()
            
            # Add element to project
            if not hasattr(project, 'element_ids') or project.element_ids is None:
                project.element_ids = []
            project.element_ids.append(str(project_element.id))
            
            print(f'✅ Provisioned element: {project_element.name} (ID: {project_element.id})')
            provisioned_count += 1
            
        except Exception as e:
            print(f'❌ Failed to provision element from template {template.name}: {e}')
    
    # Update project with new element IDs
    await project.save()
    
    print(f'🎯 Provisioned {provisioned_count} financial elements for Nike analysis')


async def main():
    """Main function."""
    try:
        result = await create_sample_financial_project()
        
        print("\n" + "="*60)
        print("SAMPLE FINANCIAL PROJECT CREATION SUMMARY")
        print("="*60)
        print(f"Project ID: {result['project_id']}")
        print(f"Status: {result['status']}")
        print("="*60)
        print("\n🎯 Sample financial project created successfully!")
        print("💡 The project keywords ['Nike', 'NKE', 'Athletic Footwear', 'Sportswear', 'Consumer Discretionary']")
        print("   serve as the target company identifiers for financial report generation.")
        print("\n📋 Next steps:")
        print("   1. Upload Nike financial documents to the project")
        print("   2. Use the provisioned elements to generate company-specific financial analysis")
        print("   3. The RAG system will retrieve relevant chunks and generate Nike-focused reports")
        
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 