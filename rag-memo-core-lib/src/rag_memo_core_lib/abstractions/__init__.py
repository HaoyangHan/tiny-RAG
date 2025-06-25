"""
TinyRAG Core Library Abstractions

Abstract base classes and interfaces for the TinyRAG core library.
Provides extensible and pluggable architecture following SOLID principles.
"""

from .base import BaseConfig, BaseProvider, BaseProcessor
from .llm import LLMProvider, LLMRequest, LLMResponse, LLMMessage, LLMConfig
from .vector_store import VectorStore, VectorDocument, SearchResult, VectorStoreConfig
from .document_processor import DocumentProcessor, ProcessingResult, DocumentProcessorConfig
from .generator import Generator, GeneratorConfig, GenerationContext
from .evaluator import Evaluator, EvaluatorConfig, EvaluationContext
from .workflow import WorkflowEngine, WorkflowConfig, WorkflowContext

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
    
    # Document processing abstractions
    "DocumentProcessor",
    "ProcessingResult",
    "DocumentProcessorConfig",
    
    # Generator abstractions
    "Generator",
    "GeneratorConfig",
    "GenerationContext",
    
    # Evaluator abstractions
    "Evaluator",
    "EvaluatorConfig", 
    "EvaluationContext",
    
    # Workflow abstractions
    "WorkflowEngine",
    "WorkflowConfig",
    "WorkflowContext",
] 