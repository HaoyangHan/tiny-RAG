"""
Element Generation Service for TinyRAG v1.4.2
Handles template substitution with retrieved chunks and additional instructions
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.llm_factory import get_llm_provider
from api.v1.documents.service import DocumentService
from models.element import Element
from models.element_generation import ElementGeneration, GenerationStatus, GenerationMetrics
from models.project import Project

logger = logging.getLogger(__name__)


class ElementGenerationService:
    """
    Service for generating content from elements with template substitution.
    
    Handles the complete flow of:
    1. Document retrieval based on element's retrieval prompt
    2. Template substitution with retrieved chunks and additional instructions
    3. LLM generation with proper error handling
    """
    
    def __init__(self, document_service: DocumentService, llm_provider: str = "openai"):
        self.document_service = document_service
        self.llm_client = get_llm_provider(llm_provider)
        self.logger = logging.getLogger(__name__)
    
    async def generate_element_content(
        self,
        element_id: str,
        user_id: str,
        project_id: str,
        additional_instructions: Optional[str] = None,
        generation_config: Optional[Dict[str, Any]] = None
    ) -> ElementGeneration:
        """
        Generate content for an element with template substitution.
        
        Args:
            element_id: ID of the element to generate content for
            user_id: ID of the user requesting generation
            project_id: ID of the project containing the element
            additional_instructions: Optional additional instructions from user
            generation_config: Optional generation configuration
            
        Returns:
            ElementGeneration: Generated content with metadata
        """
        try:
            # Get element and validate access
            element = await Element.get(element_id)
            if not element:
                raise ValueError(f"Element not found: {element_id}")
            
            # Validate project access
            project = await Project.get(project_id)
            if not project or not project.is_accessible_by(user_id):
                raise ValueError("Access denied to project")
            
            # Create generation record
            generation = ElementGeneration(
                element_id=element_id,
                project_id=project_id,
                user_id=user_id,
                tenant_type=element.tenant_type,
                task_type=element.task_type,
                status=GenerationStatus.PENDING,
                additional_instructions=additional_instructions,
                metrics=GenerationMetrics()
            )
            
            await generation.insert()
            
            # Start generation process
            start_time = datetime.utcnow()
            
            try:
                # Update status to processing
                generation.status = GenerationStatus.PROCESSING
                await generation.save()
                
                # Step 1: Retrieve relevant document chunks
                retrieval_start = datetime.utcnow()
                source_chunks = await self._retrieve_relevant_chunks(
                    element=element,
                    project_id=project_id,
                    user_id=user_id
                )
                retrieval_time = (datetime.utcnow() - retrieval_start).total_seconds()
                
                # Step 2: Format template with retrieved chunks and additional instructions
                formatted_prompt = self._format_template(
                    template_content=element.template.generation_prompt,
                    retrieved_chunks=source_chunks,
                    additional_instructions=additional_instructions or ""
                )
                
                # Step 3: Generate content using LLM
                generation_start = datetime.utcnow()
                generated_content = await self._generate_with_llm(
                    prompt=formatted_prompt,
                    config=generation_config or element.template.execution_config
                )
                generation_time = (datetime.utcnow() - generation_start).total_seconds()
                
                # Step 4: Update generation with results
                generation.source_chunks = source_chunks
                generation.generated_content = [generated_content]
                generation.status = GenerationStatus.COMPLETED
                generation.completed_at = datetime.utcnow()
                
                # Update metrics
                generation.metrics.generation_time_ms = int(generation_time * 1000)
                generation.metrics.processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                generation.metrics.documents_retrieved = len(source_chunks)
                
                await generation.save()
                
                self.logger.info(f"Successfully generated content for element {element_id}")
                return generation
                
            except Exception as e:
                # Update generation with error
                generation.status = GenerationStatus.FAILED
                generation.error_details = {
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                    "stage": "generation"
                }
                await generation.save()
                
                self.logger.error(f"Generation failed for element {element_id}: {e}")
                raise
                
        except Exception as e:
            self.logger.error(f"Failed to create generation for element {element_id}: {e}")
            raise
    
    async def _retrieve_relevant_chunks(
        self,
        element: Element,
        project_id: str,
        user_id: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for the element.
        
        Args:
            element: Element to retrieve chunks for
            project_id: Project ID to limit document search
            user_id: User ID for access control
            top_k: Number of top chunks to retrieve
            
        Returns:
            List of relevant document chunks
        """
        try:
            # Use element's retrieval prompt if available, otherwise use generation prompt
            search_query = element.template.retrieval_prompt or element.template.generation_prompt
            
            # Get project documents
            project = await Project.get(project_id)
            if not project or not project.document_ids:
                return []
            
            # Search for relevant chunks
            chunks = await self.document_service.search_documents(
                user_id=user_id,
                query=search_query,
                document_ids=project.document_ids,
                top_k=top_k
            )
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve chunks for element {element.id}: {e}")
            return []
    
    def _format_template(
        self,
        template_content: str,
        retrieved_chunks: List[Dict[str, Any]],
        additional_instructions: str
    ) -> str:
        """
        Format the template with retrieved chunks and additional instructions.
        
        Args:
            template_content: Template content with placeholders
            retrieved_chunks: List of retrieved document chunks
            additional_instructions: Additional instructions from user
            
        Returns:
            Formatted template ready for LLM generation
        """
        try:
            # Format retrieved chunks
            if retrieved_chunks:
                chunks_text = self._format_chunks(retrieved_chunks)
            else:
                chunks_text = "No relevant document chunks found for this query."
            
            # Safely handle additional instructions (assign empty string if None/empty)
            safe_additional_instructions = additional_instructions.strip() if additional_instructions else ""
            
            # If additional instructions are empty, provide a default message
            if not safe_additional_instructions:
                safe_additional_instructions = "No additional instructions provided."
            
            # Perform template substitution
            formatted_prompt = template_content.format(
                retrieved_chunks=chunks_text,
                additional_instructions=safe_additional_instructions
            )
            
            return formatted_prompt
            
        except KeyError as e:
            self.logger.error(f"Template formatting error - missing placeholder: {e}")
            raise ValueError(f"Template contains undefined placeholder: {e}")
        except Exception as e:
            self.logger.error(f"Template formatting error: {e}")
            raise ValueError(f"Failed to format template: {e}")
    
    def _format_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format document chunks for inclusion in the prompt.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Formatted chunks text
        """
        if not chunks:
            return "No relevant document chunks found."
        
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            document_title = chunk.get('document_title', 'Unknown Document')
            chunk_text = chunk.get('chunk_text', '')
            page_number = chunk.get('page_number', 'Unknown')
            
            formatted_chunk = f"""
**Document Chunk {i+1}:**
- Source: {document_title}
- Page: {page_number}
- Content: {chunk_text}
"""
            formatted_chunks.append(formatted_chunk)
        
        return "\n".join(formatted_chunks)
    
    async def _generate_with_llm(
        self,
        prompt: str,
        config: Dict[str, Any]
    ) -> str:
        """
        Generate content using LLM with the formatted prompt.
        
        Args:
            prompt: Formatted prompt for LLM
            config: Generation configuration
            
        Returns:
            Generated content
        """
        try:
            # Extract configuration parameters
            model = config.get('model', 'gpt-4o-mini')
            temperature = config.get('temperature', 0.7)
            max_tokens = config.get('max_tokens', 2000)
            
            # Generate content
            response = await self.llm_client.generate_text(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            raise ValueError(f"Failed to generate content: {e}")
    
    async def bulk_generate_elements(
        self,
        project_id: str,
        user_id: str,
        element_ids: Optional[List[str]] = None,
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate content for multiple elements in bulk.
        
        Args:
            project_id: Project ID
            user_id: User ID
            element_ids: Specific element IDs to generate (if None, generate all)
            additional_instructions: Additional instructions for all elements
            
        Returns:
            Bulk generation results
        """
        try:
            # Get project and validate access
            project = await Project.get(project_id)
            if not project or not project.is_accessible_by(user_id):
                raise ValueError("Access denied to project")
            
            # Get elements to generate
            if element_ids:
                elements = await Element.find(
                    {"_id": {"$in": element_ids}, "project_id": project_id}
                ).to_list()
            else:
                elements = await Element.find({"project_id": project_id}).to_list()
            
            if not elements:
                return {
                    "message": "No elements found to generate",
                    "total_elements": 0,
                    "successful": 0,
                    "failed": 0
                }
            
            # Generate content for each element
            results = {
                "total_elements": len(elements),
                "successful": 0,
                "failed": 0,
                "generations": [],
                "errors": []
            }
            
            for element in elements:
                try:
                    generation = await self.generate_element_content(
                        element_id=str(element.id),
                        user_id=user_id,
                        project_id=project_id,
                        additional_instructions=additional_instructions
                    )
                    
                    results["generations"].append({
                        "element_id": str(element.id),
                        "element_name": element.name,
                        "generation_id": str(generation.id),
                        "status": generation.status.value
                    })
                    results["successful"] += 1
                    
                except Exception as e:
                    results["errors"].append({
                        "element_id": str(element.id),
                        "element_name": element.name,
                        "error": str(e)
                    })
                    results["failed"] += 1
                    
                    self.logger.error(f"Bulk generation failed for element {element.id}: {e}")
            
            self.logger.info(f"Bulk generation completed: {results['successful']}/{results['total_elements']} successful")
            return results
            
        except Exception as e:
            self.logger.error(f"Bulk generation failed for project {project_id}: {e}")
            raise


# Global service instance
_element_generation_service = None


def get_element_generation_service() -> ElementGenerationService:
    """Get the global element generation service instance."""
    global _element_generation_service
    
    if _element_generation_service is None:
        from api.v1.documents.service import DocumentService
        
        document_service = DocumentService()
        _element_generation_service = ElementGenerationService(document_service)
    
    return _element_generation_service 