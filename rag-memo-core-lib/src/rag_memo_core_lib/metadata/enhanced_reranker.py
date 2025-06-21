"""
Enhanced metadata-aware reranker with LLM integration.

This module provides advanced reranking capabilities that leverage
LLM-extracted metadata for superior retrieval performance.
"""

import asyncio
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pydantic import BaseModel, Field
import numpy as np

from .schemas import ChunkMetadata, ExtractedKeyword, ExtractedEntity, MetadataType
from .llm_extractors import LLMMetadataExtractionPipeline, LLMConfig


@dataclass
class EnhancedRetrievalResult:
    """Enhanced retrieval result with LLM-extracted metadata."""
    chunk_id: str
    content: str
    base_score: float
    metadata: Optional[ChunkMetadata] = None
    query_metadata: Optional[ChunkMetadata] = None
    final_score: Optional[float] = None
    score_breakdown: Optional[Dict[str, float]] = None
    explanation: Optional[str] = None


class EnhancedRerankerConfig(BaseModel):
    """Configuration for enhanced metadata reranker."""
    
    # LLM Configuration
    llm_provider: str = Field(default="openai", description="LLM provider")
    llm_model: str = Field(default="gpt-4o-mini", description="LLM model")
    llm_api_key: Optional[str] = Field(default=None, description="LLM API key")
    
    # Scoring weights
    semantic_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    keyword_weight: float = Field(default=0.25, ge=0.0, le=1.0)
    entity_weight: float = Field(default=0.20, ge=0.0, le=1.0)
    topic_weight: float = Field(default=0.15, ge=0.0, le=1.0)
    temporal_weight: float = Field(default=0.10, ge=0.0, le=1.0)
    quality_weight: float = Field(default=0.05, ge=0.0, le=1.0)
    
    # Keyword matching
    exact_match_bonus: float = Field(default=0.5, description="Bonus for exact keyword matches")
    semantic_match_bonus: float = Field(default=0.3, description="Bonus for semantic keyword matches")
    keyword_frequency_factor: float = Field(default=0.2, description="Factor for keyword frequency")
    
    # Entity matching
    entity_exact_match_bonus: float = Field(default=0.6, description="Bonus for exact entity matches")
    entity_type_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "person": 1.0,
            "organization": 0.9,
            "location": 0.8,
            "product": 0.7,
            "event": 0.6,
            "misc": 0.4
        }
    )
    
    # Topic matching
    topic_similarity_threshold: float = Field(default=0.3, description="Threshold for topic similarity")
    topic_overlap_bonus: float = Field(default=0.4, description="Bonus for topic overlap")
    
    # Temporal relevance
    recency_decay_days: int = Field(default=365, description="Days for recency decay")
    temporal_boost_recent: float = Field(default=0.3, description="Boost for recent content")
    temporal_penalty_old: float = Field(default=0.2, description="Penalty for old content")
    
    # Quality assessment
    min_confidence_threshold: float = Field(default=0.4, description="Minimum confidence threshold")
    readability_weight: float = Field(default=0.3, description="Weight for readability score")
    information_density_weight: float = Field(default=0.4, description="Weight for information density")
    summary_quality_weight: float = Field(default=0.3, description="Weight for summary quality")
    
    # Performance settings
    max_concurrent_extractions: int = Field(default=5, description="Max concurrent LLM extractions")
    cache_extractions: bool = Field(default=True, description="Cache extraction results")


class EnhancedMetadataReranker:
    """
    Enhanced reranker with LLM-based metadata extraction.
    
    This reranker uses LLM to extract high-quality metadata from both
    queries and documents, then applies sophisticated scoring algorithms
    for optimal retrieval performance.
    """
    
    def __init__(self, config: EnhancedRerankerConfig):
        """Initialize the enhanced reranker."""
        self.config = config
        
        # Initialize LLM extractor
        llm_config = LLMConfig(
            provider=config.llm_provider,
            model=config.llm_model,
            api_key=config.llm_api_key
        )
        self.llm_extractor = LLMMetadataExtractionPipeline(llm_config)
        
        # Cache for extractions
        self.extraction_cache: Dict[str, ChunkMetadata] = {}
    
    async def rerank(
        self, 
        query: str, 
        results: List[EnhancedRetrievalResult],
        extract_query_metadata: bool = True
    ) -> List[EnhancedRetrievalResult]:
        """
        Rerank retrieval results using LLM-enhanced metadata.
        
        Args:
            query: Search query
            results: List of retrieval results
            extract_query_metadata: Whether to extract metadata from query
            
        Returns:
            Reranked results with scores and explanations
        """
        # Extract query metadata if needed
        query_metadata = None
        if extract_query_metadata:
            query_metadata = await self._extract_query_metadata(query)
        
        # Extract metadata for results that don't have it
        await self._extract_results_metadata(results)
        
        # Calculate enhanced scores
        for result in results:
            result.query_metadata = query_metadata
            score_breakdown = await self._calculate_enhanced_score(
                query, query_metadata, result
            )
            
            result.score_breakdown = score_breakdown
            result.final_score = sum(score_breakdown.values())
            result.explanation = self._generate_detailed_explanation(score_breakdown)
        
        # Sort by final score
        ranked_results = sorted(results, key=lambda r: r.final_score, reverse=True)
        
        # Apply diversity filtering
        return self._apply_enhanced_diversity_filtering(ranked_results)
    
    async def _extract_query_metadata(self, query: str) -> Optional[ChunkMetadata]:
        """Extract metadata from the search query."""
        try:
            cache_key = f"query_{hash(query)}"
            
            if self.config.cache_extractions and cache_key in self.extraction_cache:
                return self.extraction_cache[cache_key]
            
            extraction_result = await self.llm_extractor.extract(query, "query")
            
            if extraction_result.success:
                if self.config.cache_extractions:
                    self.extraction_cache[cache_key] = extraction_result.metadata
                return extraction_result.metadata
            
        except Exception as e:
            print(f"Query metadata extraction failed: {e}")
        
        return None
    
    async def _extract_results_metadata(self, results: List[EnhancedRetrievalResult]):
        """Extract metadata for results that don't have it."""
        # Find results without metadata
        results_to_extract = [
            (i, result) for i, result in enumerate(results) 
            if result.metadata is None
        ]
        
        if not results_to_extract:
            return
        
        # Create semaphore for concurrent extractions
        semaphore = asyncio.Semaphore(self.config.max_concurrent_extractions)
        
        async def extract_with_semaphore(index: int, result: EnhancedRetrievalResult):
            async with semaphore:
                try:
                    cache_key = f"content_{hash(result.content)}"
                    
                    if self.config.cache_extractions and cache_key in self.extraction_cache:
                        result.metadata = self.extraction_cache[cache_key]
                        return
                    
                    extraction_result = await self.llm_extractor.extract(
                        result.content, result.chunk_id
                    )
                    
                    if extraction_result.success:
                        result.metadata = extraction_result.metadata
                        if self.config.cache_extractions:
                            self.extraction_cache[cache_key] = extraction_result.metadata
                
                except Exception as e:
                    print(f"Metadata extraction failed for {result.chunk_id}: {e}")
        
        # Run extractions concurrently
        tasks = [
            extract_with_semaphore(index, result) 
            for index, result in results_to_extract
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _calculate_enhanced_score(
        self, 
        query: str, 
        query_metadata: Optional[ChunkMetadata], 
        result: EnhancedRetrievalResult
    ) -> Dict[str, float]:
        """Calculate enhanced scoring with detailed breakdown."""
        score_breakdown = {}
        
        # Base semantic score
        score_breakdown['semantic'] = result.base_score * self.config.semantic_weight
        
        # Enhanced keyword matching
        score_breakdown['keyword'] = self._calculate_enhanced_keyword_score(
            query, query_metadata, result.metadata
        ) * self.config.keyword_weight
        
        # Enhanced entity matching
        score_breakdown['entity'] = self._calculate_enhanced_entity_score(
            query_metadata, result.metadata
        ) * self.config.entity_weight
        
        # Topic similarity scoring
        score_breakdown['topic'] = self._calculate_topic_similarity_score(
            query_metadata, result.metadata
        ) * self.config.topic_weight
        
        # Enhanced temporal relevance
        score_breakdown['temporal'] = self._calculate_enhanced_temporal_score(
            result.metadata
        ) * self.config.temporal_weight
        
        # Content quality assessment
        score_breakdown['quality'] = self._calculate_enhanced_quality_score(
            result.metadata
        ) * self.config.quality_weight
        
        return score_breakdown
    
    def _calculate_enhanced_keyword_score(
        self, 
        query: str, 
        query_metadata: Optional[ChunkMetadata], 
        content_metadata: Optional[ChunkMetadata]
    ) -> float:
        """Calculate enhanced keyword matching score."""
        if not content_metadata or not content_metadata.keywords:
            return 0.0
        
        # Get query keywords from metadata or extract from query text
        query_keywords = set()
        if query_metadata and query_metadata.keywords:
            query_keywords = {kw.term.lower() for kw in query_metadata.keywords}
        else:
            # Fallback to simple query tokenization
            query_keywords = {word.lower() for word in query.split() if len(word) > 2}
        
        if not query_keywords:
            return 0.0
        
        content_keyword_map = {
            kw.term.lower(): kw for kw in content_metadata.keywords
        }
        
        total_score = 0.0
        matched_keywords = 0
        
        for query_keyword in query_keywords:
            # Exact match
            if query_keyword in content_keyword_map:
                keyword_obj = content_keyword_map[query_keyword]
                match_score = (
                    keyword_obj.score * self.config.exact_match_bonus +
                    (keyword_obj.frequency / 10) * self.config.keyword_frequency_factor
                )
                total_score += match_score
                matched_keywords += 1
            else:
                # Semantic similarity (partial match)
                best_similarity = 0.0
                for content_keyword in content_keyword_map:
                    # Simple substring matching as proxy for semantic similarity
                    if (query_keyword in content_keyword or 
                        content_keyword in query_keyword or
                        self._calculate_string_similarity(query_keyword, content_keyword) > 0.7):
                        
                        keyword_obj = content_keyword_map[content_keyword]
                        similarity_score = (
                            keyword_obj.score * self.config.semantic_match_bonus
                        )
                        best_similarity = max(best_similarity, similarity_score)
                
                total_score += best_similarity
        
        # Normalize by query keywords and add match ratio bonus
        if query_keywords:
            match_ratio = matched_keywords / len(query_keywords)
            normalized_score = total_score / len(query_keywords)
            return min(normalized_score * (1 + match_ratio), 1.0)
        
        return 0.0
    
    def _calculate_enhanced_entity_score(
        self, 
        query_metadata: Optional[ChunkMetadata], 
        content_metadata: Optional[ChunkMetadata]
    ) -> float:
        """Calculate enhanced entity matching score."""
        if (not query_metadata or not query_metadata.entities or
            not content_metadata or not content_metadata.entities):
            return 0.0
        
        query_entities = {ent.text.lower(): ent for ent in query_metadata.entities}
        content_entities = {ent.text.lower(): ent for ent in content_metadata.entities}
        
        total_score = 0.0
        matched_entities = 0
        
        for query_entity_text, query_entity in query_entities.items():
            if query_entity_text in content_entities:
                content_entity = content_entities[query_entity_text]
                
                # Entity type weight
                entity_type_weight = self.config.entity_type_weights.get(
                    content_entity.label.value, 0.5
                )
                
                # Confidence-weighted score
                entity_score = (
                    content_entity.confidence * 
                    entity_type_weight * 
                    self.config.entity_exact_match_bonus
                )
                
                total_score += entity_score
                matched_entities += 1
        
        # Normalize by query entities
        if query_entities:
            return min(total_score / len(query_entities), 1.0)
        
        return 0.0
    
    def _calculate_topic_similarity_score(
        self, 
        query_metadata: Optional[ChunkMetadata], 
        content_metadata: Optional[ChunkMetadata]
    ) -> float:
        """Calculate topic similarity score."""
        if (not query_metadata or not query_metadata.topics or
            not content_metadata or not content_metadata.topics):
            return 0.0
        
        query_topics = {topic.topic_id: topic for topic in query_metadata.topics}
        content_topics = {topic.topic_id: topic for topic in content_metadata.topics}
        
        # Direct topic overlap
        common_topics = set(query_topics.keys()) & set(content_topics.keys())
        if common_topics:
            overlap_score = len(common_topics) / len(query_topics)
            return min(overlap_score * self.config.topic_overlap_bonus, 1.0)
        
        # Semantic topic similarity using topic words
        max_similarity = 0.0
        for query_topic in query_metadata.topics:
            for content_topic in content_metadata.topics:
                word_overlap = set(query_topic.topic_words) & set(content_topic.topic_words)
                if word_overlap:
                    similarity = len(word_overlap) / max(len(query_topic.topic_words), 1)
                    if similarity > self.config.topic_similarity_threshold:
                        weighted_similarity = (
                            similarity * 
                            query_topic.probability * 
                            content_topic.probability
                        )
                        max_similarity = max(max_similarity, weighted_similarity)
        
        return min(max_similarity, 1.0)
    
    def _calculate_enhanced_temporal_score(self, metadata: Optional[ChunkMetadata]) -> float:
        """Calculate enhanced temporal relevance score."""
        if not metadata or not metadata.dates:
            return 0.5  # Neutral score for undated content
        
        current_time = datetime.utcnow()
        
        # Find the most relevant date (most recent)
        most_recent_date = max(date.date for date in metadata.dates)
        days_diff = (current_time - most_recent_date).days
        
        # Enhanced temporal scoring
        if days_diff < 30:  # Very recent
            return min(0.5 + self.config.temporal_boost_recent, 1.0)
        elif days_diff < 365:  # Recent
            decay_factor = math.exp(-days_diff / self.config.recency_decay_days)
            return 0.5 + (decay_factor * self.config.temporal_boost_recent * 0.5)
        else:  # Old content
            penalty = min(self.config.temporal_penalty_old, 0.4)
            return max(0.5 - penalty, 0.1)
    
    def _calculate_enhanced_quality_score(self, metadata: Optional[ChunkMetadata]) -> float:
        """Calculate enhanced content quality score."""
        if not metadata:
            return 0.5
        
        quality_components = []
        
        # Readability score
        if metadata.readability_score is not None:
            quality_components.append(
                metadata.readability_score * self.config.readability_weight
            )
        
        # Information density
        if metadata.information_density is not None:
            quality_components.append(
                metadata.information_density * self.config.information_density_weight
            )
        
        # Summary quality (based on length and coherence)
        if metadata.summary:
            summary_quality = min(len(metadata.summary) / 200, 1.0)  # Optimal ~200 chars
            quality_components.append(
                summary_quality * self.config.summary_quality_weight
            )
        
        # Metadata confidence (average of keyword and entity confidences)
        confidence_scores = []
        if metadata.keywords:
            avg_keyword_confidence = sum(kw.score for kw in metadata.keywords) / len(metadata.keywords)
            confidence_scores.append(avg_keyword_confidence)
        
        if metadata.entities:
            avg_entity_confidence = sum(ent.confidence for ent in metadata.entities) / len(metadata.entities)
            confidence_scores.append(avg_entity_confidence)
        
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            if avg_confidence >= self.config.min_confidence_threshold:
                quality_components.append(avg_confidence * 0.3)
        
        # Calculate final quality score
        if quality_components:
            return min(sum(quality_components), 1.0)
        else:
            return 0.5
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple string similarity."""
        if str1 == str2:
            return 1.0
        
        # Jaccard similarity on character level
        set1 = set(str1)
        set2 = set(str2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_detailed_explanation(self, score_breakdown: Dict[str, float]) -> str:
        """Generate detailed explanation for the reranking decision."""
        explanations = []
        
        # Sort components by contribution
        sorted_components = sorted(
            score_breakdown.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for component, score in sorted_components:
            if score > 0.1:  # Only include significant contributors
                if component == 'semantic':
                    explanations.append(f"Strong semantic match (score: {score:.2f})")
                elif component == 'keyword':
                    explanations.append(f"Keyword relevance (score: {score:.2f})")
                elif component == 'entity':
                    explanations.append(f"Entity match found (score: {score:.2f})")
                elif component == 'topic':
                    explanations.append(f"Topic alignment (score: {score:.2f})")
                elif component == 'temporal':
                    if score > 0.6:
                        explanations.append("Recent content")
                    elif score < 0.3:
                        explanations.append("Older content")
                elif component == 'quality':
                    if score > 0.7:
                        explanations.append("High-quality content")
        
        return "; ".join(explanations) if explanations else "Standard relevance scoring"
    
    def _apply_enhanced_diversity_filtering(
        self, 
        results: List[EnhancedRetrievalResult]
    ) -> List[EnhancedRetrievalResult]:
        """Apply enhanced diversity filtering to results."""
        if len(results) <= 5:
            return results
        
        filtered_results = []
        used_topics = set()
        used_entities = set()
        
        for result in results:
            # Check topic diversity
            result_topics = set()
            if result.metadata and result.metadata.topics:
                result_topics = {topic.topic_id for topic in result.metadata.topics}
            
            # Check entity diversity
            result_entities = set()
            if result.metadata and result.metadata.entities:
                result_entities = {ent.text.lower() for ent in result.metadata.entities[:3]}
            
            # Calculate similarity to already selected results
            topic_overlap = len(result_topics & used_topics) / max(len(result_topics), 1)
            entity_overlap = len(result_entities & used_entities) / max(len(result_entities), 1)
            
            # Allow if not too similar or if we need more results
            if (topic_overlap < 0.7 and entity_overlap < 0.5) or len(filtered_results) < 3:
                filtered_results.append(result)
                used_topics.update(result_topics)
                used_entities.update(result_entities)
                
                # Limit total results
                if len(filtered_results) >= 10:
                    break
        
        return filtered_results


def create_enhanced_reranker(
    llm_provider: str = "openai",
    llm_model: str = "gpt-4o-mini",
    llm_api_key: Optional[str] = None,
    **config_kwargs
) -> EnhancedMetadataReranker:
    """
    Create an enhanced metadata reranker with LLM integration.
    
    Args:
        llm_provider: LLM provider
        llm_model: LLM model name
        llm_api_key: LLM API key
        **config_kwargs: Additional configuration parameters
        
    Returns:
        Configured enhanced reranker
    """
    config = EnhancedRerankerConfig(
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
        **config_kwargs
    )
    
    return EnhancedMetadataReranker(config) 