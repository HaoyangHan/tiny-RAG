"""
LlamaIndex-based Document Processor for TinyRAG
==============================================

This module implements document processing using LlamaIndex ingestion pipeline
and metadata extraction following the instruction document patterns.

Author: TinyRAG Development Team
Version: 1.4.3
Last Updated: January 2025
"""

import logging
import tempfile
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# LlamaIndex imports
from llama_index.core import (
    SimpleDirectoryReader, 
    VectorStoreIndex, 
    Document as LlamaDocument
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

# OpenAI client for metadata extraction
from openai import OpenAI as OpenAIClient

# PyMuPDF import (optional)
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    print("Warning: PyMuPDF not available - table and image extraction may be limited")
    PYMUPDF_AVAILABLE = False

# TinyRAG imports
from models.document import Document, DocumentChunk, DocumentMetadata
from models.document import TableData, ImageData
from services.metadata_extractor import TinyRAGMetadataExtractor
from services.enhanced_document_processor import EnhancedDocumentProcessor
from prompt_template import format_prompt, get_prompt_template

logger = logging.getLogger(__name__)


class LlamaIndexDocumentProcessor:
    """
    LlamaIndex-based document processor with comprehensive metadata extraction.
    
    Implements the ingestion pipeline and metadata extraction patterns from
    the LlamaIndex instruction document while maintaining TinyRAG compatibility.
    """
    
    def __init__(self, openai_api_key: str, openai_base_url: str = "https://api.openai-proxy.org/v1"):
        """Initialize the LlamaIndex document processor."""
        
        # Store API key for later use
        self.openai_api_key = openai_api_key
        
        # Initialize LLM and embedding models
        self.llm = OpenAI(
            model="gpt-4o-mini",
            api_key=openai_api_key,
            base_url=openai_base_url
        )
        
        self.embed_model = OpenAIEmbedding(
            model="text-embedding-ada-002",
            api_key=openai_api_key,
            base_url=openai_base_url
        )
        
        # Create OpenAI client for metadata extraction
        self.openai_client = OpenAIClient(
            api_key=openai_api_key,
            base_url=openai_base_url
        )
        
        # Initialize enhanced document processor for metadata extraction
        self.enhanced_processor = EnhancedDocumentProcessor(openai_api_key)
        
        logger.info("LlamaIndex document processor initialized")

    async def process_document(self, file_path: Path, user_id: str, document_id: str, project_id: str = None) -> Document:
        """
        Process an uploaded document using LlamaIndex ingestion pipeline.
        
        Args:
            file_path: Path to the uploaded file
            user_id: ID of the user uploading the document
            document_id: ID of the document being processed
            project_id: ID of the project (required for v1.4)
            
        Returns:
            TinyRAGDocument: Processed document with enhanced metadata
        """
        try:
            # Read file metadata
            content_type = self._get_content_type(file_path)
            file_size = file_path.stat().st_size
            filename = file_path.name
            
            # Create document metadata
            metadata = DocumentMetadata(
                filename=filename,
                content_type=content_type,
                size=file_size
            )
            
            # Create document instance
            document = Document(
                user_id=user_id,
                project_id=project_id,
                filename=filename,
                content_type=content_type,
                file_size=file_size,
                status="processing",
                metadata=metadata,
                chunks=[]
            )
            
            # Process document based on content type
            if content_type == "application/pdf":
                await self._process_pdf_with_llamaindex(file_path, document, document_id)
            elif content_type.startswith('text/'):
                await self._process_text_with_llamaindex(file_path, document, document_id)
            elif content_type.startswith('image/'):
                await self._process_image_with_llamaindex(file_path, document, document_id)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Update status
            document.status = "completed"
            document.metadata.processed = True
            
            # Save document
            await document.save()
            return document
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            if 'document' in locals():
                document.metadata.error = str(e)
                document.metadata.processed = False
                document.status = "failed"
                await document.save()
            raise

    async def _process_pdf_with_llamaindex(self, file_path: Path, document: Document, document_id: str) -> None:
        """Process PDF document using LlamaIndex ingestion pipeline."""
        
        try:
            # For now, let's use a simpler approach without tempfile
            # Create a simple document from the file path
            llama_doc = LlamaDocument(
                text=f"PDF document: {file_path.name}",
                metadata={
                    "source": str(file_path),
                    "filename": file_path.name,
                    "content_type": "application/pdf",
                    "document_id": document_id,
                    "user_id": document.user_id,
                    "project_id": document.project_id,
                    "upload_date": datetime.utcnow().isoformat()
                }
            )
            
            # Split text into chunks
            text = llama_doc.text
            chunks = self._split_text_into_chunks(text, 512, 20)
            
            for j, chunk_text in enumerate(chunks):
                # Create enhanced chunk with metadata using enhanced processor
                await self._create_enhanced_chunk(
                    document=document,
                    text=chunk_text,
                    chunk_type="text",
                    page_number=1,
                    document_id=document_id,
                    start_pos=j * 512,
                    section="Content"
                )
            
            # Process tables and images with enhanced metadata
            await self._process_tables_and_images_enhanced(file_path, document, document_id)
            
        except Exception as e:
            logger.error(f"Error processing PDF with LlamaIndex: {e}")
            raise

    async def _process_text_with_llamaindex(self, file_path: Path, document: Document, document_id: str) -> None:
        """Process text document using LlamaIndex ingestion pipeline."""
        
        try:
            # Read text content
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Create LlamaIndex document
            llama_doc = LlamaDocument(
                text=text_content,
                metadata={
                    "source": str(file_path),
                    "filename": file_path.name,
                    "content_type": document.content_type,
                    "document_id": document_id,
                    "user_id": document.user_id,
                    "project_id": document.project_id,
                    "upload_date": datetime.utcnow().isoformat()
                }
            )
            
            # Split text into chunks
            chunks = self._split_text_into_chunks(text_content, 512, 20)
            
            for j, chunk_text in enumerate(chunks):
                # Create enhanced chunk with metadata using enhanced processor
                await self._create_enhanced_chunk(
                    document=document,
                    text=chunk_text,
                    chunk_type="text",
                    page_number=1,
                    document_id=document_id,
                    start_pos=j * 512,
                    section="Content"
                )
                
        except Exception as e:
            logger.error(f"Error processing text with LlamaIndex: {e}")
            raise

    async def _process_image_with_llamaindex(self, file_path: Path, document: Document, document_id: str) -> None:
        """Process image document using LlamaIndex with enhanced metadata."""
        
        try:
            # Read image bytes
            image_bytes = await self._read_image_bytes(file_path)
            
            # Create enhanced image chunk with metadata
            await self._create_enhanced_image_chunk(
                document=document,
                image_data=image_bytes,
                page_number=1,
                document_id=document_id,
                start_pos=0,
                section="Image"
            )
            
        except Exception as e:
            logger.error(f"Error processing image with LlamaIndex: {e}")
            raise

    async def _process_tables_and_images_enhanced(self, file_path: Path, document: Document, document_id: str) -> None:
        """Process tables and images with enhanced metadata extraction."""
        
        try:
            # Use the existing enhanced processor for table/image extraction
            temp_processor = self.enhanced_processor
            
            # Extract tables and images using PyMuPDF in single loop
            try:
                doc = fitz.open(str(file_path))
                total_pages = len(doc)
                logger.info(f"Processing PDF with {total_pages} pages")
                
                for page_num in range(total_pages):  # Process only existing pages
                    page = doc[page_num]
                    logger.info(f"Processing page {page_num + 1}/{total_pages}")
                    
                    # Extract tables from this page with enhanced metadata
                    if hasattr(temp_processor, '_extract_tables_with_pymupdf') and PYMUPDF_AVAILABLE:
                        try:
                            tables = temp_processor._extract_tables_with_pymupdf(file_path, page_num + 1)
                            if tables:
                                document.metadata.has_tables = True
                                for table_idx, table_data in enumerate(tables):
                                    table_text = temp_processor._format_table_for_summary(table_data)
                                    
                                    # Create enhanced table chunk with metadata and reuse the results
                                    table_summary, table_metadata = await self._create_enhanced_table_chunk(
                                        document=document,
                                        table_text=table_text,
                                        page_number=page_num + 1,
                                        document_id=document_id,
                                        start_pos=table_idx * 1000,  # Approximate position
                                        section="Table"
                                    )
                                    
                                    # Create table data object for backward compatibility using reused metadata
                                    table_data_obj = TableData(
                                        page_number=page_num + 1,
                                        table_index=table_idx,
                                        content=table_data,
                                        summary=table_summary,
                                        row_count=len(table_data),
                                        column_count=len(table_data[0]) if table_data else 0
                                    )
                                    document.tables.append(table_data_obj)
                        except Exception as e:
                            logger.error(f"Error extracting tables from page {page_num + 1}: {e}")
                    
                                        # Extract images from this page with enhanced metadata
                    if PYMUPDF_AVAILABLE:
                        try:
                            images = temp_processor._extract_images_from_page(page)
                            if images:
                                document.metadata.has_images = True
                                logger.info(f"Found {len(images)} images on page {page_num + 1}")
                                for img_idx, img_data in enumerate(images):
                                    # Create enhanced image chunk with metadata and reuse the results
                                    description, image_metadata = await self._create_enhanced_image_chunk(
                                        document=document,
                                        image_data=img_data,
                                        page_number=page_num + 1,
                                        document_id=document_id,
                                        start_pos=img_idx * 1000,  # Approximate position
                                        section="Image"
                                    )
                                    
                                    # Create image data object for backward compatibility using reused metadata
                                    image_data_obj = ImageData(
                                        page_number=page_num + 1,
                                        image_index=img_idx + 1,
                                        content=img_data,
                                        description=description
                                    )
                                    document.images.append(image_data_obj)
                            else:
                                logger.info(f"No images found on page {page_num + 1}")
                        except Exception as e:
                            logger.error(f"Error extracting images from page {page_num + 1}: {e}")
                    else:
                        logger.info(f"PyMuPDF not available - skipping image extraction on page {page_num + 1}")
                
                doc.close()
            except Exception as e:
                logger.error(f"Error extracting tables and images: {e}")
                            
        except Exception as e:
            logger.error(f"Error processing tables and images: {e}")
            # Don't raise - this is optional processing

    async def _create_enhanced_chunk(self,
                                   document: Document,
                                   text: str,
                                   chunk_type: str,
                                   page_number: int,
                                   document_id: str,
                                   start_pos: int,
                                   section: str) -> None:
        """Create a document chunk with comprehensive metadata extraction."""
        
        import uuid
        import time
        from datetime import datetime
        
        start_time = time.time()
        chunk_id = str(uuid.uuid4())
        chunk_index = len(document.chunks)
        end_pos = start_pos + len(text)
        
        # Generate both summary and comprehensive metadata in one LLM call
        summary, chunk_metadata = await self.enhanced_processor._generate_text_summary_with_metadata(text)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        chunk_metadata["processing_time"] = processing_time
        
        # Add required chunk metadata fields
        chunk_metadata.update({
            "chunk_id": chunk_id,
            "document_id": document_id,
            "chunk_index": chunk_index,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "page_number": page_number,
            "section": section,
            "summary": summary  # Store summary in metadata
        })
        
        # Generate embedding from summary (or text if summary is empty)
        embedding_text = summary if summary else text
        embedding = await self._generate_embedding(embedding_text)
        
        # Create enhanced document chunk
        chunk = DocumentChunk(
            text=text,
            page_number=page_number,
            chunk_index=chunk_index,
            chunk_type=chunk_type,
            embedding=embedding,
            chunk_metadata=chunk_metadata,
            start_pos=start_pos,
            end_pos=end_pos,
            section=section
        )
        
        document.chunks.append(chunk)
        
        logger.debug(f"Created enhanced LlamaIndex chunk {chunk_index} with comprehensive metadata: "
                    f"keywords={len(chunk_metadata.get('keywords', []))}, "
                    f"entities={len(chunk_metadata.get('entities', []))}, "
                    f"topics={len(chunk_metadata.get('topics', []))}, "
                    f"sentiment={chunk_metadata.get('sentiment', 'N/A')}")

    async def _create_enhanced_table_chunk(self,
                                         document: Document,
                                         table_text: str,
                                         page_number: int,
                                         document_id: str,
                                         start_pos: int,
                                         section: str) -> tuple[str, dict]:
        """Create table chunk with comprehensive metadata extraction and return summary and metadata for reuse."""
        
        import time
        import uuid
        from datetime import datetime
        
        start_time = time.time()
        
        try:
            # Get both summary and comprehensive metadata in one LLM call using enhanced processor
            summary, chunk_metadata = await self.enhanced_processor._generate_table_summary_with_metadata(table_text)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            chunk_metadata["processing_time"] = processing_time
            
            # Generate embedding from summary
            embedding = await self._generate_embedding(summary)
            
            # Create chunk
            chunk_id = str(uuid.uuid4())
            chunk_index = len(document.chunks)
            end_pos = start_pos + len(summary)
            
            # Add summary to metadata
            chunk_metadata["summary"] = summary
            
            chunk = DocumentChunk(
                text=table_text,
                page_number=page_number,
                chunk_index=chunk_index,
                chunk_type="table",
                embedding=embedding,
                chunk_metadata=chunk_metadata,
                start_pos=start_pos,
                end_pos=end_pos,
                section=section
            )
            
            document.chunks.append(chunk)
            logger.debug(f"Created enhanced LlamaIndex table chunk {chunk_index} with comprehensive metadata: "
                        f"keywords={len(chunk_metadata.get('keywords', []))}, "
                        f"entities={len(chunk_metadata.get('entities', []))}, "
                        f"topics={len(chunk_metadata.get('topics', []))}, "
                        f"sentiment={chunk_metadata.get('sentiment', 'N/A')}")
            
            # Return summary and metadata for reuse
            return summary, chunk_metadata
            
        except Exception as e:
            logger.error(f"Error creating enhanced LlamaIndex table chunk: {e}")
            return "", {}

    async def _create_enhanced_image_chunk(self,
                                         document: Document,
                                         image_data: bytes,
                                         page_number: int,
                                         document_id: str,
                                         start_pos: int,
                                         section: str) -> tuple[str, dict]:
        """Create image chunk with comprehensive metadata extraction and return description and metadata for reuse."""
        
        import time
        import uuid
        from datetime import datetime
        
        start_time = time.time()
        
        try:
            # Get both description and comprehensive metadata in one LLM call using enhanced processor
            description, chunk_metadata = await self.enhanced_processor._process_image_with_gpt4_and_metadata(image_data)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            chunk_metadata["processing_time"] = processing_time
            
            # Generate embedding from description
            embedding = await self._generate_embedding(description)
            
            # Create chunk
            chunk_id = str(uuid.uuid4())
            chunk_index = len(document.chunks)
            end_pos = start_pos + len(description)
            
            # Add description to metadata
            chunk_metadata["summary"] = description
            
            chunk = DocumentChunk(
                text=description,  # Use description as text instead of raw image data
                page_number=page_number,
                chunk_index=chunk_index,
                chunk_type="image",
                embedding=embedding,
                chunk_metadata=chunk_metadata,
                start_pos=start_pos,
                end_pos=end_pos,
                section=section
            )
            
            document.chunks.append(chunk)
            logger.debug(f"Created enhanced LlamaIndex image chunk {chunk_index} with comprehensive metadata: "
                        f"keywords={len(chunk_metadata.get('keywords', []))}, "
                        f"entities={len(chunk_metadata.get('entities', []))}, "
                        f"topics={len(chunk_metadata.get('topics', []))}, "
                        f"sentiment={chunk_metadata.get('sentiment', 'N/A')}")
            
            # Return description and metadata for reuse
            return description, chunk_metadata
            
        except Exception as e:
            logger.error(f"Error creating enhanced LlamaIndex image chunk: {e}")
            return "", {}

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    def _split_text_into_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Simple text splitting function."""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
            if start >= text_length:
                break
                
        return chunks

    async def _process_image_with_gpt4(self, file_path: Path) -> str:
        """Process image with GPT-4 Vision."""
        
        try:
            image_bytes = await self._read_image_bytes(file_path)
            
            template = get_prompt_template("image_description")
            response_text = await self.llm.apredict(
                prompt=template.user_prompt_template
            )
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error processing image with GPT-4: {e}")
            return f"Error analyzing image: {str(e)}"

    async def _read_image_bytes(self, file_path: Path) -> bytes:
        """Read image file as bytes."""
        with open(file_path, 'rb') as f:
            return f.read()

    def _get_content_type(self, file_path: Path) -> str:
        """Get content type based on file extension."""
        extension = file_path.suffix.lower()
        
        content_types = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        }
        
        return content_types.get(extension, 'application/octet-stream')


def create_llamaindex_document_processor(openai_api_key: str, openai_base_url: str = "https://api.openai-proxy.org/v1") -> LlamaIndexDocumentProcessor:
    """Create and return a LlamaIndex document processor instance."""
    return LlamaIndexDocumentProcessor(openai_api_key, openai_base_url) 