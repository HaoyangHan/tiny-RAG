"""
Metadata extraction framework for TinyRAG.

This module provides advanced metadata extraction capabilities for documents
and chunks, enabling enhanced retrieval and reranking strategies.
"""

from .extractors import (
    BaseMetadataExtractor,
    DateExtractor,
    KeywordExtractor,
    SummarizationExtractor,
    EntityExtractor,
    MetadataExtractionPipeline
)
from .reranker import (
    MetadataReranker,
    HybridReranker,
    RerankerConfig
)
from .schemas import (
    MetadataSchema,
    ChunkMetadata,
    DocumentMetadata,
    ExtractionResult
)

__all__ = [
    # Extractors
    "BaseMetadataExtractor",
    "DateExtractor", 
    "KeywordExtractor",
    "SummarizationExtractor",
    "EntityExtractor",
    "MetadataExtractionPipeline",
    
    # Rerankers
    "MetadataReranker",
    "HybridReranker", 
    "RerankerConfig",
    
    # Schemas
    "MetadataSchema",
    "ChunkMetadata",
    "DocumentMetadata", 
    "ExtractionResult"
] 