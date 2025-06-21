"""
Metadata-aware rerankers for TinyRAG framework.

This module implements advanced reranking strategies that leverage extracted
metadata to improve retrieval relevance and quality.
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from pydantic import BaseModel, Field
import numpy as np

from .schemas import ChunkMetadata, ExtractedKeyword, ExtractedEntity, MetadataType, ConfidenceLevel


@dataclass
class RetrievalResult:
    """
    Represents a single retrieval result with metadata.
    
    Attributes:
        chunk_id: Unique identifier for the chunk
        content: Text content of the chunk
        base_score: Original retrieval score (e.g., from vector similarity)
        metadata: Associated chunk metadata
        final_score: Final score after reranking
        explanation: Explanation of the reranking decision
    """
    chunk_id: str
    content: str
    base_score: float
    metadata: ChunkMetadata
    final_score: Optional[float] = None
    explanation: Optional[str] = None


class RerankerConfig(BaseModel):
    """
    Configuration for metadata rerankers.
    
    Defines weights and parameters for different reranking strategies.
    """
    
    # Base scoring weights
    semantic_weight: float = Field(default=0.4, ge=0.0, le=1.0, description="Weight for semantic similarity")
    keyword_weight: float = Field(default=0.2, ge=0.0, le=1.0, description="Weight for keyword matching")
    entity_weight: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for entity matching")
    temporal_weight: float = Field(default=0.1, ge=0.0, le=1.0, description="Weight for temporal relevance")
    quality_weight: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for content quality")
    
    # Keyword matching parameters
    exact_match_bonus: float = Field(default=0.3, description="Bonus for exact keyword matches")
    partial_match_bonus: float = Field(default=0.1, description="Bonus for partial keyword matches")
    keyword_density_factor: float = Field(default=0.2, description="Factor for keyword density scoring")
    
    # Entity matching parameters
    entity_match_bonus: float = Field(default=0.25, description="Bonus for entity matches")
    entity_type_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "person": 1.0,
            "organization": 0.9,
            "location": 0.8,
            "date": 0.7,
            "misc": 0.5
        },
        description="Weights for different entity types"
    )
    
    # Temporal parameters
    recency_decay_days: int = Field(default=365, description="Days for recency decay")
    temporal_boost_factor: float = Field(default=0.2, description="Boost factor for recent content")
    
    # Quality parameters
    min_confidence_threshold: float = Field(default=0.3, description="Minimum confidence threshold")
    length_penalty_factor: float = Field(default=0.1, description="Penalty factor for very short/long chunks")
    
    # Diversity parameters
    diversity_factor: float = Field(default=0.1, description="Factor for promoting diversity")
    max_similar_results: int = Field(default=3, description="Maximum similar results to return")


class BaseReranker(ABC):
    """Abstract base class for rerankers."""
    
    def __init__(self, config: RerankerConfig):
        """
        Initialize the reranker with configuration.
        
        Args:
            config: Reranker configuration
        """
        self.config = config
    
    @abstractmethod
    def rerank(
        self, 
        query: str, 
        results: List[RetrievalResult],
        query_metadata: Optional[ChunkMetadata] = None
    ) -> List[RetrievalResult]:
        """
        Rerank retrieval results based on metadata.
        
        Args:
            query: Original search query
            results: List of retrieval results to rerank
            query_metadata: Optional metadata extracted from the query
            
        Returns:
            Reranked list of results
        """
        pass


class MetadataReranker(BaseReranker):
    """
    Metadata-aware reranker that uses extracted metadata for scoring.
    
    This reranker combines multiple signals including keyword matching,
    entity matching, temporal relevance, and content quality.
    """
    
    def rerank(
        self, 
        query: str, 
        results: List[RetrievalResult],
        query_metadata: Optional[ChunkMetadata] = None
    ) -> List[RetrievalResult]:
        """Rerank results using metadata signals."""
        
        # Extract query terms and entities if not provided
        if not query_metadata:
            query_metadata = self._extract_query_metadata(query)
        
        # Calculate reranking scores
        for result in results:
            score_components = self._calculate_score_components(
                query, query_metadata, result
            )
            
            # Combine scores with weights
            final_score = (
                result.base_score * self.config.semantic_weight +
                score_components['keyword_score'] * self.config.keyword_weight +
                score_components['entity_score'] * self.config.entity_weight +
                score_components['temporal_score'] * self.config.temporal_weight +
                score_components['quality_score'] * self.config.quality_weight
            )
            
            result.final_score = final_score
            result.explanation = self._generate_explanation(score_components)
        
        # Sort by final score and apply diversity filtering
        ranked_results = sorted(results, key=lambda r: r.final_score, reverse=True)
        
        if self.config.diversity_factor > 0:
            ranked_results = self._apply_diversity_filtering(ranked_results)
        
        return ranked_results
    
    def _extract_query_metadata(self, query: str) -> ChunkMetadata:
        """Extract basic metadata from query text."""
        # Simple keyword extraction from query
        query_words = query.lower().split()
        keywords = [
            ExtractedKeyword(
                term=word,
                score=1.0,
                frequency=query_words.count(word)
            )
            for word in set(query_words)
            if len(word) > 2
        ]
        
        return ChunkMetadata(
            chunk_id="query",
            document_id="query",
            chunk_index=0,
            text_length=len(query),
            start_pos=0,
            end_pos=len(query),
            keywords=keywords
        )
    
    def _calculate_score_components(
        self, 
        query: str, 
        query_metadata: ChunkMetadata, 
        result: RetrievalResult
    ) -> Dict[str, float]:
        """Calculate individual score components."""
        components = {}
        
        # Keyword matching score
        components['keyword_score'] = self._calculate_keyword_score(
            query_metadata.keywords, result.metadata.keywords
        )
        
        # Entity matching score
        components['entity_score'] = self._calculate_entity_score(
            query_metadata.entities, result.metadata.entities
        )
        
        # Temporal relevance score
        components['temporal_score'] = self._calculate_temporal_score(
            result.metadata
        )
        
        # Content quality score
        components['quality_score'] = self._calculate_quality_score(
            result.metadata
        )
        
        return components
    
    def _calculate_keyword_score(
        self, 
        query_keywords: List[ExtractedKeyword], 
        chunk_keywords: List[ExtractedKeyword]
    ) -> float:
        """Calculate keyword matching score."""
        if not query_keywords or not chunk_keywords:
            return 0.0
        
        query_terms = {kw.term.lower() for kw in query_keywords}
        chunk_terms = {kw.term.lower(): kw.score for kw in chunk_keywords}
        
        total_score = 0.0
        matched_terms = 0
        
        for query_term in query_terms:
            if query_term in chunk_terms:
                # Exact match
                total_score += chunk_terms[query_term] + self.config.exact_match_bonus
                matched_terms += 1
            else:
                # Check for partial matches
                for chunk_term in chunk_terms:
                    if query_term in chunk_term or chunk_term in query_term:
                        total_score += chunk_terms[chunk_term] * self.config.partial_match_bonus
                        break
        
        # Normalize by number of query terms
        if len(query_terms) > 0:
            match_ratio = matched_terms / len(query_terms)
            total_score = (total_score / len(query_terms)) * (1 + match_ratio * self.config.keyword_density_factor)
        
        return min(total_score, 1.0)
    
    def _calculate_entity_score(
        self, 
        query_entities: List[ExtractedEntity], 
        chunk_entities: List[ExtractedEntity]
    ) -> float:
        """Calculate entity matching score."""
        if not query_entities or not chunk_entities:
            return 0.0
        
        query_entity_texts = {ent.text.lower() for ent in query_entities}
        chunk_entity_map = {ent.text.lower(): ent for ent in chunk_entities}
        
        total_score = 0.0
        matched_entities = 0
        
        for query_entity_text in query_entity_texts:
            if query_entity_text in chunk_entity_map:
                chunk_entity = chunk_entity_map[query_entity_text]
                entity_type_weight = self.config.entity_type_weights.get(
                    chunk_entity.label.value, 0.5
                )
                
                entity_score = (
                    chunk_entity.confidence * 
                    entity_type_weight * 
                    self.config.entity_match_bonus
                )
                
                total_score += entity_score
                matched_entities += 1
        
        # Normalize by number of query entities
        if len(query_entities) > 0:
            total_score /= len(query_entities)
        
        return min(total_score, 1.0)
    
    def _calculate_temporal_score(self, metadata: ChunkMetadata) -> float:
        """Calculate temporal relevance score."""
        if not metadata.dates:
            return 0.5  # Neutral score for content without dates
        
        current_time = datetime.utcnow()
        most_recent_date = max(date.date for date in metadata.dates)
        
        # Calculate days since most recent date
        days_diff = (current_time - most_recent_date).days
        
        # Apply exponential decay
        decay_factor = math.exp(-days_diff / self.config.recency_decay_days)
        temporal_score = 0.5 + (decay_factor * self.config.temporal_boost_factor)
        
        return min(temporal_score, 1.0)
    
    def _calculate_quality_score(self, metadata: ChunkMetadata) -> float:
        """Calculate content quality score."""
        quality_score = 0.5  # Base quality score
        
        # Factor in metadata confidence levels
        confidence_scores = []
        
        if metadata.keywords:
            avg_keyword_confidence = sum(kw.score for kw in metadata.keywords) / len(metadata.keywords)
            confidence_scores.append(avg_keyword_confidence)
        
        if metadata.entities:
            avg_entity_confidence = sum(ent.confidence for ent in metadata.entities) / len(metadata.entities)
            confidence_scores.append(avg_entity_confidence)
        
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            quality_score += (avg_confidence - 0.5) * 0.3
        
        # Factor in content length (penalize very short or very long chunks)
        optimal_length = 500  # characters
        length_ratio = metadata.text_length / optimal_length
        
        if length_ratio < 0.2 or length_ratio > 3.0:
            quality_score -= self.config.length_penalty_factor
        
        # Factor in information density
        if metadata.information_density:
            quality_score += (metadata.information_density - 0.5) * 0.2
        
        return max(min(quality_score, 1.0), 0.0)
    
    def _generate_explanation(self, score_components: Dict[str, float]) -> str:
        """Generate human-readable explanation for the reranking decision."""
        explanations = []
        
        if score_components['keyword_score'] > 0.5:
            explanations.append(f"Strong keyword match (score: {score_components['keyword_score']:.2f})")
        
        if score_components['entity_score'] > 0.3:
            explanations.append(f"Entity match found (score: {score_components['entity_score']:.2f})")
        
        if score_components['temporal_score'] > 0.7:
            explanations.append("Recent content")
        elif score_components['temporal_score'] < 0.3:
            explanations.append("Older content")
        
        if score_components['quality_score'] > 0.7:
            explanations.append("High-quality content")
        elif score_components['quality_score'] < 0.3:
            explanations.append("Lower-quality content")
        
        return "; ".join(explanations) if explanations else "Standard relevance scoring"
    
    def _apply_diversity_filtering(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """Apply diversity filtering to avoid too many similar results."""
        if len(results) <= self.config.max_similar_results:
            return results
        
        filtered_results = []
        used_keywords = set()
        
        for result in results:
            # Check if this result is too similar to already selected ones
            result_keywords = {kw.term.lower() for kw in result.metadata.keywords[:5]}  # Top 5 keywords
            
            similarity = len(result_keywords.intersection(used_keywords)) / max(len(result_keywords), 1)
            
            if similarity < 0.7 or len(filtered_results) < self.config.max_similar_results:
                filtered_results.append(result)
                used_keywords.update(result_keywords)
        
        return filtered_results


class HybridReranker(BaseReranker):
    """
    Hybrid reranker that combines multiple reranking strategies.
    
    This reranker can combine semantic similarity, BM25 scoring,
    and metadata-based scoring for optimal results.
    """
    
    def __init__(self, config: RerankerConfig):
        """Initialize hybrid reranker."""
        super().__init__(config)
        self.metadata_reranker = MetadataReranker(config)
    
    def rerank(
        self, 
        query: str, 
        results: List[RetrievalResult],
        query_metadata: Optional[ChunkMetadata] = None
    ) -> List[RetrievalResult]:
        """Rerank using hybrid approach."""
        
        # First pass: metadata-based reranking
        metadata_ranked = self.metadata_reranker.rerank(query, results, query_metadata)
        
        # Second pass: apply additional hybrid scoring
        for result in metadata_ranked:
            # Calculate BM25-like score for keyword matching
            bm25_score = self._calculate_bm25_score(query, result.content)
            
            # Combine with metadata score
            hybrid_score = (
                result.final_score * 0.7 +  # Metadata score
                bm25_score * 0.3            # BM25 score
            )
            
            result.final_score = hybrid_score
        
        # Final ranking
        return sorted(metadata_ranked, key=lambda r: r.final_score, reverse=True)
    
    def _calculate_bm25_score(self, query: str, document: str, k1: float = 1.5, b: float = 0.75) -> float:
        """Calculate BM25 score for query-document pair."""
        query_terms = query.lower().split()
        doc_terms = document.lower().split()
        doc_length = len(doc_terms)
        
        # Simplified BM25 calculation (without corpus statistics)
        avgdl = 100  # Assumed average document length
        score = 0.0
        
        for term in query_terms:
            tf = doc_terms.count(term)
            if tf > 0:
                idf = math.log(1000 / (tf + 1))  # Simplified IDF
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (doc_length / avgdl))
                score += idf * (numerator / denominator)
        
        return min(score / len(query_terms), 1.0) if query_terms else 0.0


def create_reranker(reranker_type: str = "metadata", config: Optional[RerankerConfig] = None) -> BaseReranker:
    """
    Factory function to create rerankers.
    
    Args:
        reranker_type: Type of reranker ('metadata' or 'hybrid')
        config: Optional reranker configuration
        
    Returns:
        Configured reranker instance
    """
    if config is None:
        config = RerankerConfig()
    
    if reranker_type == "metadata":
        return MetadataReranker(config)
    elif reranker_type == "hybrid":
        return HybridReranker(config)
    else:
        raise ValueError(f"Unknown reranker type: {reranker_type}")


# Example usage and testing functions
def example_usage():
    """Example of how to use the metadata reranker."""
    
    # Create sample results
    sample_results = [
        RetrievalResult(
            chunk_id="chunk_1",
            content="This is a document about machine learning algorithms published in 2023.",
            base_score=0.8,
            metadata=ChunkMetadata(
                chunk_id="chunk_1",
                document_id="doc_1",
                chunk_index=0,
                text_length=100,
                start_pos=0,
                end_pos=100,
                keywords=[
                    ExtractedKeyword(term="machine", score=0.9, frequency=2),
                    ExtractedKeyword(term="learning", score=0.8, frequency=2),
                    ExtractedKeyword(term="algorithms", score=0.7, frequency=1)
                ]
            )
        )
    ]
    
    # Create reranker
    config = RerankerConfig(
        semantic_weight=0.4,
        keyword_weight=0.3,
        entity_weight=0.2,
        temporal_weight=0.1
    )
    
    reranker = MetadataReranker(config)
    
    # Rerank results
    query = "machine learning algorithms"
    reranked_results = reranker.rerank(query, sample_results)
    
    # Display results
    for i, result in enumerate(reranked_results):
        print(f"Rank {i+1}: {result.chunk_id}")
        print(f"  Base Score: {result.base_score:.3f}")
        print(f"  Final Score: {result.final_score:.3f}")
        print(f"  Explanation: {result.explanation}")
        print()


if __name__ == "__main__":
    example_usage() 