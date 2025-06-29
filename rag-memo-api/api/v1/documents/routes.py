"""
Document routes for TinyRAG v1.4.

This module contains document management endpoints adapted for the v1.4 API structure,
maintaining compatibility with existing document functionality.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from pydantic import BaseModel, Field

from auth.models import User
from auth.service import get_current_active_user
from .service import DocumentService
from models import DocumentStatus

router = APIRouter()


class DocumentChunkResponse(BaseModel):
    """Response schema for document chunk data."""
    
    text: str = Field(description="Chunk text content")
    page_number: int = Field(description="Page number in source document")
    chunk_index: int = Field(description="Index of chunk within document")
    chunk_type: str = Field(default="text", description="Type of chunk: text, table, or image")
    embedding: Optional[List[float]] = Field(description="Vector embedding for the chunk")


class TableDataResponse(BaseModel):
    """Response schema for table data extracted from documents."""
    
    page_number: int = Field(description="Page number where table is located")
    table_index: int = Field(description="Index of table on the page")
    content: List[List[str]] = Field(description="Table content as rows and columns")
    summary: str = Field(description="AI-generated summary of table content")
    row_count: int = Field(description="Number of rows in the table")
    column_count: int = Field(description="Number of columns in the table")


class ImageDataResponse(BaseModel):
    """Response schema for image data extracted from documents."""
    
    page_number: int = Field(description="Page number where image is located")
    image_index: int = Field(description="Index of image on the page")
    description: str = Field(description="AI-generated description of image content")
    # Note: Raw image content is not included in API response for performance


class DocumentResponse(BaseModel):
    """Response schema for document data with enhanced table and image support."""
    
    id: str = Field(description="Document ID")
    filename: str = Field(description="Original filename")
    project_id: Optional[str] = Field(description="Associated project ID")
    content_type: str = Field(description="File content type")
    file_size: int = Field(description="File size in bytes")
    status: str = Field(description="Processing status")
    chunks: List[DocumentChunkResponse] = Field(description="Document chunks with text and embeddings")
    tables: List[TableDataResponse] = Field(description="Extracted tables with summaries")
    images: List[ImageDataResponse] = Field(description="Extracted images with descriptions")
    chunk_count: int = Field(description="Number of text chunks")
    table_count: int = Field(description="Number of extracted tables")
    image_count: int = Field(description="Number of extracted images")
    has_tables: bool = Field(description="Whether document contains tables")
    has_images: bool = Field(description="Whether document contains images")
    created_at: str = Field(description="Upload timestamp")
    updated_at: str = Field(description="Last update timestamp")


class DocumentListResponse(BaseModel):
    """Response schema for document list - matches frontend PaginatedResponse."""
    
    items: List[DocumentResponse] = Field(description="List of documents")
    total_count: int = Field(description="Total number of documents")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="List documents",
    description="Get a list of documents accessible to the current user"
)
async def list_documents(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by processing status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: User = Depends(get_current_active_user)
) -> DocumentListResponse:
    """List documents."""
    try:
        # Convert status string to enum if provided
        status_filter = None
        if status:
            try:
                status_filter = DocumentStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status: {status}"
                )
        
        # Get documents using service
        document_service = DocumentService()
        documents, total = await document_service.list_documents(
            user_id=str(current_user.id),
            page=page,
            page_size=page_size,
            project_id=project_id,
            status=status_filter
        )
        
        # Convert to response models
        response_items = [
            DocumentResponse(
                id=str(doc.id),
                filename=doc.filename,
                project_id=doc.project_id,
                content_type=doc.content_type,
                file_size=doc.file_size,
                status=doc.status,
                chunks=[
                    DocumentChunkResponse(
                        text=chunk.text,
                        page_number=chunk.page_number,
                        chunk_index=chunk.chunk_index,
                        chunk_type=getattr(chunk, 'chunk_type', 'text'),
                        embedding=chunk.embedding
                    )
                    for chunk in doc.chunks
                ],
                tables=[
                    TableDataResponse(
                        page_number=table.page_number,
                        table_index=table.table_index,
                        content=table.content,
                        summary=table.summary,
                        row_count=getattr(table, 'row_count', 0),
                        column_count=getattr(table, 'column_count', 0)
                    )
                    for table in doc.tables
                ],
                images=[
                    ImageDataResponse(
                        page_number=image.page_number,
                        image_index=image.image_index,
                        description=image.description
                    )
                    for image in doc.images
                ],
                chunk_count=len(doc.chunks),
                table_count=len(doc.tables),
                image_count=len(doc.images),
                has_tables=bool(doc.tables),
                has_images=bool(doc.images),
                created_at=doc.created_at.isoformat(),
                updated_at=doc.updated_at.isoformat()
            )
            for doc in documents
        ]
        
        # Calculate pagination metadata
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        has_next = page < total_pages
        has_prev = page > 1
        
        return DocumentListResponse(
            items=response_items,
            total_count=total,
            page=page,
            page_size=page_size,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document",
    description="Upload a new document and associate with project"
)
async def upload_document(
    file: UploadFile = File(...),
    project_id: Optional[str] = Query(None, description="Project ID to associate with"),
    current_user: User = Depends(get_current_active_user)
) -> DocumentResponse:
    """Upload a document."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Require project_id for v1.4
        if not project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project ID is required for v1.4 document upload"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Upload document using service
        document_service = DocumentService()
        document = await document_service.upload_document(
            project_id=project_id,
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            user_id=str(current_user.id)
        )
        
        # Convert to response model
        return DocumentResponse(
            id=str(document.id),
            filename=document.filename,
            project_id=document.project_id,
            content_type=document.content_type,
            file_size=document.file_size,
            status=document.status,
            chunks=[
                DocumentChunkResponse(
                    text=chunk.text,
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    chunk_type=getattr(chunk, 'chunk_type', 'text'),
                    embedding=chunk.embedding
                )
                for chunk in document.chunks
            ],
            tables=[
                TableDataResponse(
                    page_number=table.page_number,
                    table_index=table.table_index,
                    content=table.content,
                    summary=table.summary,
                    row_count=getattr(table, 'row_count', 0),
                    column_count=getattr(table, 'column_count', 0)
                )
                for table in document.tables
            ],
            images=[
                ImageDataResponse(
                    page_number=image.page_number,
                    image_index=image.image_index,
                    description=image.description
                )
                for image in document.images
            ],
            chunk_count=len(document.chunks),
            table_count=len(document.tables),
            image_count=len(document.images),
            has_tables=bool(document.tables),
            has_images=bool(document.images),
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document details",
    description="Get detailed information about a specific document"
)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
) -> DocumentResponse:
    """Get document details."""
    try:
        document_service = DocumentService()
        document = await document_service.get_document(
            document_id=document_id,
            user_id=str(current_user.id)
        )
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return DocumentResponse(
            id=str(document.id),
            filename=document.filename,
            project_id=document.project_id,
            content_type=document.content_type,
            file_size=document.file_size,
            status=document.status,
            chunks=[
                DocumentChunkResponse(
                    text=chunk.text,
                    page_number=chunk.page_number,
                    chunk_index=chunk.chunk_index,
                    chunk_type=getattr(chunk, 'chunk_type', 'text'),
                    embedding=chunk.embedding
                )
                for chunk in document.chunks
            ],
            tables=[
                TableDataResponse(
                    page_number=table.page_number,
                    table_index=table.table_index,
                    content=table.content,
                    summary=table.summary,
                    row_count=getattr(table, 'row_count', 0),
                    column_count=getattr(table, 'column_count', 0)
                )
                for table in document.tables
            ],
            images=[
                ImageDataResponse(
                    page_number=image.page_number,
                    image_index=image.image_index,
                    description=image.description
                )
                for image in document.images
            ],
            chunk_count=len(document.chunks),
            table_count=len(document.tables),
            image_count=len(document.images),
            has_tables=bool(document.tables),
            has_images=bool(document.images),
            created_at=document.created_at.isoformat(),
            updated_at=document.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.get(
    "/{document_id}/content",
    response_model=dict,
    summary="Get document content with chunks",
    description="Get the full content of a document including all chunks and embeddings"
)
async def get_document_content(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """Get document content with full chunk details."""
    try:
        document_service = DocumentService()
        content = await document_service.get_document_content(
            document_id=document_id,
            user_id=str(current_user.id)
        )
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return content
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document content: {str(e)}"
        )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete document",
    description="Delete a document"
)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """Delete a document."""
    # TODO: Adapt existing document deletion functionality
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Document deletion adapted for v1.4 not implemented yet"
    ) 