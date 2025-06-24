"""
Project model for TinyRAG v1.4.

This module contains the Project model which serves as the central organizing
unit for documents, elements, and generations in the tenant-based architecture.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Indexed
from pydantic import Field, validator
from models.base import BaseDocument
from models.enums import TenantType, ProjectStatus, VisibilityType, get_default_task_type


class ProjectConfiguration(BaseDocument):
    """
    Project configuration and settings.
    
    Contains tenant-specific configuration and processing parameters
    for the project's workflow and generation pipeline.
    """
    
    # Generation settings
    default_model: Optional[str] = Field(
        None,
        description="Default LLM model for generations"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default temperature for LLM generations"
    )
    max_tokens: int = Field(
        default=1000,
        ge=1,
        le=8192,
        description="Default max tokens for generations"
    )
    
    # RAG settings
    retrieval_top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of documents to retrieve for RAG"
    )
    similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for document retrieval"
    )
    
    # Additional tenant-specific settings
    custom_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tenant-specific custom settings"
    )


class Project(BaseDocument):
    """
    Project model for organizing documents and RAG context.
    
    Projects serve as the central organizing unit in the v1.4 architecture,
    containing documents, elements, and their generated content within
    a specific tenant context.
    
    Attributes:
        name: Project name
        description: Project description
        keywords: Search keywords for project discovery
        tenant_type: Type of tenant (HR, coding, etc.)
        owner_id: User ID of project owner
        collaborators: List of collaborator user IDs
        visibility: Project visibility and access control
        status: Project lifecycle status
        document_ids: List of associated document IDs
        element_ids: List of associated element IDs
        generation_ids: List of associated generation IDs
        configuration: Project-specific configuration
        statistics: Project usage and performance statistics
    """
    
    # Basic Information
    name: str = Field(
        max_length=200,
        description="Project name"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Project description"
    )
    keywords: List[str] = Field(
        default_factory=list,
        max_items=10,
        description="Project keywords for search and discovery"
    )
    
    # Tenant Configuration
    tenant_type: TenantType = Field(
        description="Type of tenant (HR, coding, etc.)"
    )
    
    # Ownership & Access Control
    owner_id: Indexed(str) = Field(
        description="User ID of project owner"
    )
    collaborators: List[str] = Field(
        default_factory=list,
        description="List of collaborator user IDs"
    )
    visibility: VisibilityType = Field(
        default=VisibilityType.PRIVATE,
        description="Project visibility and access control"
    )
    
    # Status & Lifecycle
    status: ProjectStatus = Field(
        default=ProjectStatus.ACTIVE,
        description="Project lifecycle status"
    )
    
    # Associated Content IDs
    document_ids: List[str] = Field(
        default_factory=list,
        description="List of associated document IDs"
    )
    element_ids: List[str] = Field(
        default_factory=list,
        description="List of associated element IDs"
    )
    generation_ids: List[str] = Field(
        default_factory=list,
        description="List of associated generation IDs"
    )
    
    # Configuration
    configuration: ProjectConfiguration = Field(
        default_factory=ProjectConfiguration,
        description="Project-specific configuration and settings"
    )
    
    # Statistics
    statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Project usage and performance statistics"
    )
    
    @validator('keywords')
    def validate_keywords(cls, v: List[str]) -> List[str]:
        """Validate and normalize keywords."""
        return [keyword.lower().strip() for keyword in v if keyword.strip()]
    
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate project name."""
        if not v.strip():
            raise ValueError('Project name cannot be empty')
        return v.strip()
    
    def get_task_type(self):
        """Get the default task type for this project's tenant."""
        return get_default_task_type(self.tenant_type)
    
    def add_collaborator(self, user_id: str) -> None:
        """Add a collaborator to the project."""
        if user_id not in self.collaborators and user_id != self.owner_id:
            self.collaborators.append(user_id)
            self.update_timestamp()
    
    def remove_collaborator(self, user_id: str) -> None:
        """Remove a collaborator from the project."""
        if user_id in self.collaborators:
            self.collaborators.remove(user_id)
            self.update_timestamp()
    
    def is_accessible_by(self, user_id: str) -> bool:
        """
        Check if a user can access this project.
        
        Args:
            user_id: User ID to check access for
            
        Returns:
            bool: True if user has access, False otherwise
        """
        if self.owner_id == user_id:
            return True
        
        if self.visibility == VisibilityType.PUBLIC:
            return True
            
        if self.visibility == VisibilityType.SHARED and user_id in self.collaborators:
            return True
            
        return False
    
    def add_document(self, document_id: str) -> None:
        """Add a document to the project."""
        if document_id not in self.document_ids:
            self.document_ids.append(document_id)
            self.update_timestamp()
    
    def remove_document(self, document_id: str) -> None:
        """Remove a document from the project."""
        if document_id in self.document_ids:
            self.document_ids.remove(document_id)
            self.update_timestamp()
    
    def add_element(self, element_id: str) -> None:
        """Add an element to the project."""
        if element_id not in self.element_ids:
            self.element_ids.append(element_id)
            self.update_timestamp()
    
    def remove_element(self, element_id: str) -> None:
        """Remove an element from the project."""
        if element_id in self.element_ids:
            self.element_ids.remove(element_id)
            self.update_timestamp()
    
    def add_generation(self, generation_id: str) -> None:
        """Add a generation to the project."""
        if generation_id not in self.generation_ids:
            self.generation_ids.append(generation_id)
            self.update_timestamp()
    
    def update_statistics(self, key: str, value: Any) -> None:
        """Update project statistics."""
        self.statistics[key] = value
        self.update_timestamp()
    
    class Settings:
        name = "projects"
        indexes = [
            "owner_id",
            "tenant_type",
            "status",
            "visibility",
            "keywords",
            "name",
            "created_at",
            "updated_at",
            "is_deleted"
        ] 