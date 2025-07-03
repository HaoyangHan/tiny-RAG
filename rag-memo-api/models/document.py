from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Document as BeanieDocument, Indexed
from pydantic import BaseModel, Field

class TableData(BaseModel):
    """Model for table data extracted from documents."""
    page_number: int
    table_index: int
    content: List[List[str]]  # Table data as list of rows
    summary: str
    row_count: int = 0
    column_count: int = 0

class ImageData(BaseModel):
    """Model for image data extracted from documents."""
    page_number: int
    image_index: int
    content: bytes  # Raw image data
    description: str

class DocumentMetadata(BaseModel):
    """Metadata for uploaded documents."""
    filename: str
    content_type: str
    size: int
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
    has_tables: bool = False
    has_images: bool = False
    error: Optional[str] = None
    extracted_metadata: Optional[Dict[str, Any]] = None

class DocumentChunk(BaseModel):
    """A chunk of text from a document with comprehensive metadata."""
    text: str
    page_number: int
    chunk_index: int
    chunk_type: str = "text"  # One of: "text", "table", "image"
    embedding: Optional[List[float]] = None
    
    # Enhanced metadata fields
    chunk_metadata: Optional[Dict[str, Any]] = None  # Comprehensive metadata from extractor
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    section: Optional[str] = None

class Document(BeanieDocument):
    """Document model for storing uploaded documents and their chunks."""
    user_id: Indexed(str)
    project_id: Optional[Indexed(str)] = None
    
    # Required fields for MongoDB validation
    filename: str
    content_type: str
    file_size: int
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional fields
    metadata: DocumentMetadata
    chunks: List[DocumentChunk] = Field(default_factory=list)
    tables: List[TableData] = Field(default_factory=list)
    images: List[ImageData] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = False

    class Settings:
        name = "documents"
        indexes = [
            "user_id",
            "project_id",
            "filename",
            "status",
            "created_at"
        ]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "project_id": "project123",
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