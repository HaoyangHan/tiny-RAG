"""
Base Element Template Inserter for TinyRAG v1.4.2 Element Management System.

This module provides the BaseElementTemplateInserter abstract class for implementing
tenant-specific element template insertion scripts with MongoDB integration.
"""

import asyncio
import logging
import logging.config
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

import motor.motor_asyncio
from beanie import init_beanie
from bson import ObjectId

# Import models - using standalone ElementTemplate for provisioning
from models.element_template import ElementTemplate as StandaloneElementTemplate
from models.element import Element  # Keep for compatibility
from models.enums import TenantType, TaskType, ElementType, ElementStatus
from models.project import Project
from database import get_database_url

# Import configuration
from .config import (
    DATABASE_NAME, DEFAULT_USER_ID, DEFAULT_PROJECT_IDS,
    DEFAULT_LLM_CONFIG, DRY_RUN, CHECK_DUPLICATES, COMMON_TAGS,
    TENANT_TAG_PREFIXES, LOGGING_CONFIG
)

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class BaseElementTemplateInserter(ABC):
    """
    Abstract base class for tenant-specific element template insertion.
    
    Creates standalone element templates that can be automatically provisioned
    to new projects during creation.
    """
    
    def __init__(self, tenant_type: TenantType, created_by: Optional[str] = None):
        """
        Initialize the element template inserter.
        
        Args:
            tenant_type: The tenant type for this inserter
            created_by: User ID who created the templates
        """
        self.tenant_type = tenant_type
        self.created_by = created_by or DEFAULT_USER_ID
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database = None
        self.inserted_templates: List[str] = []  # Track inserted template IDs
    
    async def connect_to_database(self) -> None:
        """Connect to MongoDB and initialize Beanie."""
        try:
            logger.info(f"Connecting to MongoDB at {get_database_url()}")
            self.client = motor.motor_asyncio.AsyncIOMotorClient(get_database_url())
            self.database = self.client[DATABASE_NAME]
            
            # Initialize Beanie with required models
            await init_beanie(
                database=self.database,
                document_models=[StandaloneElementTemplate, Element, Project]
            )
            logger.info("Successfully connected to database")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    async def close_database_connection(self) -> None:
        """Close the database connection."""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")
    
    async def check_duplicate_template(self, name: str) -> bool:
        """
        Check if a template with the given name already exists for this tenant.
        
        Args:
            name: Template name to check
            
        Returns:
            bool: True if duplicate exists, False otherwise
        """
        if not CHECK_DUPLICATES:
            return False
            
        try:
            existing = await StandaloneElementTemplate.find_one({
                "name": name,
                "tenant_type": self.tenant_type
            })
            
            if existing:
                logger.warning(f"Template '{name}' already exists for tenant {self.tenant_type}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking for duplicate template '{name}': {str(e)}")
            return False
    
    def create_element_tags(self, specific_tags: List[str]) -> List[str]:
        """
        Create standardized tags for a template.
        
        Args:
            specific_tags: Template-specific tags
            
        Returns:
            List[str]: Combined tags list
        """
        prefix = TENANT_TAG_PREFIXES.get(self.tenant_type, "misc")
        
        tags = COMMON_TAGS.copy()
        tags.append(prefix)
        tags.extend(specific_tags)
        
        # Remove duplicates and normalize
        return list(set(tag.lower().strip() for tag in tags if tag.strip()))
    
    async def insert_template(self, template_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a single element template into the database.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            Optional[str]: Inserted template ID if successful
        """
        try:
            # Check for duplicates
            if await self.check_duplicate_template(template_data["name"]):
                logger.info(f"Skipping duplicate template: {template_data['name']}")
                return None
            
            # Create standalone element template instance
            template = StandaloneElementTemplate(
                name=template_data["name"],
                description=template_data.get("description", ""),
                tenant_type=self.tenant_type,
                task_type=template_data["task_type"],
                element_type=template_data["element_type"],
                generation_prompt=template_data["generation_prompt"],
                retrieval_prompt=template_data.get("retrieval_prompt"),
                variables=template_data.get("variables", []),
                execution_config=template_data.get("execution_config", DEFAULT_LLM_CONFIG.copy()),
                is_system_default=template_data.get("is_system_default", True),
                version=template_data.get("version", "1.0.0"),
                tags=template_data.get("tags", []),
                status=ElementStatus.ACTIVE,
                created_by=self.created_by
            )
            
            # Validate template
            template.dict()  # This will raise validation errors if any
            
            if DRY_RUN:
                logger.info(f"[DRY RUN] Would insert template: {template.name}")
                return f"dry-run-{template.name}"
            
            # Insert template
            await template.insert()
            template_id = str(template.id)
            self.inserted_templates.append(template_id)
            
            logger.info(f"✅ Inserted template: {template.name} (ID: {template_id})")
            return template_id
            
        except Exception as e:
            logger.error(f"❌ Failed to insert template {template_data.get('name', 'unknown')}: {str(e)}")
            return None
    
    async def insert_templates(self, templates_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Insert multiple element templates and return summary.
        
        Args:
            templates_data: List of template data dictionaries
            
        Returns:
            Dict[str, Any]: Insertion summary
        """
        logger.info(f"Starting insertion of {len(templates_data)} templates for tenant {self.tenant_type}")
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for template_data in templates_data:
            result = await self.insert_template(template_data)
            
            if result is None:
                skipped_count += 1
            elif result.startswith("dry-run-"):
                success_count += 1  # Count dry runs as successes
            else:
                success_count += 1
        
        failed_count = len(templates_data) - success_count - skipped_count
        
        summary = {
            "tenant_type": self.tenant_type.value,
            "total_templates": len(templates_data),
            "successful": success_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "inserted_ids": self.inserted_templates,
            "dry_run": DRY_RUN
        }
        
        logger.info(
            f"Insertion complete - Success: {success_count}, "
            f"Failed: {failed_count}, Skipped: {skipped_count}"
        )
        
        return summary
    
    @abstractmethod
    def get_templates_data(self) -> List[Dict[str, Any]]:
        """
        Get the list of element templates to insert for this tenant.
        
        This method must be implemented by each tenant-specific subclass.
        
        Returns:
            List[Dict[str, Any]]: List of template data dictionaries
        """
        pass
    
    async def run(self) -> Dict[str, Any]:
        """
        Main execution method to run the template insertion process.
        
        Returns:
            Dict[str, Any]: Insertion summary
        """
        try:
            # Connect to database
            await self.connect_to_database()
            
            # Get templates data
            templates_data = self.get_templates_data()
            
            if not templates_data:
                logger.warning("No templates data provided")
                return {"error": "No templates data provided"}
            
            # Insert templates
            summary = await self.insert_templates(templates_data)
            
            return summary
            
        except Exception as e:
            logger.error(f"Template insertion failed: {str(e)}")
            return {"error": str(e)}
            
        finally:
            await self.close_database_connection()


# Keep the old class for backward compatibility but deprecate it
class BaseElementInserter(BaseElementTemplateInserter):
    """
    Deprecated: Use BaseElementTemplateInserter instead.
    
    This class is kept for backward compatibility but should not be used
    for new implementations.
    """
    
    def __init__(self, tenant_type: TenantType, project_id: Optional[str] = None):
        logger.warning(
            "BaseElementInserter is deprecated. Use BaseElementTemplateInserter instead."
        )
        super().__init__(tenant_type, DEFAULT_USER_ID)
        self.project_id = project_id or DEFAULT_PROJECT_IDS.get(tenant_type)
    
    def get_elements_data(self) -> List[Dict[str, Any]]:
        """Deprecated method - use get_templates_data instead."""
        return self.get_templates_data()


async def run_template_inserter(inserter_class, tenant_type: TenantType, created_by: Optional[str] = None):
    """
    Utility function to run a template inserter class.
    
    Args:
        inserter_class: The inserter class to instantiate and run
        tenant_type: Tenant type for the inserter
        created_by: User ID who created the templates
    
    Returns:
        Dict[str, Any]: Insertion summary
    """
    inserter = inserter_class(tenant_type, created_by)
    return await inserter.run()


# Backward compatibility function
async def run_inserter(inserter_class, tenant_type: TenantType, project_id: Optional[str] = None):
    """
    Deprecated: Use run_template_inserter instead.
    """
    logger.warning("run_inserter is deprecated. Use run_template_inserter instead.")
    return await run_template_inserter(inserter_class, tenant_type, DEFAULT_USER_ID) 