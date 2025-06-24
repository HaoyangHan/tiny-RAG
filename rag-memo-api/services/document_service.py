from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import tempfile
import motor.motor_asyncio
import redis.asyncio as redis
from fastapi import UploadFile

from models.document import Document, DocumentChunk
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class DocumentService:
    """Service for managing documents and their processing."""
    
    def __init__(self, database: motor.motor_asyncio.AsyncIOMotorDatabase, 
                 redis_client: redis.Redis, llm_extractor=None):
        """Initialize the document service."""
        self.database = database
        self.redis_client = redis_client
        self.llm_extractor = llm_extractor
        self.processor = None
        
    def set_processor(self, processor: DocumentProcessor):
        """Set the document processor."""
        self.processor = processor
    
    async def upload_and_process(self, file: UploadFile, user_id: str, 
                                extract_metadata: bool = True) -> Document:
        """Upload and process a document file."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = Path(temp_file.name)

            # Create document processor if not available
            if not self.processor:
                from dependencies import get_document_processor
                self.processor = get_document_processor()

            # Process document
            document = await self.processor.process_document(temp_path, user_id)
            
            # Set filename from uploaded file
            if hasattr(document, 'filename'):
                document.filename = file.filename
            elif hasattr(document, 'metadata'):
                document.metadata.filename = file.filename
            
            # Extract metadata if LLM extractor is available and requested
            if extract_metadata and self.llm_extractor and hasattr(document, 'chunks') and document.chunks:
                try:
                    sample_text = " ".join([chunk.text for chunk in document.chunks[:3]])
                    metadata = await self.llm_extractor.extract_metadata(
                        sample_text, 
                        file.filename
                    )
                    
                    if metadata:
                        if hasattr(document, 'metadata'):
                            document.metadata.extracted_metadata = metadata
                        await document.save()
                        
                except Exception as e:
                    logger.warning(f"Failed to extract metadata: {e}")
            
            # Clean up temporary file
            temp_path.unlink()
            
            return document
            
        except Exception as e:
            logger.error(f"Error uploading and processing document: {str(e)}")
            raise
    
    async def create_document(self, file_path: Path, user_id: str, 
                            filename: Optional[str] = None) -> Document:
        """Create and process a new document."""
        try:
            if not self.processor:
                raise ValueError("Document processor not initialized")
                
            document = await self.processor.process_document(file_path, user_id)
            
            # Extract metadata if LLM extractor is available
            if self.llm_extractor and document.chunks:
                try:
                    sample_text = " ".join([chunk.text for chunk in document.chunks[:3]])
                    metadata = await self.llm_extractor.extract_metadata(
                        sample_text, 
                        filename or document.metadata.filename
                    )
                    
                    if metadata:
                        document.metadata.extracted_metadata = metadata
                        await document.save()
                        
                except Exception as e:
                    logger.warning(f"Failed to extract metadata: {e}")
            
            return document
            
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[Document]:
        """Get a document by ID for a specific user."""
        try:
            document = await Document.get(document_id)
            if document and document.user_id == user_id:
                return document
            return None
            
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            return None
    
    async def get_user_document(self, document_id: str, user_id: str) -> Optional[Document]:
        """Get a document by ID for a specific user (alias for get_document)."""
        return await self.get_document(document_id, user_id)
    
    async def list_documents(self, user_id: str, skip: int = 0, 
                           limit: int = 20) -> List[Document]:
        """List documents for a user."""
        try:
            documents = await Document.find(
                {"user_id": user_id}
            ).skip(skip).limit(limit).to_list()
            
            return documents
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return []
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document."""
        try:
            document = await Document.get(document_id)
            if document and document.user_id == user_id:
                await document.delete()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    async def search_documents(self, user_id: str, query: str, 
                             document_ids: Optional[List[str]] = None,
                             top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant document chunks."""
        try:
            # Build filter for user documents
            filter_query = {"user_id": user_id}
            if document_ids:
                # Convert string IDs to ObjectIds for MongoDB
                from beanie import PydanticObjectId
                try:
                    object_ids = [PydanticObjectId(doc_id) for doc_id in document_ids]
                    filter_query["_id"] = {"$in": object_ids}
                except Exception as e:
                    logger.error(f"🔍 Error converting document IDs to ObjectIds: {e}")
                    # Fallback: try as strings
                    filter_query["_id"] = {"$in": document_ids}
            
            logger.info(f"🔍 Search filter: {filter_query}")
            documents = await Document.find(filter_query).to_list()
            logger.info(f"🔍 Found {len(documents)} documents for user")
            
            if not documents:
                logger.warning("🔍 No documents found for search")
                return []
            
            # Search through all chunks
            all_results = []
            
            for document in documents:
                logger.info(f"🔍 Processing document {document.id}: {len(document.chunks) if document.chunks else 0} chunks")
                
                if not document.chunks:
                    logger.warning(f"🔍 Document {document.id} has no chunks")
                    continue
                    
                # Use the processor to find similar chunks
                if self.processor:
                    logger.info(f"🔍 Using processor to find similar chunks for query: '{query}'")
                    similar_chunks = await self.processor.get_similar_chunks(
                        query, document, top_k
                    )
                    logger.info(f"🔍 Found {len(similar_chunks)} similar chunks")
                    
                    for i, chunk in enumerate(similar_chunks):
                        result = {
                            "document_id": str(document.id),
                            "document_title": document.metadata.filename,
                            "chunk_text": chunk.text,
                            "page_number": chunk.page_number,
                            "chunk_index": chunk.chunk_index,
                            "metadata": getattr(document.metadata, 'extracted_metadata', {}) or {}
                        }
                        all_results.append(result)
                        logger.info(f"🔍 Added chunk {i+1}: {chunk.text[:100]}...")
                else:
                    logger.error(f"🔍 No processor available for document search!")
            
            # Sort by relevance and return top results
            logger.info(f"🔍 Total results before limiting: {len(all_results)}")
            final_results = all_results[:top_k]
            logger.info(f"🔍 Returning {len(final_results)} final results")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    async def get_document_stats(self, user_id: str) -> Dict[str, Any]:
        """Get document statistics for a user."""
        try:
            total_docs = await Document.find({"user_id": user_id}).count()
            processed_docs = await Document.find({
                "user_id": user_id,
                "metadata.processed": True
            }).count()
            
            return {
                "total_documents": total_docs,
                "processed_documents": processed_docs,
                "processing_rate": processed_docs / total_docs if total_docs > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting document stats: {str(e)}")
            return {"total_documents": 0, "processed_documents": 0, "processing_rate": 0} 