"""
Vector Store Abstractions for TinyRAG Core Library

Provides abstract interfaces for vector databases with support for
similarity search, metadata filtering, and document management.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Union
from pydantic import BaseModel, Field
from ..abstractions.base import BaseProvider, BaseConfig


class VectorDocument(BaseModel):
    """
    Document with vector embedding and metadata.
    
    Standardized format for storing documents in vector databases
    with support for rich metadata and embedding vectors.
    """
    
    id: str = Field(description="Unique document identifier")
    content: str = Field(description="Document content/text")
    embedding: List[float] = Field(description="Vector embedding")
    
    # Metadata for filtering and organization
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    
    # Optional fields for enhanced functionality
    chunk_index: Optional[int] = Field(None, description="Chunk index for multi-chunk documents")
    parent_id: Optional[str] = Field(None, description="Parent document ID for chunks")
    source: Optional[str] = Field(None, description="Source file or URL")
    timestamp: Optional[float] = Field(None, description="Creation or update timestamp")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True


class SearchResult(BaseModel):
    """
    Search result from vector store.
    
    Encapsulates a retrieved document with similarity score
    and ranking information.
    """
    
    document: VectorDocument = Field(description="Retrieved document")
    score: float = Field(description="Similarity score (0.0 to 1.0)")
    rank: int = Field(description="Result rank (1-based)")
    
    # Additional result metadata
    distance: Optional[float] = Field(None, description="Distance metric (if different from score)")
    explanation: Optional[Dict[str, Any]] = Field(None, description="Search explanation/debug info")


class SearchQuery(BaseModel):
    """
    Search query parameters for vector store.
    
    Comprehensive search configuration with filtering,
    ranking, and result customization options.
    """
    
    # Core search parameters
    query_embedding: List[float] = Field(description="Query vector embedding")
    top_k: int = Field(default=5, ge=1, le=100, description="Number of results to return")
    
    # Filtering
    filter_metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    include_metadata: bool = Field(default=True, description="Include metadata in results")
    
    # Score thresholds
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum similarity score")
    max_distance: Optional[float] = Field(None, ge=0.0, description="Maximum distance threshold")
    
    # Result customization
    include_embeddings: bool = Field(default=False, description="Include embeddings in results")
    search_params: Optional[Dict[str, Any]] = Field(None, description="Provider-specific search parameters")


class VectorStoreConfig(BaseConfig):
    """
    Configuration for vector stores.
    
    Comprehensive configuration supporting various vector database
    backends with connection, performance, and security settings.
    """
    
    # Collection/Index settings
    collection_name: str = Field(description="Collection/index name")
    dimension: int = Field(description="Vector dimension")
    similarity_metric: str = Field(default="cosine", description="Similarity metric (cosine, dot, euclidean)")
    
    # Connection settings
    host: Optional[str] = Field(None, description="Vector store host")
    port: Optional[int] = Field(None, description="Vector store port")
    url: Optional[str] = Field(None, description="Complete connection URL")
    
    # Authentication
    api_key: Optional[str] = Field(None, description="API key for authentication")
    username: Optional[str] = Field(None, description="Username for authentication")
    password: Optional[str] = Field(None, description="Password for authentication")
    
    # Performance settings
    batch_size: int = Field(default=100, ge=1, le=1000, description="Batch size for operations")
    connection_pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    index_type: Optional[str] = Field(None, description="Index type (HNSW, IVF, etc.)")
    
    # Storage settings
    persist_path: Optional[str] = Field(None, description="Local persistence path")
    backup_enabled: bool = Field(default=False, description="Enable automatic backups")
    
    # Provider-specific settings
    provider_settings: Optional[Dict[str, Any]] = Field(None, description="Provider-specific configuration")


class VectorStore(BaseProvider[List[SearchResult]], ABC):
    """
    Abstract base class for vector stores.
    
    Defines the interface for vector databases with support for
    document storage, similarity search, and collection management.
    """
    
    def __init__(self, config: VectorStoreConfig) -> None:
        """
        Initialize vector store.
        
        Args:
            config: Vector store configuration
        """
        super().__init__(config)
        self.config: VectorStoreConfig = config
    
    @abstractmethod
    async def create_collection(
        self, 
        collection_name: Optional[str] = None,
        dimension: Optional[int] = None,
        similarity_metric: Optional[str] = None
    ) -> bool:
        """
        Create a new collection/index.
        
        Args:
            collection_name: Name of the collection (uses config default if None)
            dimension: Vector dimension (uses config default if None)
            similarity_metric: Similarity metric (uses config default if None)
            
        Returns:
            bool: True if created successfully
            
        Raises:
            VectorStoreError: If creation fails
        """
        pass
    
    @abstractmethod
    async def delete_collection(self, collection_name: Optional[str] = None) -> bool:
        """
        Delete a collection/index.
        
        Args:
            collection_name: Name of the collection (uses config default if None)
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            VectorStoreError: If deletion fails
        """
        pass
    
    @abstractmethod
    async def collection_exists(self, collection_name: Optional[str] = None) -> bool:
        """
        Check if collection exists.
        
        Args:
            collection_name: Name of the collection (uses config default if None)
            
        Returns:
            bool: True if collection exists
        """
        pass
    
    @abstractmethod
    async def add_documents(self, documents: List[VectorDocument]) -> bool:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents with embeddings
            
        Returns:
            bool: True if added successfully
            
        Raises:
            VectorStoreError: If addition fails
        """
        pass
    
    @abstractmethod
    async def search(self, query: SearchQuery) -> List[SearchResult]:
        """
        Search for similar documents.
        
        Args:
            query: Search query with parameters
            
        Returns:
            List[SearchResult]: Search results ranked by similarity
            
        Raises:
            VectorStoreError: If search fails
        """
        pass
    
    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """
        Get a specific document by ID.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Optional[VectorDocument]: Document if found, None otherwise
            
        Raises:
            VectorStoreError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """
        Delete documents from vector store.
        
        Args:
            document_ids: List of document IDs to delete
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            VectorStoreError: If deletion fails
        """
        pass
    
    @abstractmethod
    async def update_document(self, document: VectorDocument) -> bool:
        """
        Update existing document.
        
        Args:
            document: Updated document
            
        Returns:
            bool: True if updated successfully
            
        Raises:
            VectorStoreError: If update fails
        """
        pass
    
    @abstractmethod
    async def count_documents(self, filter_metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents in the collection.
        
        Args:
            filter_metadata: Optional metadata filter
            
        Returns:
            int: Number of documents
            
        Raises:
            VectorStoreError: If count fails
        """
        pass
    
    # Convenience methods with default implementations
    
    async def search_by_embedding(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None
    ) -> List[SearchResult]:
        """
        Search using embedding vector (convenience method).
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            filter_metadata: Metadata filters
            min_score: Minimum similarity score
            
        Returns:
            List[SearchResult]: Search results
        """
        query = SearchQuery(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata,
            min_score=min_score
        )
        return await self.search(query)
    
    async def add_document(self, document: VectorDocument) -> bool:
        """
        Add a single document (convenience method).
        
        Args:
            document: Document to add
            
        Returns:
            bool: True if added successfully
        """
        return await self.add_documents([document])
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a single document (convenience method).
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            bool: True if deleted successfully
        """
        return await self.delete_documents([document_id])
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get collection information.
        
        Returns:
            Dict[str, Any]: Collection metadata and statistics
        """
        return {
            "collection_name": self.config.collection_name,
            "dimension": self.config.dimension,
            "similarity_metric": self.config.similarity_metric,
            "document_count": await self.count_documents(),
            "exists": await self.collection_exists()
        } 