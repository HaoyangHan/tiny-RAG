"""
LlamaIndex-based RAG Service for TinyRAG
========================================

This module implements RAG (Retrieval-Augmented Generation) using LlamaIndex
following the instruction document patterns for enhanced document processing
and generation capabilities.

Author: TinyRAG Development Team
Version: 1.4.3
Last Updated: January 2025
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# LlamaIndex imports
from llama_index.core import (
    VectorStoreIndex, 
    StorageContext, 
    Document,
    QueryBundle
)
from llama_index.core.llms import LLM
from llama_index.core.embeddings import BaseEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

# TinyRAG imports
from models.document import Document as TinyRAGDocument, DocumentChunk
from prompt_template import format_prompt

logger = logging.getLogger(__name__)


class LlamaIndexRAGService:
    """
    LlamaIndex-based RAG service for document retrieval and generation.
    
    Implements the RAG patterns from the instruction document with enhanced
    retrieval and generation capabilities.
    """
    
    def __init__(self, openai_api_key: str, openai_base_url: str = "https://api.openai-proxy.org/v1"):
        """Initialize the LlamaIndex RAG service."""
        
        # Configure LlamaIndex settings
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
        
        # Initialize vector store (Qdrant)
        self.vector_store = QdrantVectorStore(
            client=None,  # Will be configured when needed
            collection_name="tinyrag_documents"
        )
        
        # Initialize storage context
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
        
        # Initialize index
        self.index = None
        
        logger.info("LlamaIndex RAG service initialized")

    async def create_index_from_documents(self, documents: List[TinyRAGDocument]) -> VectorStoreIndex:
        """
        Create LlamaIndex vector store index from TinyRAG documents.
        
        Args:
            documents: List of TinyRAG documents
            
        Returns:
            VectorStoreIndex: Created index
        """
        try:
            # Convert TinyRAG documents to LlamaIndex documents
            llama_documents = []
            
            for doc in documents:
                # Create LlamaIndex document from chunks
                for chunk in doc.chunks:
                    llama_doc = Document(
                        text=chunk.text,
                        metadata={
                            "document_id": str(doc.id),
                            "user_id": doc.user_id,
                            "project_id": doc.project_id,
                            "filename": doc.filename,
                            "content_type": doc.content_type,
                            "chunk_id": chunk.chunk_id if hasattr(chunk, 'chunk_id') else f"chunk_{chunk.chunk_index}",
                            "chunk_index": chunk.chunk_index,
                            "chunk_type": chunk.chunk_type,
                            "page_number": chunk.page_number,
                            "section": getattr(chunk, 'section', None),
                            "metadata": chunk.metadata if hasattr(chunk, 'metadata') else {}
                        }
                    )
                    llama_documents.append(llama_doc)
            
            # Create index from documents
            self.index = VectorStoreIndex.from_documents(
                llama_documents,
                storage_context=self.storage_context,
                show_progress=True
            )
            
            logger.info(f"Created LlamaIndex index with {len(llama_documents)} documents")
            return self.index
            
        except Exception as e:
            logger.error(f"Error creating LlamaIndex index: {e}")
            raise

    async def query_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query documents using LlamaIndex retrieval.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of retrieved document chunks with metadata
        """
        try:
            if not self.index:
                raise ValueError("Index not initialized. Call create_index_from_documents first.")
            
            # Create query engine
            query_engine = self.index.as_query_engine(
                similarity_top_k=top_k,
                response_mode="compact"
            )
            
            # Execute query
            response = query_engine.query(query)
            
            # Extract source nodes (retrieved documents)
            results = []
            for node in response.source_nodes:
                result = {
                    "text": node.text,
                    "score": node.score if hasattr(node, 'score') else None,
                    "metadata": node.metadata,
                    "node_id": node.node_id
                }
                results.append(result)
            
            logger.info(f"Retrieved {len(results)} documents for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            raise

    async def generate_response(self, query: str, context: List[Dict[str, Any]], 
                              prompt_template: str = "rag_generation") -> Dict[str, Any]:
        """
        Generate response using LlamaIndex with retrieved context.
        
        Args:
            query: User query
            context: Retrieved document chunks
            prompt_template: Prompt template to use
            
        Returns:
            Generated response with metadata
        """
        try:
            # Format context for generation
            context_text = self._format_context_for_generation(context)
            
            # Create generation prompt
            generation_prompt = format_prompt(
                prompt_template,
                query=query,
                context=context_text
            )
            
            # Generate response using LlamaIndex LLM
            response_text = await self.llm.apredict(
                prompt=generation_prompt["user_prompt"]
            )
            
            # Extract citations from source nodes
            citations = self._extract_citations(context)
            
            result = {
                "response": response_text,
                "query": query,
                "context": context,
                "citations": citations,
                "metadata": {
                    "model": self.llm.model,
                    "prompt_template": prompt_template,
                    "context_chunks": len(context),
                    "generation_timestamp": datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"Generated response for query: {query}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def process_document_for_rag(self, document: TinyRAGDocument) -> VectorStoreIndex:
        """
        Process a single document for RAG indexing.
        
        Args:
            document: TinyRAG document to process
            
        Returns:
            VectorStoreIndex: Updated index
        """
        try:
            # Convert document to LlamaIndex format
            llama_documents = []
            
            for chunk in document.chunks:
                llama_doc = Document(
                    text=chunk.text,
                    metadata={
                        "document_id": str(document.id),
                        "user_id": document.user_id,
                        "project_id": document.project_id,
                        "filename": document.filename,
                        "content_type": document.content_type,
                        "chunk_id": chunk.chunk_id if hasattr(chunk, 'chunk_id') else f"chunk_{chunk.chunk_index}",
                        "chunk_index": chunk.chunk_index,
                        "chunk_type": chunk.chunk_type,
                        "page_number": chunk.page_number,
                        "section": getattr(chunk, 'section', None),
                        "metadata": chunk.metadata if hasattr(chunk, 'metadata') else {}
                    }
                )
                llama_documents.append(llama_doc)
            
            # Add documents to existing index or create new one
            if self.index:
                # Insert documents into existing index
                for doc in llama_documents:
                    self.index.insert(doc)
            else:
                # Create new index
                self.index = VectorStoreIndex.from_documents(
                    llama_documents,
                    storage_context=self.storage_context,
                    show_progress=True
                )
            
            logger.info(f"Processed document {document.filename} for RAG indexing")
            return self.index
            
        except Exception as e:
            logger.error(f"Error processing document for RAG: {e}")
            raise

    def _format_context_for_generation(self, context: List[Dict[str, Any]]) -> str:
        """Format retrieved context for generation prompt."""
        
        formatted_context = []
        
        for i, chunk in enumerate(context, 1):
            metadata = chunk.get("metadata", {})
            filename = metadata.get("filename", "Unknown")
            page_number = metadata.get("page_number", "Unknown")
            chunk_type = metadata.get("chunk_type", "text")
            
            context_entry = f"[{i}] Source: {filename} (Page {page_number}, Type: {chunk_type})\n"
            context_entry += f"Content: {chunk['text']}\n"
            
            formatted_context.append(context_entry)
        
        return "\n".join(formatted_context)

    def _extract_citations(self, context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract citation information from retrieved context."""
        
        citations = []
        
        for chunk in context:
            metadata = chunk.get("metadata", {})
            
            citation = {
                "source": metadata.get("filename", "Unknown"),
                "page_number": metadata.get("page_number", "Unknown"),
                "chunk_type": metadata.get("chunk_type", "text"),
                "document_id": metadata.get("document_id", "Unknown"),
                "score": chunk.get("score"),
                "text_preview": chunk.get("text", "")[:200] + "..." if len(chunk.get("text", "")) > 200 else chunk.get("text", "")
            }
            
            citations.append(citation)
        
        return citations

    async def get_document_summary(self, document: TinyRAGDocument) -> str:
        """
        Generate document summary using LlamaIndex.
        
        Args:
            document: TinyRAG document
            
        Returns:
            Document summary
        """
        try:
            # Create LlamaIndex document from all chunks
            full_text = "\n".join([chunk.text for chunk in document.chunks])
            
            llama_doc = Document(
                text=full_text,
                metadata={
                    "document_id": str(document.id),
                    "filename": document.filename,
                    "content_type": document.content_type
                }
            )
            
            # Create index for single document
            doc_index = VectorStoreIndex.from_documents([llama_doc])
            
            # Generate summary
            summary_prompt = "Please provide a comprehensive summary of this document, highlighting the key points and main themes."
            
            query_engine = doc_index.as_query_engine()
            response = query_engine.query(summary_prompt)
            
            return response.response
            
        except Exception as e:
            logger.error(f"Error generating document summary: {e}")
            return f"Summary generation failed: {str(e)}"

    async def get_document_keywords(self, document: TinyRAGDocument) -> List[str]:
        """
        Extract keywords from document using LlamaIndex.
        
        Args:
            document: TinyRAG document
            
        Returns:
            List of keywords
        """
        try:
            # Create LlamaIndex document
            full_text = "\n".join([chunk.text for chunk in document.chunks])
            
            llama_doc = Document(
                text=full_text,
                metadata={
                    "document_id": str(document.id),
                    "filename": document.filename
                }
            )
            
            # Use LlamaIndex keyword extractor
            from llama_index.core.extractors import KeywordExtractor
            
            keyword_extractor = KeywordExtractor(keywords=10)
            metadata = keyword_extractor.extract([llama_doc])
            
            if metadata and len(metadata) > 0:
                keywords = metadata[0].get("keywords", [])
                return keywords
            
            return []
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []


def create_llamaindex_rag_service(openai_api_key: str, openai_base_url: str = "https://api.openai-proxy.org/v1") -> LlamaIndexRAGService:
    """Factory function to create LlamaIndex RAG service."""
    return LlamaIndexRAGService(openai_api_key, openai_base_url) 