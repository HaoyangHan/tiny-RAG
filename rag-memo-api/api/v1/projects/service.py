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

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Service class for project management operations.
    
    Handles all business logic related to projects including creation,
    retrieval, updates, deletion, and collaboration management.
    """
    
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
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            tenant_type: Type of tenant
            keywords: Project keywords for search
            visibility: Project visibility setting
            owner_id: ID of the project owner
            
        Returns:
            Project: Created project instance
            
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