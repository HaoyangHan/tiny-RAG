"""
TenantConfiguration model for TinyRAG v1.4.

This module contains the TenantConfiguration model which stores configuration
settings and metadata for each tenant type in the system.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from beanie import Indexed
from pydantic import Field, validator
from models.base import BaseDocument
from models.enums import TenantType, TaskType, ElementType


class TenantConfiguration(BaseDocument):
    """
    Configuration model for tenant-specific settings and metadata.
    
    Stores configuration settings, capabilities, and metadata for each
    tenant type in the TinyRAG system. Each tenant type has one
    configuration document that defines its behavior and capabilities.
    
    Attributes:
        tenant_type: Unique tenant identifier
        display_name: Human-readable tenant name
        description: Detailed tenant description
        default_task_type: Default task processing approach
        default_llm_config: Default LLM configuration settings
        auto_provision_templates: Whether to auto-provision templates to new projects
        template_count: Current number of available templates
        allowed_element_types: Element types supported by this tenant
        custom_settings: Tenant-specific custom settings
        is_active: Whether tenant is currently active
        created_by: User ID of configuration creator
        feature_flags: Tenant-specific feature enablement flags
        analytics: Usage and performance analytics
    """
    
    # Basic Information
    tenant_type: Indexed(TenantType) = Field(
        description="Unique tenant identifier",
        unique=True
    )
    display_name: str = Field(
        max_length=100,
        description="Human-readable tenant name"
    )
    description: str = Field(
        max_length=500,
        description="Detailed tenant description"
    )
    
    # Default Configuration
    default_task_type: TaskType = Field(
        description="Default task processing approach for this tenant"
    )
    default_llm_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default LLM configuration settings"
    )
    
    # Template Management
    auto_provision_templates: bool = Field(
        default=True,
        description="Whether to automatically provision templates to new projects"
    )
    template_count: int = Field(
        default=0,
        ge=0,
        description="Current number of available templates for this tenant"
    )
    
    # Capabilities and Restrictions
    allowed_element_types: List[ElementType] = Field(
        default_factory=list,
        description="Element types supported by this tenant"
    )
    max_elements_per_project: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum number of elements allowed per project"
    )
    max_template_size_kb: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum template size in kilobytes"
    )
    
    # Customization
    custom_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tenant-specific custom settings and configurations"
    )
    
    # Feature Flags
    feature_flags: Dict[str, bool] = Field(
        default_factory=dict,
        description="Tenant-specific feature enablement flags"
    )
    
    # Status and Lifecycle
    is_active: bool = Field(
        default=True,
        description="Whether tenant is currently active and available"
    )
    
    # Ownership and Management
    created_by: Indexed(str) = Field(
        description="User ID of configuration creator"
    )
    last_modified_by: Optional[str] = Field(
        None,
        description="User ID of last configuration modifier"
    )
    
    # Usage Analytics
    analytics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Usage and performance analytics for this tenant"
    )
    
    # Project Statistics
    project_count: int = Field(
        default=0,
        ge=0,
        description="Number of projects using this tenant type"
    )
    element_count: int = Field(
        default=0,
        ge=0,
        description="Total number of elements across all projects"
    )
    
    @validator('display_name')
    def validate_display_name(cls, v: str) -> str:
        """Validate display name."""
        if not v.strip():
            raise ValueError('Display name cannot be empty')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v: str) -> str:
        """Validate description."""
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()
    
    @validator('allowed_element_types')
    def validate_element_types(cls, v: List[ElementType]) -> List[ElementType]:
        """Validate allowed element types."""
        if not v:
            # Default to all element types if none specified
            return list(ElementType)
        return list(set(v))  # Remove duplicates
    
    @validator('default_llm_config')
    def validate_llm_config(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate LLM configuration."""
        # Set defaults if not provided
        defaults = {
            "temperature": 0.7,
            "max_tokens": 2000,
            "model": "gpt-4o-mini"
        }
        
        # Merge with defaults
        config = defaults.copy()
        config.update(v)
        
        # Validate temperature
        if not 0.0 <= config.get("temperature", 0.7) <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        
        # Validate max_tokens
        if not 1 <= config.get("max_tokens", 2000) <= 8192:
            raise ValueError("Max tokens must be between 1 and 8192")
        
        return config
    
    def increment_project_count(self) -> None:
        """Increment the project count for this tenant."""
        self.project_count += 1
        self.update_timestamp()
    
    def decrement_project_count(self) -> None:
        """Decrement the project count for this tenant."""
        if self.project_count > 0:
            self.project_count -= 1
        self.update_timestamp()
    
    def increment_element_count(self, count: int = 1) -> None:
        """Increment the element count for this tenant."""
        self.element_count += count
        self.update_timestamp()
    
    def decrement_element_count(self, count: int = 1) -> None:
        """Decrement the element count for this tenant."""
        self.element_count = max(0, self.element_count - count)
        self.update_timestamp()
    
    def update_template_count(self, count: int) -> None:
        """Update the template count for this tenant."""
        self.template_count = max(0, count)
        self.update_timestamp()
    
    def is_element_type_allowed(self, element_type: ElementType) -> bool:
        """Check if an element type is allowed for this tenant."""
        return element_type in self.allowed_element_types
    
    def can_create_element(self, project_element_count: int) -> bool:
        """Check if a new element can be created based on limits."""
        if self.max_elements_per_project is None:
            return True
        return project_element_count < self.max_elements_per_project
    
    def enable_feature(self, feature_name: str) -> None:
        """Enable a feature flag for this tenant."""
        self.feature_flags[feature_name] = True
        self.update_timestamp()
    
    def disable_feature(self, feature_name: str) -> None:
        """Disable a feature flag for this tenant."""
        self.feature_flags[feature_name] = False
        self.update_timestamp()
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled for this tenant."""
        return self.feature_flags.get(feature_name, False)
    
    def update_analytics(self, key: str, value: Any) -> None:
        """Update analytics data for this tenant."""
        self.analytics[key] = value
        self.update_timestamp()
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get a summary of tenant analytics."""
        return {
            "tenant_type": self.tenant_type.value,
            "project_count": self.project_count,
            "element_count": self.element_count,
            "template_count": self.template_count,
            "avg_elements_per_project": round(
                self.element_count / max(1, self.project_count), 2
            ),
            "is_active": self.is_active,
            "custom_analytics": self.analytics
        }
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of tenant configuration for display."""
        return {
            "tenant_type": self.tenant_type.value,
            "display_name": self.display_name,
            "description": self.description,
            "default_task_type": self.default_task_type.value,
            "auto_provision_templates": self.auto_provision_templates,
            "allowed_element_types": [et.value for et in self.allowed_element_types],
            "max_elements_per_project": self.max_elements_per_project,
            "is_active": self.is_active,
            "project_count": self.project_count,
            "element_count": self.element_count,
            "template_count": self.template_count,
            "feature_flags": self.feature_flags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    async def get_by_tenant_type(cls, tenant_type: TenantType) -> Optional['TenantConfiguration']:
        """Get configuration by tenant type."""
        return await cls.find_one({"tenant_type": tenant_type})
    
    @classmethod
    async def get_active_tenants(cls) -> List['TenantConfiguration']:
        """Get all active tenant configurations."""
        return await cls.find({"is_active": True}).to_list()
    
    @classmethod
    async def initialize_default_tenants(cls, created_by: str) -> List['TenantConfiguration']:
        """Initialize default tenant configurations if they don't exist."""
        from models.enums import TENANT_TASK_MAPPING
        
        default_configs = []
        
        for tenant_type, task_type in TENANT_TASK_MAPPING.items():
            existing = await cls.get_by_tenant_type(tenant_type)
            if not existing:
                # Create default configuration
                config = cls(
                    tenant_type=tenant_type,
                    display_name=tenant_type.value.replace('_', ' ').title(),
                    description=f"Default configuration for {tenant_type.value.replace('_', ' ').title()} tenant type",
                    default_task_type=task_type,
                    created_by=created_by,
                    allowed_element_types=list(ElementType),  # Allow all by default
                    feature_flags={
                        "auto_provision": True,
                        "retrieval_prompt_generation": True,
                        "analytics_tracking": True
                    }
                )
                await config.insert()
                default_configs.append(config)
        
        return default_configs
    
    class Settings:
        name = "tenant_configurations"
        indexes = [
            "tenant_type",
            "is_active",
            "created_by",
            "last_modified_by",
            "project_count",
            "element_count",
            "template_count"
        ] 