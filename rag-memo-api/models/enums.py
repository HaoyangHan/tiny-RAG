"""
Enums for TinyRAG v1.4 models.

This module contains all enumeration types used across the TinyRAG API,
following the tenant-based architecture design.
"""

from enum import Enum
from typing import Dict


class TenantType(str, Enum):
    """
    Tenant types defining different task categories.
    
    Each tenant type corresponds to a specific domain and task approach,
    enabling specialized workflows and processing pipelines.
    """
    
    HR = "hr"                          # Human Resource tasks
    CODING = "coding"                  # Coding-related tasks  
    FINANCIAL_REPORT = "financial_report"  # Financial analysis
    DEEP_RESEARCH = "deep_research"    # Research tasks
    QA_GENERATION = "qa_generation"    # Question & Answer generation
    RAW_RAG = "raw_rag"               # Raw RAG without specific domain


class TaskType(str, Enum):
    """
    Task types defining the processing approach.
    
    Determines the execution strategy and framework used for
    content generation and processing.
    """
    
    RAG = "rag"                       # Retrieval Augmented Generation
    MCP = "mcp"                       # Model Context Protocol
    AGENTIC_WORKFLOW = "agentic_workflow"  # Multi-agent workflows
    LLM = "llm"                       # Direct LLM interaction


class ProjectStatus(str, Enum):
    """Project lifecycle status enumeration."""
    
    ACTIVE = "active"                 # Project is active and usable
    INACTIVE = "inactive"             # Project is inactive but preserved
    ARCHIVED = "archived"             # Project is archived
    DELETED = "deleted"               # Project marked for deletion


class VisibilityType(str, Enum):
    """Project visibility and access control."""
    
    PRIVATE = "private"               # Only owner can access
    SHARED = "shared"                 # Owner + collaborators can access
    PUBLIC = "public"                 # Anyone can view (read-only)


class ElementType(str, Enum):
    """Element template type enumeration."""
    
    PROMPT_TEMPLATE = "prompt_template"     # LLM prompt templates
    MCP_CONFIG = "mcp_config"              # Model Context Protocol config
    AGENTIC_TOOL = "agentic_tool"          # Agentic workflow tools
    RAG_CONFIG = "rag_config"              # RAG-specific configuration


class ElementStatus(str, Enum):
    """Element lifecycle status."""
    
    DRAFT = "draft"                   # Element is in draft state
    ACTIVE = "active"                 # Element is active and ready
    DEPRECATED = "deprecated"         # Element is deprecated
    ARCHIVED = "archived"             # Element is archived


class GenerationStatus(str, Enum):
    """Generation task status enumeration."""
    
    PENDING = "pending"               # Generation task is pending
    PROCESSING = "processing"         # Generation is in progress
    COMPLETED = "completed"           # Generation completed successfully
    FAILED = "failed"                 # Generation failed
    CANCELLED = "cancelled"           # Generation was cancelled


class EvaluationStatus(str, Enum):
    """Evaluation task status enumeration."""
    
    PENDING = "pending"               # Evaluation is pending
    PROCESSING = "processing"         # Evaluation in progress
    COMPLETED = "completed"           # Evaluation completed
    FAILED = "failed"                 # Evaluation failed


class DocumentStatus(str, Enum):
    """Document processing status enumeration."""
    
    UPLOADING = "uploading"           # Document is being uploaded
    PROCESSING = "processing"         # Document is being processed
    COMPLETED = "completed"           # Document processing completed
    FAILED = "failed"                 # Document processing failed
    ARCHIVED = "archived"             # Document is archived


# Tenant to Task Type Mapping
TENANT_TASK_MAPPING: Dict[TenantType, TaskType] = {
    TenantType.HR: TaskType.RAG,
    TenantType.CODING: TaskType.MCP,
    TenantType.FINANCIAL_REPORT: TaskType.AGENTIC_WORKFLOW,
    TenantType.DEEP_RESEARCH: TaskType.AGENTIC_WORKFLOW,
    TenantType.QA_GENERATION: TaskType.RAG,
    TenantType.RAW_RAG: TaskType.LLM,
}


def get_default_task_type(tenant_type: TenantType) -> TaskType:
    """
    Get the default task type for a given tenant type.
    
    Args:
        tenant_type: The tenant type to get task type for
        
    Returns:
        TaskType: The corresponding task type
        
    Raises:
        ValueError: If tenant type is not mapped
    """
    if tenant_type not in TENANT_TASK_MAPPING:
        raise ValueError(f"No task type mapping found for tenant type: {tenant_type}")
    
    return TENANT_TASK_MAPPING[tenant_type] 