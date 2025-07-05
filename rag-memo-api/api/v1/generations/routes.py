"""
Generation routes for TinyRAG v1.4.

This module contains generation management endpoints for tracking and managing
LLM-generated content and their evaluation results.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from models import GenerationStatus, ElementGeneration
from auth.models import User
from auth.service import get_current_active_user
from .service import ElementGenerationService
from .dependencies import get_generation_service

router = APIRouter()


class GenerationResponse(BaseModel):
    """Response schema for generation data."""
    
    id: str = Field(description="Generation ID")
    element_id: str = Field(description="Element ID that generated this content")
    project_id: str = Field(description="Associated project ID")
    status: GenerationStatus = Field(description="Generation status")
    model_used: Optional[str] = Field(description="LLM model used")
    chunk_count: int = Field(description="Number of content chunks")
    token_usage: int = Field(description="Total tokens used")
    created_at: str = Field(description="Creation timestamp")
    updated_at: str = Field(description="Last update timestamp")
    # Optional fields for enhanced responses
    content: Optional[str] = Field(None, description="Generated content (optional)")
    cost_usd: Optional[float] = Field(None, description="Generation cost in USD (optional)")
    generation_time_ms: Optional[int] = Field(None, description="Generation time in milliseconds (optional)")


class GenerationDetailResponse(GenerationResponse):
    """Response schema for detailed generation data."""
    
    additional_instructions: Optional[str] = Field(description="Additional instructions provided")
    content: str = Field(description="Generated content")
    cost_usd: float = Field(description="Generation cost in USD")
    generation_time_ms: int = Field(description="Generation time in milliseconds")
    error_message: Optional[str] = Field(description="Error message if failed")


class GenerationListResponse(BaseModel):
    """Response schema for generation list with pagination."""
    
    items: List[GenerationResponse] = Field(description="List of generations")
    total_count: int = Field(description="Total number of generations")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


@router.get(
    "/",
    response_model=GenerationListResponse,
    summary="List generations",
    description="Get a list of generations"
)
async def list_generations(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    element_id: Optional[str] = Query(None, description="Filter by element ID"),
    execution_id: Optional[str] = Query(None, description="Filter by execution ID"),
    status: Optional[GenerationStatus] = Query(None, description="Filter by status"),
    include_content: bool = Query(False, description="Include generated content in response"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_active_user),
    generation_service: ElementGenerationService = Depends(get_generation_service)
) -> GenerationListResponse:
    """List generations."""
    try:
        generations, total_count = await generation_service.list_generations(
            user_id=str(current_user.id),
            page=page,
            page_size=page_size,
            project_id=project_id,
            element_id=element_id,
            execution_id=execution_id,
            status=status
        )
        
        generation_responses = []
        for generation in generations:
            # Base response data
            response_data = {
                "id": str(generation.id),
                "element_id": generation.element_id,
                "project_id": generation.project_id,
                "status": generation.status,
                "model_used": generation.model_used,
                "chunk_count": len(generation.generated_content),
                "token_usage": generation.metrics.total_tokens if generation.metrics else 0,
                "created_at": generation.created_at.isoformat(),
                "updated_at": generation.updated_at.isoformat()
            }
            
            # Optionally include content and metrics
            if include_content:
                # Get full content from generated chunks
                full_content = ""
                if generation.generated_content:
                    full_content = "\n\n".join([chunk.content for chunk in generation.generated_content])
                
                response_data.update({
                    "content": full_content,
                    "cost_usd": generation.metrics.estimated_cost if generation.metrics and generation.metrics.estimated_cost else 0.0,
                    "generation_time_ms": generation.metrics.generation_time_ms if generation.metrics and generation.metrics.generation_time_ms else 0
                })
            
            generation_responses.append(GenerationResponse(**response_data))
        
        # Calculate pagination metadata
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        return GenerationListResponse(
            items=generation_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list generations: {str(e)}"
        )


@router.get(
    "/{generation_id}",
    response_model=GenerationDetailResponse,
    summary="Get generation details",
    description="Get detailed information about a specific generation"
)
async def get_generation(
    generation_id: str,
    current_user: User = Depends(get_current_active_user),
    generation_service: ElementGenerationService = Depends(get_generation_service)
) -> GenerationDetailResponse:
    """Get generation details."""
    generation = await generation_service.get_generation(generation_id, str(current_user.id))
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )
    
    # Get full content from generated chunks
    full_content = ""
    if generation.generated_content:
        full_content = "\n\n".join([chunk.content for chunk in generation.generated_content])
    
    return GenerationDetailResponse(
        id=str(generation.id),
        element_id=generation.element_id,
        project_id=generation.project_id,
        status=generation.status,
        model_used=generation.model_used,
        chunk_count=len(generation.generated_content),
        token_usage=generation.metrics.total_tokens if generation.metrics else 0,
        additional_instructions=generation.additional_instructions,
        content=full_content,
        cost_usd=generation.metrics.estimated_cost if generation.metrics and generation.metrics.estimated_cost else 0.0,
        generation_time_ms=generation.metrics.generation_time_ms if generation.metrics and generation.metrics.generation_time_ms else 0,
        error_message=generation.error_details.get("error_message") if generation.error_details else None,
        created_at=generation.created_at.isoformat(),
        updated_at=generation.updated_at.isoformat()
    ) 