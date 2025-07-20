"""
Document Models for TinyRAG v1.4.3
==================================

This module defines the data models for documents, chunks, and metadata
with comprehensive extraction capabilities.

Author: TinyRAG Development Team
Version: 1.4.3
Last Updated: January 2025
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from beanie import Document as BeanieDocument


class DocumentStatus(str, Enum):
    """Document processing status."""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Metadata for document processing and analysis."""
    filename: str
    content_type: str
    size: int
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False
    has_tables: bool = False
    has_images: bool = False
    error: Optional[str] = None
    extracted_metadata: Optional[Dict[str, Any]] = None
    content_hash: Optional[str] = None  # SHA256 hash for duplicate detection


class DocumentChunk(BaseModel):
    """A chunk of text from a document with comprehensive metadata."""
    text: str
    page_number: int
    chunk_index: int
    chunk_type: str = "text"  # text, table, image
    embedding: Optional[List[float]] = None
    chunk_metadata: Optional[Dict[str, Any]] = None
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    section: Optional[str] = None


class TableData(BaseModel):
    """Table data extracted from documents."""
    page_number: int
    table_index: int
    content: List[List[str]]
    summary: Optional[str] = None
    row_count: int = 0
    column_count: int = 0


class ImageData(BaseModel):
    """Image data extracted from documents."""
    page_number: int
    image_index: int
    content: bytes
    description: Optional[str] = None


class Document(BeanieDocument):
    """Document model with enhanced processing capabilities."""
    
    user_id: str
    project_id: str
    filename: str
    content_type: str
    file_size: int
    status: DocumentStatus = DocumentStatus.UPLOADING
    metadata: DocumentMetadata
    chunks: List[DocumentChunk] = []
    tables: List[TableData] = []
    images: List[ImageData] = []
    is_deleted: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "documents"
    
    def get_chunk_count(self) -> int:
        """Get total number of chunks."""
        return len(self.chunks)
    
    def get_table_count(self) -> int:
        """Get total number of tables."""
        return len(self.tables)
    
    def get_image_count(self) -> int:
        """Get total number of images."""
        return len(self.images)
    
    def get_text_chunks(self) -> List[DocumentChunk]:
        """Get text chunks only."""
        return [chunk for chunk in self.chunks if chunk.chunk_type == "text"]
    
    def get_table_chunks(self) -> List[DocumentChunk]:
        """Get table chunks only."""
        return [chunk for chunk in self.chunks if chunk.chunk_type == "table"]
    
    def get_image_chunks(self) -> List[DocumentChunk]:
        """Get image chunks only."""
        return [chunk for chunk in self.chunks if chunk.chunk_type == "image"]
    
    def get_metadata_summary(self) -> Dict[str, Any]:
        """Get summary of metadata extraction."""
        summary = {
            "total_chunks": self.get_chunk_count(),
            "text_chunks": len(self.get_text_chunks()),
            "table_chunks": len(self.get_table_chunks()),
            "image_chunks": len(self.get_image_chunks()),
            "tables": self.get_table_count(),
            "images": self.get_image_count(),
            "has_tables": self.metadata.has_tables,
            "has_images": self.metadata.has_images,
            "processed": self.metadata.processed
        }
        
        # Add metadata extraction summary if available
        if self.chunks:
            metadata_fields = 0
            for chunk in self.chunks:
                if chunk.chunk_metadata:
                    metadata_fields += len(chunk.chunk_metadata)
            summary["metadata_fields_extracted"] = metadata_fields
        
        return summary 