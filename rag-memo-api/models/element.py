"""
Element model for TinyRAG v1.4.

This module contains the Element model which serves as containers for
prompt templates, MCP configurations, or Agentic tools within projects.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Indexed
from pydantic import Field, validator
from models.base import BaseDocument
from models.enums import TenantType, TaskType, ElementType, ElementStatus


class ElementContent(BaseDocument):
    """
    Element content and configuration.
    
    Contains the actual element content, variables, and execution
    parameters for different element types.
    """
    
    # Content and Dual Prompt System
    content: str = Field(
        description="Legacy template content (prompt, config, etc.)"
    )
    generation_prompt: Optional[str] = Field(
        None,
        description="Full detailed prompt for generation with complete context"
    )
    retrieval_prompt: Optional[str] = Field(
        None,
        description="Summarized prompt for retrieval and indexing"
    )
    
    variables: List[str] = Field(
        default_factory=list,
        description="Template variables that can be substituted"
    )
    
    # Execution parameters
    execution_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Execution-specific configuration parameters"
    )
    
    # Version control
    version: str = Field(
        default="1.0.0",
        description="Template version following semantic versioning"
    )
    changelog: List[str] = Field(
        default_factory=list,
        description="List of changes made to the template"
    )


class ElementExecution(BaseDocument):
    """
    Tracking for element execution instances.
    
    Records individual executions of elements including
    input parameters, results, and performance metrics.
    """
    
    # Execution context
    input_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Input variables provided for execution"
    )
    output_content: Optional[str] = Field(
        None,
        description="Generated output content"
    )
    
    # Performance metrics
    execution_time_ms: Optional[int] = Field(
        None,
        description="Execution time in milliseconds"
    )
    token_usage: Dict[str, int] = Field(
        default_factory=dict,
        description="Token usage statistics"
    )
    
    # Status and results
    status: str = Field(
        default="pending",
        description="Execution status"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if execution failed"
    )
    
    # Evaluation results
    evaluation_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Evaluation scores for the execution"
    )
    
    class Settings:
        name = "element_executions"


class Element(BaseDocument):
    """
    Element model for template containers and execution tracking.
    
    Elements serve as containers for prompt templates, MCP configurations,
    or Agentic tools within projects, enabling reusable and versioned
    content generation components.
    
    Attributes:
        name: Element name
        description: Element description
        project_id: Associated project ID
        tenant_type: Type of tenant this element belongs to
        task_type: Type of task this element performs
        element_type: Type of element (prompt, MCP, etc.)
        status: Element lifecycle status
        template: Template content and configuration
        execution_history: List of execution records
        usage_statistics: Element usage and performance statistics
        tags: Searchable tags for element discovery
        owner_id: User ID of element owner
    """
    
    # Basic Information
    name: str = Field(
        max_length=200,
        description="Element name"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Element description"
    )
    
    # Project Association
    project_id: Indexed(str) = Field(
        description="Associated project ID"
    )
    
    # Tenant and Task Configuration
    tenant_type: TenantType = Field(
        description="Type of tenant this element belongs to"
    )
    task_type: TaskType = Field(
        description="Type of task this element performs"
    )
    element_type: ElementType = Field(
        description="Type of element (prompt template, MCP config, etc.)"
    )
    
    # Status and Lifecycle
    status: ElementStatus = Field(
        default=ElementStatus.DRAFT,
        description="Element lifecycle status"
    )
    
    # Template Content
    template: ElementContent = Field(
        description="Template content and configuration"
    )
    
    # Source and Template Tracking (NEW)
    is_default_element: bool = Field(
        default=False,
        description="Whether this element was created from a template vs user-created"
    )
    template_id: Optional[str] = Field(
        None,
        description="Source template ID if this element was created from a template"
    )
    insertion_batch_id: Optional[str] = Field(
        None,
        description="Batch ID for script-inserted elements (for removal tracking)"
    )
    
    # Execution Tracking
    execution_history: List[str] = Field(
        default_factory=list,
        description="List of execution record IDs"
    )
    
    # Statistics and Metrics
    usage_statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Element usage and performance statistics"
    )
    
    # Searchability
    tags: List[str] = Field(
        default_factory=list,
        max_items=20,
        description="Searchable tags for element discovery"
    )
    
    # Ownership
    owner_id: Indexed(str) = Field(
        description="User ID of element owner"
    )
    
    @validator('name')
    def validate_name(cls, v: str) -> str:
        """Validate element name."""
        if not v.strip():
            raise ValueError('Element name cannot be empty')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate and normalize tags."""
        return [tag.lower().strip() for tag in v if tag.strip()]
    
    @validator('task_type')
    def validate_task_type_compatibility(cls, v: TaskType, values: Dict[str, Any]) -> TaskType:
        """Validate that task type is compatible with tenant type."""
        if 'tenant_type' in values:
            from models.enums import TENANT_TASK_MAPPING
            expected_task_type = TENANT_TASK_MAPPING.get(values['tenant_type'])
            if expected_task_type and v != expected_task_type:
                # Allow override but log warning
                pass
        return v
    
    def add_execution(self, execution_id: str) -> None:
        """Add an execution record to the history."""
        if execution_id not in self.execution_history:
            self.execution_history.append(execution_id)
            self.update_timestamp()
    
    def update_usage_statistics(self, key: str, value: Any) -> None:
        """Update element usage statistics."""
        self.usage_statistics[key] = value
        self.update_timestamp()
    
    def increment_usage_count(self) -> None:
        """Increment the usage count for this element."""
        current_count = self.usage_statistics.get('usage_count', 0)
        self.usage_statistics['usage_count'] = current_count + 1
        self.usage_statistics['last_used'] = datetime.utcnow().isoformat()
        self.update_timestamp()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the element."""
        normalized_tag = tag.lower().strip()
        if normalized_tag and normalized_tag not in self.tags:
            self.tags.append(normalized_tag)
            self.update_timestamp()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the element."""
        normalized_tag = tag.lower().strip()
        if normalized_tag in self.tags:
            self.tags.remove(normalized_tag)
            self.update_timestamp()
    
    def update_template_version(self, new_version: str, changelog_entry: str) -> None:
        """Update template version with changelog entry."""
        self.template.version = new_version
        self.template.changelog.append(f"{new_version}: {changelog_entry}")
        self.update_timestamp()
    
    def is_ready_for_execution(self) -> bool:
        """Check if element is ready for execution."""
        return self.status == ElementStatus.ACTIVE and bool(self.template.content)
    
    def get_execution_count(self) -> int:
        """Get the total number of executions for this element."""
        return len(self.execution_history)
    
    def set_from_template(self, template_id: str, batch_id: Optional[str] = None) -> None:
        """Mark this element as created from a template."""
        self.is_default_element = True
        self.template_id = template_id
        self.insertion_batch_id = batch_id
        self.update_timestamp()
    
    def has_generation_prompt(self) -> bool:
        """Check if element has a generation prompt."""
        return bool(self.template.generation_prompt and self.template.generation_prompt.strip())
    
    def has_retrieval_prompt(self) -> bool:
        """Check if element has a retrieval prompt."""
        return bool(self.template.retrieval_prompt and self.template.retrieval_prompt.strip())
    
    def update_generation_prompt(self, prompt: str) -> None:
        """Update the generation prompt."""
        self.template.generation_prompt = prompt.strip()
        self.update_timestamp()
    
    def update_retrieval_prompt(self, prompt: str) -> None:
        """Update the retrieval prompt."""
        self.template.retrieval_prompt = prompt.strip()
        self.update_timestamp()
    
    def get_effective_prompt(self, use_generation: bool = True) -> str:
        """Get the effective prompt for execution."""
        if use_generation and self.has_generation_prompt():
            return self.template.generation_prompt
        elif self.has_retrieval_prompt():
            return self.template.retrieval_prompt
        else:
            return self.template.content
    
    def is_script_inserted(self) -> bool:
        """Check if this element was inserted by a script."""
        return bool(self.insertion_batch_id)
    
    def get_element_summary(self) -> Dict[str, Any]:
        """Get a summary of element information for display."""
        return {
            "id": str(self.id),
            "name": self.name,
            "project_id": self.project_id,
            "tenant_type": self.tenant_type.value,
            "element_type": self.element_type.value,
            "status": self.status.value,
            "is_default_element": self.is_default_element,
            "template_id": self.template_id,
            "insertion_batch_id": self.insertion_batch_id,
            "has_generation_prompt": self.has_generation_prompt(),
            "has_retrieval_prompt": self.has_retrieval_prompt(),
            "usage_count": self.usage_statistics.get('usage_count', 0),
            "execution_count": self.get_execution_count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    class Settings:
        name = "elements"
        indexes = [
            "project_id",
            "owner_id",
            "tenant_type",
            "task_type",
            "element_type",
            "status",
            "tags",
            "name",
            "created_at",
            "updated_at",
            "is_deleted",
            # New indexes for template tracking
            "is_default_element",
            "template_id",
            "insertion_batch_id",
            # Compound indexes
            ("project_id", "is_default_element"),
            ("template_id", "project_id"),
            ("insertion_batch_id", "tenant_type")
        ] 