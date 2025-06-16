"""Application constants for RAG Memo Core Library."""

from typing import Dict, List

# Version information
VERSION = "1.2.0"
API_VERSION = "v1"

# Default models
DEFAULT_MODELS = {
    "openai": {
        "default": "gpt-4-mini-2025-04-16",
        "available": [
            "gpt-4-mini-2025-04-16",
            "gpt-4.1-nano-2025-04-14",
        ]
    },
    "gemini": {
        "default": "gemini-2.0-flash-lite",
        "available": [
            "gemini-2.0-flash-lite",
            "gemini-2.5-pro-preview-06-05",
            "gemini-2.5-flash-preview-05-20",
        ]
    }
}

# Embedding models
EMBEDDING_MODELS = {
    "openai": [
        "text-embedding-3-small",
        "text-embedding-3-large",
        "text-embedding-ada-002",
    ],
    "default": "text-embedding-3-small"
}

# Document processing constants
SUPPORTED_DOCUMENT_FORMATS = {
    "text": ["pdf", "docx", "doc", "txt", "md", "html"],
    "image": ["png", "jpg", "jpeg", "tiff", "bmp", "gif"],
    "all": ["pdf", "docx", "doc", "txt", "md", "html", "png", "jpg", "jpeg", "tiff", "bmp", "gif"]
}

# File size limits (in bytes)
FILE_SIZE_LIMITS = {
    "pdf": 50 * 1024 * 1024,      # 50MB
    "docx": 25 * 1024 * 1024,     # 25MB
    "doc": 25 * 1024 * 1024,      # 25MB
    "txt": 10 * 1024 * 1024,      # 10MB
    "md": 10 * 1024 * 1024,       # 10MB
    "html": 10 * 1024 * 1024,     # 10MB
    "png": 20 * 1024 * 1024,      # 20MB
    "jpg": 20 * 1024 * 1024,      # 20MB
    "jpeg": 20 * 1024 * 1024,     # 20MB
    "tiff": 50 * 1024 * 1024,     # 50MB
    "bmp": 20 * 1024 * 1024,      # 20MB
    "gif": 10 * 1024 * 1024,      # 10MB
}

# Text processing constants
TEXT_PROCESSING = {
    "min_chunk_size": 100,
    "max_chunk_size": 4000,
    "default_chunk_size": 1000,
    "min_overlap": 0,
    "max_overlap": 500,
    "default_overlap": 200,
    "sentence_separators": [".", "!", "?", "\n\n"],
    "paragraph_separators": ["\n\n", "\n\n\n"],
}

# RAG framework constants
RAG_FRAMEWORKS = {
    "llamaindex": {
        "name": "LlamaIndex",
        "version": "0.10.0",
        "description": "Advanced document processing and retrieval framework",
        "features": ["multi_modal", "advanced_retrieval", "custom_indices"]
    },
    "langchain": {
        "name": "LangChain",
        "version": "0.1.0",
        "description": "Flexible framework with agent capabilities",
        "features": ["agents", "memory", "chains", "tools"]
    }
}

# Vector store configurations
VECTOR_STORES = {
    "mongodb_atlas": {
        "name": "MongoDB Atlas Vector Search",
        "dimensions": {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        },
        "similarity_metrics": ["cosine", "euclidean", "dotProduct"]
    },
    "chroma": {
        "name": "ChromaDB",
        "dimensions": {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        },
        "similarity_metrics": ["cosine", "l2", "ip"]
    }
}

# OCR configurations
OCR_ENGINES = {
    "tesseract": {
        "name": "Tesseract OCR",
        "supported_languages": ["eng", "fra", "deu", "spa", "ita", "por", "rus", "chi_sim", "chi_tra", "jpn", "kor"],
        "default_config": "--oem 3 --psm 6"
    }
}

# Evaluation metrics
EVALUATION_METRICS = {
    "faithfulness": {
        "description": "How well the generated content is grounded in the source material",
        "scale": "0-5",
        "higher_is_better": True
    },
    "relevance": {
        "description": "How relevant the generated content is to the query",
        "scale": "0-5",
        "higher_is_better": True
    },
    "coherence": {
        "description": "How well-structured and coherent the generated content is",
        "scale": "0-5",
        "higher_is_better": True
    },
    "citation_accuracy": {
        "description": "How accurately citations are attributed to source material",
        "scale": "0-1",
        "higher_is_better": True
    }
}

# Error codes
ERROR_CODES = {
    "DOCUMENT_PARSING_ERROR": "DOC_001",
    "UNSUPPORTED_FORMAT": "DOC_002",
    "FILE_TOO_LARGE": "DOC_003",
    "CORRUPTED_FILE": "DOC_004",
    "LLM_API_ERROR": "LLM_001",
    "LLM_RATE_LIMIT": "LLM_002",
    "LLM_TIMEOUT": "LLM_003",
    "EMBEDDING_ERROR": "EMB_001",
    "VECTOR_STORE_ERROR": "VEC_001",
    "RAG_PROCESSING_ERROR": "RAG_001",
    "CONFIGURATION_ERROR": "CFG_001",
    "VALIDATION_ERROR": "VAL_001",
}

# HTTP status codes for API responses
HTTP_STATUS_CODES = {
    "SUCCESS": 200,
    "CREATED": 201,
    "ACCEPTED": 202,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "UNPROCESSABLE_ENTITY": 422,
    "TOO_MANY_REQUESTS": 429,
    "INTERNAL_SERVER_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
}

# Logging configuration
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "document_processing_time": 30,  # seconds
    "memo_generation_time": 60,      # seconds
    "api_response_time": 0.2,        # seconds
    "max_memory_usage": 1024,        # MB
    "max_cpu_usage": 80,             # percentage
}

# Cache settings
CACHE_SETTINGS = {
    "default_ttl": 3600,             # 1 hour
    "embedding_cache_ttl": 86400,    # 24 hours
    "document_cache_ttl": 7200,      # 2 hours
    "llm_response_cache_ttl": 1800,  # 30 minutes
}

# Rate limiting
RATE_LIMITS = {
    "openai": {
        "requests_per_minute": 3000,
        "tokens_per_minute": 250000,
    },
    "gemini": {
        "requests_per_minute": 1000,
        "tokens_per_minute": 100000,
    },
    "default": {
        "requests_per_minute": 100,
        "tokens_per_minute": 10000,
    }
} 