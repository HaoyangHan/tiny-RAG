"""
ElementTemplate model for TinyRAG v1.4.

This module contains the ElementTemplate model which stores default element
templates for each tenant type that can be automatically provisioned to projects.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Indexed
from pydantic import Field, validator
from models.base import BaseDocument
from models.enums import TenantType, TaskType, ElementType, ElementStatus


class ElementTemplate(BaseDocument):
    """
    Element template model for storing default tenant-specific templates.
    
    Templates serve as blueprints for creating project elements automatically
    when projects are created. They contain the default prompts, configurations,
    and settings for each tenant type.
    
    Attributes:
        name: Template name (unique per tenant)
        description: Template description
        tenant_type: Associated tenant type
        task_type: Task processing approach
        element_type: Type of element (prompt, MCP, etc.)
        generation_prompt: Full detailed prompt for generation
        retrieval_prompt: Summarized prompt for retrieval
        variables: Template variables that can be substituted
        execution_config: Execution-specific configuration parameters
        is_system_default: Whether this is a system-created template
        version: Template version following semantic versioning
        tags: Searchable tags for template discovery
        status: Template lifecycle status
        created_by: User ID of template creator
        usage_count: Number of times template has been used
        last_used_at: Timestamp of last template usage
    """
    
    # Basic Information
    name: str = Field(
        max_length=200,
        description="Template name (unique per tenant)"
    )
    description: str = Field(
        max_length=1000,
        description="Template description"
    )
    
    # Tenant and Task Configuration
    tenant_type: Indexed(TenantType) = Field(
        description="Associated tenant type"
    )
    task_type: TaskType = Field(
        description="Task processing approach"
    )
    element_type: ElementType = Field(
        description="Type of element (prompt template, MCP config, etc.)"
    )
    
    # Dual Prompt System
    generation_prompt: str = Field(
        description="Full detailed prompt for generation with complete context"
    )
    retrieval_prompt: Optional[str] = Field(
        None,
        description="Summarized prompt for retrieval and indexing"
    )
    
    # Template Configuration
    variables: List[str] = Field(
        default_factory=list,
        description="Template variables that can be substituted"
    )
    execution_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Execution-specific configuration parameters"
    )
    
    # Source and Type
    is_system_default: bool = Field(
        default=True,
        description="Whether this is a system-created template vs user-created"
    )
    
    # Version Control
    version: str = Field(
        default="1.0.0",
        description="Template version following semantic versioning"
    )
    changelog: List[str] = Field(
        default_factory=list,
        description="List of changes made to the template"
    )
    
    # Searchability and Classification
    tags: List[str] = Field(
        default_factory=list,
        max_items=20,
        description="Searchable tags for template discovery"
    )
    
    # Status and Lifecycle
    status: ElementStatus = Field(
        default=ElementStatus.ACTIVE,
        description="Template lifecycle status"
    )
    
    # Ownership and Usage
    created_by: Indexed(str) = Field(
        description="User ID of template creator"
    )
    usage_count: int = Field(
        default=0,
        description="Number of times template has been used"
    )
    last_used_at: Optional[datetime] = Field(
        None,
        description="Timestamp of last template usage"
    )
    
    # Statistics and Analytics
    element_count: int = Field(
        default=0,
        description="Number of elements created from this template"
    )
    success_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Success rate of elements created from this template"
    )
    
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate template name."""
        if not v.strip():
            raise ValueError('Template name cannot be empty')
        return v.strip()
    
    @validator('generation_prompt')
    def validate_generation_prompt(cls, v: str) -> str:
        """Validate generation prompt."""
        if not v.strip():
            raise ValueError('Generation prompt cannot be empty')
        if len(v) < 50:
            raise ValueError('Generation prompt should be at least 50 characters')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate and normalize tags."""
        return [tag.lower().strip() for tag in v if tag.strip()]
    
    @validator('variables')
    def validate_variables(cls, v: List[str]) -> List[str]:
        """Validate and normalize variables."""
        return [var.strip() for var in v if var.strip()]
    
    @validator('version')
    def validate_version(cls, v: str) -> str:
        """Validate semantic version format."""
        import re
        version_pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(version_pattern, v):
            raise ValueError('Version must follow semantic versioning (e.g., 1.0.0)')
        return v
    
    def increment_usage(self) -> None:
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        self.update_timestamp()
    
    def increment_element_count(self) -> None:
        """Increment the count of elements created from this template."""
        self.element_count += 1
        self.update_timestamp()
    
    def update_success_rate(self, success_count: int) -> None:
        """Update the success rate based on successful element executions."""
        if self.element_count > 0:
            self.success_rate = success_count / self.element_count
        self.update_timestamp()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the template."""
        normalized_tag = tag.lower().strip()
        if normalized_tag and normalized_tag not in self.tags:
            self.tags.append(normalized_tag)
            self.update_timestamp()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the template."""
        normalized_tag = tag.lower().strip()
        if normalized_tag in self.tags:
            self.tags.remove(normalized_tag)
            self.update_timestamp()
    
    def update_version(self, new_version: str, changelog_entry: str) -> None:
        """Update template version and add changelog entry."""
        self.version = new_version
        self.changelog.append(f"{new_version}: {changelog_entry} ({datetime.utcnow().isoformat()})")
        self.update_timestamp()
    
    def is_ready_for_use(self) -> bool:
        """Check if template is ready for use in projects."""
        return (
            self.status == ElementStatus.ACTIVE and
            bool(self.generation_prompt) and
            len(self.generation_prompt) >= 50
        )
    
    def has_retrieval_prompt(self) -> bool:
        """Check if template has a retrieval prompt."""
        return bool(self.retrieval_prompt and self.retrieval_prompt.strip())
    
    def get_template_summary(self) -> Dict[str, Any]:
        """Get a summary of template information for display."""
        return {
            "id": str(self.id),
            "name": self.name,
            "tenant_type": self.tenant_type.value,
            "element_type": self.element_type.value,
            "version": self.version,
            "status": self.status.value,
            "usage_count": self.usage_count,
            "element_count": self.element_count,
            "success_rate": round(self.success_rate * 100, 2),
            "has_retrieval_prompt": self.has_retrieval_prompt(),
            "is_system_default": self.is_system_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None
        }
    
    class Settings:
        name = "element_templates"
        indexes = [
            "tenant_type",
            "element_type",
            "status",
            "created_by",
            "is_system_default",
            ("tenant_type", "name"),  # Compound index for unique constraints
            ("tenant_type", "element_type"),
            ("created_by", "tenant_type"),
            "usage_count",
            "last_used_at"
        ] 