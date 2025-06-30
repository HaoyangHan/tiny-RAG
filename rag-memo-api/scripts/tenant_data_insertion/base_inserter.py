"""
Base Element Inserter for TinyRAG v1.4.2 Element Management System.

This module provides the BaseElementInserter abstract class for implementing
tenant-specific element insertion scripts with MongoDB integration.
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

# Import models
from models.element import Element, ElementTemplate
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


class BaseElementInserter(ABC):
    """
    Abstract base class for tenant-specific element insertion.
    
    Provides common functionality for connecting to MongoDB, validating data,
    and inserting elements with proper error handling and logging.
    """
    
    def __init__(self, tenant_type: TenantType, project_id: Optional[str] = None):
        """
        Initialize the element inserter.
        
        Args:
            tenant_type: The tenant type for this inserter
            project_id: Optional project ID, uses default if not provided
        """
        self.tenant_type = tenant_type
        self.project_id = project_id or DEFAULT_PROJECT_IDS.get(tenant_type)
        self.user_id = DEFAULT_USER_ID
        self.client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
        self.database = None
        self.inserted_elements: List[str] = []  # Track inserted element IDs
        
        if not self.project_id:
            raise ValueError(f"No project ID configured for tenant type: {tenant_type}")
    
    async def connect_to_database(self) -> None:
        """Connect to MongoDB and initialize Beanie."""
        try:
            logger.info(f"Connecting to MongoDB at {get_database_url()}")
            self.client = motor.motor_asyncio.AsyncIOMotorClient(get_database_url())
            self.database = self.client[DATABASE_NAME]
            
            # Initialize Beanie with required models
            await init_beanie(
                database=self.database,
                document_models=[Element, ElementTemplate, Project]
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
    
    async def validate_project_exists(self) -> bool:
        """
        Validate that the project exists and is accessible.
        
        Returns:
            bool: True if project exists and is valid
        """
        try:
            # Convert string ID to ObjectId if needed
            project_oid = ObjectId(self.project_id) if isinstance(self.project_id, str) else self.project_id
            project = await Project.get(project_oid)
            
            if not project:
                logger.error(f"Project {self.project_id} not found")
                return False
                
            if project.tenant_type != self.tenant_type:
                logger.warning(
                    f"Project {self.project_id} has tenant type {project.tenant_type}, "
                    f"expected {self.tenant_type}"
                )
                
            logger.info(f"Project '{project.name}' validated for tenant {self.tenant_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating project {self.project_id}: {str(e)}")
            return False
    
    async def check_duplicate_element(self, name: str) -> bool:
        """
        Check if an element with the given name already exists in the project.
        
        Args:
            name: Element name to check
            
        Returns:
            bool: True if duplicate exists, False otherwise
        """
        if not CHECK_DUPLICATES:
            return False
            
        try:
            existing = await Element.find_one({
                "name": name,
                "project_id": self.project_id,
                "is_deleted": False
            })
            
            if existing:
                logger.warning(f"Element '{name}' already exists in project {self.project_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking for duplicate element '{name}': {str(e)}")
            return False
    
    def create_element_template(
        self,
        content: str,
        generation_prompt: Optional[str] = None,
        retrieval_prompt: Optional[str] = None,
        variables: List[str] = None,
        execution_config: Optional[Dict[str, Any]] = None,
        version: str = "1.0.0"
    ) -> ElementTemplate:
        """
        Create an ElementTemplate instance.
        
        Args:
            content: Legacy template content
            generation_prompt: Full detailed prompt for generation
            retrieval_prompt: Summarized prompt for retrieval
            variables: Template variables
            execution_config: Execution configuration
            version: Template version
            
        Returns:
            ElementTemplate: Created template instance
        """
        config = execution_config or DEFAULT_LLM_CONFIG.copy()
        vars_list = variables or []
        
        return ElementTemplate(
            content=content,
            generation_prompt=generation_prompt,
            retrieval_prompt=retrieval_prompt,
            variables=vars_list,
            execution_config=config,
            version=version
        )
    
    def create_element_tags(self, specific_tags: List[str]) -> List[str]:
        """
        Create standardized tags for an element.
        
        Args:
            specific_tags: Element-specific tags
            
        Returns:
            List[str]: Combined tags list
        """
        prefix = TENANT_TAG_PREFIXES.get(self.tenant_type, "misc")
        
        tags = COMMON_TAGS.copy()
        tags.append(prefix)
        tags.extend(specific_tags)
        
        # Remove duplicates and normalize
        return list(set(tag.lower().strip() for tag in tags if tag.strip()))
    
    async def insert_element(self, element_data: Dict[str, Any]) -> Optional[str]:
        """
        Insert a single element into the database.
        
        Args:
            element_data: Element data dictionary
            
        Returns:
            Optional[str]: Inserted element ID if successful
        """
        try:
            # Check for duplicates
            if await self.check_duplicate_element(element_data["name"]):
                logger.info(f"Skipping duplicate element: {element_data['name']}")
                return None
            
            # Create element instance
            element = Element(
                name=element_data["name"],
                description=element_data.get("description"),
                project_id=self.project_id,
                tenant_type=self.tenant_type,
                task_type=element_data["task_type"],
                element_type=element_data["element_type"],
                status=element_data.get("status", ElementStatus.ACTIVE),
                template=element_data["template"],
                tags=element_data.get("tags", []),
                owner_id=self.user_id
            )
            
            # Validate element
            element.dict()  # This will raise validation errors if any
            
            if DRY_RUN:
                logger.info(f"[DRY RUN] Would insert element: {element.name}")
                return f"dry-run-{element.name}"
            
            # Insert element
            await element.insert()
            element_id = str(element.id)
            self.inserted_elements.append(element_id)
            
            logger.info(f"✅ Inserted element: {element.name} (ID: {element_id})")
            return element_id
            
        except Exception as e:
            logger.error(f"❌ Failed to insert element {element_data.get('name', 'unknown')}: {str(e)}")
            return None
    
    async def insert_elements(self, elements_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Insert multiple elements and return summary.
        
        Args:
            elements_data: List of element data dictionaries
            
        Returns:
            Dict[str, Any]: Insertion summary
        """
        logger.info(f"Starting insertion of {len(elements_data)} elements for tenant {self.tenant_type}")
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for element_data in elements_data:
            result = await self.insert_element(element_data)
            
            if result is None:
                skipped_count += 1
            elif result.startswith("dry-run-"):
                success_count += 1  # Count dry runs as successes
            else:
                success_count += 1
        
        failed_count = len(elements_data) - success_count - skipped_count
        
        summary = {
            "tenant_type": self.tenant_type.value,
            "total_elements": len(elements_data),
            "successful": success_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "inserted_ids": self.inserted_elements,
            "dry_run": DRY_RUN
        }
        
        logger.info(
            f"Insertion complete - Success: {success_count}, "
            f"Failed: {failed_count}, Skipped: {skipped_count}"
        )
        
        return summary
    
    @abstractmethod
    def get_elements_data(self) -> List[Dict[str, Any]]:
        """
        Get the list of elements to insert for this tenant.
        
        This method must be implemented by each tenant-specific subclass.
        
        Returns:
            List[Dict[str, Any]]: List of element data dictionaries
        """
        pass
    
    async def run(self) -> Dict[str, Any]:
        """
        Main execution method to run the element insertion process.
        
        Returns:
            Dict[str, Any]: Insertion summary
        """
        try:
            # Connect to database
            await self.connect_to_database()
            
            # Validate project
            if not await self.validate_project_exists():
                raise ValueError(f"Project validation failed for {self.project_id}")
            
            # Get elements data
            elements_data = self.get_elements_data()
            
            if not elements_data:
                logger.warning("No elements data provided")
                return {"error": "No elements data provided"}
            
            # Insert elements
            summary = await self.insert_elements(elements_data)
            
            return summary
            
        except Exception as e:
            logger.error(f"Element insertion failed: {str(e)}")
            return {"error": str(e)}
            
        finally:
            await self.close_database_connection()


async def run_inserter(inserter_class, tenant_type: TenantType, project_id: Optional[str] = None):
    """
    Utility function to run an inserter class.
    
    Args:
        inserter_class: The inserter class to instantiate and run
        tenant_type: Tenant type for the inserter
        project_id: Optional project ID
    
    Returns:
        Dict[str, Any]: Insertion summary
    """
    inserter = inserter_class(tenant_type, project_id)
    return await inserter.run() 