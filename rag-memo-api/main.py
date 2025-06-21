"""
TinyRAG API - Main FastAPI Application with Authentication and Enhanced Metadata Extraction.

This is the main entry point for the TinyRAG API service, integrating:
- JWT-based authentication and authorization
- LLM-powered metadata extraction
- Enhanced reranking capabilities
- Document processing and RAG workflows
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import motor.motor_asyncio
from beanie import init_beanie
import redis.asyncio as redis

# Import authentication components
from auth.service import AuthService
from auth.routes import init_auth_routes
from auth.models import User, APIKey, UserRole

# Import core models and services
from models.document import Document
from models.generation import Generation
from services.document_service import DocumentService
from services.generation_service import GenerationService

# Import enhanced metadata components
from rag_memo_core_lib.metadata.llm_extractors import create_llm_extractor
from rag_memo_core_lib.metadata.enhanced_reranker import create_enhanced_reranker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global services
auth_service: Optional[AuthService] = None
document_service: Optional[DocumentService] = None
generation_service: Optional[GenerationService] = None
llm_extractor = None
enhanced_reranker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    global auth_service, document_service, generation_service, llm_extractor, enhanced_reranker
    
    # Startup
    logger.info("Starting TinyRAG API v1.3...")
    
    try:
        # Initialize MongoDB connection
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://tinyrag-mongodb:27017")
        client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        database = client.tinyrag
        
        # Initialize Beanie with all document models
        await init_beanie(
            database=database,
            document_models=[User, APIKey, Document, Generation]
        )
        logger.info("Database initialized successfully")
        
        # Initialize Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://tinyrag-redis:6379")
        redis_client = redis.from_url(redis_url)
        await redis_client.ping()
        logger.info("Redis connection established")
        
        # Initialize authentication service
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        if not jwt_secret:
            raise ValueError("JWT_SECRET_KEY environment variable is required")
        
        auth_service = AuthService(
            secret_key=jwt_secret,
            algorithm=os.getenv("JWT_ALGORITHM", "HS256")
        )
        logger.info("Authentication service initialized")
        
        # Initialize LLM metadata extractor
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            llm_extractor = create_llm_extractor(
                provider="openai",
                model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                api_key=openai_api_key
            )
            logger.info("LLM metadata extractor initialized")
        else:
            logger.warning("OPENAI_API_KEY not found, LLM features disabled")
        
        # Initialize enhanced reranker
        if llm_extractor:
            enhanced_reranker = create_enhanced_reranker(
                llm_provider="openai",
                llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
                llm_api_key=openai_api_key
            )
            logger.info("Enhanced reranker initialized")
        
        # Initialize core services
        document_service = DocumentService(
            database=database,
            redis_client=redis_client,
            llm_extractor=llm_extractor
        )
        
        generation_service = GenerationService(
            database=database,
            redis_client=redis_client,
            document_service=document_service,
            enhanced_reranker=enhanced_reranker
        )
        
        logger.info("Core services initialized")
        
        # Create default admin user if none exists
        await create_default_admin_user()
        
        logger.info("TinyRAG API startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to start TinyRAG API: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down TinyRAG API...")
    if redis_client:
        await redis_client.close()
    logger.info("TinyRAG API shutdown completed")


async def create_default_admin_user():
    """Create default admin user if none exists."""
    try:
        admin_count = await User.find({"role": UserRole.ADMIN}).count()
        
        if admin_count == 0:
            default_admin = User(
                email=os.getenv("DEFAULT_ADMIN_EMAIL", "admin@tinyrag.local"),
                username=os.getenv("DEFAULT_ADMIN_USERNAME", "admin"),
                hashed_password=auth_service.get_password_hash(
                    os.getenv("DEFAULT_ADMIN_PASSWORD", "TinyRAG2024!")
                ),
                full_name="Default Administrator",
                role=UserRole.ADMIN,
                status="active"
            )
            
            await default_admin.save()
            logger.info(f"Default admin user created: {default_admin.email}")
            logger.warning("Please change the default admin password immediately!")
        
    except Exception as e:
        logger.error(f"Failed to create default admin user: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="TinyRAG API",
    description="Advanced RAG system with LLM-powered metadata extraction and intelligent reranking",
    version="1.3.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security)
) -> User:
    """Get current authenticated user."""
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not available"
        )
    return await auth_service.get_current_user(credentials)


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.3.0",
        "services": {
            "auth": auth_service is not None,
            "llm_extractor": llm_extractor is not None,
            "enhanced_reranker": enhanced_reranker is not None,
            "document_service": document_service is not None,
            "generation_service": generation_service is not None
        }
    }


# Document endpoints
@app.post("/documents/upload")
@limiter.limit("10/minute")
async def upload_document(
    file: UploadFile = File(...),
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Upload and process a document with enhanced metadata extraction."""
    if not document_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document service not available"
        )
    
    try:
        # Process document with LLM-enhanced metadata extraction
        document = await document_service.upload_and_process(
            file=file,
            user_id=str(current_user.id),
            extract_metadata=True
        )
        
        return {
            "document_id": str(document.id),
            "filename": document.filename,
            "status": document.status,
            "metadata_extracted": document.metadata is not None,
            "message": "Document uploaded and processing started"
        }
        
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {str(e)}"
        )


@app.get("/documents")
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """List user's documents."""
    if not document_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document service not available"
        )
    
    documents = await document_service.list_user_documents(
        user_id=str(current_user.id),
        skip=skip,
        limit=limit
    )
    
    return {
        "documents": [
            {
                "id": str(doc.id),
                "filename": doc.filename,
                "status": doc.status,
                "created_at": doc.created_at,
                "metadata_available": doc.metadata is not None
            }
            for doc in documents
        ]
    }


@app.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get document details with metadata."""
    if not document_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document service not available"
        )
    
    document = await document_service.get_user_document(
        document_id=document_id,
        user_id=str(current_user.id)
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {
        "id": str(document.id),
        "filename": document.filename,
        "status": document.status,
        "content": document.content,
        "metadata": document.metadata,
        "created_at": document.created_at,
        "updated_at": document.updated_at
    }


# Generation endpoints
@app.post("/generate")
@limiter.limit("5/minute")
async def generate_response(
    request: GenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate response using enhanced RAG with metadata-aware reranking."""
    if not generation_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Generation service not available"
        )
    
    try:
        generation = await generation_service.create_generation(
            query=request.query,
            document_ids=request.document_ids,
            user_id=str(current_user.id),
            use_enhanced_reranking=True
        )
        
        return {
            "generation_id": str(generation.id),
            "status": generation.status,
            "message": "Generation started"
        }
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@app.get("/generations/{generation_id}")
async def get_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get generation result with enhanced metadata and explanations."""
    if not generation_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Generation service not available"
        )
    
    generation = await generation_service.get_user_generation(
        generation_id=generation_id,
        user_id=str(current_user.id)
    )
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation not found"
        )
    
    return {
        "id": str(generation.id),
        "query": generation.query,
        "status": generation.status,
        "response": generation.response,
        "sources": generation.sources,
        "metadata": generation.metadata,
        "created_at": generation.created_at,
        "completed_at": generation.completed_at
    }


# Admin endpoints
@app.get("/admin/users")
async def admin_list_users(
    skip: int = 0,
    limit: int = 50,
    current_admin: User = Depends(get_current_admin_user)
):
    """Admin endpoint to list all users."""
    users = await User.find().skip(skip).limit(limit).to_list()
    
    return {
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "status": user.status,
                "created_at": user.created_at,
                "last_login": user.last_login
            }
            for user in users
        ]
    }


@app.get("/admin/system-stats")
async def admin_system_stats(
    current_admin: User = Depends(get_current_admin_user)
):
    """Admin endpoint for system statistics."""
    try:
        user_count = await User.find().count()
        document_count = await Document.find().count()
        generation_count = await Generation.find().count()
        
        return {
            "users": user_count,
            "documents": document_count,
            "generations": generation_count,
            "services": {
                "auth_service": auth_service is not None,
                "llm_extractor": llm_extractor is not None,
                "enhanced_reranker": enhanced_reranker is not None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system statistics"
        )


# Include authentication routes
@app.on_event("startup")
async def setup_auth_routes():
    """Setup authentication routes after services are initialized."""
    if auth_service:
        auth_router = init_auth_routes(auth_service)
        app.include_router(auth_router)


# Request/Response models
from pydantic import BaseModel
from typing import List, Optional

class GenerationRequest(BaseModel):
    """Request model for generation endpoint."""
    query: str
    document_ids: Optional[List[str]] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    ) 