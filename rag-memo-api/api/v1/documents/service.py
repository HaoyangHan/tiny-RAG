"""
Document service for TinyRAG v1.4.

This module contains the business logic for document management including
file upload, processing, project integration, and document analytics.
"""

import logging
import hashlib
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from beanie import PydanticObjectId
from beanie.operators import In, And, Or

from models import Document, Project, DocumentStatus
from models.document import DocumentMetadata, DocumentChunk

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service class for document management operations in v1.4.
    
    Handles all business logic related to documents including file upload,
    processing, project integration, and analytics while maintaining
    compatibility with existing document processing logic.
    """
    
    def __init__(self):
        """Initialize the document service."""
        self.legacy_service = None
    
    async def _check_duplicate_document(
        self,
        project_id: str,
        file_content: bytes,
        filename: str
    ) -> Optional[Document]:
        """
        Check if a document with the same content already exists in the project.
        
        Args:
            project_id: Project ID to check within
            file_content: File content bytes for hash comparison
            filename: Original filename
            
        Returns:
            Document: Existing document if duplicate found, None otherwise
        """
        try:
            # Generate content hash
            content_hash = hashlib.sha256(file_content).hexdigest()
            
            # Check for existing documents in the same project with the same hash or filename
            existing_docs = await Document.find(
                And(
                    Document.project_id == project_id,
                    Document.is_deleted == False,
                    Or(
                        Document.filename == filename,
                        # We'll store content_hash in metadata for comparison
                        Document.metadata.content_hash == content_hash
                    )
                )
            ).to_list()
            
            # Check for exact content match
            for doc in existing_docs:
                if hasattr(doc.metadata, 'content_hash') and doc.metadata.content_hash == content_hash:
                    logger.info(f"Found duplicate document by content hash: {doc.id}")
                    return doc
                elif doc.filename == filename and doc.file_size == len(file_content):
                    logger.info(f"Found potential duplicate document by filename and size: {doc.id}")
                    return doc
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking for duplicate document: {str(e)}")
            return None
    
    async def upload_document(
        self,
        project_id: str,
        file_content: bytes,
        filename: str,
        content_type: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Document:
        """
        Upload and process a document for a project.
        
        Args:
            project_id: Associated project ID
            file_content: File content bytes
            filename: Original filename
            content_type: MIME content type
            user_id: ID of the uploading user
            metadata: Optional document metadata
            
        Returns:
            Document: Created document instance
            
        Raises:
            ValueError: If validation fails or duplicate found
            Exception: If upload/processing fails
        """
        try:
            logger.info(f"Starting document upload: {filename} ({len(file_content)} bytes) for project {project_id}")
            
            # Verify project exists and user has access
            project = await Project.get(PydanticObjectId(project_id))
            if not project or project.is_deleted:
                raise ValueError("Project not found")
            
            if not project.is_accessible_by(user_id):
                raise ValueError("Access denied to project")
            
            # Check for duplicate documents
            duplicate_doc = await self._check_duplicate_document(project_id, file_content, filename)
            if duplicate_doc:
                raise ValueError(f"Document already exists in project: {duplicate_doc.filename} (ID: {duplicate_doc.id})")
            
            # Generate content hash for future duplicate detection
            content_hash = hashlib.sha256(file_content).hexdigest()
            
            # Create document metadata with content hash
            doc_metadata = DocumentMetadata(
                filename=filename,
                content_type=content_type,
                size=len(file_content),
                upload_date=datetime.utcnow(),
                processed=False,
                content_hash=content_hash  # Add content hash for duplicate detection
            )
            
            # Create document instance
            document = Document(
                user_id=user_id,
                project_id=project_id,  # Direct field
                filename=filename,
                file_size=len(file_content),
                content_type=content_type,
                status=DocumentStatus.UPLOADING,
                metadata=doc_metadata,
                chunks=[]
            )
            
            # Save to database first
            await document.insert()
            logger.info(f"Document saved to database with ID: {document.id}")
            
            try:
                # Process document with chunking and embeddings
                import tempfile
                import os
                from pathlib import Path
                from services.document_processor import DocumentProcessor
                
                # Get OpenAI API key for processing
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if not openai_api_key:
                    logger.warning("OpenAI API key not configured - basic processing only")
                    
                    # Basic processing without LLM
                    document.status = DocumentStatus.COMPLETED
                    document.metadata.processed = True
                    logger.info("Document processed without embeddings (no OpenAI key)")
                    
                else:
                    # Full processing with chunking and embeddings
                    processor = DocumentProcessor(openai_api_key)
                    logger.info("Starting document processing with OpenAI embeddings")
                    
                    # Create temporary file for processing
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
                        temp_file.write(file_content)
                        temp_path = Path(temp_file.name)
                    
                    try:
                        # Process document (this will populate chunks and embeddings)
                        if content_type == "application/pdf":
                            await processor._process_pdf(temp_path, document)
                            document.status = DocumentStatus.COMPLETED
                            document.metadata.processed = True
                            logger.info(f"PDF processed successfully with {len(document.chunks)} chunks")
                        elif content_type.startswith('text/'):
                            # Handle text files
                            text_content = file_content.decode('utf-8', errors='ignore')
                            chunks = processor.text_splitter.split_text(text_content)
                            
                            # Create document chunks with embeddings
                            for chunk_idx, chunk_text in enumerate(chunks):
                                chunk = DocumentChunk(
                                    text=chunk_text,
                                    page_number=1,  # Text files are single page
                                    chunk_index=chunk_idx
                                )
                                # Generate embedding
                                chunk.embedding = await processor._generate_embedding(chunk_text)
                                document.chunks.append(chunk)
                            
                            document.status = DocumentStatus.COMPLETED
                            document.metadata.processed = True
                            logger.info(f"Text file processed successfully with {len(document.chunks)} chunks")
                        else:
                            # Unsupported file type - store without processing
                            document.status = DocumentStatus.COMPLETED
                            document.metadata.processed = False
                            logger.warning(f"Unsupported content type for processing: {content_type}")
                        
                    finally:
                        # Clean up temporary file
                        temp_path.unlink()
                
                # Save updates
                await document.save()
                
                # Add to project's document list
                project.add_document(str(document.id))
                await project.save()
                
                logger.info(f"Successfully uploaded and processed document {document.id} to project {project_id} with {len(document.chunks)} chunks")
                return document
                
            except Exception as processing_error:
                # Update status to failed
                document.status = DocumentStatus.FAILED
                document.metadata.error = str(processing_error)
                await document.save()
                logger.error(f"Document processing failed: {str(processing_error)}")
                raise processing_error
                
        except Exception as e:
            logger.error(f"Failed to upload document: {str(e)}")
            raise
    
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
                        "embedding": chunk.embedding  # Include full embedding vector
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
        Get list of project IDs accessible to a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of accessible project ID strings
        """
        try:
            # Get projects where user is owner or collaborator AND not deleted
            projects = await Project.find(
                And(
                    Project.is_deleted == False,
                    Or(
                        Project.owner_id == user_id,
                        In(user_id, Project.collaborators)
                    )
                )
            ).to_list()
            
            logger.info(f"Found {len(projects)} accessible projects for user {user_id}")
            project_ids = [str(project.id) for project in projects]
            logger.info(f"Accessible project IDs: {project_ids}")
            
            return project_ids
            
        except Exception as e:
            logger.error(f"Failed to get accessible projects: {str(e)}")
            return [] 