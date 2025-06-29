from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List
import tempfile
from pathlib import Path

from models.document import Document
from services.document_processor import DocumentProcessor
from auth.models import User
from auth.service import AuthService

router = APIRouter(prefix="/documents", tags=["documents"])

# Global auth service reference - will be set by main.py
auth_service: AuthService = None

def set_auth_service(service: AuthService):
    """Set the auth service instance from main.py"""
    global auth_service
    auth_service = service

def get_auth_service() -> AuthService:
    """Get the authentication service instance."""
    if auth_service is None:
        raise HTTPException(
            status_code=500,
            detail="Authentication service not initialized"
        )
    return auth_service

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> User:
    """Dependency to get current authenticated user."""
    service = get_auth_service()
    return await service.get_current_user(credentials)

def get_document_processor() -> DocumentProcessor:
    """Get a DocumentProcessor instance."""
    import os
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    return DocumentProcessor(openai_api_key)

@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    document_processor: DocumentProcessor = Depends(get_document_processor)
) -> Document:
    """Upload and process a document."""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        # Process document with user ID
        document = await document_processor.process_document(
            temp_path,
            str(current_user.id)  # Convert User object to string ID
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
    current_user: User = Depends(get_current_user)
) -> List[Document]:
    """List all documents for the current user."""
    try:
        documents = await Document.find(
            Document.user_id == str(current_user.id)
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
    current_user: User = Depends(get_current_user)
) -> Document:
    """Get a specific document by ID."""
    try:
        document = await Document.get(document_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        if document.user_id != str(current_user.id):
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
    current_user: User = Depends(get_current_user)
):
    """Delete a document."""
    try:
        document = await Document.get(document_id)
        if not document:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        if document.user_id != str(current_user.id):
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