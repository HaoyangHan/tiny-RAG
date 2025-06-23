"""Generation models for the RAG Memo platform."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    """Request model for RAG generation."""
    
    query: str
    user_id: str
    workspace_id: Optional[str] = None
    document_ids: List[str] = Field(default_factory=list)
    
    # Generation parameters
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 0.9
    
    # RAG parameters
    top_k_documents: int = 5
    similarity_threshold: float = 0.7
    use_reranking: bool = True
    
    # Context
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic config."""
        
        use_enum_values = True
        validate_assignment = True


class DocumentSource(BaseModel):
    """Source document information for generation."""
    
    document_id: str
    document_title: str
    chunk_content: str
    relevance_score: float
    page_number: Optional[int] = None
    chunk_index: int


class GenerationResponse(BaseModel):
    """Response model for RAG generation."""
    
    request_id: str
    response: str
    sources: List[DocumentSource] = Field(default_factory=list)
    
    # Generation metadata
    tokens_used: int
    response_time_ms: int
    model_used: str
    
    # Quality metrics
    confidence_score: float
    relevance_score: float
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        
        use_enum_values = True
        validate_assignment = True 