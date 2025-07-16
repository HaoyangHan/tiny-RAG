"""
Generation Routes for TinyRAG v1.4.3
====================================

This module provides API routes for managing element generations,
LLM-generated content and their evaluation.

Author: TinyRAG Development Team
Version: 1.4.3
Last Updated: January 2025
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from datetime import datetime

from models import GenerationStatus, ElementGeneration, GenerationRequest
from auth.models import User
from auth.service import get_current_active_user as get_current_user
from .service import ElementGenerationService
from .dependencies import get_generation_service
from models import Document
from dependencies import get_llamaindex_rag_service

router = APIRouter()


class GenerationRequest(BaseModel):
    """Request model for generation operations."""
    project_id: str = Field(..., description="Project ID")
    prompt: str = Field(..., description="Generation prompt")
    additional_instructions: Optional[str] = Field(None, description="Additional instructions")


class GenerationResponse(BaseModel):
    """Response model for generation data."""
    id: str
    user_id: str
    element_id: Optional[str]
    project_id: str
    status: GenerationStatus
    model_used: Optional[str]
    chunk_count: int
    token_usage: int
    additional_instructions: Optional[str]
    content: str
    cost_usd: float
    generation_time_ms: int
    error_message: Optional[str]
    created_at: str
    updated_at: str


class GenerationListResponse(BaseModel):
    """Response model for generation list with pagination."""
    generations: List[GenerationResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


@router.get("/", response_model=GenerationListResponse)
async def list_generations(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    element_id: Optional[str] = Query(None, description="Filter by element ID"),
    execution_id: Optional[str] = Query(None, description="Filter by execution ID"),
    status: Optional[GenerationStatus] = Query(None, description="Filter by status"),
    include_content: bool = Query(False, description="Include generated content in response"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_user),
    generation_service: ElementGenerationService = Depends(get_generation_service)
) -> GenerationListResponse:
    """List generations."""
    try:
        generations, total_count = await generation_service.list_generations(
            user_id=str(current_user.id),
            project_id=project_id,
            element_id=element_id,
            execution_id=execution_id,
            status=status,
            include_content=include_content,
            page=page,
            page_size=page_size
        )
        
        # Convert to response models
        generation_responses = []
        for generation in generations:
            # Get full content if requested
            full_content = generation.get_full_content() if include_content else ""
            
            response = GenerationResponse(
                id=str(generation.id),
                user_id=generation.user_id,
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
            generation_responses.append(response)
        
        total_pages = (total_count + page_size - 1) // page_size
        
        return GenerationListResponse(
            generations=generation_responses,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing generations: {str(e)}"
        )


@router.get("/{generation_id}", response_model=GenerationResponse)
async def get_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user),
    generation_service: ElementGenerationService = Depends(get_generation_service)
) -> GenerationResponse:
    """Get a specific generation by ID."""
    try:
        generation = await generation_service.get_generation(generation_id, str(current_user.id))
        
        if not generation:
            raise HTTPException(
                status_code=404,
                detail="Generation not found"
            )
        
        # Get full content
        full_content = generation.get_full_content()
        
        return GenerationResponse(
            id=str(generation.id),
            user_id=generation.user_id,
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
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting generation: {str(e)}"
        )


@router.post("/generate-llamaindex", response_model=ElementGeneration)
async def generate_with_llamaindex(
    request: GenerationRequest,
    current_user: User = Depends(get_current_user),
    llamaindex_rag_service = Depends(get_llamaindex_rag_service)
) -> ElementGeneration:
    """Generate content using LlamaIndex RAG service."""
    try:
        # Create generation record
        generation = ElementGeneration(
            user_id=str(current_user.id),
            project_id=request.project_id,
            prompt=request.prompt,
            status=GenerationStatus.PROCESSING,
            created_at=datetime.utcnow()
        )
        await generation.insert()
        
        try:
            # Get documents for the project
            documents = await Document.find(
                Document.project_id == request.project_id,
                Document.is_deleted == False
            ).to_list()
            
            if not documents:
                raise HTTPException(
                    status_code=404,
                    detail="No documents found for the specified project"
                )
            
            # Create LlamaIndex index from documents
            await llamaindex_rag_service.create_index_from_documents(documents)
            
            # Query documents
            retrieved_context = await llamaindex_rag_service.query_documents(
                query=request.prompt,
                top_k=5
            )
            
            # Generate response
            generation_result = await llamaindex_rag_service.generate_response(
                query=request.prompt,
                context=retrieved_context,
                prompt_template="rag_generation"
            )
            
            # Update generation record
            generation.response = generation_result["response"]
            generation.context = generation_result["context"]
            generation.citations = generation_result["citations"]
            generation.metadata = generation_result["metadata"]
            generation.status = GenerationStatus.COMPLETED
            generation.completed_at = datetime.utcnow()
            
            await generation.save()
            
            return generation
            
        except Exception as e:
            # Update generation record with error
            generation.status = GenerationStatus.FAILED
            generation.error = str(e)
            generation.completed_at = datetime.utcnow()
            await generation.save()
            
            raise HTTPException(
                status_code=500,
                detail=f"Generation failed: {str(e)}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in LlamaIndex generation: {str(e)}"
        ) 