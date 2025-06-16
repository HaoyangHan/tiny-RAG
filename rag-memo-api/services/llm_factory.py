import os
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from abc import ABC, abstractmethod

import google.generativeai as genai
from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"

class LLMModel(str, Enum):
    """Supported LLM models."""
    # OpenAI Models
    GPT_4_MINI = "gpt-4-mini-2025-04-16"
    GPT_4_NANO = "gpt-4.1-nano-2025-04-14"
    
    # Gemini Models
    GEMINI_2_0_FLASH_LITE = "gemini-2.0-flash-lite"
    GEMINI_2_5_PRO_PREVIEW = "gemini-2.5-pro-preview-06-05"
    GEMINI_2_5_FLASH_PREVIEW = "gemini-2.5-flash-preview-05-20"

class LLMMessage(BaseModel):
    """Standard message format for LLM interactions."""
    role: str  # "system", "user", "assistant"
    content: str

class LLMResponse(BaseModel):
    """Standard response format from LLM."""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, Any]] = None

class BaseLLM(ABC):
    """Abstract base class for LLM implementations."""
    
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
    
    @abstractmethod
    async def generate(
        self, 
        messages: List[LLMMessage], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass

class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation."""
    
    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)
        self.client = OpenAI(
            base_url='https://api.openai-proxy.org/v1',
            api_key=api_key,
        )
    
    async def generate(
        self, 
        messages: List[LLMMessage], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate a response using OpenAI API."""
        try:
            # Convert messages to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            # Prepare request parameters
            request_params = {
                "messages": openai_messages,
                "model": self.model,
                "temperature": temperature,
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            # Make API call
            response = self.client.chat.completions.create(**request_params)
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                provider=LLMProvider.OPENAI,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {str(e)}")
            raise

class GeminiLLM(BaseLLM):
    """Google Gemini LLM implementation."""
    
    def __init__(self, model: str, api_key: str):
        super().__init__(model, api_key)
        
        # Configure Gemini client
        genai.configure(
            api_key=api_key,
            transport="rest",
            client_options={"api_endpoint": "https://api.openai-proxy.org/google"},
        )
        
        self.client = genai.GenerativeModel(model)
    
    async def generate(
        self, 
        messages: List[LLMMessage], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate a response using Gemini API."""
        try:
            # Convert messages to Gemini format
            # For simplicity, we'll combine all messages into a single prompt
            # In production, you might want to handle conversation history differently
            prompt_parts = []
            for msg in messages:
                if msg.role == "system":
                    prompt_parts.append(f"System: {msg.content}")
                elif msg.role == "user":
                    prompt_parts.append(f"User: {msg.content}")
                elif msg.role == "assistant":
                    prompt_parts.append(f"Assistant: {msg.content}")
            
            prompt = "\n".join(prompt_parts)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
            )
            
            if max_tokens:
                generation_config.max_output_tokens = max_tokens
            
            # Make API call
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return LLMResponse(
                content=response.text,
                model=self.model,
                provider=LLMProvider.GEMINI,
                usage={
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0),
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {str(e)}")
            raise

class LLMFactory:
    """Factory class for creating and managing LLM instances."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Default models
        self.default_openai_model = LLMModel.GPT_4_MINI
        self.default_gemini_model = LLMModel.GEMINI_2_0_FLASH_LITE
        
        # Model to provider mapping
        self.model_providers = {
            LLMModel.GPT_4_MINI: LLMProvider.OPENAI,
            LLMModel.GPT_4_NANO: LLMProvider.OPENAI,
            LLMModel.GEMINI_2_0_FLASH_LITE: LLMProvider.GEMINI,
            LLMModel.GEMINI_2_5_PRO_PREVIEW: LLMProvider.GEMINI,
            LLMModel.GEMINI_2_5_FLASH_PREVIEW: LLMProvider.GEMINI,
        }
    
    def create_llm(self, model: Optional[str] = None) -> BaseLLM:
        """Create an LLM instance for the specified model."""
        if not model:
            model = self.default_gemini_model
        
        # Validate model
        if model not in self.model_providers:
            raise ValueError(f"Unsupported model: {model}")
        
        provider = self.model_providers[model]
        
        if provider == LLMProvider.OPENAI:
            if not self.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return OpenAILLM(model, self.openai_api_key)
        
        elif provider == LLMProvider.GEMINI:
            if not self.gemini_api_key:
                raise ValueError("Gemini API key not configured")
            return GeminiLLM(model, self.gemini_api_key)
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models by provider."""
        models_by_provider = {}
        
        for model, provider in self.model_providers.items():
            if provider not in models_by_provider:
                models_by_provider[provider] = []
            models_by_provider[provider].append(model)
        
        return models_by_provider
    
    def get_default_model(self, provider: Optional[str] = None) -> str:
        """Get the default model for a provider."""
        if provider == LLMProvider.OPENAI:
            return self.default_openai_model
        elif provider == LLMProvider.GEMINI:
            return self.default_gemini_model
        else:
            return self.default_gemini_model  # Default to Gemini
    
    async def generate_response(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate a response using the specified model."""
        llm = self.create_llm(model)
        return await llm.generate(messages, temperature, max_tokens)

# Global factory instance
llm_factory = LLMFactory() 