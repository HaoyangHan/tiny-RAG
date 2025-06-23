from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, Field

class DocumentMetadata(BaseModel):
    """Metadata for uploaded documents."""
    filename: str
    content_type: str
    size: int
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
    error: Optional[str] = None

class DocumentChunk(BaseModel):
    """A chunk of text from a document."""
    text: str
    page_number: int
    chunk_index: int
    embedding: Optional[List[float]] = None

class Document(Document):
    """Document model for storing uploaded documents and their chunks."""
    user_id: Indexed(str)
    
    # Required fields for MongoDB validation
    filename: str
    content_type: str
    file_size: int
    status: str = "processing"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional fields
    metadata: DocumentMetadata
    chunks: List[DocumentChunk] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "documents"
        indexes = [
            "user_id",
            "filename",
            "status",
            "created_at"
        ]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "filename": "example.pdf",
                "content_type": "application/pdf", 
                "file_size": 1024,
                "status": "completed",
                "metadata": {
                    "filename": "example.pdf",
                    "content_type": "application/pdf",
                    "size": 1024,
                    "upload_date": "2024-02-20T12:00:00",
                    "processed": True
                },
                "chunks": [
                    {
                        "text": "Example document chunk",
                        "page_number": 1,
                        "chunk_index": 0
                    }
                ]
            }
        } 