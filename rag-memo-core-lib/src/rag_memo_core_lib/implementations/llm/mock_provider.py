"""
Mock LLM Provider Implementation

A mock implementation of LLMProvider for testing and development.
Provides predictable responses without external API dependencies.
"""

import asyncio
import random
import time
from typing import List, Dict, Any, Optional, AsyncGenerator

from ...abstractions.llm import LLMProvider, LLMRequest, LLMResponse, LLMConfig
from ...exceptions import LLMError


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider for testing and development.
    
    Simulates LLM behavior with configurable responses and delays.
    Useful for testing, development, and demonstrations.
    """
    
    SUPPORTED_MODELS = [
        "mock-gpt-4",
        "mock-gpt-3.5-turbo", 
        "mock-claude-3",
        "mock-llama-2"
    ]
    
    def __init__(self, config: LLMConfig) -> None:
        """Initialize mock LLM provider."""
        super().__init__(config)
        self._response_delay = 0.1  # Simulate processing time
        self._fail_rate = 0.0  # Failure simulation rate (0.0 = never fail)
        
        # Configurable responses
        self._default_responses = [
            "This is a mock response from the LLM provider.",
            "Mock LLM is working correctly and processing your request.",
            "I'm a simulated language model response for testing purposes.",
            "Mock response: Your query has been processed successfully.",
            "This is another example of a mock LLM response."
        ]
    
    async def initialize(self) -> None:
        """Initialize the mock provider."""
        await asyncio.sleep(0.01)  # Simulate initialization time
        self._initialized = True
        self._logger.info("Mock LLM provider initialized")
    
    async def health_check(self) -> bool:
        """Mock health check - always returns True."""
        return True
    
    async def cleanup(self) -> None:
        """Cleanup mock provider."""
        self._initialized = False
        self._logger.info("Mock LLM provider cleaned up")
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate mock response.
        
        Args:
            request: LLM request
            
        Returns:
            LLMResponse: Mock response
            
        Raises:
            LLMError: If configured to fail
        """
        if not self._initialized:
            raise LLMError("Mock provider not initialized")
        
        # Simulate failure if configured
        if random.random() < self._fail_rate:
            raise LLMError("Mock provider simulated failure")
        
        # Simulate processing delay
        await asyncio.sleep(self._response_delay)
        
        # Generate mock response based on request
        if request.messages:
            last_message = request.messages[-1].content
            response_content = self._generate_mock_content(last_message, request)
        else:
            response_content = random.choice(self._default_responses)
        
        # Calculate mock token usage
        input_tokens = sum(len(msg.content.split()) for msg in request.messages)
        output_tokens = len(response_content.split())
        
        return LLMResponse(
            content=response_content,
            model=request.model,
            usage={
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            },
            finish_reason="stop",
            response_id=f"mock_{int(time.time())}",
            created_at=time.time(),
            metadata={
                "mock_provider": True,
                "processing_time": self._response_delay
            }
        )
    
    async def stream_generate(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Generate streaming mock response.
        
        Args:
            request: LLM request
            
        Yields:
            str: Response chunks
        """
        if not self._initialized:
            raise LLMError("Mock provider not initialized")
        
        # Generate full response first
        response = await self.generate(request)
        words = response.content.split()
        
        # Stream words with delay
        for word in words:
            await asyncio.sleep(0.05)  # Simulate streaming delay
            yield word + " "
    
    async def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Generate mock embedding vector.
        
        Args:
            text: Text to embed
            model: Model name (ignored)
            
        Returns:
            List[float]: Mock embedding vector
        """
        if not self._initialized:
            raise LLMError("Mock provider not initialized")
        
        await asyncio.sleep(0.01)  # Simulate processing
        
        # Generate deterministic mock embedding based on text hash
        text_hash = hash(text)
        random.seed(text_hash)
        
        # Generate 384-dimensional vector (common embedding size)
        embedding = [random.gauss(0, 1) for _ in range(384)]
        
        # Normalize vector
        magnitude = sum(x**2 for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    async def get_embeddings_batch(
        self, 
        texts: List[str], 
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate batch embeddings.
        
        Args:
            texts: Texts to embed
            model: Model name (ignored)
            
        Returns:
            List[List[float]]: Mock embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text, model)
            embeddings.append(embedding)
        return embeddings
    
    def get_supported_models(self) -> List[str]:
        """Get supported model list."""
        return self.SUPPORTED_MODELS.copy()
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get mock model information.
        
        Args:
            model: Model identifier
            
        Returns:
            Dict[str, Any]: Model information
        """
        if model not in self.SUPPORTED_MODELS:
            raise LLMError(f"Unknown model: {model}")
        
        return {
            "name": model,
            "context_length": 4096,
            "max_tokens": 4096,
            "capabilities": ["text_generation", "embeddings"],
            "provider": "mock",
            "cost_per_token": 0.0  # Mock provider is free
        }
    
    def _generate_mock_content(self, user_message: str, request: LLMRequest) -> str:
        """Generate mock content based on user message."""
        message_lower = user_message.lower()
        
        # Simple pattern matching for more realistic responses
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! I'm a mock LLM provider. How can I help you today?"
        elif "weather" in message_lower:
            return "I'm a mock provider, so I can't check real weather, but it's always sunny in mock land!"
        elif "question" in message_lower or "?" in user_message:
            return f"That's an interesting question! As a mock LLM, I'll provide a simulated answer based on your query: '{user_message[:50]}...'"
        elif "test" in message_lower:
            return "Test successful! Mock LLM provider is responding correctly."
        else:
            # Default response with reference to user message
            return f"I received your message: '{user_message[:100]}{'...' if len(user_message) > 100 else ''}'. This is a mock response for development and testing purposes."
    
    def configure_mock_behavior(
        self, 
        response_delay: float = None,
        fail_rate: float = None,
        custom_responses: List[str] = None
    ) -> None:
        """
        Configure mock behavior for testing.
        
        Args:
            response_delay: Delay in seconds for responses
            fail_rate: Rate of simulated failures (0.0 to 1.0)
            custom_responses: Custom response templates
        """
        if response_delay is not None:
            self._response_delay = max(0, response_delay)
        
        if fail_rate is not None:
            self._fail_rate = max(0.0, min(1.0, fail_rate))
        
        if custom_responses:
            self._default_responses = custom_responses.copy()
        
        self._logger.info(
            f"Mock behavior configured: delay={self._response_delay}s, "
            f"fail_rate={self._fail_rate}, responses={len(self._default_responses)}"
        ) 