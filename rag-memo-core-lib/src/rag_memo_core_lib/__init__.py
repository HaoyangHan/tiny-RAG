"""
RAG Memo Core Library

A comprehensive core library for TinyRAG document processing and memo generation platform.
Provides shared models, services, and utilities for enterprise-grade RAG capabilities.
"""

__version__ = "1.2.0"
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

__all__ = [
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
] 