"""
LLM Provider Abstractions for TinyRAG Core Library

Provides abstract interfaces for LLM providers with standardized
request/response formats and streaming support.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, AsyncGenerator
from pydantic import BaseModel, Field
from ..abstractions.base import BaseProvider, BaseConfig


class LLMMessage(BaseModel):
    """
    Standard message format for LLM interactions.
    
    Provides unified interface across different LLM providers
    with support for various message types and metadata.
    """
    
    role: str = Field(description="Message role (system, user, assistant, tool)")
    content: str = Field(description="Message content")
    name: Optional[str] = Field(None, description="Name of the message sender")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls in message")
    tool_call_id: Optional[str] = Field(None, description="Tool call ID for tool responses")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LLMRequest(BaseModel):
    """
    Standard request format for LLM providers.
    
    Unified request structure supporting various LLM capabilities
    including function calling, streaming, and custom parameters.
    """
    
    messages: List[LLMMessage] = Field(description="Conversation messages")
    model: str = Field(description="Model identifier")
    
    # Generation parameters
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: int = Field(default=1000, ge=1, description="Maximum tokens to generate")
    top_p: float = Field(default=1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0, description="Presence penalty")
    
    # Advanced features
    stream: bool = Field(default=False, description="Enable streaming response")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Available tools/functions")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Tool choice strategy")
    
    # Response format
    response_format: Optional[Dict[str, Any]] = Field(None, description="Response format specification")
    
    # Request metadata
    user_id: Optional[str] = Field(None, description="User identifier for tracking")
    session_id: Optional[str] = Field(None, description="Session identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Request metadata")


class LLMResponse(BaseModel):
    """
    Standard response format from LLM providers.
    
    Unified response structure with comprehensive usage statistics
    and support for various completion reasons.
    """
    
    content: str = Field(description="Generated content")
    model: str = Field(description="Model used for generation")
    
    # Usage statistics
    usage: Dict[str, int] = Field(description="Token usage statistics")
    
    # Completion information
    finish_reason: str = Field(description="Reason for completion (stop, length, tool_calls, etc.)")
    
    # Tool calling
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls made")
    
    # Response metadata
    response_id: Optional[str] = Field(None, description="Response identifier")
    created_at: Optional[float] = Field(None, description="Response creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")


class LLMConfig(BaseConfig):
    """
    Configuration for LLM providers.
    
    Extends base configuration with LLM-specific settings
    including authentication, endpoints, and provider options.
    """
    
    # Authentication
    api_key: Optional[str] = Field(None, description="API key for authentication")
    organization: Optional[str] = Field(None, description="Organization identifier")
    project: Optional[str] = Field(None, description="Project identifier")
    
    # Endpoints
    base_url: Optional[str] = Field(None, description="Base URL for API")
    api_version: Optional[str] = Field(None, description="API version")
    
    # Connection settings
    timeout_seconds: int = Field(default=60, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay_seconds: float = Field(default=1.0, description="Delay between retries")
    
    # Rate limiting
    requests_per_minute: Optional[int] = Field(None, description="Rate limit for requests")
    tokens_per_minute: Optional[int] = Field(None, description="Rate limit for tokens")
    
    # Default model settings
    default_model: str = Field(default="gpt-3.5-turbo", description="Default model to use")
    embedding_model: str = Field(default="text-embedding-ada-002", description="Default embedding model")
    
    # Provider-specific settings
    provider_settings: Optional[Dict[str, Any]] = Field(None, description="Provider-specific configuration")


class LLMProvider(BaseProvider[LLMResponse], ABC):
    """
    Abstract base class for LLM providers.
    
    Defines the interface for language model providers with support for
    text generation, streaming, embeddings, and function calling.
    """
    
    def __init__(self, config: LLMConfig) -> None:
        """
        Initialize LLM provider.
        
        Args:
            config: LLM provider configuration
        """
        super().__init__(config)
        self.config: LLMConfig = config
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate response from LLM.
        
        Args:
            request: LLM request with messages and parameters
            
        Returns:
            LLMResponse: Generated response
            
        Raises:
            LLMError: If generation fails
            LLMTimeoutError: If request times out
            LLMQuotaError: If quota is exceeded
        """
        pass
    
    @abstractmethod
    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Generate streaming response from LLM.
        
        Args:
            request: LLM request with streaming enabled
            
        Yields:
            str: Chunks of generated content
            
        Raises:
            LLMError: If streaming generation fails
        """
        pass
    
    @abstractmethod
    async def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Get text embedding from LLM provider.
        
        Args:
            text: Text to embed
            model: Optional embedding model override
            
        Returns:
            List[float]: Text embedding vector
            
        Raises:
            LLMError: If embedding generation fails
        """
        pass
    
    @abstractmethod
    async def get_embeddings_batch(
        self, 
        texts: List[str], 
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Get embeddings for multiple texts in batch.
        
        Args:
            texts: List of texts to embed
            model: Optional embedding model override
            
        Returns:
            List[List[float]]: List of embedding vectors
            
        Raises:
            LLMError: If batch embedding fails
        """
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """
        Get list of supported models.
        
        Returns:
            List[str]: List of supported model identifiers
        """
        pass
    
    @abstractmethod
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model: Model identifier
            
        Returns:
            Dict[str, Any]: Model information (context_length, capabilities, etc.)
            
        Raises:
            LLMError: If model not found
        """
        pass
    
    async def validate_request(self, request: LLMRequest) -> bool:
        """
        Validate LLM request before processing.
        
        Args:
            request: Request to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            ValidationError: If request is invalid
        """
        if not request.messages:
            return False
        
        if request.model not in self.get_supported_models():
            return False
        
        return True
    
    async def estimate_tokens(self, text: str, model: Optional[str] = None) -> int:
        """
        Estimate token count for text.
        
        Default implementation provides rough estimate.
        Override for accurate provider-specific counting.
        
        Args:
            text: Text to count tokens for
            model: Model for tokenization (optional)
            
        Returns:
            int: Estimated token count
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    async def count_message_tokens(self, messages: List[LLMMessage], model: Optional[str] = None) -> int:
        """
        Count tokens in a list of messages.
        
        Args:
            messages: Messages to count tokens for
            model: Model for tokenization (optional)
            
        Returns:
            int: Total token count
        """
        total_tokens = 0
        for message in messages:
            total_tokens += await self.estimate_tokens(message.content, model)
            # Add overhead for message formatting
            total_tokens += 10
        
        return total_tokens 