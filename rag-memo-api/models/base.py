"""
Base models for TinyRAG v1.4.

This module contains the base document class and common fields
used across all Beanie models in the system.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from beanie import Document
from pydantic import Field


class BaseDocument(Document):
    """
    Base document class for all TinyRAG models.
    
    Provides common fields and functionality shared across all
    document types in the system, following MongoDB best practices.
    
    Attributes:
        created_at: Document creation timestamp
        updated_at: Document last update timestamp
        metadata: Additional flexible metadata storage
        is_deleted: Soft delete flag
        deleted_at: Deletion timestamp
    """
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Document creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Document last update timestamp"
    )
    
    # Flexible metadata storage
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the document"
    )
    
    # Soft delete support
    is_deleted: bool = Field(
        default=False,
        description="Soft delete flag"
    )
    deleted_at: Optional[datetime] = Field(
        None,
        description="Deletion timestamp"
    )
    
    def mark_deleted(self) -> None:
        """Mark document as deleted with timestamp."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a soft-deleted document."""
        self.is_deleted = False
        self.deleted_at = None
        self.updated_at = datetime.utcnow()
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    class Settings:
        """Base settings for all documents."""
        # Common indexes that most documents will benefit from
        indexes = [
            "created_at",
            "updated_at", 
            "is_deleted"
        ] 