from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import tempfile
from pathlib import Path

from models.document import Document
from services.document_processor import DocumentProcessor
from dependencies import get_current_user, get_document_processor

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    document_processor: DocumentProcessor = Depends(get_document_processor)
) -> Document:
    """Upload and process a document."""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        # Process document
        document = await document_processor.process_document(
            temp_path,
            current_user
        )

        # Clean up temporary file
        temp_path.unlink()

        return document

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

@router.get("/", response_model=List[Document])
async def list_documents(
    current_user: str = Depends(get_current_user)
) -> List[Document]:
    """List all documents for the current user."""
    try:
        documents = await Document.find(
            Document.user_id == current_user
        ).to_list()
        return documents

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )

@router.get("/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    current_user: str = Depends(get_current_user)
) -> Document:
    """Get a specific document by ID."""
    try:
        document = await Document.get(document_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        if document.user_id != current_user:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this document"
            )
        return document

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving document: {str(e)}"
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a document."""
    try:
        document = await Document.get(document_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        if document.user_id != current_user:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this document"
            )
        await document.delete()
        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        ) 