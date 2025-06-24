"""
TinyRAG API - Main FastAPI Application with Authentication and Enhanced Metadata Extraction.

This is the main entry point for the TinyRAG API service, integrating:
- JWT-based authentication and authorization
- LLM-powered metadata extraction (OpenAI/Gemini)
- Enhanced reranking capabilities
- Document processing and RAG workflows
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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

# Import v1.4 models
from models import (
    Project, Element, ElementGeneration, Evaluation,
    BaseDocument, TenantType, TaskType, ElementType, ElementStatus,
    GenerationStatus, EvaluationStatus, DocumentStatus, ProjectStatus, VisibilityType
)

# Import route modules
from routes.documents import router as documents_router
from routes.memos import router as memos_router

# Import v1.4 API routes
from api.v1.router import api_router as v1_router

# Import enhanced metadata components (temporarily disabled for v1.3 testing)
# from rag_memo_core_lib.metadata.llm_extractors import create_llm_extractor
# from rag_memo_core_lib.metadata.enhanced_reranker import create_enhanced_reranker

# Request/Response models
class GenerationRequest(BaseModel):
    """Request model for generation endpoint."""
    query: str
    document_ids: Optional[List[str]] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

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
async def lifespan(app_instance: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    global auth_service, document_service, generation_service, llm_extractor, enhanced_reranker
    
    # Startup
    logger.info("Starting TinyRAG API v1.3...")
    
    try:
        # Initialize MongoDB connection
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://tinyrag-mongodb:27017")
        client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        database = client.tinyrag
        
        # Initialize Beanie with all document models (v1.3 + v1.4)
        await init_beanie(
            database=database,
            document_models=[
                # v1.3 legacy models
                User, APIKey, Document, Generation,
                # v1.4 models
                Project, Element, ElementGeneration, Evaluation
            ]
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
        
        # Set global auth service for dependency injection
        from auth.service import set_auth_service as set_global_auth_service
        set_global_auth_service(auth_service)
        logger.info("Authentication service initialized")
        
        # Initialize LLM metadata extractor (temporarily disabled for v1.3 testing)
        # llm_provider = os.getenv("LLM_PROVIDER", "openai")
        # llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        
        # if llm_provider == "openai":
        #     api_key = os.getenv("OPENAI_API_KEY")
        #     base_url = os.getenv("OPENAI_BASE_URL")
        # elif llm_provider == "gemini":
        #     api_key = os.getenv("GEMINI_API_KEY")
        #     base_url = os.getenv("GEMINI_BASE_URL")
        #     if llm_model == "gpt-4o-mini":  # Default model override for Gemini
        #         llm_model = "gemini-2.0-flash-lite"
        # else:
        #     logger.warning(f"Unknown LLM provider: {llm_provider}, defaulting to OpenAI")
        #     llm_provider = "openai"
        #     api_key = os.getenv("OPENAI_API_KEY")
        #     base_url = os.getenv("OPENAI_BASE_URL")
        
        # if api_key:
        #     llm_extractor = create_llm_extractor(
        #         provider=llm_provider,
        #         model=llm_model,
        #         api_key=api_key,
        #         base_url=base_url
        #     )
        #     logger.info(f"LLM metadata extractor initialized with {llm_provider}")
        # else:
        #     logger.warning(f"{llm_provider.upper()}_API_KEY not found, LLM features disabled")
        
        # Initialize enhanced reranker (temporarily disabled for v1.3 testing)
        # if llm_extractor:
        #     enhanced_reranker = create_enhanced_reranker(
        #         llm_provider=llm_provider,
        #         llm_model=llm_model,
        #         llm_api_key=api_key
        #     )
        #     logger.info("Enhanced reranker initialized")
        
        logger.info("LLM features temporarily disabled for v1.3 testing")
        
        # Initialize core services
        document_service = DocumentService(
            database=database,
            redis_client=redis_client,
            llm_extractor=None  # Temporarily disabled
        )
        
        # Initialize and set document processor
        from dependencies import get_document_processor
        document_processor = get_document_processor()
        document_service.set_processor(document_processor)
        logger.info("Document processor initialized and set")
        
        generation_service = GenerationService(
            database=database,
            redis_client=redis_client,
            document_service=document_service,
            enhanced_reranker=None  # Temporarily disabled
        )
        
        logger.info("Core services initialized")
        
        # Initialize authentication routes
        if auth_service:
            auth_router = init_auth_routes(auth_service)
            app_instance.include_router(auth_router)
            logger.info("Authentication routes initialized")
            
            # Set auth service in dependencies for proper authentication
            from dependencies import set_auth_service
            set_auth_service(auth_service)
            
            # Set auth service in documents router
            from routes.documents import set_auth_service as set_docs_auth_service
            set_docs_auth_service(auth_service)
            
            # Set auth service in v1.4 auth routes
            from api.v1.auth.routes import set_auth_service as set_v14_auth_service
            set_v14_auth_service(auth_service)
        
        # Include legacy routes (v1.3)
        app_instance.include_router(documents_router)
        app_instance.include_router(memos_router)
        logger.info("Legacy v1.3 routes initialized")
        
        # Include v1.4 API routes
        app_instance.include_router(v1_router, prefix="/api/v1")
        logger.info("v1.4 API routes initialized")
        
        # Create default admin user if none exists
        await create_default_admin_user()
        
        logger.info("TinyRAG API startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to start TinyRAG API: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down TinyRAG API...")
    if 'redis_client' in locals():
        await redis_client.close()
    logger.info("TinyRAG API shutdown completed")


async def create_default_admin_user():
    """Create default admin user if none exists."""
    try:
        admin_count = await User.find({"role": UserRole.ADMIN}).count()
        
        if admin_count == 0:
            default_admin = User(
                email=os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com"),
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
    description="""
    # TinyRAG API v1.4 - Project-Based RAG Platform
    
    A comprehensive RAG (Retrieval-Augmented Generation) platform with:
    
    ## 🚀 Core Features
    - **Project-Based Architecture**: Organize work by tenant types (HR, CODING, FINANCIAL_REPORT, etc.)
    - **Element Management**: Create and manage prompt templates, MCP configurations, and agentic tools
    - **LLM Generation**: Track and manage AI-generated content with comprehensive metrics
    - **Evaluation Framework**: LLM-as-a-judge system for content quality assessment
    - **Document Processing**: Intelligent document upload, processing, and analytics
    - **Multi-User Collaboration**: Granular permissions and collaboration features
    
    ## 📊 API Structure
    - **Legacy v1.3 Routes**: `/documents`, `/memos`, `/generate` (backward compatibility)
    - **v1.4 Routes**: `/api/v1/*` (new project-based architecture)
    
    ## 🔐 Authentication
    All endpoints require JWT authentication. Get your token from `/auth/login`.
    
    ## 📖 Documentation
    - **Interactive API Docs**: Available at `/docs` (Swagger UI)
    - **Alternative Docs**: Available at `/redoc` (ReDoc)
    """,
    version="1.4.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints"
        },
        {
            "name": "Projects",
            "description": "Project management operations with tenant-based organization"
        },
        {
            "name": "Elements", 
            "description": "Template and tool management (prompts, MCP configs, agentic tools)"
        },
        {
            "name": "Generations",
            "description": "LLM content generation tracking and analytics"
        },
        {
            "name": "Evaluations",
            "description": "LLM-as-a-judge evaluation framework and scoring"
        },
        {
            "name": "Documents",
            "description": "Document upload, processing, and content management"
        },
        {
            "name": "Users",
            "description": "User profile management and analytics"
        },
        {
            "name": "Legacy v1.3",
            "description": "Backward compatibility endpoints from v1.3"
        },
        {
            "name": "Health & Admin",
            "description": "System health checks and administrative operations"
        }
    ]
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


# Dependency functions moved to dependencies.py


# Import get_current_user from dependencies
from dependencies import get_current_user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# Health check endpoint
@app.get("/health", tags=["Health & Admin"])
async def health_check():
    """
    Health check endpoint with comprehensive service status.
    
    Returns system health status including all v1.3 and v1.4 services.
    """
    return {
        "status": "healthy",
        "version": "1.4.0",
        "api_versions": {
            "v1.3": "legacy endpoints (/documents, /memos, /generate)",
            "v1.4": "project-based endpoints (/api/v1/*)"
        },
        "services": {
            # Legacy v1.3 services
            "auth": auth_service is not None,
            "llm_extractor": llm_extractor is not None,
            "enhanced_reranker": enhanced_reranker is not None,
            "document_service": document_service is not None,
            "generation_service": generation_service is not None,
            # v1.4 services status
            "v1.4_api": True,
            "project_service": True,
            "element_service": True,
            "element_generation_service": True,
            "evaluation_service": True,
            "user_service": True,
            "v1.4_document_service": True
        },
        "database": {
            "models_registered": [
                "User", "APIKey", "Document", "Generation",  # v1.3
                "Project", "Element", "ElementGeneration", "Evaluation"  # v1.4
            ]
        },
        "llm_config": {
            "provider": os.getenv("LLM_PROVIDER", "openai"),
            "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
            "status": "temporarily_disabled_for_testing"
        }
    }


# Document endpoints
# Document upload endpoint moved to routes/documents.py


# Document endpoints moved to routes/documents.py


# Generation endpoints
@app.post("/generate", tags=["Legacy v1.3"])
@limiter.limit("5/minute")
async def generate_response(
    request: Request,
    generation_request: GenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate response using enhanced RAG with metadata-aware reranking.
    
    **Legacy v1.3 endpoint** - Use `/api/v1/generations/` for new implementations.
    
    Example request:
    ```json
    {
        "query": "What is the main topic of the uploaded documents?",
        "document_ids": ["60f4d2e5e8b4a12345678901"],
        "max_tokens": 1000,
        "temperature": 0.7
    }
    ```
    """
    if not generation_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Generation service not available"
        )
    
    try:
        generation = await generation_service.create_generation(
            query=generation_request.query,
            document_ids=generation_request.document_ids,
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


@app.get("/generations/{generation_id}", tags=["Legacy v1.3"])
async def get_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get generation result with enhanced metadata and explanations.
    
    **Legacy v1.3 endpoint** - Use `/api/v1/generations/{generation_id}` for new implementations.
    
    Returns detailed generation information including:
    - Generation status and response
    - Source documents used
    - Metadata and processing details
    """
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


@app.post("/debug/process-generation/{generation_id}", tags=["Health & Admin"])
async def debug_process_generation(
    generation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Debug endpoint to manually trigger generation processing.
    
    **Development/Debug endpoint** - Manually processes a generation that may be stuck.
    """
    if not generation_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Generation service not available"
        )
    
    try:
        logger.info(f"🔧 DEBUG: Manually triggering processing for generation {generation_id}")
        generation = await generation_service.process_generation(generation_id)
        
        return {
            "message": "Processing completed successfully",
            "generation_id": generation_id,
            "status": generation.status,
            "response": generation.response
        }
        
    except Exception as e:
        logger.error(f"🔥 DEBUG: Generation processing failed: {str(e)}")
        return {
            "error": str(e),
            "generation_id": generation_id,
            "message": "Processing failed"
        }


# Admin endpoints
@app.get("/admin/users", tags=["Health & Admin"])
async def admin_list_users(
    skip: int = 0,
    limit: int = 50,
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Admin endpoint to list all users.
    
    **Requires admin privileges.** Returns paginated list of all system users.
    
    Parameters:
    - skip: Number of users to skip (for pagination)
    - limit: Maximum number of users to return (max 50)
    """
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


@app.get("/admin/system-stats", tags=["Health & Admin"])
async def admin_system_stats(
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Admin endpoint for comprehensive system statistics.
    
    **Requires admin privileges.** Returns detailed system statistics including:
    - User, document, generation counts (v1.3 + v1.4)
    - Service health status
    - LLM configuration
    - v1.4 model statistics
    """
    try:
        # v1.3 legacy model counts
        user_count = await User.find().count()
        document_count = await Document.find().count()
        generation_count = await Generation.find().count()
        
        # v1.4 model counts
        project_count = await Project.find().count()
        element_count = await Element.find().count()
        element_generation_count = await ElementGeneration.find().count()
        evaluation_count = await Evaluation.find().count()
        
        return {
            "v1.3_models": {
                "users": user_count,
                "documents": document_count,
                "generations": generation_count
            },
            "v1.4_models": {
                "projects": project_count,
                "elements": element_count,
                "element_generations": element_generation_count,
                "evaluations": evaluation_count
            },
            "services": {
                "auth_service": auth_service is not None,
                "llm_extractor": llm_extractor is not None,
                "enhanced_reranker": enhanced_reranker is not None,
                "document_service": document_service is not None,
                "generation_service": generation_service is not None,
                "v1.4_api": True
            },
            "llm_config": {
                "provider": os.getenv("LLM_PROVIDER", "openai"),
                "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
                "status": "temporarily_disabled_for_testing"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system statistics"
        )


# Authentication routes are now initialized in the lifespan startup


# Moved to top of file - see line 50


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    ) 