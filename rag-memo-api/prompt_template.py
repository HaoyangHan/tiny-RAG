"""
TinyRAG Prompt Templates
========================

Centralized repository for all AI prompts used throughout the TinyRAG system.
This module contains all prompts for document processing, content generation,
analysis, and evaluation to ensure consistency and easy maintenance.

Author: TinyRAG Development Team
Version: 1.4.3
Last Updated: January 2025
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Base class for prompt templates."""
    name: str
    description: str
    system_prompt: str
    user_prompt_template: str
    variables: List[str]
    temperature: float = 0.7
    max_tokens: int = 1000
    model: str = "gpt-4o-mini"


class DocumentProcessingPrompts:
    """Prompts for document processing and analysis."""
    
    @staticmethod
    def get_table_summary_prompt() -> PromptTemplate:
        """Prompt for generating table summaries."""
        return PromptTemplate(
            name="table_summary",
            description="Generate concise summaries of table content",
            system_prompt="You are a table analysis expert. Provide a concise summary of the table content, highlighting key data points and patterns.",
            user_prompt_template="Please summarize this table:\n{table_text}",
            variables=["table_text"],
            temperature=0.3,
            max_tokens=500,
            model="gpt-4o-mini"
        )
    
    @staticmethod
    def get_image_description_prompt() -> PromptTemplate:
        """Prompt for generating image descriptions using GPT-4 Vision."""
        return PromptTemplate(
            name="image_description",
            description="Describe images in detail including text and visual elements",
            system_prompt="You are an expert image analyst. Provide detailed descriptions of images including any text, diagrams, charts, or important visual elements.",
            user_prompt_template="Please describe this image in detail, including any text, diagrams, or important visual elements.",
            variables=[],  # Image data passed separately
            temperature=0.4,
            max_tokens=800,
            model="gpt-4-vision-preview"
        )


class MemoGenerationPrompts:
    """Prompts for memo and content generation."""
    
    @staticmethod
    def get_memo_section_prompt() -> PromptTemplate:
        """Prompt for generating memo sections."""
        return PromptTemplate(
            name="memo_section",
            description="Generate clear and concise memo sections",
            system_prompt="""You are an expert memo writer. Your task is to write a clear and concise section for a memo based on the provided context. Focus on extracting and synthesizing the most relevant information. Use proper citations when referencing specific information. Format citations as [citation:doc_id] where doc_id is the document identifier.""",
            user_prompt_template="""Write the '{section_title}' section for a memo.
Use the following context to inform your writing:

{context}

Format the section with clear paragraphs and proper citations using the format [citation:doc_id].""",
            variables=["section_title", "context"],
            temperature=0.7,
            max_tokens=1000,
            model="gpt-4o-mini"
        )


class TenantSpecificPrompts:
    """Tenant-specific prompt templates for different use cases."""
    
    @staticmethod
    def get_hr_policy_analysis_prompt() -> PromptTemplate:
        """Prompt for HR policy document analysis."""
        return PromptTemplate(
            name="hr_policy_analysis",
            description="Comprehensive analysis of HR policy documents",
            system_prompt="You are an HR policy expert. Analyze documents for compliance, implementation guidelines, and potential issues.",
            user_prompt_template="""Analyze the following HR policy document and provide a comprehensive analysis:

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
            temperature=0.3,
            max_tokens=2000,
            model="gpt-4o-mini"
        )


class RAGPrompts:
    """Prompts for RAG (Retrieval-Augmented Generation) workflows."""
    
    @staticmethod
    def get_factual_query_prompt() -> PromptTemplate:
        """Prompt for factual queries with context."""
        return PromptTemplate(
            name="factual_query",
            description="Answer factual questions based on provided context",
            system_prompt="You are a helpful assistant that answers questions based on provided context. Be accurate and cite sources when possible.",
            user_prompt_template="""Based on the provided context, answer the following question accurately and concisely.

Context:
{context}

Question: {query}

Instructions:
- Provide a direct, factual answer
- Cite specific sources when possible
- If information is not in the context, clearly state so
- Use bullet points for multiple facts

Answer:""",
            variables=["context", "query"],
            temperature=0.2,
            max_tokens=800,
            model="gpt-4o-mini"
        )


class PromptTemplateManager:
    """Manager class for accessing all prompt templates."""
    
    def __init__(self):
        """Initialize the prompt template manager."""
        self._templates: Dict[str, PromptTemplate] = {}
        self._load_all_templates()
    
    def _load_all_templates(self):
        """Load all available prompt templates."""
        # Document Processing
        self._templates["table_summary"] = DocumentProcessingPrompts.get_table_summary_prompt()
        self._templates["image_description"] = DocumentProcessingPrompts.get_image_description_prompt()
        
        # Memo Generation
        self._templates["memo_section"] = MemoGenerationPrompts.get_memo_section_prompt()
        
        # Tenant-Specific
        self._templates["hr_policy_analysis"] = TenantSpecificPrompts.get_hr_policy_analysis_prompt()
        
        # RAG
        self._templates["factual_query"] = RAGPrompts.get_factual_query_prompt()
    
    def get_template(self, name: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if name not in self._templates:
            raise ValueError(f"Template '{name}' not found. Available templates: {list(self._templates.keys())}")
        return self._templates[name]
    
    def format_prompt(self, template_name: str, **kwargs) -> Dict[str, str]:
        """Format a prompt template with provided variables."""
        template = self.get_template(template_name)
        
        # Check if all required variables are provided
        missing_vars = [var for var in template.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables for template '{template_name}': {missing_vars}")
        
        # Format the user prompt
        formatted_user_prompt = template.user_prompt_template.format(**kwargs)
        
        return {
            "system_prompt": template.system_prompt,
            "user_prompt": formatted_user_prompt,
            "temperature": template.temperature,
            "max_tokens": template.max_tokens,
            "model": template.model
        }


# Global instance for easy access
prompt_manager = PromptTemplateManager()


def get_prompt_template(name: str) -> PromptTemplate:
    """Convenience function to get a prompt template."""
    return prompt_manager.get_template(name)


def format_prompt(template_name: str, **kwargs) -> Dict[str, str]:
    """Convenience function to format a prompt template."""
    return prompt_manager.format_prompt(template_name, **kwargs)


def list_available_templates() -> List[str]:
    """Convenience function to list all available templates."""
    return list(prompt_manager._templates.keys())
