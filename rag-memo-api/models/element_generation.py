"""
ElementGeneration model for TinyRAG v1.4.

This module contains the ElementGeneration model which stores LLM-generated
content with chunks, documents, and evaluation tracking.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Indexed
from pydantic import Field, validator
from models.base import BaseDocument
from models.enums import GenerationStatus, TenantType, TaskType


class GenerationChunk(BaseDocument):
    """
    A chunk of generated content with metadata.
    
    Contains individual pieces of generated content with
    source tracking and evaluation results.
    """
    
    # Content
    content: str = Field(
        description="Generated content chunk"
    )
    chunk_index: int = Field(
        description="Index of this chunk in the generation"
    )
    
    # Source tracking
    source_documents: List[str] = Field(
        default_factory=list,
        description="Document IDs that contributed to this chunk"
    )
    source_elements: List[str] = Field(
        default_factory=list,
        description="Element IDs that contributed to this chunk"
    )
    
    # Metadata
    token_count: Optional[int] = Field(
        None,
        description="Token count for this chunk"
    )
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score for this chunk"
    )
    
    # Evaluation results
    relevance_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Relevance score from evaluation"
    )
    accuracy_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Accuracy score from evaluation"
    )


class GenerationMetrics(BaseDocument):
    """
    Performance metrics for content generation.
    
    Tracks performance, cost, and quality metrics
    for the generation process.
    """
    
    # Performance metrics
    generation_time_ms: Optional[int] = Field(
        None,
        description="Total generation time in milliseconds"
    )
    processing_time_ms: Optional[int] = Field(
        None,
        description="Processing time in milliseconds"
    )
    
    # Token usage
    prompt_tokens: int = Field(
        default=0,
        description="Number of prompt tokens used"
    )
    completion_tokens: int = Field(
        default=0,
        description="Number of completion tokens generated"
    )
    total_tokens: int = Field(
        default=0,
        description="Total tokens used"
    )
    
    # Cost estimation
    estimated_cost: Optional[float] = Field(
        None,
        description="Estimated cost in USD"
    )
    
    # Quality metrics
    average_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Average confidence across all chunks"
    )
    
    # Retrieval metrics (for RAG)
    documents_retrieved: int = Field(
        default=0,
        description="Number of documents retrieved for context"
    )
    average_retrieval_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Average retrieval relevance score"
    )


class ElementGeneration(BaseDocument):
    """
    ElementGeneration model for storing LLM-generated content.
    
    Stores the results of content generation from elements,
    including the generated content, metadata, evaluation results,
    and performance metrics.
    
    Attributes:
        element_id: ID of the element that generated this content
        project_id: ID of the associated project
        user_id: ID of the user who triggered the generation
        tenant_type: Type of tenant for the generation
        task_type: Type of task performed
        status: Generation status
        input_data: Input data provided for generation
        generated_content: List of generated content chunks
        metrics: Performance and quality metrics
        evaluation_id: ID of associated evaluation (if any)
        error_details: Error information if generation failed
        context_data: Additional context used for generation
    """
    
    # Association IDs
    element_id: Indexed(str) = Field(
        description="ID of the element that generated this content"
    )
    project_id: Indexed(str) = Field(
        description="ID of the associated project"
    )
    user_id: Indexed(str) = Field(
        description="ID of the user who triggered the generation"
    )
    
    # Tenant and Task Context
    tenant_type: TenantType = Field(
        description="Type of tenant for the generation"
    )
    task_type: TaskType = Field(
        description="Type of task performed"
    )
    
    # Generation Status
    status: GenerationStatus = Field(
        default=GenerationStatus.PENDING,
        description="Current status of the generation"
    )
    
    # Input and Output
    # input_data: Dict[str, Any] = Field(
    #     default_factory=dict,
    #     description="Input data provided for generation"
    # )  # REMOVED: Simplified to chunks + additional_instructions approach
    
    additional_instructions: Optional[str] = Field(
        None,
        description="Optional additional instructions provided by user"
    )
    
    source_chunks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Document chunks retrieved and used for generation"
    )
    generated_content: List[GenerationChunk] = Field(
        default_factory=list,
        description="List of generated content chunks"
    )
    
    # Performance Metrics
    metrics: GenerationMetrics = Field(
        default_factory=GenerationMetrics,
        description="Performance and quality metrics"
    )
    
    # Evaluation
    evaluation_id: Optional[str] = Field(
        None,
        description="ID of associated evaluation (if any)"
    )
    evaluation_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of evaluation results"
    )
    
    # Error Handling
    error_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Error information if generation failed"
    )
    
    # Context Information
    context_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context used for generation"
    )
    
    # Model and Configuration
    model_used: Optional[str] = Field(
        None,
        description="LLM model used for generation"
    )
    generation_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration used for generation"
    )
    
    @validator('status')
    def validate_status_transition(cls, v: GenerationStatus, values: Dict[str, Any]) -> GenerationStatus:
        """Validate status transitions are logical."""
        # Add status transition validation logic here if needed
        return v
    
    def add_chunk(self, content: str, chunk_index: int, 
                  source_documents: List[str] = None,
                  source_elements: List[str] = None) -> None:
        """Add a content chunk to the generation."""
        chunk = GenerationChunk(
            content=content,
            chunk_index=chunk_index,
            source_documents=source_documents or [],
            source_elements=source_elements or []
        )
        self.generated_content.append(chunk)
        self.update_timestamp()
    
    def set_completed(self, total_tokens: int = None) -> None:
        """Mark generation as completed."""
        self.status = GenerationStatus.COMPLETED
        if total_tokens:
            self.metrics.total_tokens = total_tokens
        self.update_timestamp()
    
    def set_failed(self, error_message: str, error_details: Dict[str, Any] = None) -> None:
        """Mark generation as failed with error details."""
        self.status = GenerationStatus.FAILED
        self.error_details = {
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
            **(error_details or {})
        }
        self.update_timestamp()
    
    def get_total_content(self) -> str:
        """Get all generated content as a single string."""
        return "\n\n".join([chunk.content for chunk in self.generated_content])
    
    def get_chunk_count(self) -> int:
        """Get the number of generated chunks."""
        return len(self.generated_content)
    
    def update_metrics(self, **kwargs) -> None:
        """Update generation metrics."""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
        self.update_timestamp()
    
    def calculate_average_confidence(self) -> Optional[float]:
        """Calculate average confidence score across all chunks."""
        scores = [chunk.confidence_score for chunk in self.generated_content 
                 if chunk.confidence_score is not None]
        if scores:
            avg_score = sum(scores) / len(scores)
            self.metrics.average_confidence = avg_score
            return avg_score
        return None
    
    def get_source_documents(self) -> List[str]:
        """Get all unique source documents used in generation."""
        all_docs = []
        for chunk in self.generated_content:
            all_docs.extend(chunk.source_documents)
        return list(set(all_docs))
    
    def get_source_elements(self) -> List[str]:
        """Get all unique source elements used in generation."""
        all_elements = []
        for chunk in self.generated_content:
            all_elements.extend(chunk.source_elements)
        return list(set(all_elements))
    
    def is_successful(self) -> bool:
        """Check if generation was successful."""
        return self.status == GenerationStatus.COMPLETED and len(self.generated_content) > 0
    
    class Settings:
        name = "element_generations"
        indexes = [
            "element_id",
            "project_id", 
            "user_id",
            "tenant_type",
            "task_type",
            "status",
            "model_used",
            "created_at",
            "updated_at",
            "is_deleted"
        ] 