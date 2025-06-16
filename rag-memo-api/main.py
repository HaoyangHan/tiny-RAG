from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings
from typing import Dict, Any
import logging
import uvicorn

from database import Database
from routes import documents, memos

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings."""
    APP_NAME: str = "TinyRAG API"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TinyRAG"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "tinyrag"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379"
    
    # LLM API settings
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai-proxy.org/v1"
    GEMINI_API_KEY: str = ""
    GEMINI_BASE_URL: str = "https://api.openai-proxy.org/google"
    
    # RAG framework settings
    RAG_FRAMEWORK: str = "llamaindex"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    VECTOR_STORE: str = "mongodb_atlas"
    
    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Worker settings
    DRAMATIQ_BROKER: str = "redis"
    WORKER_CONCURRENCY: int = 4
    REQUEST_TIMEOUT: int = 300
    
    # Document processing settings
    MAX_CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_FILE_SIZE: int = 52428800
    SUPPORTED_FORMATS: str = "pdf,docx,png,jpg,jpeg,tiff"
    OCR_ENGINE: str = "tesseract"
    OCR_LANGUAGES: str = "eng"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(memos.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    await Database.connect_to_database(
        settings.MONGODB_URL,
        settings.MONGODB_DB_NAME
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown."""
    await Database.close_database_connection()

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint returning API information."""
    return {
        "name": settings.APP_NAME,
        "version": "1.1.0",
        "status": "operational",
        "features": [
            "Document processing",
            "Memo generation",
            "Multi-LLM support (OpenAI, Gemini)",
            "Citation system"
        ]
    }

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 