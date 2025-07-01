from typing import List, Optional, Dict, Any, Tuple
import logging
from pathlib import Path
import tempfile
import magic
from pypdf import PdfReader
import camelot
import cv2
import numpy as np
from PIL import Image
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI

from models.document import Document, DocumentChunk, DocumentMetadata, TableData, ImageData

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing uploaded documents with enhanced table and image support."""
    
    def __init__(self, openai_api_key: str):
        """Initialize the document processor."""
        self.openai_client = OpenAI(
            base_url='https://api.openai-proxy.org/v1',
            api_key=openai_api_key,
        )
        self.embedding_model = "text-embedding-ada-002"
        self.vision_model = "gpt-4-vision-preview"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    async def process_document(self, file_path: Path, user_id: str) -> Document:
        """Process an uploaded document with enhanced table and image detection."""
        try:
            # Read file metadata
            content_type = magic.from_file(str(file_path), mime=True)
            file_size = file_path.stat().st_size
            filename = file_path.name
            
            # Create document metadata
            metadata = DocumentMetadata(
                filename=filename,
                content_type=content_type,
                size=file_size,
                has_tables=False,
                has_images=False
            )
            
            # Create document instance
            document = Document(
                user_id=user_id,
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
                await self._process_pdf(file_path, document)
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

    async def _process_pdf(self, file_path: Path, document: Document) -> None:
        """Process a PDF document with table and image detection."""
        try:
            # Read PDF
            reader = PdfReader(str(file_path))
            
            # Process each page
            for page_num, page in enumerate(reader.pages):
                # 1. Extract tables using Camelot
                tables = camelot.read_pdf(str(file_path), pages=str(page_num + 1))
                if len(tables) > 0:
                    document.metadata.has_tables = True
                    for table_idx, table in enumerate(tables):
                        # Generate table summary using GPT-4
                        table_text = table.df.to_string()
                        table_summary = await self._generate_table_summary(table_text)
                        
                        # Create table data
                        table_data = TableData(
                            page_number=page_num + 1,
                            table_index=table_idx,
                            content=table.df.values.tolist(),
                            summary=table_summary,
                            row_count=len(table.df),
                            column_count=len(table.df.columns)
                        )
                        document.tables.append(table_data)
                        
                        # Generate and store embedding for table summary
                        table_embedding = await self._generate_embedding(table_summary)
                        document.chunks.append(DocumentChunk(
                            text=table_summary,
                            page_number=page_num + 1,
                            chunk_index=len(document.chunks),
                            chunk_type="table",
                            embedding=table_embedding
                        ))
                
                # 2. Extract images
                images = self._extract_images_from_page(page)
                if images:
                    document.metadata.has_images = True
                    for img_idx, img_data in enumerate(images):
                        # Process image with GPT-4 Vision
                        image_description = await self._process_image_with_gpt4(img_data)
                        
                        # Create image data
                        image_data = ImageData(
                            page_number=page_num + 1,
                            image_index=img_idx,
                            content=img_data,
                            description=image_description
                        )
                        document.images.append(image_data)
                        
                        # Generate and store embedding for image description
                        image_embedding = await self._generate_embedding(image_description)
                        document.chunks.append(DocumentChunk(
                            text=image_description,
                            page_number=page_num + 1,
                            chunk_index=len(document.chunks),
                            chunk_type="image",
                            embedding=image_embedding
                        ))
                
                # 3. Extract and process regular text
                text = page.extract_text()
                if text.strip():  # Only process non-empty text
                    chunks = self.text_splitter.split_text(text)
                    for chunk_idx, chunk_text in enumerate(chunks):
                        chunk = DocumentChunk(
                            text=chunk_text,
                            page_number=page_num + 1,
                            chunk_index=len(document.chunks),
                            chunk_type="text",
                            embedding=await self._generate_embedding(chunk_text)
                        )
                        document.chunks.append(chunk)
            
            document.metadata.processed = True
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

    def _extract_images_from_page(self, page) -> List[bytes]:
        """Extract images from a PDF page."""
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
        """Process image using GPT-4 Vision API."""
        try:
            from prompt_template import get_prompt_template
            import base64
            
            # Get centralized prompt template
            template = get_prompt_template("image_description")
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            response = self.openai_client.chat.completions.create(
                model=template.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": template.user_prompt_template
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ],
                temperature=template.temperature,
                max_tokens=template.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error processing image with GPT-4 Vision: {e}")
            return "Failed to process image"

    async def _generate_table_summary(self, table_text: str) -> str:
        """Generate a summary of table content using GPT-4."""
        try:
            from prompt_template import format_prompt
            
            # Use centralized prompt template
            prompt_config = format_prompt("table_summary", table_text=table_text)
            
            response = self.openai_client.chat.completions.create(
                model=prompt_config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": prompt_config["system_prompt"]
                    },
                    {
                        "role": "user",
                        "content": prompt_config["user_prompt"]
                    }
                ],
                temperature=prompt_config["temperature"],
                max_tokens=prompt_config["max_tokens"]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating table summary: {e}")
            return "Failed to summarize table"

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    async def get_similar_chunks(self, query: str, document: Document, top_k: int = 3) -> List[DocumentChunk]:
        """Find similar chunks in a document based on a query."""
        try:
            query_embedding = await self._generate_embedding(query)
            chunks_with_scores = []
            for chunk in document.chunks:
                if chunk.embedding:
                    similarity = self._cosine_similarity(query_embedding, chunk.embedding)
                    chunks_with_scores.append((chunk, similarity))
            
            chunks_with_scores.sort(key=lambda x: x[1], reverse=True)
            return [chunk for chunk, _ in chunks_with_scores[:top_k]]
            
        except Exception as e:
            logger.error(f"Error finding similar chunks: {str(e)}")
            raise

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)) 