"""
RAG Memo Core Library

A comprehensive core library for TinyRAG document processing and memo generation platform.
Provides shared models, services, utilities, and abstractions for enterprise-grade RAG capabilities.
"""

__version__ = "1.4.0"
__author__ = "TinyRAG Team"
__email__ = "team@tinyrag.com"

# Core exports
from .config.settings import CoreSettings
from .models.document import Document
from .models.generation import GenerationRequest, GenerationResponse
from .models.llm import LLMMessage, LLMResponse
from .services.rag.factory import RAGFactory
from .services.parsers.factory import ParserFactory
from .services.llm.factory import LLMFactory

# V1.4 Abstractions
from .abstractions.base import BaseConfig, BaseProvider, BaseProcessor
from .abstractions.llm import LLMProvider, LLMRequest, LLMResponse as AbstractLLMResponse, LLMMessage as AbstractLLMMessage, LLMConfig
from .abstractions.vector_store import VectorStore, VectorDocument, SearchResult, VectorStoreConfig

# V1.4 Factories  
from .factories.llm_factory import LLMFactory as AbstractLLMFactory
from .factories.vector_store_factory import VectorStoreFactory

# V1.4 Implementations
from .implementations.llm.mock_provider import MockLLMProvider

# V1.4 Exceptions
from .exceptions import TinyRAGError, LLMError, VectorStoreError

__all__ = [
    # Core
    "__version__",
    "CoreSettings",
    "Document",
    "GenerationRequest",
    "GenerationResponse",
    "LLMMessage",
    "LLMResponse",
    "RAGFactory",
    "ParserFactory",
    "LLMFactory",
    
    # V1.4 Abstractions
    "BaseConfig",
    "BaseProvider", 
    "BaseProcessor",
    "LLMProvider",
    "LLMRequest",
    "AbstractLLMResponse",
    "AbstractLLMMessage", 
    "LLMConfig",
    "VectorStore",
    "VectorDocument",
    "SearchResult",
    "VectorStoreConfig",
    
    # V1.4 Factories
    "AbstractLLMFactory",
    "VectorStoreFactory",
    
    # V1.4 Implementations
    "MockLLMProvider",
    
    # V1.4 Exceptions
    "TinyRAGError",
    "LLMError", 
    "VectorStoreError",
] 