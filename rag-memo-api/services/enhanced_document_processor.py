"""
Enhanced Document Processor for TinyRAG v1.4.3
==============================================

This module provides enhanced document processing with comprehensive metadata extraction
using LlamaIndex-style extractors while maintaining compatibility with existing functionality.

Author: TinyRAG Development Team
Version: 1.4.3
Last Updated: January 2025
"""

import logging
import uuid
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import tempfile
import magic
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI

from models.document import Document, DocumentChunk, DocumentMetadata
from prompt_template import get_prompt_template

logger = logging.getLogger(__name__)

# Define missing models for compatibility
class TableData:
    def __init__(self, page_number, table_index, content, summary, row_count=0, column_count=0):
        self.page_number = page_number
        self.table_index = table_index
        self.content = content
        self.summary = summary
        self.row_count = row_count
        self.column_count = column_count

class ImageData:
    def __init__(self, page_number, image_index, content, description):
        self.page_number = page_number
        self.image_index = image_index
        self.content = content
        self.description = description

# Optional imports with fallbacks
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    logger.warning("Camelot not available - table extraction disabled")
    CAMELOT_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    logger.warning("OpenCV not available - advanced image processing disabled")
    CV2_AVAILABLE = False

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    logger.warning("PIL not available - image processing disabled")
    PIL_AVAILABLE = False

try:
    from services.metadata_extractor import create_metadata_extractor, BaseNode
    METADATA_EXTRACTOR_AVAILABLE = True
except ImportError:
    logger.warning("Metadata extractor not available - using basic metadata only")
    METADATA_EXTRACTOR_AVAILABLE = False

class EnhancedDocumentProcessor:
    """
    Enhanced document processor with comprehensive metadata extraction.
    
    Integrates LlamaIndex-style metadata extraction with existing table and image
    processing capabilities for comprehensive document understanding.
    """
    
    def __init__(self, openai_api_key: str):
        """Initialize the enhanced document processor."""
        self.openai_client = OpenAI(
            base_url='https://api.openai-proxy.org/v1',
            api_key=openai_api_key,
        )
        
        # Text processing
        self.embedding_model = "text-embedding-ada-002"
        self.vision_model = "gpt-4-vision-preview"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Metadata extractor
        if METADATA_EXTRACTOR_AVAILABLE:
            self.metadata_extractor = create_metadata_extractor(
                openai_client=self.openai_client
            )
        else:
            self.metadata_extractor = None
        
        logger.info("Enhanced document processor initialized with metadata extraction")

    async def process_document(self, file_path: Path, user_id: str, document_id: str, project_id: str = None) -> Document:
        """
        Process an uploaded document with enhanced metadata extraction.
        
        Args:
            file_path: Path to the uploaded file
            user_id: ID of the user uploading the document
            document_id: ID of the document being processed
            project_id: ID of the project (required for v1.4)
            
        Returns:
            Document: Processed document with enhanced metadata
        """
        try:
            # Read file metadata
            content_type = magic.from_file(str(file_path), mime=True)
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
                chunks=[],
                tables=[],
                images=[]
            )
            
            # Process document based on content type
            if content_type == "application/pdf":
                await self._process_pdf_enhanced(file_path, document, document_id)
            elif content_type.startswith('text/'):
                await self._process_text_enhanced(file_path, document, document_id)
            elif content_type.startswith('image/'):
                await self._process_image_enhanced(file_path, document, document_id)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Update status
            document.status = "completed"
            document.metadata.processed = True
            
            logger.info(f"Enhanced processing completed: {len(document.chunks)} chunks, "
                       f"{len(document.tables)} tables, {len(document.images)} images")
            
            return document
            
        except Exception as e:
            logger.error(f"Error in enhanced document processing: {str(e)}")
            if 'document' in locals():
                document.metadata.error = str(e)
                document.metadata.processed = False
                document.status = "failed"
            raise

    async def _process_pdf_enhanced(self, file_path: Path, document: Document, document_id: str) -> None:
        """Process a PDF document with enhanced metadata extraction."""
        try:
            # Read PDF
            reader = PdfReader(str(file_path))
            full_text = ""
            text_positions = []  # Track text positions for metadata
            
            # Process each page
            for page_num, page in enumerate(reader.pages):
                page_start_pos = len(full_text)
                
                # 1. Extract tables using Camelot
                if CAMELOT_AVAILABLE:
                    tables = camelot.read_pdf(str(file_path), pages=str(page_num + 1))
                    if len(tables) > 0:
                        for table_idx, table in enumerate(tables):
                            # Get table text for processing
                            table_text = table.df.to_string()
                            
                            # Create optimized table chunk (summary + metadata in one LLM call)
                            await self._create_enhanced_table_chunk(
                                document=document,
                                table_text=table_text,
                                page_number=page_num + 1,
                                document_id=document_id,
                                start_pos=page_start_pos,
                                section=f"Table {table_idx + 1}"
                            )
                            
                            # Create table data for backward compatibility (use the summary from chunk)
                            if document.chunks:
                                latest_chunk = document.chunks[-1]
                                table_summary = latest_chunk.text
                            else:
                                table_summary = "Table processing failed"
                            
                            table_data = TableData(
                                page_number=page_num + 1,
                                table_index=table_idx,
                                content=table.df.values.tolist(),
                                summary=table_summary,
                                row_count=len(table.df),
                                column_count=len(table.df.columns)
                            )
                            document.tables.append(table_data)
                
                # 2. Extract images
                images = self._extract_images_from_page(page)
                if images:
                    for img_idx, img_data in enumerate(images):
                        # Create optimized image chunk (description + metadata in one LLM call)
                        await self._create_enhanced_image_chunk(
                            document=document,
                            image_data=img_data,
                            page_number=page_num + 1,
                            document_id=document_id,
                            start_pos=page_start_pos,
                            section=f"Image {img_idx + 1}"
                        )
                        
                        # Create image data for backward compatibility (use the description from chunk)
                        if document.chunks:
                            latest_chunk = document.chunks[-1]
                            image_description = latest_chunk.text
                        else:
                            image_description = "Image processing failed"
                        
                        image_data_obj = ImageData(
                            page_number=page_num + 1,
                            image_index=img_idx,
                            content=img_data,
                            description=image_description
                        )
                        document.images.append(image_data_obj)
                
                # 3. Extract and process regular text
                page_text = page.extract_text()
                if page_text.strip():
                    full_text += page_text + "\n"
                    text_positions.append((page_start_pos, len(full_text), page_num + 1))
            
            # Process full text with enhanced chunking and metadata
            if full_text.strip():
                await self._process_text_chunks_enhanced(
                    document=document,
                    full_text=full_text,
                    document_id=document_id,
                    text_positions=text_positions
                )
            
            document.metadata.processed = True
            
        except Exception as e:
            logger.error(f"Error in enhanced PDF processing: {str(e)}")
            raise

    async def _process_text_enhanced(self, file_path: Path, document: Document, document_id: str) -> None:
        """Process a text file with enhanced metadata extraction."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            await self._process_text_chunks_enhanced(
                document=document,
                full_text=text_content,
                document_id=document_id,
                text_positions=[(0, len(text_content), 1)]
            )
            
        except Exception as e:
            logger.error(f"Error in enhanced text processing: {str(e)}")
            raise

    async def _process_image_enhanced(self, file_path: Path, document: Document, document_id: str) -> None:
        """Process a standalone image file with enhanced metadata extraction."""
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # Create optimized image chunk (description + metadata in one LLM call)
            await self._create_enhanced_image_chunk(
                document=document,
                image_data=image_data,
                page_number=1,
                document_id=document_id,
                start_pos=0,
                section="Main Image"
            )
            
            # Create image data for backward compatibility
            if document.chunks:
                latest_chunk = document.chunks[-1]
                image_description = latest_chunk.text
            else:
                image_description = "Image processing failed"
            
            image_data_obj = ImageData(
                page_number=1,
                image_index=0,
                content=image_data,
                description=image_description
            )
            document.images.append(image_data_obj)
            
        except Exception as e:
            logger.error(f"Error in enhanced image processing: {str(e)}")
            raise

    async def _process_text_chunks_enhanced(self, 
                                          document: Document,
                                          full_text: str,
                                          document_id: str,
                                          text_positions: List[Tuple[int, int, int]]) -> None:
        """Process text into chunks with enhanced metadata extraction."""
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(full_text)
        
        # Track position in original text
        current_pos = 0
        
        for chunk_idx, chunk_text in enumerate(chunks):
            # Find which page this chunk belongs to
            page_number = 1
            for start_pos, end_pos, page_num in text_positions:
                if current_pos >= start_pos and current_pos < end_pos:
                    page_number = page_num
                    break
            
            # Create enhanced chunk with metadata
            await self._create_enhanced_chunk(
                document=document,
                text=chunk_text,
                chunk_type="text",
                page_number=page_number,
                document_id=document_id,
                start_pos=current_pos,
                section="Content"
            )
            
            current_pos += len(chunk_text)

    async def _create_enhanced_chunk(self,
                                   document: Document,
                                   text: str,
                                   chunk_type: str,
                                   page_number: int,
                                   document_id: str,
                                   start_pos: int,
                                   section: str) -> None:
        """Create a document chunk with enhanced metadata extraction."""
        
        chunk_id = str(uuid.uuid4())
        chunk_index = len(document.chunks)
        end_pos = start_pos + len(text)
        
        # Extract comprehensive metadata
        if self.metadata_extractor:
            chunk_metadata = self.metadata_extractor.extract_chunk_metadata(
                text=text,
                chunk_id=chunk_id,
                document_id=document_id,
                chunk_index=chunk_index,
                start_pos=start_pos,
                end_pos=end_pos,
                page_number=page_number,
                section=section
            )
        else:
            # Fallback metadata when extractor is not available
            chunk_metadata = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "chunk_index": chunk_index,
                "text_length": len(text),
                "start_pos": start_pos,
                "end_pos": end_pos,
                "page_number": page_number,
                "section": section,
                "extraction_timestamp": datetime.utcnow().isoformat(),
                "extractor_version": "1.4.3_fallback"
            }
        
        # Generate embedding
        embedding = await self._generate_embedding(text)
        
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
        
        logger.debug(f"Created enhanced chunk {chunk_index} with {len(chunk_metadata)} metadata fields")
    
    async def _create_enhanced_table_chunk(self,
                                         document: Document,
                                         table_text: str,
                                         page_number: int,
                                         document_id: str,
                                         start_pos: int,
                                         section: str) -> None:
        """Create table chunk with summary and metadata in single LLM call."""
        
        import time
        start_time = time.time()
        
        try:
            # Get both summary and metadata in one LLM call
            summary, chunk_metadata = await self._generate_table_summary_with_metadata(table_text)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            chunk_metadata["processing_time"] = processing_time
            
            # Generate embedding from summary
            embedding = await self._generate_embedding(summary)
            
            # Create chunk
            chunk_id = str(uuid.uuid4())
            chunk_index = len(document.chunks)
            end_pos = start_pos + len(summary)
            
            chunk = DocumentChunk(
                text=summary,
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
            logger.debug(f"Created optimized table chunk {chunk_index} with single LLM call")
            
        except Exception as e:
            logger.error(f"Error creating enhanced table chunk: {e}")
    
    async def _create_enhanced_image_chunk(self,
                                         document: Document,
                                         image_data: bytes,
                                         page_number: int,
                                         document_id: str,
                                         start_pos: int,
                                         section: str) -> None:
        """Create image chunk with description and metadata in single LLM call."""
        
        import time
        start_time = time.time()
        
        try:
            # Get both description and metadata in one LLM call
            description, chunk_metadata = await self._process_image_with_gpt4_and_metadata(image_data)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            chunk_metadata["processing_time"] = processing_time
            
            # Generate embedding from description
            embedding = await self._generate_embedding(description)
            
            # Create chunk
            chunk_id = str(uuid.uuid4())
            chunk_index = len(document.chunks)
            end_pos = start_pos + len(description)
            
            chunk = DocumentChunk(
                text=description,
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
            logger.debug(f"Created optimized image chunk {chunk_index} with single LLM call")
            
        except Exception as e:
            logger.error(f"Error creating enhanced image chunk: {e}")

    def _extract_images_from_page(self, page) -> List[bytes]:
        """Extract images from a PDF page."""
        if not PIL_AVAILABLE:
            logger.warning("PIL not available - image extraction disabled")
            return []
            
        images = []
        for image in page.images:
            try:
                image_bytes = image.data
                # Convert to PIL Image to verify it's a valid image
                img = Image.open(io.BytesIO(image_bytes))
                images.append(image_bytes)
            except Exception as e:
                logger.warning(f"Failed to extract image: {e}")
        return images

    async def _process_image_with_gpt4(self, image_data: bytes) -> str:
        """Process image using GPT-4 Vision API with centralized prompts."""
        try:
            import base64
            
            # Get centralized prompt template
            template = get_prompt_template("image_description")
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = self.openai_client.chat.completions.create(
                model=template.model,
                messages=[
                    {
                        "role": "system",
                        "content": template.system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": template.user_prompt_template
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=template.max_tokens,
                temperature=template.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error processing image with GPT-4: {e}")
            return f"Image processing failed: {str(e)}"
    
    async def _process_image_with_gpt4_and_metadata(self, image_data: bytes) -> tuple[str, Dict[str, Any]]:
        """Process image using GPT-4 Vision AND extract metadata in single LLM call."""
        try:
            import base64
            
            # Get combined prompt template
            template = get_prompt_template("image_description_with_metadata")
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = self.openai_client.chat.completions.create(
                model=template.model,
                messages=[
                    {
                        "role": "system",
                        "content": template.system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": template.user_prompt_template
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=template.max_tokens,
                temperature=template.temperature
            )
            
            # Parse JSON response
            import json
            response_text = response.choices[0].message.content.strip()
            
            try:
                parsed_response = json.loads(response_text)
                description = parsed_response.get("description", "")
                metadata = parsed_response.get("metadata", {})
                
                # Add basic metadata fields
                metadata.update({
                    "extraction_timestamp": datetime.utcnow().isoformat(),
                    "extractor_version": "1.4.3_combined",
                    "processing_time": 0.0  # Will be filled by caller
                })
                
                return description, metadata
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                # Fallback: treat as description only
                return response_text, {}
            
        except Exception as e:
            logger.error(f"Error processing image with GPT-4 and metadata: {e}")
            return f"Image processing failed: {str(e)}", {}

    async def _generate_table_summary(self, table_text: str) -> str:
        """Generate table summary using centralized prompts."""
        try:
            template = get_prompt_template("table_summary")
            
            response = self.openai_client.chat.completions.create(
                model=template.model,
                messages=[
                    {
                        "role": "system",
                        "content": template.system_prompt
                    },
                    {
                        "role": "user",
                        "content": template.user_prompt_template.format(table_text=table_text)
                    }
                ],
                max_tokens=template.max_tokens,
                temperature=template.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating table summary: {e}")
            return f"Table summary generation failed: {str(e)}"
    
    async def _generate_table_summary_with_metadata(self, table_text: str) -> tuple[str, Dict[str, Any]]:
        """Generate table summary AND metadata in single LLM call."""
        try:
            template = get_prompt_template("table_summary_with_metadata")
            
            response = self.openai_client.chat.completions.create(
                model=template.model,
                messages=[
                    {
                        "role": "system",
                        "content": template.system_prompt
                    },
                    {
                        "role": "user",
                        "content": template.user_prompt_template.format(table_text=table_text)
                    }
                ],
                max_tokens=template.max_tokens,
                temperature=template.temperature
            )
            
            # Parse JSON response
            import json
            response_text = response.choices[0].message.content.strip()
            
            try:
                parsed_response = json.loads(response_text)
                summary = parsed_response.get("summary", "")
                metadata = parsed_response.get("metadata", {})
                
                # Add basic metadata fields
                metadata.update({
                    "extraction_timestamp": datetime.utcnow().isoformat(),
                    "extractor_version": "1.4.3_combined",
                    "processing_time": 0.0  # Will be filled by caller
                })
                
                return summary, metadata
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                # Fallback: treat as summary only
                return response_text, {}
            
        except Exception as e:
            logger.error(f"Error generating table summary with metadata: {e}")
            return f"Table processing failed: {str(e)}", {}

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    async def get_similar_chunks(self, query: str, document: Document, top_k: int = 3) -> List[DocumentChunk]:
        """Find similar chunks in a document based on query."""
        try:
            # Generate query embedding
            query_embedding = await self._generate_embedding(query)
            
            if not query_embedding:
                return []
            
            # Calculate similarities
            similarities = []
            for chunk in document.chunks:
                if chunk.embedding:
                    similarity = self._cosine_similarity(query_embedding, chunk.embedding)
                    similarities.append((similarity, chunk))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [chunk for _, chunk in similarities[:top_k]]
            
        except Exception as e:
            logger.error(f"Error finding similar chunks: {e}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            import numpy as np
            
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0


# Factory function for easy instantiation
def create_enhanced_document_processor(openai_api_key: str) -> EnhancedDocumentProcessor:
    """
    Create an enhanced document processor with metadata extraction.
    
    Args:
        openai_api_key: OpenAI API key for LLM operations
        
    Returns:
        Configured EnhancedDocumentProcessor instance
    """
    return EnhancedDocumentProcessor(openai_api_key) 