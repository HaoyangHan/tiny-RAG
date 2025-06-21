"""
Metadata schemas for TinyRAG extraction framework.

This module defines the data structures for storing and managing metadata
extracted from documents and chunks during the RAG pipeline.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator


class MetadataType(str, Enum):
    """Types of metadata that can be extracted."""
    DATE = "date"
    KEYWORD = "keyword"
    SUMMARY = "summary"
    ENTITY = "entity"
    TOPIC = "topic"
    SENTIMENT = "sentiment"
    LANGUAGE = "language"
    CUSTOM = "custom"


class EntityType(str, Enum):
    """Types of named entities that can be extracted."""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    PERCENT = "percent"
    PRODUCT = "product"
    EVENT = "event"
    MISC = "misc"


class SentimentType(str, Enum):
    """Sentiment classification types."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class ConfidenceLevel(str, Enum):
    """Confidence levels for extracted metadata."""
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"        # < 0.5


class ExtractedEntity(BaseModel):
    """
    Represents a named entity extracted from text.
    
    Attributes:
        text: The entity text
        label: Entity type/category
        confidence: Extraction confidence score
        start_pos: Start position in original text
        end_pos: End position in original text
        metadata: Additional entity-specific metadata
    """
    
    text: str = Field(..., description="Entity text")
    label: EntityType = Field(..., description="Entity type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    start_pos: Optional[int] = Field(None, description="Start position in text")
    end_pos: Optional[int] = Field(None, description="End position in text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ExtractedKeyword(BaseModel):
    """
    Represents a keyword extracted from text.
    
    Attributes:
        term: The keyword term
        score: Relevance/importance score
        frequency: Frequency in the text
        tfidf_score: TF-IDF score if available
        context: Surrounding context
    """
    
    term: str = Field(..., description="Keyword term")
    score: float = Field(..., ge=0.0, description="Relevance score")
    frequency: int = Field(..., ge=1, description="Frequency in text")
    tfidf_score: Optional[float] = Field(None, description="TF-IDF score")
    context: Optional[str] = Field(None, description="Surrounding context")


class ExtractedDate(BaseModel):
    """
    Represents a date extracted from text.
    
    Attributes:
        date: Parsed datetime object
        text: Original date text
        confidence: Extraction confidence
        date_type: Type of date (publication, event, etc.)
        format: Detected date format
    """
    
    date: datetime = Field(..., description="Parsed datetime")
    text: str = Field(..., description="Original date text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    date_type: str = Field(default="general", description="Type of date")
    format: Optional[str] = Field(None, description="Detected format")


class TopicInfo(BaseModel):
    """
    Represents topic information for a text chunk.
    
    Attributes:
        topic_id: Unique topic identifier
        topic_words: Key words representing the topic
        probability: Topic probability score
        coherence: Topic coherence score
    """
    
    topic_id: str = Field(..., description="Topic identifier")
    topic_words: List[str] = Field(..., description="Representative words")
    probability: float = Field(..., ge=0.0, le=1.0, description="Topic probability")
    coherence: Optional[float] = Field(None, description="Coherence score")


class SentimentInfo(BaseModel):
    """
    Represents sentiment analysis results.
    
    Attributes:
        sentiment: Overall sentiment classification
        confidence: Confidence in sentiment classification
        scores: Detailed sentiment scores
        aspects: Aspect-based sentiment if available
    """
    
    sentiment: SentimentType = Field(..., description="Sentiment classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    scores: Dict[str, float] = Field(default_factory=dict, description="Detailed scores")
    aspects: Optional[Dict[str, SentimentType]] = Field(None, description="Aspect sentiment")


class ChunkMetadata(BaseModel):
    """
    Comprehensive metadata for a text chunk.
    
    This class stores all extracted metadata for a single chunk of text,
    enabling advanced retrieval and reranking strategies.
    """
    
    # Basic information
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    chunk_index: int = Field(..., ge=0, description="Index within document")
    text_length: int = Field(..., ge=0, description="Length of chunk text")
    
    # Position information
    start_pos: int = Field(..., ge=0, description="Start position in document")
    end_pos: int = Field(..., ge=0, description="End position in document")
    page_number: Optional[int] = Field(None, description="Page number if applicable")
    section: Optional[str] = Field(None, description="Document section")
    
    # Extracted metadata
    keywords: List[ExtractedKeyword] = Field(default_factory=list, description="Extracted keywords")
    entities: List[ExtractedEntity] = Field(default_factory=list, description="Named entities")
    dates: List[ExtractedDate] = Field(default_factory=list, description="Extracted dates")
    topics: List[TopicInfo] = Field(default_factory=list, description="Topic information")
    sentiment: Optional[SentimentInfo] = Field(None, description="Sentiment analysis")
    
    # Language and structure
    language: Optional[str] = Field(None, description="Detected language")
    text_type: Optional[str] = Field(None, description="Text type (paragraph, list, etc.)")
    
    # Quality metrics
    readability_score: Optional[float] = Field(None, description="Readability score")
    information_density: Optional[float] = Field(None, description="Information density")
    
    # Summary and context
    summary: Optional[str] = Field(None, description="Chunk summary")
    key_phrases: List[str] = Field(default_factory=list, description="Key phrases")
    
    # Processing metadata
    extraction_timestamp: datetime = Field(default_factory=datetime.utcnow)
    extractor_version: str = Field(default="1.0", description="Extractor version")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    
    # Custom metadata
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata")
    
    @validator('end_pos')
    def validate_positions(cls, v: int, values: Dict[str, Any]) -> int:
        """Validate that end_pos is greater than start_pos."""
        start_pos = values.get('start_pos', 0)
        if v <= start_pos:
            raise ValueError('end_pos must be greater than start_pos')
        return v
    
    def get_confidence_level(self, metadata_type: MetadataType) -> ConfidenceLevel:
        """
        Get overall confidence level for a metadata type.
        
        Args:
            metadata_type: Type of metadata to assess
            
        Returns:
            Confidence level for the metadata type
        """
        if metadata_type == MetadataType.KEYWORD:
            if not self.keywords:
                return ConfidenceLevel.LOW
            avg_score = sum(k.score for k in self.keywords) / len(self.keywords)
        elif metadata_type == MetadataType.ENTITY:
            if not self.entities:
                return ConfidenceLevel.LOW
            avg_score = sum(e.confidence for e in self.entities) / len(self.entities)
        elif metadata_type == MetadataType.DATE:
            if not self.dates:
                return ConfidenceLevel.LOW
            avg_score = sum(d.confidence for d in self.dates) / len(self.dates)
        elif metadata_type == MetadataType.SENTIMENT:
            if not self.sentiment:
                return ConfidenceLevel.LOW
            avg_score = self.sentiment.confidence
        else:
            return ConfidenceLevel.MEDIUM
        
        if avg_score > 0.8:
            return ConfidenceLevel.HIGH
        elif avg_score > 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW


class DocumentMetadata(BaseModel):
    """
    Comprehensive metadata for a document.
    
    Aggregates metadata from all chunks and provides document-level insights.
    """
    
    # Basic information
    document_id: str = Field(..., description="Unique document identifier")
    title: Optional[str] = Field(None, description="Document title")
    author: Optional[str] = Field(None, description="Document author")
    source: Optional[str] = Field(None, description="Document source")
    
    # Document structure
    total_chunks: int = Field(..., ge=0, description="Total number of chunks")
    total_length: int = Field(..., ge=0, description="Total text length")
    page_count: Optional[int] = Field(None, description="Number of pages")
    
    # Aggregated metadata
    all_keywords: List[ExtractedKeyword] = Field(default_factory=list)
    all_entities: List[ExtractedEntity] = Field(default_factory=list)
    all_dates: List[ExtractedDate] = Field(default_factory=list)
    main_topics: List[TopicInfo] = Field(default_factory=list)
    overall_sentiment: Optional[SentimentInfo] = Field(None)
    
    # Document-level insights
    key_themes: List[str] = Field(default_factory=list, description="Main themes")
    document_type: Optional[str] = Field(None, description="Document classification")
    complexity_score: Optional[float] = Field(None, description="Document complexity")
    
    # Temporal information
    creation_date: Optional[datetime] = Field(None, description="Document creation date")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    
    # Processing metadata
    processing_timestamp: datetime = Field(default_factory=datetime.utcnow)
    chunk_metadata: List[ChunkMetadata] = Field(default_factory=list)
    
    def get_top_keywords(self, n: int = 10) -> List[ExtractedKeyword]:
        """Get top N keywords by score."""
        return sorted(self.all_keywords, key=lambda k: k.score, reverse=True)[:n]
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[ExtractedEntity]:
        """Get all entities of a specific type."""
        return [e for e in self.all_entities if e.label == entity_type]
    
    def get_date_range(self) -> Optional[tuple[datetime, datetime]]:
        """Get the date range mentioned in the document."""
        if not self.all_dates:
            return None
        
        dates = [d.date for d in self.all_dates]
        return min(dates), max(dates)


class ExtractionResult(BaseModel):
    """
    Result of metadata extraction process.
    
    Contains the extracted metadata along with processing information
    and quality metrics.
    """
    
    # Input information
    text: str = Field(..., description="Original text")
    text_id: str = Field(..., description="Text identifier")
    
    # Extraction results
    metadata: Union[ChunkMetadata, DocumentMetadata] = Field(..., description="Extracted metadata")
    
    # Processing information
    extraction_method: str = Field(..., description="Extraction method used")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")
    success: bool = Field(..., description="Whether extraction was successful")
    
    # Quality metrics
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Quality score")
    completeness_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Completeness")
    
    # Error information
    errors: List[str] = Field(default_factory=list, description="Extraction errors")
    warnings: List[str] = Field(default_factory=list, description="Extraction warnings")
    
    # Additional context
    extractor_config: Dict[str, Any] = Field(default_factory=dict, description="Extractor config")


class MetadataSchema(BaseModel):
    """
    Schema definition for metadata extraction configuration.
    
    Defines which types of metadata to extract and how to configure
    the extraction process.
    """
    
    # Extraction configuration
    extract_keywords: bool = Field(default=True, description="Extract keywords")
    extract_entities: bool = Field(default=True, description="Extract entities")
    extract_dates: bool = Field(default=True, description="Extract dates")
    extract_topics: bool = Field(default=False, description="Extract topics")
    extract_sentiment: bool = Field(default=False, description="Extract sentiment")
    extract_summary: bool = Field(default=False, description="Extract summary")
    
    # Entity extraction configuration
    entity_types: List[EntityType] = Field(
        default_factory=lambda: list(EntityType),
        description="Entity types to extract"
    )
    
    # Keyword extraction configuration
    max_keywords: int = Field(default=20, ge=1, description="Maximum keywords to extract")
    min_keyword_score: float = Field(default=0.1, ge=0.0, le=1.0, description="Minimum keyword score")
    
    # Date extraction configuration
    date_formats: List[str] = Field(
        default_factory=lambda: [
            "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%B %d, %Y", "%d %B %Y"
        ],
        description="Date formats to recognize"
    )
    
    # Processing configuration
    chunk_size: int = Field(default=1000, ge=100, description="Text chunk size")
    overlap_size: int = Field(default=200, ge=0, description="Chunk overlap size")
    
    # Quality thresholds
    min_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence")
    
    # Custom configuration
    custom_config: Dict[str, Any] = Field(default_factory=dict, description="Custom configuration") 