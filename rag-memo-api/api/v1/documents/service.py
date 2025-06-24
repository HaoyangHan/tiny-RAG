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
from services.document_service import DocumentService as LegacyDocumentService

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service class for document management operations in v1.4.
    
    Handles all business logic related to documents including file upload,
    processing, project integration, and analytics while maintaining
    compatibility with existing document processing logic.
    """
    
    def __init__(self):
        """Initialize with legacy document service for processing."""
        self.legacy_service = LegacyDocumentService()
    
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
            
            # Create document instance
            document = Document(
                filename=filename,
                file_size=len(file_content),
                content_type=content_type,
                project_id=project_id,
                uploaded_by=user_id,
                status=DocumentStatus.UPLOADING,
                metadata=metadata or {}
            )
            
            # Save to database first
            await document.insert()
            
            try:
                # Use legacy service for actual file processing
                # This maintains compatibility with existing processing logic
                processed_doc = await self.legacy_service.process_document(
                    file_content=file_content,
                    filename=filename,
                    content_type=content_type,
                    user_id=user_id
                )
                
                # Update document with processing results
                document.file_path = processed_doc.get('file_path')
                document.content_hash = processed_doc.get('content_hash')
                document.page_count = processed_doc.get('page_count', 0)
                document.word_count = processed_doc.get('word_count', 0)
                document.status = DocumentStatus.PROCESSING
                
                # Save updates
                await document.save()
                
                # Add to project
                project.add_document(str(document.id))
                await project.save()
                
                logger.info(f"Uploaded document {document.id} to project {project_id}")
                return document
                
            except Exception as processing_error:
                # Update status to failed
                document.status = DocumentStatus.FAILED
                document.error_message = str(processing_error)
                await document.save()
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
                    Document.filename.contains(search, case_insensitive=True)
                )
            
            # Build final query
            query = Document.find(And(*conditions))
            
            # Get total count
            total_count = await query.count()
            
            # Apply pagination and sorting
            documents = await query.sort(-Document.uploaded_at).skip((page - 1) * page_size).limit(page_size).to_list()
            
            return documents, total_count
            
        except Exception as e:
            logger.error(f"Failed to list documents for user {user_id}: {str(e)}")
            return [], 0
    
    async def update_document_status(
        self,
        document_id: str,
        status: DocumentStatus,
        user_id: str,
        error_message: Optional[str] = None
    ) -> Optional[Document]:
        """
        Update document status.
        
        Args:
            document_id: Document ID to update
            status: New status
            user_id: ID of the requesting user
            error_message: Optional error message if status is FAILED
            
        Returns:
            Document: Updated document instance if successful, None otherwise
        """
        try:
            document = await self.get_document(document_id, user_id)
            
            if not document:
                return None
            
            # Update status
            document.status = status
            
            if error_message:
                document.error_message = error_message
            
            if status == DocumentStatus.PROCESSED:
                document.processed_at = datetime.utcnow()
            
            # Update timestamp
            document.update_timestamp()
            
            # Save changes
            await document.save()
            
            logger.info(f"Updated document {document_id} status to {status}")
            return document
            
        except Exception as e:
            logger.error(f"Failed to update document status {document_id}: {str(e)}")
            return None
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete a document (soft delete) with access control.
        
        Args:
            document_id: Document ID to delete
            user_id: ID of the requesting user
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            document = await Document.get(PydanticObjectId(document_id))
            
            if not document or document.is_deleted:
                return False
            
            # Check project access
            project = await Project.get(PydanticObjectId(document.project_id))
            if not project or not project.is_accessible_by(user_id):
                return False
            
            # Only uploader or project owner can delete
            if document.uploaded_by != user_id and project.owner_id != user_id:
                return False
            
            # Perform soft delete
            document.mark_deleted()
            await document.save()
            
            # Remove from project
            project.remove_document(document_id)
            await project.save()
            
            logger.info(f"Deleted document {document_id} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            return False
    
    async def get_document_content(
        self,
        document_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get document content and processing results.
        
        Args:
            document_id: Document ID
            user_id: ID of the requesting user
            
        Returns:
            Dict[str, Any]: Document content if accessible, None otherwise
        """
        try:
            document = await self.get_document(document_id, user_id)
            
            if not document:
                return None
            
            # Use legacy service to get processed content
            content = await self.legacy_service.get_document_content(str(document.id))
            
            return {
                "document_id": str(document.id),
                "filename": document.filename,
                "content": content.get('content', ''),
                "chunks": content.get('chunks', []),
                "metadata": document.metadata,
                "processing_info": {
                    "page_count": document.page_count,
                    "word_count": document.word_count,
                    "status": document.status,
                    "processed_at": document.processed_at.isoformat() if document.processed_at else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get document content {document_id}: {str(e)}")
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
            project_id: Optional project ID to filter analytics
            
        Returns:
            Dict[str, Any]: Document analytics
        """
        try:
            # Get accessible project IDs
            if project_id:
                project = await Project.get(PydanticObjectId(project_id))
                if not project or not project.is_accessible_by(user_id):
                    return {}
                accessible_projects = [project_id]
            else:
                accessible_projects = await self._get_accessible_project_ids(user_id)
            
            if not accessible_projects:
                return {}
            
            # Get documents
            documents = await Document.find(
                And(
                    Document.is_deleted == False,
                    In(Document.project_id, accessible_projects)
                )
            ).to_list()
            
            if not documents:
                return {
                    "total_documents": 0,
                    "total_size_mb": 0.0,
                    "by_status": {},
                    "by_content_type": {},
                    "processing_stats": {}
                }
            
            # Calculate analytics
            total_documents = len(documents)
            total_size = sum(doc.file_size for doc in documents)
            total_size_mb = round(total_size / (1024 * 1024), 2)
            
            # Group by status
            by_status = {}
            for doc in documents:
                status = str(doc.status)
                by_status[status] = by_status.get(status, 0) + 1
            
            # Group by content type
            by_content_type = {}
            for doc in documents:
                content_type = doc.content_type or 'unknown'
                by_content_type[content_type] = by_content_type.get(content_type, 0) + 1
            
            # Processing statistics
            processed_docs = [d for d in documents if d.status == DocumentStatus.PROCESSED]
            failed_docs = [d for d in documents if d.status == DocumentStatus.FAILED]
            
            total_pages = sum(doc.page_count for doc in processed_docs if doc.page_count)
            total_words = sum(doc.word_count for doc in processed_docs if doc.word_count)
            
            return {
                "total_documents": total_documents,
                "total_size_mb": total_size_mb,
                "by_status": by_status,
                "by_content_type": by_content_type,
                "processing_stats": {
                    "processed": len(processed_docs),
                    "failed": len(failed_docs),
                    "success_rate": round(len(processed_docs) / total_documents * 100, 1) if total_documents > 0 else 0,
                    "total_pages": total_pages,
                    "total_words": total_words
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get document analytics: {str(e)}")
            return {}
    
    async def _get_accessible_project_ids(self, user_id: str) -> List[str]:
        """
        Get list of project IDs accessible to a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[str]: List of accessible project IDs
        """
        try:
            # Get projects user owns, collaborates on, or are public
            projects = await Project.find(
                And(
                    Project.is_deleted == False,
                    Or(
                        Project.owner_id == user_id,
                        In(Project.collaborators, [user_id]),
                        Project.visibility == "public"
                    )
                )
            ).to_list()
            
            return [str(project.id) for project in projects]
            
        except Exception as e:
            logger.error(f"Failed to get accessible projects for user {user_id}: {str(e)}")
            return [] 