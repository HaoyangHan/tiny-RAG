"""
Element model for TinyRAG v1.4.

This module contains the Element model which serves as containers for
prompt templates, MCP configurations, or Agentic tools within projects.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import Field, validator
from models.base import BaseDocument
from models.enums import TenantType, TaskType, ElementType, ElementStatus, GenerationStatus


class ElementTemplate(BaseDocument):
    """
    Element template content and configuration.
    
    Contains the actual element template content, variables, and execution
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
    
    # variables: List[str] = Field(
    #     default_factory=list,
    #     description="Template variables that can be substituted"
    # )  # REMOVED: Simplified to additional_instructions approach
    
    additional_instructions_template: Optional[str] = Field(
        None,
        description="Optional template text for additional user instructions"
    )
    
    # Execution parameters
    execution_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Execution-specific configuration parameters"
    )
    
    # Version control
    version: str = Field(
        default="1.0.0",
        description="Template version"
    )


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
        tags: Searchable tags for element discovery
        owner_id: User ID of element owner
        is_default_element: Whether created from template vs user-created
        template_id: Source template ID if created from template
        insertion_batch_id: Batch ID for script-inserted elements
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
    project_id: str = Field(
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
    template: ElementTemplate = Field(
        description="Template content and configuration"
    )
    
    # Source and Template Tracking (Essential for v1.4.2)
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
    
    # Searchability
    tags: List[str] = Field(
        default_factory=list,
        max_items=20,
        description="Searchable tags for element discovery"
    )
    
    # Ownership
    owner_id: str = Field(
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
        """Validate task type compatibility with tenant type."""
        # Basic validation - can be extended based on business rules
        # All element types are now supported by all tenants
        return v
    
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
    
    def update_template_version(self, new_version: str) -> None:
        """Update template version."""
        self.template.version = new_version
        self.update_timestamp()
    
    def is_ready_for_execution(self) -> bool:
        """Check if element is ready for execution."""
        return self.status == ElementStatus.ACTIVE and bool(self.template.content.strip())
    
    def set_from_template(self, template_id: str, batch_id: Optional[str] = None) -> None:
        """Mark element as created from a template."""
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
        """Check if element was inserted by a script."""
        return bool(self.insertion_batch_id)
    
    def get_element_summary(self) -> Dict[str, Any]:
        """Get a summary of element information."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "project_id": self.project_id,
            "tenant_type": self.tenant_type.value,
            "task_type": self.task_type.value,
            "element_type": self.element_type.value,
            "status": self.status.value,
            "tags": self.tags,
            "template_version": self.template.version,
            "has_generation_prompt": self.has_generation_prompt(),
            "has_retrieval_prompt": self.has_retrieval_prompt(),
            "is_default_element": self.is_default_element,
            "template_id": self.template_id,
            "is_script_inserted": self.is_script_inserted(),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    async def get_execution_count(self) -> int:
        """Get the number of executions for this element."""
        try:
            # Import here to avoid circular imports
            from models.element_generation import ElementGeneration
            
            # Count all successful executions for this element
            count = await ElementGeneration.find({
                "element_id": str(self.id),
                "status": {"$in": [
                    GenerationStatus.COMPLETED.value,
                    GenerationStatus.EVALUATED.value
                ]}
            }).count()
            
            return count
        except Exception:
            # Fallback to 0 if there's any error
            return 0
    
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for this element."""
        try:
            # Import here to avoid circular imports
            from models.element_generation import ElementGeneration
            
            # Get all executions for this element
            executions = await ElementGeneration.find({
                "element_id": str(self.id)
            }).to_list()
            
            if not executions:
                return {
                    "execution_count": 0,
                    "last_executed": None,
                    "average_execution_time": 0,
                    "success_rate": 0.0,
                    "total_tokens_used": 0,
                    "average_cost": 0.0
                }
            
            # Calculate statistics
            total_executions = len(executions)
            successful_executions = [
                ex for ex in executions 
                if ex.status in [GenerationStatus.COMPLETED, GenerationStatus.EVALUATED]
            ]
            
            success_rate = len(successful_executions) / total_executions if total_executions > 0 else 0.0
            
            # Calculate average execution time from successful executions
            execution_times = []
            total_tokens = 0
            total_cost = 0.0
            last_executed = None
            
            for execution in successful_executions:
                if execution.metrics and execution.metrics.generation_time_ms:
                    execution_times.append(execution.metrics.generation_time_ms)
                
                if execution.metrics:
                    total_tokens += execution.metrics.total_tokens
                    if execution.metrics.estimated_cost:
                        total_cost += execution.metrics.estimated_cost
                
                # Track the most recent execution
                if not last_executed or execution.created_at > last_executed:
                    last_executed = execution.created_at
            
            average_execution_time = (
                sum(execution_times) / len(execution_times) 
                if execution_times else 0
            )
            
            average_cost = total_cost / len(successful_executions) if successful_executions else 0.0
            
            return {
                "execution_count": total_executions,
                "successful_executions": len(successful_executions),
                "last_executed": last_executed.isoformat() if last_executed else None,
                "average_execution_time": round(average_execution_time, 2),
                "success_rate": round(success_rate, 3),
                "total_tokens_used": total_tokens,
                "average_cost": round(average_cost, 4)
            }
            
        except Exception:
            # Fallback to basic statistics if there's any error
            return {
                "execution_count": 0,
                "last_executed": None,
                "average_execution_time": 0,
                "success_rate": 0.0,
                "total_tokens_used": 0,
                "average_cost": 0.0
            }
    
    class Settings:
        name = "elements"
        indexes = [
            [("project_id", 1)],
            [("tenant_type", 1)],
            [("element_type", 1)],
            [("status", 1)],
            [("owner_id", 1)],
            [("tags", 1)],
            [("is_default_element", 1)],
            [("template_id", 1)],
            [("insertion_batch_id", 1)],
            [("project_id", 1), ("name", 1)],  # Unique per project
            [("project_id", 1), ("element_type", 1)],
            [("created_at", -1)],
            [("updated_at", -1)]
        ] 