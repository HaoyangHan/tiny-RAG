"""
TenantConfiguration model for TinyRAG v1.4.

This module contains the TenantConfiguration model which stores essential
configuration settings for each tenant type in the system.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import Field, validator
from models.base import BaseDocument
from models.enums import TenantType, TaskType


class TenantConfiguration(BaseDocument):
    """
    Essential configuration model for tenant-specific settings.
    
    Stores only essential configuration settings for each
    tenant type in the TinyRAG system.
    
    Attributes:
        tenant_type: Unique tenant identifier
        display_name: Human-readable tenant name
        description: Tenant description
        default_task_type: Default task processing approach
        auto_provision_templates: Whether to auto-provision templates
        is_active: Whether tenant is currently active
        created_by: User ID of configuration creator
    """
    
    # Basic Information
    tenant_type: TenantType = Field(
        description="Unique tenant identifier",
        unique=True
    )
    display_name: str = Field(
        max_length=100,
        description="Human-readable tenant name"
    )
    description: str = Field(
        max_length=500,
        description="Tenant description"
    )
    
    # Essential Configuration
    default_task_type: TaskType = Field(
        description="Default task processing approach for this tenant"
    )
    
    # Template Management
    auto_provision_templates: bool = Field(
        default=True,
        description="Whether to automatically provision templates to new projects"
    )
    
    # Status
    is_active: bool = Field(
        default=True,
        description="Whether tenant is currently active and available"
    )
    
    # Ownership
    created_by: str = Field(
        description="User ID of configuration creator"
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
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of configuration information."""
        return {
            "tenant_type": self.tenant_type.value,
            "display_name": self.display_name,
            "description": self.description,
            "default_task_type": self.default_task_type.value,
            "auto_provision_templates": self.auto_provision_templates,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
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
        """Initialize default tenant configurations."""
        default_configs = [
            {
                "tenant_type": TenantType.HR,
                "display_name": "Human Resources",
                "description": "HR policy analysis and employee management tools",
                "default_task_type": TaskType.RAG_QA
            },
            {
                "tenant_type": TenantType.CODING,
                "display_name": "Software Development",
                "description": "Code analysis, review, and documentation tools",
                "default_task_type": TaskType.STRUCTURED_GENERATION
            },
            {
                "tenant_type": TenantType.FINANCIAL_REPORT,
                "display_name": "Financial Analysis",
                "description": "Financial statement analysis and reporting tools",
                "default_task_type": TaskType.RAG_QA
            }
        ]
        
        created_configs = []
        for config_data in default_configs:
            config_data["created_by"] = created_by
            existing = await cls.find_one({"tenant_type": config_data["tenant_type"]})
            if not existing:
                config = cls(**config_data)
                await config.save()
                created_configs.append(config)
        
        return created_configs
    
    class Settings:
        name = "tenant_configurations"
        indexes = [
            [("tenant_type", 1)],  # Unique
            [("is_active", 1)],
            [("created_by", 1)],
            [("created_at", -1)],
            [("updated_at", -1)]
        ] 