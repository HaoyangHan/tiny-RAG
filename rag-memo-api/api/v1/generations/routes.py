"""
Generation routes for TinyRAG v1.4.

This module contains generation management endpoints for tracking and managing
LLM-generated content and their evaluation results.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from models import GenerationStatus
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


class GenerationDetailResponse(GenerationResponse):
    """Response schema for detailed generation data."""
    
    prompt: str = Field(description="Input prompt")
    content: str = Field(description="Generated content")
    cost_usd: float = Field(description="Generation cost in USD")
    generation_time_ms: int = Field(description="Generation time in milliseconds")
    error_message: Optional[str] = Field(description="Error message if failed")


@router.get(
    "/",
    response_model=List[GenerationResponse],
    summary="List generations",
    description="Get a list of generations"
)
async def list_generations(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    element_id: Optional[str] = Query(None, description="Filter by element ID"),
    status: Optional[GenerationStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_active_user),
    generation_service: ElementGenerationService = Depends(get_generation_service)
) -> List[GenerationResponse]:
    """List generations."""
    try:
        generations, total_count = await generation_service.list_generations(
            user_id=str(current_user.id),
            page=page,
            page_size=page_size,
            project_id=project_id,
            element_id=element_id,
            status=status
        )
        
        generation_responses = [
            GenerationResponse(
                id=str(generation.id),
                element_id=generation.element_id,
                project_id=generation.project_id,
                status=generation.status,
                model_used=generation.config.get("model"),
                chunk_count=generation.get_chunk_count(),
                token_usage=generation.metrics.total_tokens,
                created_at=generation.created_at.isoformat(),
                updated_at=generation.updated_at.isoformat()
            )
            for generation in generations
        ]
        
        return generation_responses
        
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
    
    return GenerationDetailResponse(
        id=str(generation.id),
        element_id=generation.element_id,
        project_id=generation.project_id,
        status=generation.status,
        model_used=generation.config.get("model"),
        chunk_count=generation.get_chunk_count(),
        token_usage=generation.metrics.total_tokens,
        prompt=generation.prompt,
        content=generation.get_full_content(),
        cost_usd=generation.metrics.cost_usd,
        generation_time_ms=generation.metrics.generation_time_ms,
        error_message=generation.error_message,
        created_at=generation.created_at.isoformat(),
        updated_at=generation.updated_at.isoformat()
    ) 