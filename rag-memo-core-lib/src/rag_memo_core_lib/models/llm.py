"""LLM models for the RAG Memo platform."""

from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    """Message model for LLM interactions."""
    
    role: Literal["system", "user", "assistant"]
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        
        use_enum_values = True
        validate_assignment = True


class LLMUsage(BaseModel):
    """Token usage information."""
    
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class LLMResponse(BaseModel):
    """Response model for LLM interactions."""
    
    id: str
    content: str
    model: str
    finish_reason: str
    
    # Usage information
    usage: LLMUsage
    
    # Metadata
    response_time_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic config."""
        
        use_enum_values = True
        validate_assignment = True 