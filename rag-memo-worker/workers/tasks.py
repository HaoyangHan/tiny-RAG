"""
Dramatiq tasks for TinyRAG worker service.

This module contains background tasks for document processing,
embedding generation, and other RAG-related operations.
"""

import os
import logging
from typing import Dict, Any, List
from dramatiq import actor
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AgeLimit, TimeLimit, Retries
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv('DRAMATIQ_BROKER', 'redis://redis:6379')

# Create Redis broker with middleware
results_backend = RedisBackend(url=REDIS_URL)
broker = RedisBroker(url=REDIS_URL)
broker.add_middleware(AgeLimit(max_age=3600000))  # 1 hour
broker.add_middleware(TimeLimit(time_limit=300000))  # 5 minutes
broker.add_middleware(Retries(max_retries=3))
broker.add_middleware(Results(backend=results_backend))

# Set the broker globally for dramatiq
import dramatiq
dramatiq.set_broker(broker)


@actor(broker=broker, max_retries=3)
def process_document(document_id: str, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an uploaded document for RAG indexing.
    
    Args:
        document_id: Unique identifier for the document
        file_path: Path to the uploaded file
        metadata: Document metadata (filename, type, etc.)
    
    Returns:
        Dict containing processing results
    """
    logger.info(f"Processing document {document_id}: {file_path}")
    
    try:
        # Mock processing - replace with actual implementation
        result = {
            "document_id": document_id,
            "status": "processed",
            "chunks_created": 10,
            "embeddings_generated": 10,
            "file_path": file_path,
            "metadata": metadata
        }
        
        logger.info(f"Successfully processed document {document_id}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process document {document_id}: {str(e)}")
        raise


@actor(broker=broker, max_retries=2)
def generate_embeddings(text_chunks: List[str], document_id: str) -> Dict[str, Any]:
    """
    Generate embeddings for text chunks.
    
    Args:
        text_chunks: List of text chunks to embed
        document_id: Document identifier
    
    Returns:
        Dict containing embedding results
    """
    logger.info(f"Generating embeddings for {len(text_chunks)} chunks from document {document_id}")
    
    try:
        # Mock embedding generation - replace with actual implementation
        result = {
            "document_id": document_id,
            "embeddings_count": len(text_chunks),
            "status": "completed"
        }
        
        logger.info(f"Successfully generated embeddings for document {document_id}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate embeddings for document {document_id}: {str(e)}")
        raise


@actor(broker=broker, max_retries=1)
def cleanup_temp_files(file_paths: List[str]) -> Dict[str, Any]:
    """
    Clean up temporary files after processing.
    
    Args:
        file_paths: List of file paths to clean up
    
    Returns:
        Dict containing cleanup results
    """
    logger.info(f"Cleaning up {len(file_paths)} temporary files")
    
    try:
        cleaned_count = 0
        for file_path in file_paths:
            # Mock cleanup - replace with actual file deletion
            logger.debug(f"Cleaned up file: {file_path}")
            cleaned_count += 1
        
        result = {
            "cleaned_files": cleaned_count,
            "status": "completed"
        }
        
        logger.info(f"Successfully cleaned up {cleaned_count} files")
        return result
        
    except Exception as e:
        logger.error(f"Failed to cleanup files: {str(e)}")
        raise


@actor(broker=broker)
def health_check() -> Dict[str, Any]:
    """
    Health check task for monitoring worker status.
    
    Returns:
        Dict containing health status
    """
    return {
        "status": "healthy",
        "worker": "tinyrag-worker",
        "timestamp": os.environ.get('HOSTNAME', 'unknown')
    }


# Export the broker for dramatiq CLI
__all__ = ['broker', 'process_document', 'generate_embeddings', 'cleanup_temp_files', 'health_check'] 