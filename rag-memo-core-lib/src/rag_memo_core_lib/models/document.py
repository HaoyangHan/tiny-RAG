"""Document model for the RAG Memo platform."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Document metadata model."""
    
    file_name: str
    file_size: int
    file_type: str
    upload_date: datetime
    processing_status: str = "pending"
    language: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    extracted_entities: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)


class DocumentChunk(BaseModel):
    """Document chunk model."""
    
    chunk_id: str
    content: str
    page_number: Optional[int] = None
    chunk_index: int
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    """Main document model."""
    
    id: Optional[str] = None
    title: str
    content: str
    content_type: str = "text/plain"
    user_id: str
    workspace_id: Optional[str] = None
    
    # Metadata
    metadata: DocumentMetadata
    
    # Processing results
    chunks: List[DocumentChunk] = Field(default_factory=list)
    summary: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic config."""
        
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow() 