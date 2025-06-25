"""
Element routes for TinyRAG v1.4.

This module contains element management endpoints for creating and managing
prompt templates, MCP configurations, and agentic tools.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from models import ElementType, ElementStatus, TaskType, TenantType
from auth.models import User
from auth.service import get_current_active_user
from .service import ElementService
from .dependencies import get_element_service

router = APIRouter()


class ElementCreateRequest(BaseModel):
    """Request schema for creating a new element."""
    
    name: str = Field(max_length=200, description="Element name")
    description: Optional[str] = Field(None, max_length=1000, description="Element description")
    project_id: str = Field(description="Associated project ID")
    element_type: ElementType = Field(description="Type of element")
    template_content: str = Field(description="Template content")
    variables: List[str] = Field(default_factory=list, description="Template variables")
    execution_config: Dict[str, Any] = Field(default_factory=dict, description="Execution configuration")
    tags: List[str] = Field(default_factory=list, description="Element tags")


class ElementResponse(BaseModel):
    """Response schema for element data."""
    
    id: str = Field(description="Element ID")
    name: str = Field(description="Element name")
    description: Optional[str] = Field(description="Element description")
    project_id: str = Field(description="Associated project ID")
    element_type: ElementType = Field(description="Type of element")
    status: ElementStatus = Field(description="Element status")
    template_version: str = Field(description="Template version")
    tags: List[str] = Field(description="Element tags")
    execution_count: int = Field(description="Number of executions")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")


class ElementDetailResponse(ElementResponse):
    """Response schema for detailed element data."""
    
    template_content: str = Field(description="Template content")
    template_variables: List[str] = Field(description="Template variables")
    execution_config: Dict[str, Any] = Field(description="Execution configuration")
    usage_statistics: Dict[str, Any] = Field(description="Usage statistics")


@router.post(
    "/",
    response_model=ElementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create element",
    description="Create a new element"
)
async def create_element(
    request: ElementCreateRequest,
    current_user: User = Depends(get_current_active_user),
    element_service: ElementService = Depends(get_element_service)
) -> ElementResponse:
    """Create a new element."""
    try:
        element = await element_service.create_element(
            name=request.name,
            description=request.description,
            project_id=request.project_id,
            element_type=request.element_type,
            template_content=request.template_content,
            variables=request.variables,
            execution_config=request.execution_config,
            tags=request.tags,
            owner_id=str(current_user.id)
        )
        
        return ElementResponse(
            id=str(element.id),
            name=element.name,
            description=element.description,
            project_id=element.project_id,
            element_type=element.element_type,
            status=element.status,
            template_version=element.template.version,
            tags=element.tags,
            execution_count=element.get_execution_count(),
            created_at=element.created_at.isoformat(),
            updated_at=element.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create element: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[ElementResponse],
    summary="List elements",
    description="Get a list of elements"
)
async def list_elements(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    element_type: Optional[ElementType] = Query(None, description="Filter by element type"),
    status: Optional[ElementStatus] = Query(None, description="Filter by element status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_active_user),
    element_service: ElementService = Depends(get_element_service)
) -> List[ElementResponse]:
    """List elements."""
    try:
        elements, total_count = await element_service.list_elements(
            user_id=str(current_user.id),
            page=page,
            page_size=page_size,
            project_id=project_id,
            element_type=element_type,
            status=status
        )
        
        element_responses = [
            ElementResponse(
                id=str(element.id),
                name=element.name,
                description=element.description,
                project_id=element.project_id,
                element_type=element.element_type,
                status=element.status,
                template_version=element.template.version,
                tags=element.tags,
                execution_count=element.get_execution_count(),
                created_at=element.created_at.isoformat(),
                updated_at=element.updated_at.isoformat()
            )
            for element in elements
        ]
        
        return element_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list elements: {str(e)}"
        )


@router.get(
    "/{element_id}",
    response_model=ElementDetailResponse,
    summary="Get element",
    description="Get a specific element by ID"
)
async def get_element(
    element_id: str,
    current_user: User = Depends(get_current_active_user),
    element_service: ElementService = Depends(get_element_service)
) -> ElementDetailResponse:
    """Get a specific element by ID."""
    element = await element_service.get_element(element_id, str(current_user.id))
    
    if not element:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Element not found"
        )
    
    return ElementDetailResponse(
        id=str(element.id),
        name=element.name,
        description=element.description,
        project_id=element.project_id,
        element_type=element.element_type,
        status=element.status,
        template_content=element.template.content,
        template_variables=element.template.variables,
        template_version=element.template.version,
        execution_config=element.template.execution_config,
        tags=element.tags,
        execution_count=element.get_execution_count(),
        usage_statistics=element.usage_statistics,
        created_at=element.created_at.isoformat(),
        updated_at=element.updated_at.isoformat()
    )


@router.post(
    "/{element_id}/execute",
    summary="Execute element",
    description="Execute an element with provided variables"
)
async def execute_element(
    element_id: str,
    variables: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    element_service: ElementService = Depends(get_element_service)
) -> Dict[str, Any]:
    """Execute an element."""
    try:
        execution = await element_service.execute_element(
            element_id=element_id,
            user_id=str(current_user.id),
            input_variables=variables
        )
        
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Element not found or access denied"
            )
        
        return {
            "execution_id": str(execution.id),
            "status": execution.status,
            "output_content": execution.output_content,
            "execution_time_ms": execution.execution_time_ms,
            "error_message": execution.error_message
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute element: {str(e)}"
        )


@router.put(
    "/{element_id}",
    response_model=ElementResponse,
    summary="Update element",
    description="Update an existing element"
)
async def update_element(
    element_id: str,
    updates: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    element_service: ElementService = Depends(get_element_service)
) -> ElementResponse:
    """Update an existing element."""
    try:
        element = await element_service.update_element(
            element_id=element_id,
            user_id=str(current_user.id),
            updates=updates
        )
        
        if not element:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Element not found or access denied"
            )
        
        return ElementResponse(
            id=str(element.id),
            name=element.name,
            description=element.description,
            project_id=element.project_id,
            element_type=element.element_type,
            status=element.status,
            template_version=element.template.version,
            tags=element.tags,
            execution_count=element.get_execution_count(),
            created_at=element.created_at.isoformat(),
            updated_at=element.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update element: {str(e)}"
        )


@router.delete(
    "/{element_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete element",
    description="Delete an element"
)
async def delete_element(
    element_id: str,
    current_user: User = Depends(get_current_active_user),
    element_service: ElementService = Depends(get_element_service)
) -> None:
    """Delete an element."""
    try:
        success = await element_service.delete_element(
            element_id=element_id,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Element not found or access denied"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete element: {str(e)}"
        ) 