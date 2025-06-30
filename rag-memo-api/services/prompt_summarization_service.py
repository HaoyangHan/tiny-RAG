"""
Prompt Summarization Service for TinyRAG v1.4.

This service handles LLM-based summarization of generation prompts into
retrieval prompts, enabling the dual prompt system for elements.
"""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from services.llm_factory import get_llm_provider
from models.element import Element
from models.element_template import ElementTemplate
from models.enums import TenantType


class PromptSummarizationService:
    """
    Service for generating retrieval prompts from generation prompts using LLM.
    
    This service uses configured LLM providers to automatically generate
    concise, searchable retrieval prompts from detailed generation prompts.
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        model: str = "gpt-4o-mini",
        temperature: float = 0.3,
        max_tokens: int = 500,
        batch_size: int = 5
    ):
        """
        Initialize the prompt summarization service.
        
        Args:
            llm_provider: LLM provider to use (openai, anthropic, etc.)
            model: Model name to use for summarization
            temperature: Temperature for LLM generation
            max_tokens: Maximum tokens for summarized prompt
            batch_size: Batch size for parallel processing
        """
        self.llm_provider = llm_provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.batch_size = batch_size
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM client
        try:
            self.llm_client = get_llm_provider(llm_provider)
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM provider: {e}")
            self.llm_client = None
    
    def _get_base_summarization_prompt(self) -> str:
        """Get the base prompt for summarization."""
        return """Create a concise, searchable summary of the following detailed prompt.
        
REQUIREMENTS:
- Focus on key concepts, main objectives, and searchable terms
- Keep it under {max_tokens} tokens while preserving essential meaning
- Make it suitable for retrieval and indexing operations
- Remove verbose instructions and focus on core intent
- Preserve any important domain-specific terminology
- Use clear, direct language

ORIGINAL PROMPT:
{generation_prompt}

CONCISE SUMMARY:"""
    
    def _get_tenant_specific_prompt(self, tenant_type: TenantType) -> str:
        """Get tenant-specific summarization instructions."""
        tenant_prompts = {
            TenantType.HR: """Summarize this HR-related prompt focusing on:
- Policy areas and compliance requirements
- Employee processes and procedures  
- HR functions and responsibilities
- Key stakeholders and roles""",
            
            TenantType.CODING: """Summarize this development prompt focusing on:
- Programming concepts and technologies
- Development tools and frameworks
- Code analysis and generation tasks
- Technical processes and workflows""",
            
            TenantType.FINANCIAL_REPORT: """Summarize this financial prompt focusing on:
- Financial analysis types and metrics
- Reporting objectives and requirements
- Data sources and processing methods
- Compliance and regulatory aspects""",
            
            TenantType.DEEP_RESEARCH: """Summarize this research prompt focusing on:
- Research methodologies and approaches
- Key topics and domains
- Analysis types and objectives
- Information sources and requirements""",
            
            TenantType.QA_GENERATION: """Summarize this QA prompt focusing on:
- Question types and formats
- Knowledge domains and topics
- Assessment objectives and criteria
- Context and background requirements""",
            
            TenantType.RAW_RAG: """Summarize this RAG prompt focusing on:
- Information retrieval objectives
- Context and knowledge requirements
- Processing and analysis tasks
- Output formats and specifications"""
        }
        
        return tenant_prompts.get(tenant_type, self._get_base_summarization_prompt())
    
    def _build_summarization_prompt(
        self, 
        generation_prompt: str,
        tenant_type: Optional[TenantType] = None,
        custom_instructions: Optional[str] = None
    ) -> str:
        """Build the complete summarization prompt."""
        if custom_instructions:
            base_prompt = custom_instructions
        elif tenant_type:
            base_prompt = self._get_tenant_specific_prompt(tenant_type)
        else:
            base_prompt = self._get_base_summarization_prompt()
        
        return base_prompt.format(
            generation_prompt=generation_prompt,
            max_tokens=self.max_tokens
        )
    
    async def summarize_prompt(
        self,
        generation_prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Summarize a single generation prompt into a retrieval prompt.
        
        Args:
            generation_prompt: The detailed generation prompt to summarize
            context: Optional context including tenant_type, element_type, etc.
            
        Returns:
            Summarized retrieval prompt
            
        Raises:
            Exception: If summarization fails
        """
        if not self.llm_client:
            raise Exception("LLM client not initialized")
        
        if not generation_prompt.strip():
            raise ValueError("Generation prompt cannot be empty")
        
        # Extract context information
        tenant_type = None
        custom_instructions = None
        
        if context:
            tenant_type = context.get('tenant_type')
            custom_instructions = context.get('custom_instructions')
        
        # Build summarization prompt
        summarization_prompt = self._build_summarization_prompt(
            generation_prompt=generation_prompt,
            tenant_type=tenant_type,
            custom_instructions=custom_instructions
        )
        
        try:
            # Call LLM for summarization
            response = await self.llm_client.generate_text(
                prompt=summarization_prompt,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract and clean the response
            retrieval_prompt = response.strip()
            
            if not retrieval_prompt:
                raise Exception("LLM returned empty response")
            
            # Log successful summarization
            self.logger.info(
                f"Successfully summarized prompt: "
                f"{len(generation_prompt)} -> {len(retrieval_prompt)} chars"
            )
            
            return retrieval_prompt
            
        except Exception as e:
            self.logger.error(f"Failed to summarize prompt: {e}")
            raise Exception(f"Prompt summarization failed: {str(e)}")
    
    async def batch_summarize_prompts(
        self,
        prompts: List[str],
        contexts: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Summarize multiple prompts in batches.
        
        Args:
            prompts: List of generation prompts to summarize
            contexts: Optional list of contexts for each prompt
            
        Returns:
            List of summarized retrieval prompts
        """
        if not prompts:
            return []
        
        # Prepare contexts
        if contexts is None:
            contexts = [None] * len(prompts)
        elif len(contexts) != len(prompts):
            raise ValueError("Contexts list must match prompts list length")
        
        results = []
        
        # Process in batches
        for i in range(0, len(prompts), self.batch_size):
            batch_prompts = prompts[i:i + self.batch_size]
            batch_contexts = contexts[i:i + self.batch_size]
            
            # Create tasks for parallel processing
            tasks = [
                self.summarize_prompt(prompt, context)
                for prompt, context in zip(batch_prompts, batch_contexts)
            ]
            
            try:
                # Execute batch
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Failed to summarize prompt {i+j}: {result}")
                        # Use truncated original as fallback
                        fallback = batch_prompts[j][:200] + "..." if len(batch_prompts[j]) > 200 else batch_prompts[j]
                        results.append(fallback)
                    else:
                        results.append(result)
                
                # Add delay between batches to avoid rate limiting
                if i + self.batch_size < len(prompts):
                    await asyncio.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Batch processing failed: {e}")
                # Add fallback results for this batch
                for prompt in batch_prompts:
                    fallback = prompt[:200] + "..." if len(prompt) > 200 else prompt
                    results.append(fallback)
        
        return results
    
    async def regenerate_retrieval_prompt(self, element_id: str) -> Element:
        """
        Regenerate the retrieval prompt for a specific element.
        
        Args:
            element_id: ID of the element to update
            
        Returns:
            Updated element
        """
        # Find the element
        element = await Element.get(element_id)
        if not element:
            raise ValueError(f"Element not found: {element_id}")
        
        # Check if element has generation prompt
        if not element.has_generation_prompt():
            raise ValueError("Element does not have a generation prompt")
        
        # Prepare context
        context = {
            'tenant_type': element.tenant_type,
            'element_type': element.element_type,
            'element_name': element.name
        }
        
        # Generate new retrieval prompt
        retrieval_prompt = await self.summarize_prompt(
            generation_prompt=element.template.generation_prompt,
            context=context
        )
        
        # Update element
        element.update_retrieval_prompt(retrieval_prompt)
        await element.save()
        
        self.logger.info(f"Regenerated retrieval prompt for element: {element_id}")
        
        return element
    
    async def process_elements_without_retrieval_prompts(
        self,
        tenant_type: Optional[TenantType] = None,
        project_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Tuple[int, int]:
        """
        Process elements that don't have retrieval prompts.
        
        Args:
            tenant_type: Filter by tenant type
            project_id: Filter by project ID
            limit: Maximum number of elements to process
            
        Returns:
            Tuple of (processed_count, success_count)
        """
        # Build query
        query = {
            "template.generation_prompt": {"$exists": True, "$ne": None, "$ne": ""},
            "$or": [
                {"template.retrieval_prompt": {"$exists": False}},
                {"template.retrieval_prompt": None},
                {"template.retrieval_prompt": ""}
            ]
        }
        
        if tenant_type:
            query["tenant_type"] = tenant_type.value
        if project_id:
            query["project_id"] = project_id
        
        # Find elements
        elements = await Element.find(query).limit(limit or 1000).to_list()
        
        if not elements:
            self.logger.info("No elements found without retrieval prompts")
            return 0, 0
        
        self.logger.info(f"Found {len(elements)} elements without retrieval prompts")
        
        # Prepare prompts and contexts
        prompts = [elem.template.generation_prompt for elem in elements]
        contexts = [
            {
                'tenant_type': elem.tenant_type,
                'element_type': elem.element_type,
                'element_name': elem.name
            }
            for elem in elements
        ]
        
        # Generate retrieval prompts
        retrieval_prompts = await self.batch_summarize_prompts(prompts, contexts)
        
        # Update elements
        success_count = 0
        for element, retrieval_prompt in zip(elements, retrieval_prompts):
            try:
                element.update_retrieval_prompt(retrieval_prompt)
                await element.save()
                success_count += 1
            except Exception as e:
                self.logger.error(f"Failed to update element {element.id}: {e}")
        
        self.logger.info(
            f"Processed {len(elements)} elements, "
            f"{success_count} successful updates"
        )
        
        return len(elements), success_count
    
    async def validate_prompt_quality(
        self,
        generation_prompt: str,
        retrieval_prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate the quality of a retrieval prompt against its generation prompt.
        
        Args:
            generation_prompt: Original detailed prompt
            retrieval_prompt: Generated summary prompt
            context: Optional context information
            
        Returns:
            Validation metrics and assessment
        """
        metrics = {
            "length_ratio": len(retrieval_prompt) / len(generation_prompt),
            "word_count_original": len(generation_prompt.split()),
            "word_count_summary": len(retrieval_prompt.split()),
            "compression_ratio": 1 - (len(retrieval_prompt) / len(generation_prompt)),
            "has_key_terms": False,
            "readability_score": 0.0,
            "completeness_score": 0.0
        }
        
        # Basic quality checks
        if metrics["length_ratio"] > 0.8:
            metrics["warning"] = "Summary is too long relative to original"
        elif metrics["length_ratio"] < 0.1:
            metrics["warning"] = "Summary might be too short"
        
        # Check for key term preservation
        original_words = set(generation_prompt.lower().split())
        summary_words = set(retrieval_prompt.lower().split())
        
        # Simple overlap check
        overlap = len(original_words.intersection(summary_words))
        metrics["term_overlap_ratio"] = overlap / len(original_words) if original_words else 0
        metrics["has_key_terms"] = metrics["term_overlap_ratio"] > 0.2
        
        # Simple readability assessment
        avg_word_length = sum(len(word) for word in retrieval_prompt.split()) / len(retrieval_prompt.split())
        metrics["avg_word_length"] = avg_word_length
        metrics["readability_score"] = max(0, min(1, 1 - (avg_word_length - 5) / 10))
        
        # Completeness assessment
        metrics["completeness_score"] = min(1, metrics["term_overlap_ratio"] * 2)
        
        return metrics


# Global service instance
_summarization_service = None


def get_summarization_service() -> PromptSummarizationService:
    """Get the global prompt summarization service instance."""
    global _summarization_service
    
    if _summarization_service is None:
        # Initialize with environment variables
        _summarization_service = PromptSummarizationService(
            llm_provider=os.getenv("SUMMARIZATION_LLM_PROVIDER", "openai"),
            model=os.getenv("SUMMARIZATION_LLM_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("SUMMARIZATION_LLM_TEMPERATURE", "0.3")),
            max_tokens=int(os.getenv("SUMMARIZATION_LLM_MAX_TOKENS", "500")),
            batch_size=int(os.getenv("SUMMARIZATION_BATCH_SIZE", "5"))
        )
    
    return _summarization_service 