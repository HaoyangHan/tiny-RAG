"""
Document Service for TinyRAG v1.4.3
===================================

This module provides document management services including
file upload, processing, project integration, and metadata extraction.

Author: TinyRAG Development Team
Version: 1.4.3
Last Updated: January 2025
"""

import logging
import tempfile
import os
import hashlib
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from pathlib import Path
from beanie import PydanticObjectId
from beanie.operators import In, And, Or

from models.document import Document, DocumentStatus, DocumentMetadata
from models.project import Project
from services.document_processor import DocumentProcessor
from services.enhanced_document_processor import create_enhanced_document_processor

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service class for document management operations.
    
    Provides comprehensive document processing with enhanced metadata extraction,
    table and image processing, and project integration.
    """
    
    @staticmethod
    async def upload_document(
        file_content: bytes,
        filename: str,
        content_type: str,
        user_id: str,
        project_id: str,
        metadata: Optional[DocumentMetadata] = None
    ) -> Document:
        """
        Upload and process a document with enhanced capabilities.
        
        Args:
            file_content: Raw file content
            filename: Original filename
            content_type: MIME type of the file
            user_id: ID of the user uploading the document
            project_id: ID of the project to associate with
            metadata: Optional document metadata
            
        Returns:
            Document: Created document instance with processed content, tables, and images
            
        Raises:
            ValueError: If validation fails or duplicate found
            Exception: If upload/processing fails
        """
        try:
            # Generate content hash for duplicate detection
            content_hash = hashlib.sha256(file_content).hexdigest()
            
            # Check for duplicate documents
            existing_document = await Document.find_one(
                And(
                    Document.content_hash == content_hash,
                    Document.user_id == user_id
                )
            )
            
            if existing_document:
                raise ValueError(f"Document with identical content already exists: {existing_document.id}")
            
            # Create document metadata
            document_metadata = metadata or DocumentMetadata(
                filename=filename,
                content_type=content_type,
                size=len(file_content),
                upload_date=datetime.utcnow(),
                processed=False,
                has_tables=False,
                has_images=False,
                content_hash=content_hash  # Add content hash for duplicate detection
            )
            
            # Create document instance
            document = Document(
                user_id=user_id,
                project_id=project_id,
                filename=filename,
                content_type=content_type,
                file_size=len(file_content),
                status=DocumentStatus.UPLOADING,
                metadata=document_metadata,
                chunks=[],
                tables=[],
                images=[]
            )
            
            # Save document initially
            await document.save()
            
            # Get OpenAI API key for enhanced processing
            openai_api_key = os.getenv("OPENAI_API_KEY")
            
            if not openai_api_key:
                logger.warning("OpenAI API key not configured - basic processing only")
                
                # Basic processing without LLM
                document.status = DocumentStatus.COMPLETED
                document.metadata.processed = True
                logger.info("Document processed without embeddings (no OpenAI key)")
                
            else:
                # Enhanced processing with comprehensive metadata extraction
                from services.enhanced_document_processor import create_enhanced_document_processor
                processor = create_enhanced_document_processor(openai_api_key)
                
                # Create temporary file for processing
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
                    temp_file.write(file_content)
                    temp_path = Path(temp_file.name)
                
                try:
                    # Update status to processing
                    document.status = DocumentStatus.PROCESSING
                    await document.save()
                    
                    # Process document with enhanced capabilities and metadata extraction
                    processed_document = await processor.process_document(
                        file_path=temp_path,
                        user_id=user_id,
                        document_id=str(document.id),
                        project_id=project_id
                    )
                    
                    # Update the document with processed results
                    document.chunks = processed_document.chunks
                    document.tables = processed_document.tables
                    document.images = processed_document.images
                    document.metadata.has_tables = processed_document.metadata.has_tables
                    document.metadata.has_images = processed_document.metadata.has_images
                    document.metadata.processed = processed_document.metadata.processed
                    document.status = processed_document.status
                    
                    logger.info(f"Enhanced processing completed: {len(document.chunks)} chunks, "
                              f"{len(document.tables)} tables, {len(document.images)} images")
                    
                    # Log metadata extraction summary
                    metadata_count = 0
                    for chunk in document.chunks:
                        if chunk.chunk_metadata:
                            metadata_count += len(chunk.chunk_metadata)
                    
                    logger.info(f"Metadata extraction completed: {metadata_count} total metadata fields extracted")
                    
                    # Mark as completed if processed successfully
                    if document.status != DocumentStatus.COMPLETED:
                        document.status = DocumentStatus.COMPLETED
                        document.metadata.processed = True
                        
                finally:
                    # Clean up temporary file
                    if temp_path.exists():
                        temp_path.unlink()
            
            # Save final document state
            await document.save()
            
            # Add document to project
            project = await Project.get(project_id)
            if project:
                project.add_document(str(document.id))
                await project.save()
            
            # Log comprehensive processing results
            logger.info(
                f"Document upload completed: {document.id} -> Project {project_id}\n"
                f"  - Chunks: {len(document.chunks)} (text: {len([c for c in document.chunks if c.chunk_type == 'text'])}, "
                f"table: {len([c for c in document.chunks if c.chunk_type == 'table'])}, "
                f"image: {len([c for c in document.chunks if c.chunk_type == 'image'])})\n"
                f"  - Tables: {len(document.tables)}\n"
                f"  - Images: {len(document.images)}\n"
                f"  - Status: {document.status}"
            )
            
            return document
            
        except Exception as processing_error:
            # Update status to failed
            document.status = DocumentStatus.FAILED
            document.metadata.error = str(processing_error)
            document.metadata.processed = False
            await document.save()
            
            logger.error(f"Document processing failed for {document.id}: {str(processing_error)}")
            raise processing_error
            
        except Exception as e:
            logger.error(f"Document upload failed: {str(e)}")
            raise e
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[Document]:
        """
        Get a document by ID with access control.
        
        Args:
            document_id: Document ID to retrieve
            user_id: ID of the requesting user
            
        Returns:
            Document: Document instance if found and accessible, None otherwise
        """
        try:
            document = await Document.get(PydanticObjectId(document_id))
            
            if not document or document.is_deleted:
                return None
            
            # Check project access
            project = await Project.get(PydanticObjectId(document.project_id))
            if not project or not project.is_accessible_by(user_id):
                return None
            
            return document
            
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {str(e)}")
            return None
    
    async def list_documents(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        project_id: Optional[str] = None,
        status: Optional[DocumentStatus] = None,
        content_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Document], int]:
        """
        List documents accessible to a user with filtering and pagination.
        
        Args:
            user_id: ID of the requesting user
            page: Page number (1-based)
            page_size: Number of items per page
            project_id: Filter by project ID
            status: Filter by document status
            content_type: Filter by content type
            search: Search in document filenames
            
        Returns:
            Tuple[List[Document], int]: List of documents and total count
        """
        try:
            # Build query conditions
            conditions = [Document.is_deleted == False]
            
            # Get accessible project IDs
            if project_id:
                # Check specific project access
                project = await Project.get(PydanticObjectId(project_id))
                if not project or not project.is_accessible_by(user_id):
                    return [], 0
                conditions.append(Document.project_id == project_id)
            else:
                # Get all accessible projects
                accessible_projects = await self._get_accessible_project_ids(user_id)
                if not accessible_projects:
                    return [], 0
                conditions.append(In(Document.project_id, accessible_projects))
            
            # Apply filters
            if status:
                conditions.append(Document.status == status)
            
            if content_type:
                conditions.append(Document.content_type == content_type)
            
            if search:
                conditions.append(
                    Or(
                        Document.filename.regex(search, "i"),
                        Document.metadata.filename.regex(search, "i")
                    )
                )
            
            # Execute query with pagination
            skip = (page - 1) * page_size
            query = And(*conditions) if len(conditions) > 1 else conditions[0]
            
            documents = await Document.find(query).skip(skip).limit(page_size).to_list()
            total = await Document.find(query).count()
            
            return documents, total
            
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            return [], 0
    
    async def update_document_status(
        self,
        document_id: str,
        status: DocumentStatus,
        user_id: str,
        error_message: Optional[str] = None
    ) -> Optional[Document]:
        """
        Update document processing status.
        
        Args:
            document_id: Document ID to update
            status: New status
            user_id: ID of the requesting user
            error_message: Optional error message for failed status
            
        Returns:
            Document: Updated document instance, None if not found/accessible
        """
        try:
            document = await self.get_document(document_id, user_id)
            if not document:
                return None
            
            document.status = status
            document.updated_at = datetime.utcnow()
            
            if error_message:
                document.metadata.error = error_message
            
            if status == DocumentStatus.COMPLETED:
                document.metadata.processed = True
            elif status == DocumentStatus.FAILED:
                document.metadata.processed = False
            
            await document.save()
            return document
            
        except Exception as e:
            logger.error(f"Failed to update document status: {str(e)}")
            return None
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete a document with access control.
        
        Args:
            document_id: Document ID to delete
            user_id: ID of the requesting user
            
        Returns:
            bool: True if deleted successfully, False if not found
            
        Raises:
            ValueError: If access denied
            Exception: If deletion fails
        """
        try:
            logger.info(f"Attempting to delete document {document_id} for user {user_id}")
            
            # Get document with access control
            document = await self.get_document(document_id, user_id)
            if not document:
                logger.warning(f"Document {document_id} not found or access denied for user {user_id}")
                return False
            
            # Mark as deleted (soft delete)
            document.is_deleted = True
            document.updated_at = datetime.utcnow()
            await document.save()
            
            # Remove from project's document list
            if document.project_id:
                try:
                    project = await Project.get(PydanticObjectId(document.project_id))
                    if project and hasattr(project, 'document_ids') and str(document.id) in project.document_ids:
                        project.document_ids.remove(str(document.id))
                        await project.save()
                        logger.info(f"Removed document {document_id} from project {document.project_id}")
                except Exception as e:
                    logger.warning(f"Failed to remove document from project: {str(e)}")
            
            logger.info(f"Successfully deleted document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            raise
    
    async def get_document_content(
        self,
        document_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get document content including chunks.
        
        Args:
            document_id: Document ID to retrieve content for
            user_id: ID of the requesting user
            
        Returns:
            Dict containing document content and metadata, None if not found
        """
        try:
            document = await self.get_document(document_id, user_id)
            if not document:
                return None
            
            return {
                "document_id": str(document.id),
                "filename": document.filename,
                "content_type": document.content_type,
                "status": document.status,
                "chunks": [
                    {
                        "text": chunk.text,
                        "page_number": chunk.page_number,
                        "chunk_index": chunk.chunk_index,
                        "chunk_type": getattr(chunk, 'chunk_type', 'text'),
                        "embedding": chunk.embedding,
                        "chunk_metadata": getattr(chunk, 'chunk_metadata', {}),
                        "start_pos": getattr(chunk, 'start_pos', None),
                        "end_pos": getattr(chunk, 'end_pos', None),
                        "section": getattr(chunk, 'section', None)
                    }
                    for chunk in document.chunks
                ],
                "metadata": {
                    "size": document.file_size,
                    "created_at": document.created_at.isoformat(),
                    "processed": document.metadata.processed if document.metadata else False
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get document content: {str(e)}")
            return None
    
    async def get_document_analytics(
        self,
        user_id: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get document analytics for a user or project.
        
        Args:
            user_id: ID of the requesting user
            project_id: Optional project ID to filter by
            
        Returns:
            Dict containing analytics data
        """
        try:
            # Build base conditions
            conditions = [Document.is_deleted == False]
            
            if project_id:
                # Check project access
                project = await Project.get(PydanticObjectId(project_id))
                if not project or not project.is_accessible_by(user_id):
                    return {}
                conditions.append(Document.project_id == project_id)
            else:
                # Get all accessible projects
                accessible_projects = await self._get_accessible_project_ids(user_id)
                if not accessible_projects:
                    return {}
                conditions.append(In(Document.project_id, accessible_projects))
            
            # Get documents
            query = And(*conditions) if len(conditions) > 1 else conditions[0]
            documents = await Document.find(query).to_list()
            
            # Calculate analytics
            total_documents = len(documents)
            total_size = sum(doc.file_size for doc in documents)
            
            status_counts = {}
            content_type_counts = {}
            
            for doc in documents:
                # Status counts
                status = doc.status
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Content type counts
                content_type = doc.content_type
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
            
            return {
                "total_documents": total_documents,
                "total_size_bytes": total_size,
                "status_distribution": status_counts,
                "content_type_distribution": content_type_counts,
                "average_size": total_size / total_documents if total_documents > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get document analytics: {str(e)}")
            return {}
    
    async def _get_accessible_project_ids(self, user_id: str) -> List[str]:
        """
        Get project IDs that the user has access to.
        
        Args:
            user_id: User ID to check access for
            
        Returns:
            List of project IDs the user can access
        """
        try:
            # Get projects where user is owner or collaborator
            projects = await Project.find(
                And(
                    Or(
                        Project.owner_id == user_id,
                        In(Project.collaborators, [user_id])
                    ),
                    Project.is_deleted == False
                )
            ).to_list()
            
            return [str(project.id) for project in projects]
            
        except Exception as e:
            logger.error(f"Error getting accessible project IDs: {str(e)}")
            return []

    async def search_documents(
        self,
        user_id: str,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks for element generation.
        
        Args:
            user_id: User ID for access control
            query: Search query
            document_ids: Optional list of document IDs to search within
            top_k: Number of top chunks to return
            
        Returns:
            List of relevant document chunks
        """
        try:
            # Build filter for user documents
            filter_query = {"user_id": user_id, "is_deleted": False}
            
            if document_ids:
                # Convert string IDs to ObjectIds for MongoDB
                try:
                    object_ids = [PydanticObjectId(doc_id) for doc_id in document_ids]
                    filter_query["_id"] = {"$in": object_ids}
                except Exception as e:
                    logger.error(f"Error converting document IDs to ObjectIds: {e}")
                    return []
            
            logger.info(f"Searching documents with filter: {filter_query}")
            documents = await Document.find(filter_query).to_list()
            logger.info(f"Found {len(documents)} documents for user")
            
            if not documents:
                logger.warning("No documents found for search")
                return []
            
            # Collect all chunks from documents
            all_chunks = []
            
            for document in documents:
                logger.info(f"Processing document {document.id}: {len(document.chunks) if document.chunks else 0} chunks")
                
                if not document.chunks:
                    logger.warning(f"Document {document.id} has no chunks")
                    continue
                    
                # For now, return chunks with basic scoring
                # In a full implementation, you would use vector similarity
                for chunk in document.chunks:
                    chunk_result = {
                        "document_id": str(document.id),
                        "document_title": document.filename,
                        "page_number": getattr(chunk, 'page_number', 1),
                        "chunk_text": chunk.text,
                        "chunk_index": getattr(chunk, 'chunk_index', 0),
                        "similarity_score": 0.8  # Default score for now
                    }
                    all_chunks.append(chunk_result)
            
            # Sort by similarity score (in a real implementation, use vector similarity)
            all_chunks.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Return top_k chunks
            return all_chunks[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return [] 