"""
Tests for LLM Abstractions and Mock Provider

Comprehensive test suite for the LLM provider abstractions
and mock implementation.
"""

import pytest
import asyncio
from typing import List

# Import the abstractions and implementations
from rag_memo_core_lib.abstractions.llm import LLMProvider, LLMRequest, LLMResponse, LLMMessage, LLMConfig
from rag_memo_core_lib.implementations.llm.mock_provider import MockLLMProvider
from rag_memo_core_lib.factories.llm_factory import LLMFactory
from rag_memo_core_lib.exceptions import LLMError, FactoryError


class TestLLMAbstractions:
    """Test LLM abstractions and base functionality."""
    
    def test_llm_message_creation(self):
        """Test LLM message model creation."""
        message = LLMMessage(
            role="user",
            content="Hello, how are you?",
            metadata={"test": True}
        )
        
        assert message.role == "user"
        assert message.content == "Hello, how are you?"
        assert message.metadata["test"] is True
        assert message.name is None
    
    def test_llm_request_creation(self):
        """Test LLM request model creation."""
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant."),
            LLMMessage(role="user", content="What is 2+2?")
        ]
        
        request = LLMRequest(
            messages=messages,
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=100
        )
        
        assert len(request.messages) == 2
        assert request.model == "gpt-3.5-turbo"
        assert request.temperature == 0.7
        assert request.max_tokens == 100
        assert request.stream is False
    
    def test_llm_config_validation(self):
        """Test LLM configuration validation."""
        config = LLMConfig(
            component_name="test_llm",
            api_key="test_key",
            default_model="gpt-4",
            timeout_seconds=30
        )
        
        assert config.component_name == "test_llm"
        assert config.api_key == "test_key"
        assert config.default_model == "gpt-4"
        assert config.timeout_seconds == 30


class TestMockLLMProvider:
    """Test mock LLM provider implementation."""
    
    @pytest.fixture
    async def mock_provider(self):
        """Create and initialize mock provider."""
        config = LLMConfig(
            component_name="test_mock_llm",
            default_model="mock-gpt-3.5-turbo"
        )
        provider = MockLLMProvider(config)
        await provider.initialize()
        yield provider
        await provider.cleanup()
    
    @pytest.mark.asyncio
    async def test_provider_initialization(self, mock_provider):
        """Test provider initialization and cleanup."""
        assert mock_provider.is_initialized()
        assert await mock_provider.health_check()
    
    @pytest.mark.asyncio
    async def test_text_generation(self, mock_provider):
        """Test basic text generation."""
        messages = [LLMMessage(role="user", content="Hello, how are you?")]
        request = LLMRequest(
            messages=messages,
            model="mock-gpt-3.5-turbo",
            temperature=0.7
        )
        
        response = await mock_provider.generate(request)
        
        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        assert response.model == "mock-gpt-3.5-turbo"
        assert response.finish_reason == "stop"
        assert "prompt_tokens" in response.usage
        assert "completion_tokens" in response.usage
        assert "total_tokens" in response.usage
    
    @pytest.mark.asyncio
    async def test_streaming_generation(self, mock_provider):
        """Test streaming text generation."""
        messages = [LLMMessage(role="user", content="Tell me a story")]
        request = LLMRequest(
            messages=messages,
            model="mock-gpt-3.5-turbo",
            stream=True
        )
        
        chunks = []
        async for chunk in mock_provider.stream_generate(request):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response.strip()) > 0
    
    @pytest.mark.asyncio
    async def test_embedding_generation(self, mock_provider):
        """Test embedding generation."""
        text = "This is a test sentence for embedding."
        embedding = await mock_provider.get_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # Mock provider uses 384-dim embeddings
        assert all(isinstance(x, float) for x in embedding)
        
        # Test that same text produces same embedding
        embedding2 = await mock_provider.get_embedding(text)
        assert embedding == embedding2
    
    @pytest.mark.asyncio
    async def test_batch_embeddings(self, mock_provider):
        """Test batch embedding generation."""
        texts = [
            "First test sentence.",
            "Second test sentence.", 
            "Third test sentence."
        ]
        
        embeddings = await mock_provider.get_embeddings_batch(texts)
        
        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)
        assert all(isinstance(emb, list) for emb in embeddings)
    
    def test_supported_models(self, mock_provider):
        """Test supported models list."""
        models = mock_provider.get_supported_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "mock-gpt-3.5-turbo" in models
        assert "mock-gpt-4" in models
    
    def test_model_info(self, mock_provider):
        """Test model information retrieval."""
        model_info = mock_provider.get_model_info("mock-gpt-3.5-turbo")
        
        assert isinstance(model_info, dict)
        assert "name" in model_info
        assert "context_length" in model_info
        assert "capabilities" in model_info
        assert model_info["provider"] == "mock"
    
    def test_mock_behavior_configuration(self, mock_provider):
        """Test mock behavior configuration."""
        # Test configuring response delay and failure rate
        mock_provider.configure_mock_behavior(
            response_delay=0.05,
            fail_rate=0.1,
            custom_responses=["Custom test response"]
        )
        
        # Verify configuration was applied
        assert mock_provider._response_delay == 0.05
        assert mock_provider._fail_rate == 0.1
        assert "Custom test response" in mock_provider._default_responses
    
    @pytest.mark.asyncio
    async def test_provider_validation(self, mock_provider):
        """Test request validation."""
        valid_request = LLMRequest(
            messages=[LLMMessage(role="user", content="Test")],
            model="mock-gpt-3.5-turbo"
        )
        
        invalid_request = LLMRequest(
            messages=[LLMMessage(role="user", content="Test")],
            model="unsupported-model"
        )
        
        assert await mock_provider.validate_request(valid_request)
        assert not await mock_provider.validate_request(invalid_request)


class TestLLMFactory:
    """Test LLM factory functionality."""
    
    def test_provider_registration(self):
        """Test provider registration."""
        # Clear any existing providers
        LLMFactory.clear_providers()
        
        # Register mock provider
        LLMFactory.register_provider("mock", MockLLMProvider)
        
        assert "mock" in LLMFactory.get_supported_providers()
    
    def test_provider_creation(self):
        """Test provider creation through factory."""
        # Ensure mock provider is registered
        LLMFactory.register_provider("mock", MockLLMProvider)
        
        config = {
            "api_key": "test_key",
            "default_model": "mock-gpt-4"
        }
        
        provider = LLMFactory.create_provider("mock", config)
        
        assert isinstance(provider, MockLLMProvider)
        assert provider.config.api_key == "test_key"
        assert provider.config.default_model == "mock-gpt-4"
    
    def test_unsupported_provider_error(self):
        """Test error handling for unsupported provider."""
        with pytest.raises(FactoryError) as exc_info:
            LLMFactory.create_provider("unsupported", {})
        
        assert "Unsupported LLM provider" in str(exc_info.value)
        assert "unsupported" in str(exc_info.value)
    
    def test_provider_info_retrieval(self):
        """Test provider information retrieval."""
        LLMFactory.register_provider("mock", MockLLMProvider)
        
        info = LLMFactory.get_provider_info("mock")
        
        assert info["name"] == "mock"
        assert info["class"] == "MockLLMProvider"
        assert isinstance(info["default_config"], dict)
    
    def test_provider_unregistration(self):
        """Test provider unregistration."""
        LLMFactory.register_provider("temp_mock", MockLLMProvider)
        assert "temp_mock" in LLMFactory.get_supported_providers()
        
        success = LLMFactory.unregister_provider("temp_mock")
        assert success
        assert "temp_mock" not in LLMFactory.get_supported_providers()


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test complete integration workflow."""
    # Register provider
    LLMFactory.register_provider("mock", MockLLMProvider, {
        "default_model": "mock-gpt-3.5-turbo"
    })
    
    # Create provider through factory
    provider = LLMFactory.create_provider("mock", {
        "api_key": "test_key"
    })
    
    # Initialize provider
    async with provider:
        # Test generation
        request = LLMRequest(
            messages=[LLMMessage(role="user", content="Hello!")],
            model="mock-gpt-3.5-turbo"
        )
        
        response = await provider.generate(request)
        assert "Hello" in response.content
        
        # Test embedding
        embedding = await provider.get_embedding("Test text")
        assert len(embedding) == 384
    
    # Verify cleanup
    assert not provider.is_initialized()


if __name__ == "__main__":
    # Run basic test if executed directly
    async def main():
        print("🧪 Running TinyRAG Core Library Abstractions Tests...")
        
        # Test basic functionality
        config = LLMConfig(component_name="test_llm")
        provider = MockLLMProvider(config)
        
        async with provider:
            # Test generation
            request = LLMRequest(
                messages=[LLMMessage(role="user", content="Hello world!")],
                model="mock-gpt-3.5-turbo"
            )
            
            response = await provider.generate(request)
            print(f"✅ Generated response: {response.content[:100]}...")
            
            # Test embedding
            embedding = await provider.get_embedding("Test embedding")
            print(f"✅ Generated embedding: {len(embedding)} dimensions")
            
            # Test factory
            LLMFactory.register_provider("mock", MockLLMProvider)
            factory_provider = LLMFactory.create_provider("mock", {})
            print(f"✅ Factory created provider: {type(factory_provider).__name__}")
        
        print("🎉 All basic tests passed!")
    
    asyncio.run(main()) 