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
            system_prompt="You are an expert data analyst. Your task is to analyze the provided data table and generate a concise, insightful summary.",
            user_prompt_template="""Structure your response with:
1.  A one-sentence overview describing the table's purpose.
2.  A bulleted list highlighting the most important findings, including key trends, significant data points (e.g., highs, lows, outliers), and the main conclusion.

Please answer in **valid Markdown** only. Use headings, lists, code blocks, etc., as appropriate.

Here is the table to summarize:\n{table_text}""",
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
            system_prompt="You are an AI assistant specializing in visual interpretation. Your task is to analyze the attached image and generate a concise, insightful summary of its content and purpose.",
            user_prompt_template="""The image could contain structured data (like a table or chart) or be a more general visual (like a diagram, infographic, mind map, or photograph). First, identify the type of visual, then proceed with the summary.

Your summary must be structured as follows:
1.  **A one-sentence overview** that clearly describes the image's subject matter.
2.  **A bulleted list of key observations**. This analysis should:
    *   Identify the main theme, concept, or subject.
    *   Point out the most important objects, text, or figures present.
    *   Describe the key relationships between elements (e.g., spatial, hierarchical, causal, or comparative).
    *   Conclude with the overall message, purpose, or key takeaway of the image.

Please answer in **valid Markdown** only. Use headings, lists, code blocks, etc., as appropriate.

Please analyze the attached image and provide your summary.""",
            variables=[],  # Image data passed separately
            temperature=0.4,
            max_tokens=800,
            model="gpt-4-vision-preview"
        )
    
    @staticmethod
    def get_table_summary_with_metadata_prompt() -> PromptTemplate:
        """Prompt for generating table summaries WITH metadata in one call."""
        return PromptTemplate(
            name="table_summary_with_metadata",
            description="Generate table summary and extract metadata in single call",
            system_prompt="""You are an expert data analyst and metadata extraction system. Your task is to analyze the provided data table and return BOTH a summary AND comprehensive metadata in a single JSON response.

Return ONLY a valid JSON object with this exact structure:
{
  "summary": "Your markdown-formatted table summary here",
  "metadata": {
    "keywords": [
      {"term": "string", "score": 0.8, "frequency": 3, "context": "string"}
    ],
    "entities": [
      {"text": "string", "label": "person", "confidence": 0.9, "start_pos": 10, "end_pos": 20}
    ],
    "dates": [
      {"date": "2024-01-15", "text": "January 15, 2024", "confidence": 0.95, "date_type": "publication", "format": "Long"}
    ],
    "topics": [
      {"topic_id": "finance", "topic_words": ["revenue", "profit"], "probability": 0.8}
    ],
    "sentiment": {
      "sentiment": "neutral",
      "confidence": 0.7,
      "scores": {"positive": 0.2, "negative": 0.1, "neutral": 0.7}
    },
    "key_phrases": ["important phrase", "key concept"],
    "language": "en",
    "readability_score": 0.6,
    "information_density": 0.8,
    "text_length": 250,
    "word_count": 45,
    "sentence_count": 3
  }
}

Summary Guidelines:
- One-sentence overview describing the table's purpose
- Bulleted list highlighting key findings, trends, and significant data points
- Format in valid Markdown

Metadata Guidelines:
- Extract 5-15 keywords based on importance
- Identify entities: person, organization, location, date, money, percent, product, event, misc
- Parse dates in ISO format (YYYY-MM-DD)
- Provide 2-5 main topics
- All scores between 0.0-1.0
- Be precise and avoid hallucination""",
            user_prompt_template="""Analyze this table and provide both summary and metadata:

{table_text}

JSON:""",
            variables=["table_text"],
            temperature=0.3,
            max_tokens=1200,
            model="gpt-4o-mini"
        )
    
    @staticmethod
    def get_image_description_with_metadata_prompt() -> PromptTemplate:
        """Prompt for generating image descriptions WITH metadata in one call."""
        return PromptTemplate(
            name="image_description_with_metadata",
            description="Generate image description and extract metadata in single call",
            system_prompt="""You are an AI assistant specializing in visual interpretation and metadata extraction. Your task is to analyze the attached image and return BOTH a description AND comprehensive metadata in a single JSON response.

Return ONLY a valid JSON object with this exact structure:
{
  "description": "Your markdown-formatted image description here",
  "metadata": {
    "keywords": [
      {"term": "string", "score": 0.8, "frequency": 3, "context": "string"}
    ],
    "entities": [
      {"text": "string", "label": "person", "confidence": 0.9, "start_pos": 10, "end_pos": 20}
    ],
    "dates": [
      {"date": "2024-01-15", "text": "January 15, 2024", "confidence": 0.95, "date_type": "publication", "format": "Long"}
    ],
    "topics": [
      {"topic_id": "tech", "topic_words": ["AI", "chart"], "probability": 0.8}
    ],
    "sentiment": {
      "sentiment": "neutral",
      "confidence": 0.7,
      "scores": {"positive": 0.3, "negative": 0.1, "neutral": 0.6}
    },
    "key_phrases": ["important phrase", "key concept"],
    "language": "en",
    "readability_score": 0.6,
    "information_density": 0.8,
    "text_length": 200,
    "word_count": 35,
    "sentence_count": 2
  }
}

Description Guidelines:
- One-sentence overview describing the image's subject matter
- Bulleted list of key observations: theme, objects, text, relationships, takeaways
- Format in valid Markdown

Metadata Guidelines:
- Extract keywords from visible text and implied content
- Identify entities: person, organization, location, date, money, percent, product, event, misc
- Parse any visible dates in ISO format (YYYY-MM-DD)
- Provide 2-5 main topics based on image content
- All scores between 0.0-1.0
- Be precise and avoid hallucination""",
            user_prompt_template="""Analyze this image and provide both description and metadata:

JSON:""",
            variables=[],  # Image data passed separately
            temperature=0.4,
            max_tokens=1200,
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


class MetadataExtractionPrompts:
    """Prompts for metadata extraction from documents."""
    
    @staticmethod
    def get_comprehensive_metadata_prompt() -> PromptTemplate:
        """Prompt for comprehensive metadata extraction."""
        return PromptTemplate(
            name="comprehensive_metadata",
            description="Extract comprehensive metadata from text",
            system_prompt="""You are an expert metadata extraction system. Extract comprehensive metadata from text in JSON format.

Return ONLY a valid JSON object with this structure:
{
  "keywords": [
    {"term": "string", "score": 0.8, "frequency": 3, "context": "string"}
  ],
  "entities": [
    {"text": "string", "label": "person", "confidence": 0.9, "start_pos": 10, "end_pos": 20}
  ],
  "dates": [
    {"date": "2024-01-15", "text": "January 15, 2024", "confidence": 0.95, "date_type": "publication", "format": "Long"}
  ],
  "topics": [
    {"topic_id": "tech", "topic_words": ["AI", "machine learning"], "probability": 0.8}
  ],
  "sentiment": {
    "sentiment": "positive",
    "confidence": 0.7,
    "scores": {"positive": 0.7, "negative": 0.1, "neutral": 0.2}
  },
  "summary": "Brief summary of the content",
  "key_phrases": ["important phrase", "key concept"],
  "language": "en",
  "readability_score": 0.6,
  "information_density": 0.8
}

Entity labels: person, organization, location, date, money, percent, product, event, misc
Sentiment types: positive, negative, neutral, mixed
All scores between 0.0-1.0

Guidelines:
- Extract 5-15 keywords based on text importance
- Identify all named entities with high confidence
- Parse dates in ISO format (YYYY-MM-DD)
- Provide 2-5 main topics
- Summary should be 1-3 sentences
- Be precise and avoid hallucination""",
            user_prompt_template="""Extract metadata from this text:

{text}

JSON:""",
            variables=["text"],
            temperature=0.2,
            max_tokens=1500,
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
        
        # Combined Processing (summary + metadata in one call)
        self._templates["table_summary_with_metadata"] = DocumentProcessingPrompts.get_table_summary_with_metadata_prompt()
        self._templates["image_description_with_metadata"] = DocumentProcessingPrompts.get_image_description_with_metadata_prompt()
        
        # Memo Generation
        self._templates["memo_section"] = MemoGenerationPrompts.get_memo_section_prompt()
        
        # Tenant-Specific
        self._templates["hr_policy_analysis"] = TenantSpecificPrompts.get_hr_policy_analysis_prompt()
        
        # RAG
        self._templates["factual_query"] = RAGPrompts.get_factual_query_prompt()
        
        # Metadata Extraction
        self._templates["comprehensive_metadata"] = MetadataExtractionPrompts.get_comprehensive_metadata_prompt()
    
    def get_template(self, name: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if name not in self._templates:
            raise ValueError(f"Template '{name}' not found. Available templates: {list(self._templates.keys())}")
        return self._templates[name]
    
    def format_prompt(self, template_name: str, **kwargs) -> Dict[str, Any]:
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


def format_prompt(template_name: str, **kwargs) -> Dict[str, Any]:
    """Convenience function to format a prompt template."""
    return prompt_manager.format_prompt(template_name, **kwargs)


def list_available_templates() -> List[str]:
    """Convenience function to list all available templates."""
    return list(prompt_manager._templates.keys())
