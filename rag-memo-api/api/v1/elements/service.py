"""
Element service for TinyRAG v1.4.

This module contains the business logic for element management including
CRUD operations, template management, execution tracking, and access control.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId
from beanie.operators import In, And, Or

from models import (
    Element, ElementTemplate, Project,
    ElementType, ElementStatus, TenantType, TaskType
)

logger = logging.getLogger(__name__)


class ElementService:
    """
    Service class for element management operations.
    
    Handles all business logic related to elements including creation,
    retrieval, updates, deletion, execution tracking, and template versioning.
    """
    
    async def create_element(
        self,
        name: str,
        description: Optional[str],
        project_id: str,
        element_type: ElementType,
        template_content: str,
        variables: List[str],
        execution_config: Dict[str, Any],
        tags: List[str],
        owner_id: str
    ) -> Element:
        """
        Create a new element.
        
        Args:
            name: Element name
            description: Element description
            project_id: Associated project ID
            element_type: Type of element
            template_content: Template content
            variables: Template variables
            execution_config: Execution configuration
            tags: Element tags
            owner_id: ID of the element owner
            
        Returns:
            Element: Created element instance
            
        Raises:
            ValueError: If validation fails
            Exception: If creation fails
        """
        try:
            # Verify project exists and user has access
            project = await Project.get(PydanticObjectId(project_id))
            if not project or project.is_deleted:
                raise ValueError("Project not found")
            
            if not project.is_accessible_by(owner_id):
                raise ValueError("Access denied to project")
            
            # Create template
            template = ElementTemplate(
                content=template_content,
                variables=variables,
                execution_config=execution_config,
                version="1.0.0",
                changelog=["1.0.0: Initial version"]
            )
            
            # Create element instance
            element = Element(
                name=name,
                description=description,
                project_id=project_id,
                tenant_type=project.tenant_type,
                task_type=project.get_task_type(),
                element_type=element_type,
                status=ElementStatus.DRAFT,
                template=template,
                tags=tags,
                owner_id=owner_id
            )
            
            # Save to database
            await element.insert()
            
            # Add to project
            project.add_element(str(element.id))
            await project.save()
            
            logger.info(f"Created element {element.id} for project {project_id}")
            return element
            
        except Exception as e:
            logger.error(f"Failed to create element: {str(e)}")
            raise
    
    async def get_element(self, element_id: str, user_id: str) -> Optional[Element]:
        """
        Get an element by ID with access control.
        
        Args:
            element_id: Element ID to retrieve
            user_id: ID of the requesting user
            
        Returns:
            Element: Element instance if found and accessible, None otherwise
        """
        try:
            element = await Element.get(PydanticObjectId(element_id))
            
            if not element or element.is_deleted:
                return None
            
            # Check project access
            project = await Project.get(PydanticObjectId(element.project_id))
            if not project or not project.is_accessible_by(user_id):
                return None
            
            return element
            
        except Exception as e:
            logger.error(f"Failed to get element {element_id}: {str(e)}")
            return None
    
    async def list_elements(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        project_id: Optional[str] = None,
        element_type: Optional[ElementType] = None,
        status: Optional[ElementStatus] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Element], int]:
        """
        List elements accessible to a user with filtering and pagination.
        
        Args:
            user_id: ID of the requesting user
            page: Page number (1-based)
            page_size: Number of items per page
            project_id: Filter by project ID
            element_type: Filter by element type
            status: Filter by element status
            tags: Filter by tags
            search: Search in element names and descriptions
            
        Returns:
            Tuple[List[Element], int]: List of elements and total count
        """
        try:
            # Build query conditions
            conditions = [Element.is_deleted == False]
            
            # Get accessible project IDs
            if project_id:
                # Check specific project access
                project = await Project.get(PydanticObjectId(project_id))
                if not project or not project.is_accessible_by(user_id):
                    return [], 0
                conditions.append(Element.project_id == project_id)
            else:
                # Get all accessible projects
                accessible_projects = await self._get_accessible_project_ids(user_id)
                if not accessible_projects:
                    return [], 0
                conditions.append(In(Element.project_id, accessible_projects))
            
            # Apply filters
            if element_type:
                conditions.append(Element.element_type == element_type)
            
            if status:
                conditions.append(Element.status == status)
            
            if tags:
                # Element must have at least one of the specified tags
                tag_conditions = [Element.tags.contains(tag) for tag in tags]
                conditions.append(Or(*tag_conditions))
            
            if search:
                search_conditions = [
                    Element.name.contains(search, case_insensitive=True),
                    Element.description.contains(search, case_insensitive=True)
                ]
                conditions.append(Or(*search_conditions))
            
            # Build final query
            query = Element.find(And(*conditions))
            
            # Get total count
            total_count = await query.count()
            
            # Apply pagination and sorting
            elements = await query.sort(-Element.updated_at).skip((page - 1) * page_size).limit(page_size).to_list()
            
            return elements, total_count
            
        except Exception as e:
            logger.error(f"Failed to list elements for user {user_id}: {str(e)}")
            return [], 0
    
    async def update_element(
        self,
        element_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Element]:
        """
        Update an element with access control.
        
        Args:
            element_id: Element ID to update
            user_id: ID of the requesting user
            updates: Dictionary of updates to apply
            
        Returns:
            Element: Updated element instance if successful, None otherwise
        """
        try:
            element = await Element.get(PydanticObjectId(element_id))
            
            if not element or element.is_deleted:
                return None
            
            # Check if user is owner or has project access
            project = await Project.get(PydanticObjectId(element.project_id))
            if not project or not project.is_accessible_by(user_id):
                return None
            
            # Only owner or project owner can update
            if element.owner_id != user_id and project.owner_id != user_id:
                return None
            
            # Apply updates
            template_updates = updates.pop('template', {})
            
            for field, value in updates.items():
                if hasattr(element, field):
                    setattr(element, field, value)
            
            # Update template if provided
            if template_updates:
                for field, value in template_updates.items():
                    if hasattr(element.template, field):
                        setattr(element.template, field, value)
            
            # Update timestamp
            element.update_timestamp()
            
            # Save changes
            await element.save()
            
            logger.info(f"Updated element {element_id} by user {user_id}")
            return element
            
        except Exception as e:
            logger.error(f"Failed to update element {element_id}: {str(e)}")
            return None
    
    async def delete_element(self, element_id: str, user_id: str) -> bool:
        """
        Delete an element (soft delete) with access control.
        
        Args:
            element_id: Element ID to delete
            user_id: ID of the requesting user
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            element = await Element.get(PydanticObjectId(element_id))
            
            if not element or element.is_deleted:
                return False
            
            # Check if user is owner or has project access
            project = await Project.get(PydanticObjectId(element.project_id))
            if not project or not project.is_accessible_by(user_id):
                return False
            
            # Only owner or project owner can delete
            if element.owner_id != user_id and project.owner_id != user_id:
                return False
            
            # Perform soft delete
            element.mark_deleted()
            await element.save()
            
            # Remove from project
            project.remove_element(element_id)
            await project.save()
            
            logger.info(f"Deleted element {element_id} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete element {element_id}: {str(e)}")
            return False
    
    async def execute_element(
        self,
        element_id: str,
        user_id: str,
        input_variables: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Execute an element with provided variables.
        
        Args:
            element_id: Element ID to execute
            user_id: ID of the requesting user
            input_variables: Variables for template execution
            
        Returns:
            Dict[str, Any]: Execution results if successful, None otherwise
        """
        try:
            element = await self.get_element(element_id, user_id)
            
            if not element:
                return None
            
            if not element.is_ready_for_execution():
                raise ValueError("Element is not ready for execution")
            
            # Validate required variables
            template_variables = element.template.variables or []
            missing_variables = [var for var in template_variables if var not in input_variables]
            
            if missing_variables:
                raise ValueError(f"Missing required variables: {', '.join(missing_variables)}")
            
            # Create execution record as dictionary
            execution_result = {
                "input_variables": input_variables,
                "status": "pending",
                "element_id": element_id,
                "element_name": element.name
            }
            
            start_time = datetime.utcnow()
            
            try:
                # TODO: Implement actual execution logic here
                # This would involve:
                # 1. Substitute variables in template
                # 2. Call appropriate LLM or execution engine
                # 3. Process results
                
                # For now, simulate execution with variable substitution
                template_content = element.template.content
                for var, value in input_variables.items():
                    template_content = template_content.replace(f"{{{var}}}", str(value))
                
                execution_result["output_content"] = f"Simulated execution of {element.name}: {template_content}"
                execution_result["status"] = "completed"
                execution_result["execution_time_ms"] = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
            except Exception as exec_error:
                execution_result["status"] = "failed"
                execution_result["error_message"] = str(exec_error)
            
            # Note: Since ElementExecution model was removed, we're not persisting execution records
            # In a future implementation, this could use a different execution tracking mechanism
            
            # Update element statistics (assuming these methods exist and don't depend on ElementExecution)
            try:
                # element.add_execution() - This might depend on ElementExecution, commenting out for now
                # element.increment_usage_count()
                # await element.save()
                pass
            except Exception as e:
                logger.warning(f"Failed to update element statistics: {str(e)}")
            
            logger.info(f"Executed element {element_id} by user {user_id}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Failed to execute element {element_id}: {str(e)}")
            return None
    
    async def update_element_version(
        self,
        element_id: str,
        user_id: str,
        new_version: str,
        changelog_entry: str
    ) -> bool:
        """
        Update element template version.
        
        Args:
            element_id: Element ID
            user_id: ID of the requesting user
            new_version: New version string
            changelog_entry: Changelog entry for this version
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            element = await self.get_element(element_id, user_id)
            
            if not element:
                return False
            
            # Only owner can update version
            if element.owner_id != user_id:
                return False
            
            element.update_template_version(new_version, changelog_entry)
            await element.save()
            
            logger.info(f"Updated element {element_id} version to {new_version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update element version {element_id}: {str(e)}")
            return False
    
    async def get_element_statistics(self, element_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get element usage statistics.
        
        Args:
            element_id: Element ID
            user_id: ID of the requesting user
            
        Returns:
            Dict[str, Any]: Element statistics if accessible, None otherwise
        """
        try:
            element = await self.get_element(element_id, user_id)
            
            if not element:
                return None
            
            return {
                "execution_count": element.get_execution_count(),
                "usage_statistics": element.usage_statistics,
                "template_version": element.template.version,
                "status": element.status,
                "created_at": element.created_at.isoformat(),
                "last_updated": element.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get element statistics {element_id}: {str(e)}")
            return None
    
    async def _get_accessible_project_ids(self, user_id: str) -> List[str]:
        """
        Get list of project IDs accessible to a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[str]: List of accessible project IDs
        """
        try:
            # Get projects user owns, collaborates on, or are public
            projects = await Project.find(
                And(
                    Project.is_deleted == False,
                    Or(
                        Project.owner_id == user_id,
                        In(Project.collaborators, [user_id]),
                        Project.visibility == "public"
                    )
                )
            ).to_list()
            
            return [str(project.id) for project in projects]
            
        except Exception as e:
            logger.error(f"Failed to get accessible projects for user {user_id}: {str(e)}")
            return [] 