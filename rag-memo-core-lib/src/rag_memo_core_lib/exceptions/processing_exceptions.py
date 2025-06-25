"""Processing Exception Classes"""

from .base import ProcessingError

class DocumentProcessingError(ProcessingError):
    """Exception raised for document processing errors."""
    pass

class EmbeddingError(ProcessingError):
    """Exception raised for embedding generation errors."""
    pass

class ChunkingError(ProcessingError):
    """Exception raised for text chunking errors."""
    pass

class ExtractionError(ProcessingError):
    """Exception raised for content extraction errors."""
    pass 