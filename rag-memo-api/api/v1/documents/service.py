"""
Document service for TinyRAG v1.4.

This module contains the business logic for document management including
file upload, processing, project integration, and document analytics.
"""

import logging
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
        Upload and process a document for a project with enhanced table and image extraction.
        
        Args:
            project_id: Associated project ID
            file_content: File content bytes
            filename: Original filename
            content_type: MIME content type
            user_id: ID of the uploading user
            metadata: Optional document metadata
            
        Returns:
            Document: Created document instance with processed content, tables, and images
            
        Raises:
            ValueError: If validation fails
            Exception: If upload/processing fails
        """
        try:
            # Verify project exists and user has access
            project = await Project.get(PydanticObjectId(project_id))
            if not project or project.is_deleted:
                raise ValueError("Project not found")
            
            if not project.is_accessible_by(user_id):
                raise ValueError("Access denied to project")
            
            # Create document metadata
            doc_metadata = DocumentMetadata(
                filename=filename,
                content_type=content_type,
                size=len(file_content),
                upload_date=datetime.utcnow(),
                processed=False,
                has_tables=False,
                has_images=False
            )
            
            # Create document instance
            document = Document(
                user_id=user_id,
                project_id=project_id,
                filename=filename,
                file_size=len(file_content),
                content_type=content_type,
                status=DocumentStatus.UPLOADING,
                metadata=doc_metadata,
                chunks=[],
                tables=[],
                images=[]
            )
            
            # Save to database first
            await document.insert()
            
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
                    import hashlib
                    content_hash = hashlib.sha256(file_content).hexdigest()
                    
                    # Basic word count for text files
                    if content_type.startswith('text/'):
                        word_count = len(file_content.decode('utf-8', errors='ignore').split())
                    else:
                        word_count = 0
                    
                    document.status = DocumentStatus.COMPLETED
                    document.metadata.processed = True
                    
                else:
                    # Enhanced processing with table and image extraction
                    processor = DocumentProcessor(openai_api_key)
                    
                    # Create temporary file for processing
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as temp_file:
                        temp_file.write(file_content)
                        temp_path = Path(temp_file.name)
                    
                    try:
                        # Update status to processing
                        document.status = DocumentStatus.PROCESSING
                        await document.save()
                        
                        # Process document with enhanced capabilities
                        if content_type == "application/pdf":
                            # Use the enhanced PDF processor with table and image extraction
                            await processor._process_pdf(temp_path, document)
                            
                            # Update metadata flags based on extracted content
                            document.metadata.has_tables = len(document.tables) > 0
                            document.metadata.has_images = len(document.images) > 0
                            
                            logger.info(f"PDF processing completed: {len(document.chunks)} chunks, "
                                      f"{len(document.tables)} tables, {len(document.images)} images")
                            
                        elif content_type.startswith('text/'):
                            # Handle text files with standard chunking
                            text_content = file_content.decode('utf-8', errors='ignore')
                            chunks = processor.text_splitter.split_text(text_content)
                            
                            # Create document chunks with embeddings
                            for chunk_idx, chunk_text in enumerate(chunks):
                                chunk = DocumentChunk(
                                    text=chunk_text,
                                    page_number=1,
                                    chunk_index=chunk_idx,
                                    chunk_type="text",
                                    embedding=await processor._generate_embedding(chunk_text)
                                )
                                document.chunks.append(chunk)
                            
                            logger.info(f"Text processing completed: {len(document.chunks)} chunks")
                            
                        elif content_type.startswith('image/'):
                            # Process standalone image files
                            image_description = await processor._process_image_with_gpt4(file_content)
                            
                            # Create image data
                            from models.document import ImageData
                            image_data = ImageData(
                                page_number=1,
                                image_index=0,
                                content=file_content,
                                description=image_description
                            )
                            document.images.append(image_data)
                            document.metadata.has_images = True
                            
                            # Create chunk for image description
                            image_embedding = await processor._generate_embedding(image_description)
                            chunk = DocumentChunk(
                                text=image_description,
                                page_number=1,
                                chunk_index=0,
                                chunk_type="image",
                                embedding=image_embedding
                            )
                            document.chunks.append(chunk)
                            
                            logger.info(f"Image processing completed: {image_description[:100]}...")
                            
                        else:
                            # Unsupported file type - store without processing
                            document.status = DocumentStatus.COMPLETED
                            document.metadata.processed = False
                            logger.warning(f"Unsupported content type for processing: {content_type}")
                        
                        # Mark as completed if processed successfully
                        if document.status != DocumentStatus.COMPLETED:
                            document.status = DocumentStatus.COMPLETED
                            document.metadata.processed = True
                        
                    finally:
                        # Clean up temporary file
                        if temp_path.exists():
                            temp_path.unlink()
                
                # Save all updates
                await document.save()
                
                # Add to project's document list
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
        Soft delete a document.
        
        Args:
            document_id: Document ID to delete
            user_id: ID of the requesting user
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            document = await self.get_document(document_id, user_id)
            if not document:
                return False
            
            # Soft delete
            document.is_deleted = True
            document.updated_at = datetime.utcnow()
            await document.save()
            
            # Remove from project's document list
            project = await Project.get(PydanticObjectId(document.project_id))
            if project:
                project.remove_document(str(document.id))
                await project.save()
            
            logger.info(f"Deleted document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            return False
    
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