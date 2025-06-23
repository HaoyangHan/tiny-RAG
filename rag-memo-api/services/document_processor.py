from typing import List, Optional
import logging
from pathlib import Path
import tempfile
import magic
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from models.document import Document, DocumentChunk, DocumentMetadata

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Service for processing uploaded documents."""
    
    def __init__(self, openai_api_key: str):
        """Initialize the document processor."""
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    async def process_document(self, file_path: Path, user_id: str) -> Document:
        """Process an uploaded document."""
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
            
            # Create document instance with required fields
            document = Document(
                user_id=user_id,
                filename=filename,
                content_type=content_type,
                file_size=file_size,
                status="processing",
                metadata=metadata,
                chunks=[]
            )
            
            # Process document based on content type
            if content_type == "application/pdf":
                await self._process_pdf(file_path, document)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Update status to completed
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
        """Process a PDF document."""
        try:
            # Read PDF
            reader = PdfReader(str(file_path))
            
            # Extract text from each page
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                
                # Split text into chunks
                chunks = self.text_splitter.split_text(text)
                
                # Create document chunks
                for chunk_idx, chunk_text in enumerate(chunks):
                    chunk = DocumentChunk(
                        text=chunk_text,
                        page_number=page_num + 1,
                        chunk_index=chunk_idx
                    )
                    document.chunks.append(chunk)
            
            # Generate embeddings for chunks
            for chunk in document.chunks:
                chunk.embedding = await self.embeddings.aembed_query(chunk.text)
            
            document.metadata.processed = True
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

    async def get_similar_chunks(self, query: str, document: Document, top_k: int = 3) -> List[DocumentChunk]:
        """Find similar chunks in a document based on a query."""
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Calculate similarity scores
            chunks_with_scores = []
            for chunk in document.chunks:
                if chunk.embedding:
                    similarity = self._cosine_similarity(query_embedding, chunk.embedding)
                    chunks_with_scores.append((chunk, similarity))
            
            # Sort by similarity and return top k
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