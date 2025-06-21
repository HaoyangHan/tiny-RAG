"""
LLM-based metadata extractors for TinyRAG framework.
"""

import json
import time
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from openai import AsyncOpenAI
import logging

from .schemas import (
    ChunkMetadata, ExtractionResult, ExtractedKeyword, ExtractedEntity, 
    ExtractedDate, TopicInfo, SentimentInfo, EntityType, SentimentType
)

logger = logging.getLogger(__name__)


class LLMConfig:
    """Configuration for LLM-based extractors."""
    
    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens


class BaseLLMExtractor(ABC):
    """Base class for LLM-based metadata extractors."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.name = self.__class__.__name__
        self.client = AsyncOpenAI(api_key=config.api_key)
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for the extractor."""
        pass
    
    @abstractmethod
    def get_user_prompt(self, text: str) -> str:
        """Get the user prompt for the given text."""
        pass
    
    @abstractmethod
    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured data."""
        pass
    
    async def call_llm(self, text: str) -> str:
        """Call the LLM with the given text."""
        system_prompt = self.get_system_prompt()
        user_prompt = self.get_user_prompt(text)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    async def extract(self, text: str, text_id: str) -> ExtractionResult:
        """Extract metadata from text using LLM."""
        start_time = time.time()
        errors = []
        
        try:
            llm_response = await self.call_llm(text)
            parsed_data = self.parse_llm_response(llm_response)
            
            chunk_metadata = ChunkMetadata(
                chunk_id=text_id,
                document_id=text_id.split('_')[0] if '_' in text_id else text_id,
                chunk_index=0,
                text_length=len(text),
                start_pos=0,
                end_pos=len(text),
                extraction_timestamp=datetime.utcnow(),
                processing_time=time.time() - start_time,
                **parsed_data
            )
            
            return ExtractionResult(
                text=text,
                text_id=text_id,
                metadata=chunk_metadata,
                extraction_method=self.name,
                processing_time=time.time() - start_time,
                success=True,
                errors=errors,
                warnings=[],
                extractor_config={"llm_config": self.config.__dict__}
            )
            
        except Exception as e:
            errors.append(f"LLM extraction failed: {str(e)}")
            
            empty_metadata = ChunkMetadata(
                chunk_id=text_id,
                document_id=text_id.split('_')[0] if '_' in text_id else text_id,
                chunk_index=0,
                text_length=len(text),
                start_pos=0,
                end_pos=len(text)
            )
            
            return ExtractionResult(
                text=text,
                text_id=text_id,
                metadata=empty_metadata,
                extraction_method=self.name,
                processing_time=time.time() - start_time,
                success=False,
                errors=errors,
                warnings=[],
                extractor_config={"llm_config": self.config.__dict__}
            )


class LLMComprehensiveExtractor(BaseLLMExtractor):
    """Comprehensive LLM-based extractor for all metadata types."""
    
    def get_system_prompt(self) -> str:
        return """You are an expert metadata extraction system. Extract comprehensive metadata from text in JSON format.

Return ONLY a valid JSON object with this structure:
{
  "keywords": [
    {"term": "string", "score": 0.8, "frequency": 3, "context": "string"}
  ],
  "entities": [
    {"text": "string", "label": "person", "confidence": 0.9, "start_pos": 10, "end_pos": 20}
  ],
  "dates": [
    {"date": "2024-01-15", "text": "January 15, 2024", "confidence": 0.95, "date_type": "publication", "format": "Long"}
  ],
  "topics": [
    {"topic_id": "tech", "topic_words": ["AI", "machine learning"], "probability": 0.8}
  ],
  "sentiment": {
    "sentiment": "positive",
    "confidence": 0.7,
    "scores": {"positive": 0.7, "negative": 0.1, "neutral": 0.2}
  },
  "summary": "Brief summary of the content",
  "key_phrases": ["important phrase", "key concept"],
  "language": "en",
  "readability_score": 0.6,
  "information_density": 0.8
}

Entity labels: person, organization, location, date, money, percent, product, event, misc
Sentiment types: positive, negative, neutral, mixed
All scores between 0.0-1.0"""

    def get_user_prompt(self, text: str) -> str:
        return f"""Extract metadata from this text:

{text}

JSON:"""

    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        try:
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:-3]
            
            data = json.loads(response)
            parsed_data = {}
            
            # Parse keywords
            if 'keywords' in data:
                parsed_data['keywords'] = [
                    ExtractedKeyword(
                        term=kw.get('term', ''),
                        score=float(kw.get('score', 0.0)),
                        frequency=int(kw.get('frequency', 1)),
                        context=kw.get('context')
                    )
                    for kw in data['keywords']
                ]
            
            # Parse entities
            if 'entities' in data:
                parsed_data['entities'] = [
                    ExtractedEntity(
                        text=ent.get('text', ''),
                        label=EntityType(ent.get('label', 'misc')),
                        confidence=float(ent.get('confidence', 0.0)),
                        start_pos=ent.get('start_pos'),
                        end_pos=ent.get('end_pos')
                    )
                    for ent in data['entities']
                ]
            
            # Parse dates
            if 'dates' in data:
                parsed_data['dates'] = []
                for date_info in data['dates']:
                    if date_info.get('date'):
                        try:
                            parsed_data['dates'].append(ExtractedDate(
                                date=datetime.fromisoformat(date_info['date']),
                                text=date_info.get('text', ''),
                                confidence=float(date_info.get('confidence', 0.0)),
                                date_type=date_info.get('date_type', 'general'),
                                format=date_info.get('format')
                            ))
                        except ValueError:
                            continue
            
            # Parse topics
            if 'topics' in data:
                parsed_data['topics'] = [
                    TopicInfo(
                        topic_id=topic.get('topic_id', ''),
                        topic_words=topic.get('topic_words', []),
                        probability=float(topic.get('probability', 0.0))
                    )
                    for topic in data['topics']
                ]
            
            # Parse sentiment
            if 'sentiment' in data:
                sentiment_data = data['sentiment']
                parsed_data['sentiment'] = SentimentInfo(
                    sentiment=SentimentType(sentiment_data.get('sentiment', 'neutral')),
                    confidence=float(sentiment_data.get('confidence', 0.0)),
                    scores=sentiment_data.get('scores', {})
                )
            
            # Parse simple fields
            for field in ['summary', 'language', 'readability_score', 'information_density']:
                if field in data:
                    parsed_data[field] = data[field]
            
            if 'key_phrases' in data:
                parsed_data['key_phrases'] = data['key_phrases']
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {}


class LLMMetadataExtractionPipeline:
    """Pipeline for LLM-based metadata extraction."""
    
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config
        self.extractor = LLMComprehensiveExtractor(llm_config)
    
    async def extract(self, text: str, text_id: str) -> ExtractionResult:
        """Run LLM-based extraction."""
        return await self.extractor.extract(text, text_id)


def create_llm_extractor(
    provider: str = "openai",
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None
) -> LLMMetadataExtractionPipeline:
    """Create an LLM-based metadata extraction pipeline."""
    config = LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key
    )
    
    return LLMMetadataExtractionPipeline(config)