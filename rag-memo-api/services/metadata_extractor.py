"""
LlamaIndex-style Metadata Extractor for TinyRAG
==============================================

This module provides comprehensive metadata extraction for document chunks
following LlamaIndex BaseExtractor pattern while integrating with TinyRAG's
ChunkMetadata schema.

Author: TinyRAG Development Team
Version: 1.4.3
Last Updated: January 2025
"""

import logging
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

# LlamaIndex-style imports (simulated for compatibility)
from pydantic import BaseModel

# TinyRAG imports
from prompt_template import format_prompt

logger = logging.getLogger(__name__)


class BaseNode(BaseModel):
    """Simulated LlamaIndex BaseNode for compatibility."""
    text: str
    node_id: str = ""
    metadata: Dict[str, Any] = {}
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.node_id:
            self.node_id = str(uuid.uuid4())


class BaseExtractor(ABC):
    """Base class for metadata extractors following LlamaIndex pattern."""
    
    @abstractmethod
    def extract(self, nodes: List[BaseNode]) -> List[Dict[str, Any]]:
        """Extract metadata from a list of nodes."""
        pass


class CustomMetadataExtractor(BaseExtractor):
    """
    Custom metadata extractor that extracts comprehensive metadata
    following TinyRAG's ChunkMetadata schema.
    """
    
    def __init__(self, 
                 openai_client=None,
                 extract_keywords: bool = True,
                 extract_entities: bool = True,
                 extract_dates: bool = True,
                 extract_sentiment: bool = False,
                 extract_summary: bool = False,
                 max_keywords: int = 10,
                 min_confidence: float = 0.5):
        """
        Initialize the metadata extractor.
        
        Args:
            openai_client: OpenAI client for LLM-based extraction
            extract_keywords: Whether to extract keywords
            extract_entities: Whether to extract entities
            extract_dates: Whether to extract dates
            extract_sentiment: Whether to extract sentiment
            extract_summary: Whether to extract summary
            max_keywords: Maximum number of keywords to extract
            min_confidence: Minimum confidence threshold
        """
        self.openai_client = openai_client
        self.extract_keywords = extract_keywords
        self.extract_entities = extract_entities
        self.extract_dates = extract_dates
        self.extract_sentiment = extract_sentiment
        self.extract_summary = extract_summary
        self.max_keywords = max_keywords
        self.min_confidence = min_confidence
    
    def extract(self, nodes: List[BaseNode]) -> List[Dict[str, Any]]:
        """
        Extract metadata from a list of nodes.
        
        Args:
            nodes: List of text nodes to process
            
        Returns:
            List of metadata dictionaries for each node
        """
        metadata_list = []
        
        for node in nodes:
            start_time = time.time()
            
            try:
                # Extract comprehensive metadata for this chunk
                chunk_metadata = self._extract_chunk_metadata(node)
                
                # Calculate processing time
                processing_time = time.time() - start_time
                chunk_metadata["processing_time"] = processing_time
                
                metadata_list.append(chunk_metadata)
                
            except Exception as e:
                logger.error(f"Error extracting metadata for node {node.node_id}: {e}")
                # Return basic metadata on error
                metadata_list.append({
                    "chunk_id": node.node_id,
                    "text_length": len(node.text),
                    "extraction_error": str(e),
                    "processing_time": time.time() - start_time
                })
        
        return metadata_list
    
    def _extract_chunk_metadata(self, node: BaseNode) -> Dict[str, Any]:
        """Extract comprehensive metadata for a single chunk."""
        
        # Basic metadata
        metadata = {
            "chunk_id": node.node_id,
            "text_length": len(node.text),
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "extractor_version": "1.4.3",
        }
        
        # Extract position information from node metadata if available
        if "start_pos" in node.metadata:
            metadata["start_pos"] = node.metadata["start_pos"]
        if "end_pos" in node.metadata:
            metadata["end_pos"] = node.metadata["end_pos"]
        if "page_number" in node.metadata:
            metadata["page_number"] = node.metadata["page_number"]
        if "section" in node.metadata:
            metadata["section"] = node.metadata["section"]
        
        # Simple text-based extractions
        metadata.update(self._extract_basic_features(node.text))
        
        # LLM-based extractions (if OpenAI client available)
        if self.openai_client:
            try:
                llm_metadata = self._extract_with_llm(node.text)
                metadata.update(llm_metadata)
            except Exception as e:
                logger.warning(f"LLM extraction failed for chunk {node.node_id}: {e}")
                metadata["llm_extraction_error"] = str(e)
        
        return metadata
    
    def _extract_basic_features(self, text: str) -> Dict[str, Any]:
        """Extract basic features from text without LLM."""
        
        features = {}
        
        # Basic text statistics
        words = text.split()
        sentences = text.split('.')
        
        features["word_count"] = len(words)
        features["sentence_count"] = len([s for s in sentences if s.strip()])
        features["avg_word_length"] = sum(len(word) for word in words) / len(words) if words else 0
        features["avg_sentence_length"] = len(words) / len(sentences) if sentences else 0
        
        # Simple readability estimate (Flesch-like)
        if words and sentences:
            features["readability_score"] = max(0, min(1, 
                206.835 - 1.015 * features["avg_sentence_length"] - 84.6 * (features["avg_word_length"] / 4.7)
            ) / 100)
        else:
            features["readability_score"] = 0.5
        
        # Information density estimate (ratio of unique words)
        unique_words = set(word.lower() for word in words)
        features["information_density"] = len(unique_words) / len(words) if words else 0
        
        # Detect language (simple heuristic)
        features["language"] = self._detect_language_simple(text)
        
        # Detect text type
        features["text_type"] = self._detect_text_type(text)
        
        # Extract simple keywords (most frequent meaningful words)
        if self.extract_keywords:
            features["keywords"] = self._extract_simple_keywords(text)
        
        # Extract simple dates
        if self.extract_dates:
            features["dates"] = self._extract_simple_dates(text)
        
        return features
    
    def _extract_with_llm(self, text: str) -> Dict[str, Any]:
        """Extract metadata using LLM (OpenAI)."""
        
        llm_metadata = {}
        
        try:
            # Use centralized prompt template for metadata extraction
            prompt_config = format_prompt("comprehensive_metadata", text=text)
            
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
            
            # Parse JSON response
            import json
            llm_result = json.loads(response.choices[0].message.content)
            
            # Map LLM results to our metadata format
            if "keywords" in llm_result and self.extract_keywords:
                llm_metadata["llm_keywords"] = llm_result["keywords"][:self.max_keywords]
            
            if "entities" in llm_result and self.extract_entities:
                llm_metadata["llm_entities"] = llm_result["entities"]
            
            if "dates" in llm_result and self.extract_dates:
                llm_metadata["llm_dates"] = llm_result["dates"]
            
            if "sentiment" in llm_result and self.extract_sentiment:
                llm_metadata["llm_sentiment"] = llm_result["sentiment"]
            
            if "summary" in llm_result and self.extract_summary:
                llm_metadata["llm_summary"] = llm_result["summary"]
            
            if "key_phrases" in llm_result:
                llm_metadata["llm_key_phrases"] = llm_result["key_phrases"]
            
            if "topics" in llm_result:
                llm_metadata["llm_topics"] = llm_result["topics"]
            
        except Exception as e:
            logger.error(f"LLM metadata extraction failed: {e}")
            llm_metadata["llm_error"] = str(e)
        
        return llm_metadata
    
    def _detect_language_simple(self, text: str) -> str:
        """Simple language detection based on character patterns."""
        # Very basic heuristic - in production, use proper language detection
        if any(ord(char) > 127 for char in text):
            return "non-english"
        return "en"
    
    def _detect_text_type(self, text: str) -> str:
        """Detect the type of text content."""
        text_lower = text.lower().strip()
        
        if text.count('\n') > 3:
            return "multi_paragraph"
        elif text.startswith('•') or text.startswith('-') or text.startswith('*'):
            return "list"
        elif text.count('?') > 0:
            return "question"
        elif len(text.split('.')) == 1:
            return "fragment"
        else:
            return "paragraph"
    
    def _extract_simple_keywords(self, text: str) -> List[Dict[str, Any]]:
        """Extract keywords using simple frequency analysis."""
        import re
        from collections import Counter
        
        # Simple stopwords
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        words = [word for word in words if word not in stopwords]
        
        # Count frequencies
        word_counts = Counter(words)
        
        # Convert to keyword format
        keywords = []
        total_words = len(words)
        
        for word, count in word_counts.most_common(self.max_keywords):
            score = count / total_words if total_words > 0 else 0
            if score >= self.min_confidence / 10:  # Adjust threshold for simple extraction
                keywords.append({
                    "term": word,
                    "score": score,
                    "frequency": count,
                    "context": self._get_word_context(text, word)
                })
        
        return keywords
    
    def _get_word_context(self, text: str, word: str, context_size: int = 50) -> str:
        """Get surrounding context for a word."""
        import re
        
        pattern = rf'\b{re.escape(word)}\b'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            start = max(0, match.start() - context_size)
            end = min(len(text), match.end() + context_size)
            return text[start:end].strip()
        
        return ""
    
    def _extract_simple_dates(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates using simple regex patterns."""
        import re
        from datetime import datetime
        
        dates = []
        
        # Common date patterns
        patterns = [
            (r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b', '%Y-%m-%d'),
            (r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', '%m/%d/%Y'),
            (r'\b(\d{1,2})-(\d{1,2})-(\d{4})\b', '%m-%d-%Y'),
            (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b', '%B %d %Y'),
        ]
        
        for pattern, date_format in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                try:
                    date_text = match.group(0)
                    
                    # Parse date based on format
                    if date_format == '%B %d %Y':
                        # Handle month name format
                        parsed_date = datetime.strptime(date_text.replace(',', ''), date_format)
                    else:
                        parsed_date = datetime.strptime(date_text, date_format)
                    
                    dates.append({
                        "date": parsed_date.isoformat(),
                        "text": date_text,
                        "confidence": 0.8,  # Simple extraction confidence
                        "date_type": "general",
                        "format": date_format
                    })
                    
                except ValueError:
                    # Skip invalid dates
                    continue
        
        return dates


class TinyRAGMetadataExtractor(CustomMetadataExtractor):
    """
    Specialized metadata extractor for TinyRAG that produces
    ChunkMetadata-compatible output.
    """
    
    def __init__(self, **kwargs):
        """Initialize with TinyRAG-specific defaults."""
        super().__init__(
            extract_keywords=True,
            extract_entities=True,
            extract_dates=True,
            extract_sentiment=True,
            extract_summary=True,
            max_keywords=15,
            min_confidence=0.3,
            **kwargs
        )
    
    def extract_chunk_metadata(self, text: str, 
                              chunk_id: str,
                              document_id: str,
                              chunk_index: int,
                              start_pos: int = 0,
                              end_pos: Optional[int] = None,
                              page_number: Optional[int] = None,
                              section: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract metadata for a single chunk in TinyRAG format.
        
        Args:
            text: Chunk text content
            chunk_id: Unique chunk identifier
            document_id: Parent document ID
            chunk_index: Index within document
            start_pos: Start position in document
            end_pos: End position in document
            page_number: Page number if applicable
            section: Document section
            
        Returns:
            Dictionary with ChunkMetadata-compatible structure
        """
        
        # Create a node for processing
        node = BaseNode(
            text=text,
            node_id=chunk_id,
            metadata={
                "document_id": document_id,
                "chunk_index": chunk_index,
                "start_pos": start_pos,
                "end_pos": end_pos or (start_pos + len(text)),
                "page_number": page_number,
                "section": section
            }
        )
        
        # Extract metadata
        metadata_list = self.extract([node])
        
        if metadata_list:
            metadata = metadata_list[0]
            
            # Add required ChunkMetadata fields
            metadata.update({
                "document_id": document_id,
                "chunk_index": chunk_index,
                "start_pos": start_pos,
                "end_pos": end_pos or (start_pos + len(text)),
                "page_number": page_number,
                "section": section
            })
            
            return metadata
        
        # Return minimal metadata on failure
        return {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "chunk_index": chunk_index,
            "text_length": len(text),
            "start_pos": start_pos,
            "end_pos": end_pos or (start_pos + len(text)),
            "page_number": page_number,
            "section": section,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "extractor_version": "1.4.3",
            "extraction_error": "Failed to extract metadata"
        }


# Factory function for easy instantiation
def create_metadata_extractor(openai_client=None, **kwargs) -> TinyRAGMetadataExtractor:
    """
    Create a TinyRAG metadata extractor with optional OpenAI client.
    
    Args:
        openai_client: OpenAI client for LLM-based extraction
        **kwargs: Additional configuration options
        
    Returns:
        Configured TinyRAGMetadataExtractor instance
    """
    return TinyRAGMetadataExtractor(openai_client=openai_client, **kwargs) 