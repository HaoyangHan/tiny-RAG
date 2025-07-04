"""
Project service for TinyRAG v1.4.

This module contains the business logic for project management including
CRUD operations, access control, and collaboration features.
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId
from beanie.operators import In, And, Or, Eq

from models import Project, TenantType, ProjectStatus, VisibilityType
from services.element_template_service import ElementTemplateService

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Service class for project management operations.
    
    Handles all business logic related to projects including creation,
    retrieval, updates, deletion, and collaboration management.
    """
    
    def __init__(self):
        """Initialize project service with dependencies."""
        self.element_template_service = ElementTemplateService()
    
    async def create_project(
        self,
        name: str,
        description: Optional[str],
        tenant_type: TenantType,
        keywords: List[str],
        visibility: VisibilityType,
        owner_id: str
    ) -> Project:
        """
        Create a new project with automatic element template provisioning.
        
        Args:
            name: Project name
            description: Project description
            tenant_type: Type of tenant
            keywords: Project keywords for search
            visibility: Project visibility setting
            owner_id: ID of the project owner
            
        Returns:
            Project: Created project instance with provisioned elements
            
        Raises:
            ValueError: If validation fails
            Exception: If creation fails
        """
        try:
            # Create project instance
            project = Project(
                name=name,
                description=description,
                tenant_type=tenant_type,
                keywords=keywords,
                visibility=visibility,
                owner_id=owner_id,
                status=ProjectStatus.ACTIVE
            )
            
            # Save to database
            await project.insert()
            
            logger.info(f"Created project {project.id} for user {owner_id}")
            
            # Provision element templates for the tenant type
            try:
                logger.info(f"🔧 DEBUG: Starting element template provisioning for project {project.id}")
                logger.info(f"🔧 DEBUG: Tenant type: {tenant_type}")
                logger.info(f"🔧 DEBUG: Tenant type value: {tenant_type.value}")
                
                # Test if element template service can find templates
                logger.info("🔧 DEBUG: Testing ElementTemplateService.get_templates_by_tenant...")
                test_templates = await self.element_template_service.get_templates_by_tenant(tenant_type, active_only=True)
                logger.info(f"🔧 DEBUG: ElementTemplateService found {len(test_templates)} templates")
                
                if test_templates:
                    for i, template in enumerate(test_templates[:3]):  # Log first 3 templates
                        logger.info(f"🔧 DEBUG: Template {i+1}: {template.name} (status: {getattr(template, 'status', 'MISSING')})")
                
                batch_id = f"project_creation_{project.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                logger.info(f"🔧 DEBUG: Calling provision_templates_to_project with batch_id: {batch_id}")
                
                provisioned_elements = await self.element_template_service.provision_templates_to_project(
                    project_id=str(project.id),
                    tenant_type=tenant_type,
                    batch_id=batch_id,
                    force=False
                )
                
                logger.info(f"🔧 DEBUG: provision_templates_to_project returned {len(provisioned_elements)} elements")
                
                # Update project element IDs
                if provisioned_elements:
                    project.element_ids = [str(elem.id) for elem in provisioned_elements]
                    await project.save()
                    
                    logger.info(
                        f"✅ Provisioned {len(provisioned_elements)} element templates "
                        f"to project {project.id} for tenant {tenant_type}"
                    )
                    
                    # Log element details
                    for elem in provisioned_elements:
                        logger.info(f"🔧 DEBUG: Created element: {elem.name} (ID: {elem.id})")
                else:
                    logger.warning(f"❌ No element templates found for tenant {tenant_type}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to provision element templates to project {project.id}: {str(e)}")
                logger.error(f"🔧 DEBUG: Exception type: {type(e).__name__}")
                import traceback
                logger.error(f"🔧 DEBUG: Full traceback: {traceback.format_exc()}")
                # Don't fail project creation if template provisioning fails
                # The project is still created, just without default elements
            
            return project
            
        except Exception as e:
            logger.error(f"Failed to create project: {str(e)}")
            raise
    
    async def get_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """
        Get a project by ID with access control.
        
        Args:
            project_id: Project ID to retrieve
            user_id: ID of the requesting user
            
        Returns:
            Project: Project instance if found and accessible, None otherwise
        """
        try:
            project = await Project.get(PydanticObjectId(project_id))
            
            if not project or project.is_deleted:
                return None
            
            # Check access permissions
            if not project.is_accessible_by(user_id):
                return None
            
            return project
            
        except Exception as e:
            logger.error(f"Failed to get project {project_id}: {str(e)}")
            return None
    
    async def list_projects(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        tenant_type: Optional[TenantType] = None,
        status: Optional[ProjectStatus] = None,
        visibility: Optional[VisibilityType] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Project], int]:
        """
        List projects accessible to a user with filtering and pagination.
        
        Args:
            user_id: ID of the requesting user
            page: Page number (1-based)
            page_size: Number of items per page
            tenant_type: Filter by tenant type
            status: Filter by project status
            visibility: Filter by visibility
            search: Search in project names and descriptions
            
        Returns:
            Tuple[List[Project], int]: List of projects and total count
        """
        try:
            # Build query conditions
            conditions = [
                Project.is_deleted == False
            ]
            
            # Access control: user can see projects they own, collaborate on, or public ones
            access_conditions = [
                Project.owner_id == user_id,  # Projects they own
                In(Project.collaborators, [user_id]),  # Projects they collaborate on
                Project.visibility == VisibilityType.PUBLIC  # Public projects
            ]
            conditions.append(Or(*access_conditions))
            
            # Apply filters
            if tenant_type:
                conditions.append(Project.tenant_type == tenant_type)
            
            if status:
                conditions.append(Project.status == status)
            
            if visibility:
                conditions.append(Project.visibility == visibility)
            
            if search:
                search_conditions = [
                    Project.name.contains(search, case_insensitive=True),
                    Project.description.contains(search, case_insensitive=True)
                ]
                conditions.append(Or(*search_conditions))
            
            # Build final query
            query = Project.find(And(*conditions))
            
            # Get total count
            total_count = await query.count()
            
            # Apply pagination and sorting
            projects = await query.sort(-Project.updated_at).skip((page - 1) * page_size).limit(page_size).to_list()
            
            return projects, total_count
            
        except Exception as e:
            logger.error(f"Failed to list projects for user {user_id}: {str(e)}")
            return [], 0
    
    async def list_public_projects(
        self,
        page: int = 1,
        page_size: int = 20,
        tenant_type: Optional[TenantType] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Project], int]:
        """
        List public projects with filtering and pagination.
        
        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            tenant_type: Filter by tenant type
            search: Search in project names and descriptions
            
        Returns:
            Tuple[List[Project], int]: List of projects and total count
        """
        try:
            # Build query conditions
            conditions = [
                Project.is_deleted == False,
                Project.visibility == VisibilityType.PUBLIC,
                Project.status == ProjectStatus.ACTIVE
            ]
            
            # Apply filters
            if tenant_type:
                conditions.append(Project.tenant_type == tenant_type)
            
            if search:
                search_conditions = [
                    Project.name.contains(search, case_insensitive=True),
                    Project.description.contains(search, case_insensitive=True)
                ]
                conditions.append(Or(*search_conditions))
            
            # Build final query
            query = Project.find(And(*conditions))
            
            # Get total count
            total_count = await query.count()
            
            # Apply pagination and sorting
            projects = await query.sort(-Project.updated_at).skip((page - 1) * page_size).limit(page_size).to_list()
            
            return projects, total_count
            
        except Exception as e:
            logger.error(f"Failed to list public projects: {str(e)}")
            return [], 0
    
    async def update_project(
        self,
        project_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Project]:
        """
        Update a project with access control.
        
        Args:
            project_id: Project ID to update
            user_id: ID of the requesting user
            updates: Dictionary of updates to apply
            
        Returns:
            Project: Updated project instance if successful, None otherwise
        """
        try:
            project = await Project.get(PydanticObjectId(project_id))
            
            if not project or project.is_deleted:
                return None
            
            # Check if user is owner (only owners can update projects)
            if project.owner_id != user_id:
                return None
            
            # Apply updates
            for field, value in updates.items():
                if hasattr(project, field):
                    setattr(project, field, value)
            
            # Update timestamp
            project.update_timestamp()
            
            # Save changes
            await project.save()
            
            logger.info(f"Updated project {project_id} by user {user_id}")
            return project
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {str(e)}")
            return None
    
    async def delete_project(self, project_id: str, user_id: str) -> bool:
        """
        Delete a project (soft delete) with access control.
        
        Args:
            project_id: Project ID to delete
            user_id: ID of the requesting user
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            project = await Project.get(PydanticObjectId(project_id))
            
            if not project or project.is_deleted:
                return False
            
            # Check if user is owner (only owners can delete projects)
            if project.owner_id != user_id:
                return False
            
            # Perform soft delete
            project.mark_deleted()
            await project.save()
            
            logger.info(f"Deleted project {project_id} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {str(e)}")
            return False
    
    async def add_collaborator(
        self,
        project_id: str,
        owner_id: str,
        collaborator_id: str
    ) -> bool:
        """
        Add a collaborator to a project.
        
        Args:
            project_id: Project ID
            owner_id: ID of the project owner
            collaborator_id: ID of the user to add as collaborator
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project = await Project.get(PydanticObjectId(project_id))
            
            if not project or project.is_deleted:
                return False
            
            # Check if requesting user is owner
            if project.owner_id != owner_id:
                return False
            
            # Add collaborator
            project.add_collaborator(collaborator_id)
            await project.save()
            
            logger.info(f"Added collaborator {collaborator_id} to project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add collaborator to project {project_id}: {str(e)}")
            return False
    
    async def remove_collaborator(
        self,
        project_id: str,
        owner_id: str,
        collaborator_id: str
    ) -> bool:
        """
        Remove a collaborator from a project.
        
        Args:
            project_id: Project ID
            owner_id: ID of the project owner
            collaborator_id: ID of the user to remove as collaborator
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            project = await Project.get(PydanticObjectId(project_id))
            
            if not project or project.is_deleted:
                return False
            
            # Check if requesting user is owner
            if project.owner_id != owner_id:
                return False
            
            # Remove collaborator
            project.remove_collaborator(collaborator_id)
            await project.save()
            
            logger.info(f"Removed collaborator {collaborator_id} from project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove collaborator from project {project_id}: {str(e)}")
            return False
    
    async def get_user_projects_count(self, user_id: str) -> Dict[str, int]:
        """
        Get project counts for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, int]: Project counts by category
        """
        try:
            # Projects owned by user
            owned_count = await Project.find(
                And(
                    Project.owner_id == user_id,
                    Project.is_deleted == False
                )
            ).count()
            
            # Projects user collaborates on
            collaboration_count = await Project.find(
                And(
                    In(Project.collaborators, [user_id]),
                    Project.is_deleted == False
                )
            ).count()
            
            # Active projects
            active_count = await Project.find(
                And(
                    Or(
                        Project.owner_id == user_id,
                        In(Project.collaborators, [user_id])
                    ),
                    Project.status == ProjectStatus.ACTIVE,
                    Project.is_deleted == False
                )
            ).count()
            
            return {
                "owned": owned_count,
                "collaborating": collaboration_count,
                "active": active_count,
                "total": owned_count + collaboration_count
            }
            
        except Exception as e:
            logger.error(f"Failed to get project counts for user {user_id}: {str(e)}")
            return {"owned": 0, "collaborating": 0, "active": 0, "total": 0}
    
    async def execute_all_elements(
        self,
        project_id: str,
        user_id: str,
        element_ids: Optional[List[str]] = None,
        execution_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute all elements in a project using the new element generation service.
        
        Args:
            project_id: Project ID
            user_id: User ID for access control
            element_ids: Specific element IDs to execute (optional)
            execution_config: Execution configuration (optional)
            
        Returns:
            Execution ID for tracking progress
        """
        from services.element_generation_service import get_element_generation_service
        
        try:
            # Validate project access
            project = await self.get_project(project_id, user_id)
            if not project:
                raise ValueError("Project not found or access denied")
            
            # Get additional instructions from execution config
            additional_instructions = execution_config.get('additional_instructions') if execution_config else None
            
            # Use the element generation service for bulk generation
            element_generation_service = get_element_generation_service()
            
            # Generate unique execution ID for tracking
            execution_id = f"bulk_{project_id}_{int(datetime.utcnow().timestamp())}"
            
            # Start bulk generation in background (in production, use task queue)
            results = await element_generation_service.bulk_generate_elements(
                project_id=project_id,
                user_id=user_id,
                element_ids=element_ids,
                additional_instructions=additional_instructions
            )
            
            logger.info(
                f"Bulk execution completed for project {project_id}: "
                f"{results['successful']}/{results['total_elements']} successful"
            )
            
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to execute all elements for project {project_id}: {e}")
            raise 