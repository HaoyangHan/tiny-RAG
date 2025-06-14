from datetime import datetime
from typing import List, Optional
from beanie import Document, Indexed
from pydantic import BaseModel, Field

class MemoSection(BaseModel):
    """A section within a memo."""
    title: str
    content: str
    citations: List[str] = []

class Memo(Document):
    """Memo model for storing generated memos."""
    user_id: Indexed(str)
    title: str
    sections: List[MemoSection]
    document_ids: List[str]  # References to source documents
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "completed"  # completed, processing, failed
    error: Optional[str] = None

    class Settings:
        name = "memos"
        indexes = [
            "user_id",
            "title",
            "created_at",
            "status"
        ]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "title": "Project Overview Memo",
                "sections": [
                    {
                        "title": "Executive Summary",
                        "content": "This memo provides an overview of the project...",
                        "citations": ["doc1", "doc2"]
                    }
                ],
                "document_ids": ["doc1", "doc2"],
                "status": "completed"
            }
        } 