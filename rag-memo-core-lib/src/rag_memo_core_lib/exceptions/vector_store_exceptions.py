"""Vector Store Exception Classes"""

from typing import Optional, Dict, Any
from .base import ProviderError

class VectorStoreError(ProviderError):
    """Base exception for vector store errors."""
    pass

class VectorStoreConnectionError(VectorStoreError):
    """Exception raised for connection errors."""
    pass

class VectorStoreIndexError(VectorStoreError):
    """Exception raised for index/collection errors.""" 
    pass

class VectorStoreQueryError(VectorStoreError):
    """Exception raised for query errors."""
    pass 