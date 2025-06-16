"""Core settings configuration for RAG Memo Core Library."""

from typing import List, Literal, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class CoreSettings(BaseSettings):
    """Core configuration settings for RAG Memo platform.
    
    This class manages all configuration settings for the RAG Memo platform,
    including database connections, LLM API keys, RAG framework settings,
    and document processing parameters.
    """
    
    # Database settings
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URL"
    )
    MONGODB_DB_NAME: str = Field(
        default="tinyrag",
        description="MongoDB database name"
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for caching and task queue"
    )
    
    # LLM API settings
    OPENAI_API_KEY: str = Field(
        description="OpenAI API key for GPT models"
    )
    GEMINI_API_KEY: str = Field(
        description="Google Gemini API key"
    )
    OPENAI_BASE_URL: str = Field(
        default="https://api.openai-proxy.org/v1",
        description="OpenAI API base URL (supports proxy)"
    )
    GEMINI_BASE_URL: str = Field(
        default="https://api.openai-proxy.org/google",
        description="Gemini API base URL (supports proxy)"
    )
    
    # RAG framework settings
    RAG_FRAMEWORK: Literal["llamaindex", "langchain"] = Field(
        default="llamaindex",
        description="Default RAG framework to use"
    )
    EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="Default embedding model"
    )
    VECTOR_STORE: str = Field(
        default="mongodb_atlas",
        description="Vector store backend"
    )
    
    # Document processing settings
    MAX_CHUNK_SIZE: int = Field(
        default=1000,
        description="Maximum chunk size for text splitting",
        ge=100,
        le=4000
    )
    CHUNK_OVERLAP: int = Field(
        default=200,
        description="Overlap between text chunks",
        ge=0,
        le=500
    )
    MAX_FILE_SIZE: int = Field(
        default=50 * 1024 * 1024,  # 50MB
        description="Maximum file size in bytes",
        ge=1024,  # 1KB minimum
        le=100 * 1024 * 1024  # 100MB maximum
    )
    SUPPORTED_FORMATS: List[str] = Field(
        default=["pdf", "docx", "png", "jpg", "jpeg", "tiff"],
        description="Supported document formats"
    )
    
    # OCR settings
    OCR_ENGINE: str = Field(
        default="tesseract",
        description="OCR engine for image processing"
    )
    OCR_LANGUAGES: List[str] = Field(
        default=["eng"],
        description="OCR languages to support"
    )
    
    # Performance settings
    MAX_CONCURRENT_TASKS: int = Field(
        default=4,
        description="Maximum concurrent processing tasks",
        ge=1,
        le=16
    )
    REQUEST_TIMEOUT: int = Field(
        default=300,  # 5 minutes
        description="Request timeout in seconds",
        ge=30,
        le=1800
    )
    
    # Logging settings
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_FORMAT: str = Field(
        default="json",
        description="Log format (json or text)"
    )
    
    # Development settings
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    TESTING: bool = Field(
        default=False,
        description="Enable testing mode"
    )
    
    @validator("CHUNK_OVERLAP")
    def validate_chunk_overlap(cls, v: int, values: dict) -> int:
        """Validate that chunk overlap is less than chunk size."""
        max_chunk_size = values.get("MAX_CHUNK_SIZE", 1000)
        if v >= max_chunk_size:
            raise ValueError("CHUNK_OVERLAP must be less than MAX_CHUNK_SIZE")
        return v
    
    @validator("SUPPORTED_FORMATS")
    def validate_supported_formats(cls, v: List[str]) -> List[str]:
        """Validate and normalize supported formats."""
        valid_formats = {
            "pdf", "docx", "doc", "txt", "md", "html",
            "png", "jpg", "jpeg", "tiff", "bmp", "gif"
        }
        normalized = []
        for fmt in v:
            fmt_lower = fmt.lower().strip()
            if fmt_lower in valid_formats:
                normalized.append(fmt_lower)
            else:
                raise ValueError(f"Unsupported format: {fmt}")
        return normalized
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()
    
    def get_llm_config(self, provider: str) -> dict:
        """Get LLM configuration for a specific provider.
        
        Args:
            provider: LLM provider name ("openai" or "gemini")
            
        Returns:
            Configuration dictionary for the provider
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider.lower() == "openai":
            return {
                "api_key": self.OPENAI_API_KEY,
                "base_url": self.OPENAI_BASE_URL,
                "timeout": self.REQUEST_TIMEOUT,
            }
        elif provider.lower() == "gemini":
            return {
                "api_key": self.GEMINI_API_KEY,
                "base_url": self.GEMINI_BASE_URL,
                "timeout": self.REQUEST_TIMEOUT,
            }
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def get_database_config(self) -> dict:
        """Get database configuration.
        
        Returns:
            Database configuration dictionary
        """
        return {
            "mongodb_url": self.MONGODB_URL,
            "database_name": self.MONGODB_DB_NAME,
            "redis_url": self.REDIS_URL,
        }
    
    def get_processing_config(self) -> dict:
        """Get document processing configuration.
        
        Returns:
            Processing configuration dictionary
        """
        return {
            "max_chunk_size": self.MAX_CHUNK_SIZE,
            "chunk_overlap": self.CHUNK_OVERLAP,
            "max_file_size": self.MAX_FILE_SIZE,
            "supported_formats": self.SUPPORTED_FORMATS,
            "ocr_engine": self.OCR_ENGINE,
            "ocr_languages": self.OCR_LANGUAGES,
        }
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True 