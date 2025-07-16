from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
import os
from dotenv import load_dotenv

from services.document_processor import DocumentProcessor
from auth.models import User

# Load environment variables
load_dotenv()

# Global auth service reference - will be set by main.py
auth_service = None

# HTTP Bearer for JWT tokens
security = HTTPBearer()

def set_auth_service(service):
    """Set the auth service instance from main.py"""
    global auth_service
    auth_service = service

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get the current authenticated user."""
    print(f"🔍 DEBUG: auth_service is None: {auth_service is None}")
    print(f"🔍 DEBUG: token: {credentials.credentials[:50]}...")
    
    if not auth_service:
        print("❌ DEBUG: AuthService not available")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not available"
        )
    
    try:
        print("🔄 DEBUG: Calling auth_service.get_current_user()")
        # Use AuthService's get_current_user method which expects HTTPAuthorizationCredentials
        user = await auth_service.get_current_user(credentials)
        print(f"👤 DEBUG: User returned: {user is not None}")
        if not user:
            print("❌ DEBUG: No user returned from auth service")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        print(f"✅ DEBUG: User authenticated: {user.username}")
        return user
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        print(f"💥 DEBUG: Exception in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

def get_document_processor() -> DocumentProcessor:
    """Get a DocumentProcessor instance."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured"
        )
    return DocumentProcessor(openai_api_key) 


def get_llamaindex_document_processor():
    """Get LlamaIndex document processor instance."""
    from services.llamaindex_document_processor import create_llamaindex_document_processor
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    return create_llamaindex_document_processor(openai_api_key)


def get_llamaindex_rag_service():
    """Get LlamaIndex RAG service instance."""
    from services.llamaindex_rag_service import create_llamaindex_rag_service
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    return create_llamaindex_rag_service(openai_api_key) 