"""
LLM-based metadata extractors for TinyRAG framework.

This module implements metadata extraction using Large Language Models
with structured prompts to return JSON-formatted metadata.
"""

import json
import time
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from openai import AsyncOpenAI
import google.generativeai as genai
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
        provider: str = "openai",  # "openai" or "gemini"
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ):
        """
        Initialize LLM configuration.
        
        Args:
            provider: LLM provider ("openai" or "gemini")
            model: Model name to use
            api_key: API key for the provider
            base_url: Base URL for API (optional, for proxies)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens


class BaseLLMExtractor(ABC):
    """Base class for LLM-based metadata extractors."""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the LLM extractor.
        
        Args:
            config: LLM configuration
        """
        self.config = config
        self.name = self.__class__.__name__
        
        # Initialize LLM client based on provider
        if config.provider == "openai":
            client_kwargs = {"api_key": config.api_key}
            if config.base_url:
                client_kwargs["base_url"] = config.base_url
            self.client = AsyncOpenAI(**client_kwargs)
        elif config.provider == "gemini":
            if config.api_key:
                genai.configure(api_key=config.api_key)
            self.client = genai.GenerativeModel(config.model)
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")
    
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
        """
        Call the LLM with the given text.
        
        Args:
            text: Input text to process
            
        Returns:
            LLM response string
        """
        system_prompt = self.get_system_prompt()
        user_prompt = self.get_user_prompt(text)
        
        try:
            if self.config.provider == "openai":
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
            
            elif self.config.provider == "gemini":
                # Combine system and user prompts for Gemini
                combined_prompt = f"{system_prompt}\n\n{user_prompt}"
                
                # Configure generation parameters
                generation_config = genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                )
                
                response = await self.client.generate_content_async(
                    combined_prompt,
                    generation_config=generation_config
                )
                return response.text
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    async def extract(self, text: str, text_id: str) -> ExtractionResult:
        """
        Extract metadata from text using LLM.
        
        Args:
            text: Input text to extract metadata from
            text_id: Unique identifier for the text
            
        Returns:
            ExtractionResult containing extracted metadata
        """
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
            logger.error(f"LLM extraction error: {e}")
            
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
        """Get the system prompt for comprehensive metadata extraction."""
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
All scores between 0.0-1.0

Guidelines:
- Extract 5-15 keywords based on text importance
- Identify all named entities with high confidence
- Parse dates in ISO format (YYYY-MM-DD)
- Provide 2-5 main topics
- Summary should be 1-3 sentences
- Be precise and avoid hallucination"""

    def get_user_prompt(self, text: str) -> str:
        """Get the user prompt for the given text."""
        return f"""Extract metadata from this text:

{text}

JSON:"""

    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured metadata."""
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
            logger.error(f"Response was: {response}")
            return {}


class LLMMetadataExtractionPipeline:
    """Pipeline for LLM-based metadata extraction."""
    
    def __init__(self, llm_config: LLMConfig):
        """
        Initialize the LLM extraction pipeline.
        
        Args:
            llm_config: LLM configuration
        """
        self.llm_config = llm_config
        self.extractor = LLMComprehensiveExtractor(llm_config)
    
    async def extract(self, text: str, text_id: str) -> ExtractionResult:
        """
        Run LLM-based extraction pipeline.
        
        Args:
            text: Input text
            text_id: Text identifier
            
        Returns:
            Extraction result
        """
        return await self.extractor.extract(text, text_id)


def create_llm_extractor(
    provider: str = "openai",
    model: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None
) -> LLMMetadataExtractionPipeline:
    """
    Create an LLM-based metadata extraction pipeline.
    
    Args:
        provider: LLM provider ("openai" or "gemini")
        model: Model name
        api_key: API key
        base_url: Base URL for API (optional)
        
    Returns:
        Configured LLM extraction pipeline
    """
    # Set default models based on provider
    if provider == "gemini" and model == "gpt-4o-mini":
        model = "gemini-2.0-flash-lite"
    
    config = LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url
    )
    
    return LLMMetadataExtractionPipeline(config)