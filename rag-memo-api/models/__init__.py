"""
Models package for TinyRAG v1.4.

This module exports all Beanie models and related classes
for the TinyRAG API.
"""

# Base models
from .base import BaseDocument

# Enums
from .enums import (
    TenantType,
    TaskType,
    ProjectStatus,
    VisibilityType,
    ElementType,
    ElementStatus,
    GenerationStatus,
    EvaluationStatus,
    DocumentStatus,
    TENANT_TASK_MAPPING,
    get_default_task_type
)

# Core models
from .project import Project, ProjectConfiguration
from .element import Element, ElementContent, ElementExecution
from .element_template import ElementTemplate
from .tenant_configuration import TenantConfiguration
from .element_generation import (
    ElementGeneration,
    GenerationChunk,
    GenerationMetrics
)
from .evaluation import (
    Evaluation,
    EvaluationCriteria,
    EvaluationScore,
    EvaluationResult
)

# Legacy models (preserved for backward compatibility)
from .document import Document, DocumentMetadata, DocumentChunk
from .generation import Generation
from .memo import Memo

# Auth models
from auth.models import (
    User,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserRole,
    UserStatus,
    Token,
    TokenData,
    LoginRequest,
    PasswordReset,
    PasswordResetConfirm,
    APIKey,
    APIKeyCreate,
    APIKeyResponse
)

# All models list for Beanie initialization
ALL_MODELS = [
    # Core v1.4 models
    Project,
    Element,
    ElementTemplate,
    TenantConfiguration,
    ElementGeneration,
    Evaluation,
    
    # Legacy models
    Document,
    Generation,
    Memo,
    
    # Auth models
    User,
    APIKey
]

# Export groups
V14_MODELS = [Project, Element, ElementTemplate, TenantConfiguration, ElementGeneration, Evaluation]
LEGACY_MODELS = [Document, Generation, Memo]
AUTH_MODELS = [User, APIKey]

__all__ = [
    # Base
    "BaseDocument",
    
    # Enums
    "TenantType",
    "TaskType",
    "ProjectStatus",
    "VisibilityType",
    "ElementType",
    "ElementStatus",
    "GenerationStatus",
    "EvaluationStatus",
    "DocumentStatus",
    "TENANT_TASK_MAPPING",
    "get_default_task_type",
    
    # Core models
    "Project",
    "ProjectConfiguration",
    "Element",
    "ElementContent",
    "ElementExecution",
    "ElementTemplate",
    "TenantConfiguration",
    "ElementGeneration",
    "GenerationChunk",
    "GenerationMetrics",
    "Evaluation",
    "EvaluationCriteria",
    "EvaluationScore",
    "EvaluationResult",
    
    # Legacy models
    "Document",
    "DocumentMetadata",
    "DocumentChunk",
    "Generation",
    "Memo",
    
    # Auth models
    "User",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserRole",
    "UserStatus",
    "Token",
    "TokenData",
    "LoginRequest",
    "PasswordReset",
    "PasswordResetConfirm",
    "APIKey",
    "APIKeyCreate",
    "APIKeyResponse",
    
    # Model groups
    "ALL_MODELS",
    "V14_MODELS",
    "LEGACY_MODELS",
    "AUTH_MODELS"
] 