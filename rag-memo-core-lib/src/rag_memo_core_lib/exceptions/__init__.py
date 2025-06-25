"""
TinyRAG Core Library Exceptions

Custom exception hierarchy for the TinyRAG core library.
Provides structured error handling with detailed context information.
"""

from .base import (
    TinyRAGError,
    ConfigurationError,
    ValidationError,
    InitializationError,
    ProviderError,
    ProcessingError,
    FactoryError
)

from .llm_exceptions import (
    LLMError,
    LLMTimeoutError,
    LLMQuotaError,
    LLMAuthenticationError,
    LLMModelError
)

from .vector_store_exceptions import (
    VectorStoreError,
    VectorStoreConnectionError,
    VectorStoreIndexError,
    VectorStoreQueryError
)

from .processing_exceptions import (
    DocumentProcessingError,
    EmbeddingError,
    ChunkingError,
    ExtractionError
)

from .generation_exceptions import (
    GenerationError,
    TemplateError,
    ContextError,
    WorkflowError
)

from .evaluation_exceptions import (
    EvaluationError,
    MetricError,
    ScoreError,
    ComparisonError
)

__all__ = [
    # Base exceptions
    "TinyRAGError",
    "ConfigurationError", 
    "ValidationError",
    "InitializationError",
    "ProviderError",
    "ProcessingError",
    "FactoryError",
    
    # LLM exceptions
    "LLMError",
    "LLMTimeoutError",
    "LLMQuotaError", 
    "LLMAuthenticationError",
    "LLMModelError",
    
    # Vector store exceptions
    "VectorStoreError",
    "VectorStoreConnectionError",
    "VectorStoreIndexError",
    "VectorStoreQueryError",
    
    # Processing exceptions
    "DocumentProcessingError",
    "EmbeddingError",
    "ChunkingError",
    "ExtractionError",
    
    # Generation exceptions
    "GenerationError",
    "TemplateError",
    "ContextError",
    "WorkflowError",
    
    # Evaluation exceptions
    "EvaluationError",
    "MetricError",
    "ScoreError",
    "ComparisonError",
] 