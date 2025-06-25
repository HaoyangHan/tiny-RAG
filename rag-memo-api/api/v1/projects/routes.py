"""
Project routes for TinyRAG v1.4.

This module contains all project-related API endpoints including CRUD operations,
project management, and content organization within the tenant-based architecture.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from models import Project, TenantType, ProjectStatus, VisibilityType
from auth.service import get_current_user
from auth.models import User
from .service import ProjectService
from .dependencies import get_project_service

router = APIRouter()

# Request/Response schemas
class ProjectCreateRequest(BaseModel):
    """Request schema for creating a new project."""
    
    name: str = Field(max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    tenant_type: TenantType = Field(description="Type of tenant")
    keywords: List[str] = Field(default_factory=list, max_items=10, description="Project keywords")
    visibility: VisibilityType = Field(default=VisibilityType.PRIVATE, description="Project visibility")


class ProjectUpdateRequest(BaseModel):
    """Request schema for updating a project."""
    
    name: Optional[str] = Field(None, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    keywords: Optional[List[str]] = Field(None, max_items=10, description="Project keywords")
    visibility: Optional[VisibilityType] = Field(None, description="Project visibility")
    status: Optional[ProjectStatus] = Field(None, description="Project status")


class ProjectResponse(BaseModel):
    """Response schema for project data."""
    
    id: str = Field(description="Project ID")
    name: str = Field(description="Project name")
    description: Optional[str] = Field(description="Project description")
    tenant_type: TenantType = Field(description="Type of tenant")
    keywords: List[str] = Field(description="Project keywords")
    visibility: VisibilityType = Field(description="Project visibility")
    status: ProjectStatus = Field(description="Project status")
    owner_id: str = Field(description="Project owner ID")
    collaborators: List[str] = Field(description="Collaborator user IDs")
    document_count: int = Field(description="Number of documents")
    element_count: int = Field(description="Number of elements")
    generation_count: int = Field(description="Number of generations")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")


class ProjectListResponse(BaseModel):
    """Response schema for project list."""
    
    projects: List[ProjectResponse] = Field(description="List of projects")
    total_count: int = Field(description="Total number of projects")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")


class CollaboratorRequest(BaseModel):
    """Request schema for managing collaborators."""
    
    user_id: str = Field(description="User ID to add/remove as collaborator")


class BulkExecutionStatusResponse(BaseModel):
    """Response schema for bulk element execution status."""
    
    execution_id: str = Field(description="Execution ID")
    status: str = Field(description="Overall status: PENDING|PROCESSING|COMPLETED|FAILED")
    total_elements: int = Field(description="Total number of elements to execute")
    completed_elements: int = Field(description="Number of completed elements")
    failed_elements: int = Field(description="Number of failed elements")
    progress_percentage: float = Field(description="Completion percentage")
    estimated_completion: Optional[str] = Field(description="Estimated completion time")
    element_statuses: List[Dict[str, Any]] = Field(description="Individual element statuses")


class BulkExecutionRequest(BaseModel):
    """Request schema for bulk element execution."""
    
    element_ids: Optional[List[str]] = Field(None, description="Specific element IDs to execute (if None, execute all)")
    execution_config: Dict[str, Any] = Field(default_factory=dict, description="Execution configuration")


# Project CRUD Operations
@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new project",
    description="Create a new project with the specified configuration"
)
async def create_project(
    request: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
) -> ProjectResponse:
    """Create a new project."""
    try:
        project = await project_service.create_project(
            name=request.name,
            description=request.description,
            tenant_type=request.tenant_type,
            keywords=request.keywords,
            visibility=request.visibility,
            owner_id=str(current_user.id)
        )
        
        return ProjectResponse(
            id=str(project.id),
            name=project.name,
            description=project.description,
            tenant_type=project.tenant_type,
            keywords=project.keywords,
            visibility=project.visibility,
            status=project.status,
            owner_id=project.owner_id,
            collaborators=project.collaborators,
            document_count=len(project.document_ids),
            element_count=len(project.element_ids),
            generation_count=len(project.generation_ids),
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get(
    "/",
    response_model=ProjectListResponse,
    summary="List projects",
    description="Get a paginated list of projects accessible to the current user"
)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    tenant_type: Optional[TenantType] = Query(None, description="Filter by tenant type"),
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    visibility: Optional[VisibilityType] = Query(None, description="Filter by visibility"),
    search: Optional[str] = Query(None, description="Search in project names and descriptions"),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
) -> ProjectListResponse:
    """List projects accessible to the current user."""
    try:
        projects, total_count = await project_service.list_projects(
            user_id=str(current_user.id),
            page=page,
            page_size=page_size,
            tenant_type=tenant_type,
            status=status,
            visibility=visibility,
            search=search
        )
        
        project_responses = [
            ProjectResponse(
                id=str(project.id),
                name=project.name,
                description=project.description,
                tenant_type=project.tenant_type,
                keywords=project.keywords,
                visibility=project.visibility,
                status=project.status,
                owner_id=project.owner_id,
                collaborators=project.collaborators,
                document_count=len(project.document_ids),
                element_count=len(project.element_ids),
                generation_count=len(project.generation_ids),
                created_at=project.created_at.isoformat(),
                updated_at=project.updated_at.isoformat()
            )
            for project in projects
        ]
        
        return ProjectListResponse(
            projects=project_responses,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.get(
    "/public",
    response_model=ProjectListResponse,
    summary="List public projects",
    description="Get a list of public projects visible to everyone"
)
async def list_public_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    tenant_type: Optional[TenantType] = Query(None, description="Filter by tenant type"),
    search: Optional[str] = Query(None, description="Search in project names and descriptions"),
    project_service: ProjectService = Depends(get_project_service)
) -> ProjectListResponse:
    """List public projects."""
    try:
        projects, total_count = await project_service.list_public_projects(
            page=page,
            page_size=page_size,
            tenant_type=tenant_type,
            search=search
        )
        
        project_responses = [
            ProjectResponse(
                id=str(project.id),
                name=project.name,
                description=project.description,
                tenant_type=project.tenant_type,
                keywords=project.keywords,
                visibility=project.visibility,
                status=project.status,
                owner_id=project.owner_id,
                collaborators=project.collaborators,
                document_count=len(project.document_ids),
                element_count=len(project.element_ids),
                generation_count=len(project.generation_ids),
                created_at=project.created_at.isoformat(),
                updated_at=project.updated_at.isoformat()
            )
            for project in projects
        ]
        
        return ProjectListResponse(
            projects=project_responses,
            total_count=total_count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list public projects: {str(e)}"
        )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project details",
    description="Get detailed information about a specific project"
)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
) -> ProjectResponse:
    """Get project details."""
    try:
        project = await project_service.get_project(
            project_id=project_id,
            user_id=str(current_user.id)
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return ProjectResponse(
            id=str(project.id),
            name=project.name,
            description=project.description,
            tenant_type=project.tenant_type,
            keywords=project.keywords,
            visibility=project.visibility,
            status=project.status,
            owner_id=project.owner_id,
            collaborators=project.collaborators,
            document_count=len(project.document_ids),
            element_count=len(project.element_ids),
            generation_count=len(project.generation_ids),
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
    description="Update project information"
)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
) -> ProjectResponse:
    """Update project information."""
    try:
        project = await project_service.update_project(
            project_id=project_id,
            user_id=str(current_user.id),
            updates=request.dict(exclude_unset=True)
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        
        return ProjectResponse(
            id=str(project.id),
            name=project.name,
            description=project.description,
            tenant_type=project.tenant_type,
            keywords=project.keywords,
            visibility=project.visibility,
            status=project.status,
            owner_id=project.owner_id,
            collaborators=project.collaborators,
            document_count=len(project.document_ids),
            element_count=len(project.element_ids),
            generation_count=len(project.generation_ids),
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete a project (soft delete)"
)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
) -> None:
    """Delete a project."""
    try:
        success = await project_service.delete_project(
            project_id=project_id,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )


# Project Collaboration
@router.post(
    "/{project_id}/collaborators",
    status_code=status.HTTP_201_CREATED,
    summary="Add collaborator",
    description="Add a collaborator to the project"
)
async def add_collaborator(
    project_id: str,
    request: CollaboratorRequest,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
) -> Dict[str, str]:
    """Add a collaborator to the project."""
    try:
        success = await project_service.add_collaborator(
            project_id=project_id,
            owner_id=str(current_user.id),
            collaborator_id=request.user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        
        return {"message": "Collaborator added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add collaborator: {str(e)}"
        )


@router.delete(
    "/{project_id}/collaborators/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove collaborator",
    description="Remove a collaborator from the project"
)
async def remove_collaborator(
    project_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
) -> None:
    """Remove a collaborator from the project."""
    try:
        success = await project_service.remove_collaborator(
            project_id=project_id,
            owner_id=str(current_user.id),
            collaborator_id=user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove collaborator: {str(e)}"
        )


# Bulk Element Execution
@router.post(
    "/{project_id}/elements/execute-all",
    response_model=Dict[str, str],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute all project elements",
    description="Trigger execution of all elements in the project"
)
async def execute_all_elements(
    project_id: str,
    request: BulkExecutionRequest = BulkExecutionRequest(),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
) -> Dict[str, str]:
    """Execute all elements in a project."""
    try:
        execution_id = await project_service.execute_all_elements(
            project_id=project_id,
            user_id=str(current_user.id),
            element_ids=request.element_ids,
            execution_config=request.execution_config
        )
        
        return {
            "execution_id": execution_id,
            "message": "Bulk element execution started",
            "status": "PENDING"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute elements: {str(e)}"
        )


@router.get(
    "/{project_id}/elements/execute-all-status",
    response_model=BulkExecutionStatusResponse,
    summary="Get bulk execution status",
    description="Get the status of bulk element execution"
)
async def get_bulk_execution_status(
    project_id: str,
    execution_id: str = Query(description="Execution ID to check status for"),
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service)
) -> BulkExecutionStatusResponse:
    """Get the status of bulk element execution."""
    try:
        status_data = await project_service.get_bulk_execution_status(
            project_id=project_id,
            execution_id=execution_id,
            user_id=str(current_user.id)
        )
        
        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )
        
        return BulkExecutionStatusResponse(**status_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution status: {str(e)}"
        ) 