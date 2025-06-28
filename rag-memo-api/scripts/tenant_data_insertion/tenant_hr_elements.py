"""
HR Tenant Element Insertion Script.

This script contains predefined elements for HR tenant type, including
prompt templates, configurations, and tools for human resource workflows.
"""

import asyncio
from typing import List, Dict, Any

from models.enums import TenantType, TaskType, ElementType, ElementStatus
from .base_inserter import BaseElementInserter


class HRElementInserter(BaseElementInserter):
    """Element inserter for HR tenant type."""
    
    def get_elements_data(self) -> List[Dict[str, Any]]:
        """
        Get predefined HR elements.
        
        Returns:
            List[Dict[str, Any]]: List of HR element data
        """
        return [
            # HR Policy Analyzer Prompt Template
            {
                "name": "HR Policy Analyzer",
                "description": "Comprehensive template for analyzing HR policies and procedures",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Analyze the following HR policy document and provide a comprehensive analysis:

**Document to Analyze:**
{document_content}

**Analysis Focus Area:**
{focus_area}

**Please provide:**

1. **Key Policy Points:**
   - Main policy objectives
   - Critical requirements and regulations
   - Scope and applicability

2. **Compliance Requirements:**
   - Legal compliance aspects
   - Industry standards alignment
   - Risk management considerations

3. **Implementation Guidelines:**
   - Recommended action steps
   - Timeline considerations
   - Resource requirements

4. **Potential Issues & Recommendations:**
   - Identify potential gaps or conflicts
   - Suggest improvements or clarifications
   - Risk mitigation strategies

**Format your response in clear sections with actionable insights.**""",
                    variables=["document_content", "focus_area"],
                    execution_config={
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "model": "gpt-4o-mini"
                    }
                ),
                "tags": self.create_element_tags(["policy", "analysis", "compliance"])
            },
            
            # Employee Onboarding Guide Generator
            {
                "name": "Employee Onboarding Guide Generator",
                "description": "Template for generating personalized employee onboarding guides",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Create a comprehensive onboarding guide for a new employee:

**Employee Information:**
- Position: {position}
- Department: {department}
- Start Date: {start_date}
- Manager: {manager_name}

**Company Information Context:**
{company_context}

**Generate an onboarding guide that includes:**

1. **Welcome Message**
   - Personalized greeting
   - Company mission and values overview

2. **First Week Schedule**
   - Day-by-day activities
   - Key meetings and introductions
   - Training sessions

3. **Essential Information**
   - IT setup requirements
   - Access credentials and systems
   - Office logistics and policies

4. **Department-Specific Details**
   - Team structure and roles
   - Key projects and priorities
   - Success metrics and expectations

5. **Resources and Contacts**
   - Important contact information
   - HR resources and support
   - Learning and development opportunities

**Make the guide engaging, informative, and actionable.**""",
                    variables=["position", "department", "start_date", "manager_name", "company_context"],
                    execution_config={
                        "temperature": 0.6,
                        "max_tokens": 2500,
                        "model": "gpt-4o-mini"
                    }
                ),
                "tags": self.create_element_tags(["onboarding", "employee", "guide", "training"])
            },
            
            # Performance Review Template
            {
                "name": "Performance Review Template",
                "description": "Template for conducting structured performance reviews",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Generate a structured performance review based on the provided information:

**Employee Details:**
- Name: {employee_name}
- Position: {position}
- Review Period: {review_period}
- Manager: {manager_name}

**Performance Data:**
{performance_data}

**Goals and Objectives:**
{goals_objectives}

**Create a performance review that covers:**

1. **Performance Summary**
   - Overall performance rating
   - Key achievements and accomplishments
   - Areas of strength

2. **Goal Achievement Analysis**
   - Progress on previously set objectives
   - Quantifiable results and metrics
   - Challenges encountered and overcome

3. **Areas for Development**
   - Skills to improve
   - Learning opportunities
   - Professional development recommendations

4. **Future Goals and Objectives**
   - Short-term goals (next quarter)
   - Long-term career development
   - Required support and resources

5. **Action Plan**
   - Specific development activities
   - Timeline for improvement
   - Follow-up schedule

**Provide constructive, actionable feedback that promotes growth and engagement.**""",
                    variables=["employee_name", "position", "review_period", "manager_name", "performance_data", "goals_objectives"],
                    execution_config={
                        "temperature": 0.4,
                        "max_tokens": 2200,
                        "model": "gpt-4o-mini"
                    }
                ),
                "tags": self.create_element_tags(["performance", "review", "evaluation", "feedback"])
            },
            
            # Job Description Generator
            {
                "name": "Job Description Generator",
                "description": "Template for creating comprehensive job descriptions",
                "task_type": TaskType.RAG,
                "element_type": ElementType.PROMPT_TEMPLATE,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""Create a comprehensive job description for the following position:

**Position Information:**
- Job Title: {job_title}
- Department: {department}
- Reporting Manager: {reporting_manager}
- Location: {location}
- Employment Type: {employment_type}

**Company Context:**
{company_context}

**Role Requirements:**
{role_requirements}

**Generate a job description that includes:**

1. **Position Summary**
   - Brief overview of the role
   - Key purpose and impact
   - Position within organizational structure

2. **Key Responsibilities**
   - Primary duties and tasks
   - Decision-making authority
   - Collaboration requirements

3. **Required Qualifications**
   - Education requirements
   - Professional experience
   - Technical skills and certifications

4. **Preferred Qualifications**
   - Additional skills that would be beneficial
   - Industry-specific experience
   - Leadership or specialized expertise

5. **Working Conditions**
   - Work environment details
   - Travel requirements
   - Physical demands (if applicable)

6. **Compensation and Benefits**
   - Salary range or compensation structure
   - Benefits package highlights
   - Growth opportunities

**Ensure the description is clear, compelling, and compliant with employment laws.**""",
                    variables=["job_title", "department", "reporting_manager", "location", "employment_type", "company_context", "role_requirements"],
                    execution_config={
                        "temperature": 0.5,
                        "max_tokens": 2300,
                        "model": "gpt-4o-mini"
                    }
                ),
                "tags": self.create_element_tags(["job_description", "recruitment", "hiring", "requirements"])
            },
            
            # HR RAG Configuration
            {
                "name": "HR Document RAG Configuration",
                "description": "RAG configuration optimized for HR document retrieval and analysis",
                "task_type": TaskType.RAG,
                "element_type": ElementType.RAG_CONFIG,
                "status": ElementStatus.ACTIVE,
                "template": self.create_element_template(
                    content="""HR-optimized RAG configuration for document retrieval and analysis.

This configuration is specifically tuned for HR documents including:
- Employee handbooks and policies
- Legal compliance documents
- Training materials
- Organizational charts and role descriptions

Configuration Parameters:
- Similarity threshold: {similarity_threshold}
- Top-k retrieval: {top_k}
- Chunk size: {chunk_size}
- Overlap: {overlap}
- Reranking enabled: {reranking}""",
                    variables=["similarity_threshold", "top_k", "chunk_size", "overlap", "reranking"],
                    execution_config={
                        "similarity_threshold": 0.75,
                        "top_k": 8,
                        "chunk_size": 1000,
                        "overlap": 200,
                        "reranking": True,
                        "embedding_model": "text-embedding-ada-002"
                    }
                ),
                "tags": self.create_element_tags(["rag", "configuration", "retrieval", "documents"])
            }
        ]


async def main():
    """Main function to run HR element insertion."""
    inserter = HRElementInserter(TenantType.HR)
    result = await inserter.run()
    
    print("\n" + "="*50)
    print("HR ELEMENT INSERTION SUMMARY")
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