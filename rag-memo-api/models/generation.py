from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Document, Indexed
from pydantic import BaseModel, Field

class GenerationMetadata(BaseModel):
    """Metadata for a generation response."""
    retrieval_time: Optional[float] = None
    generation_time: Optional[float] = None
    total_documents_searched: Optional[int] = None
    documents_used: Optional[int] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class Generation(Document):
    """Generation model for storing generation requests and responses."""
    user_id: Indexed(str)
    query: str
    response: Optional[str] = None
    document_ids: List[str] = []  # References to source documents
    sources: List[Dict[str, Any]] = []  # Source document snippets with metadata
    metadata: Optional[GenerationMetadata] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: str = "processing"  # processing, completed, failed
    error: Optional[str] = None
    
    # Request parameters
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

    class Settings:
        name = "generations"
        indexes = [
            "user_id",
            "query",
            "created_at",
            "status"
        ]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "query": "What are the main findings about machine learning?",
                "response": "Based on the documents, the main findings about machine learning are...",
                "document_ids": ["doc1", "doc2"],
                "sources": [
                    {
                        "document_id": "doc1",
                        "title": "ML Research Paper",
                        "content": "Relevant excerpt...",
                        "score": 0.95
                    }
                ],
                "status": "completed",
                "max_tokens": 1000,
                "temperature": 0.7
            }
        } 