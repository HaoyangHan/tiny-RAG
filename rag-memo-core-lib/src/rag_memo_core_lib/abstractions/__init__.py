"""
TinyRAG Core Library Abstractions

Abstract base classes and interfaces for the TinyRAG core library.
Provides extensible and pluggable architecture following SOLID principles.
"""

from .base import BaseConfig, BaseProvider, BaseProcessor
from .llm import LLMProvider, LLMRequest, LLMResponse, LLMMessage, LLMConfig
from .vector_store import VectorStore, VectorDocument, SearchResult, VectorStoreConfig

__all__ = [
    # Base abstractions
    "BaseConfig",
    "BaseProvider", 
    "BaseProcessor",
    
    # LLM abstractions
    "LLMProvider",
    "LLMRequest",
    "LLMResponse", 
    "LLMMessage",
    "LLMConfig",
    
    # Vector store abstractions
    "VectorStore",
    "VectorDocument",
    "SearchResult",
    "VectorStoreConfig",
] 