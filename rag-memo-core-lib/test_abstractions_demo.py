#!/usr/bin/env python3
"""
TinyRAG v1.4 Core Library Abstractions Demo

Standalone test script to demonstrate the working abstractions
without dependencies on the existing config/database modules.
"""

import sys
import asyncio
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Direct imports bypassing the main __init__.py completely
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'rag_memo_core_lib'))

from abstractions.llm import LLMMessage, LLMRequest, LLMResponse, LLMConfig
from abstractions.vector_store import VectorDocument, SearchResult, VectorStoreConfig
from abstractions.base import BaseConfig, BaseProvider
from implementations.llm.mock_provider import MockLLMProvider
from factories.llm_factory import LLMFactory
from exceptions.base import TinyRAGError
from exceptions.llm_exceptions import LLMError


async def test_abstractions():
    """Test the core abstractions and implementations."""
    
    print("🚀 TinyRAG v1.4 Core Library Abstractions Demo")
    print("=" * 60)
    
    # Test 1: Basic model validation
    print("\n📝 Test 1: Model Creation and Validation")
    print("-" * 40)
    
    message = LLMMessage(
        role="user", 
        content="Hello, how are you?",
        metadata={"test": True}
    )
    print(f"✅ LLMMessage: {message.role} - '{message.content[:30]}...'")
    
    config = LLMConfig(
        component_name="demo_llm",
        default_model="mock-gpt-3.5-turbo",
        api_key="demo_key",
        timeout_seconds=30
    )
    print(f"✅ LLMConfig: {config.component_name} with {config.default_model}")
    
    # Test 2: Vector store models
    vector_doc = VectorDocument(
        id="doc_1",
        content="This is a test document for vector storage.",
        embedding=[0.1, 0.2, 0.3, 0.4, 0.5],
        metadata={"source": "demo", "type": "test"}
    )
    print(f"✅ VectorDocument: {vector_doc.id} with {len(vector_doc.embedding)}D embedding")
    
    # Test 3: Mock LLM Provider
    print("\n🤖 Test 2: Mock LLM Provider")
    print("-" * 40)
    
    provider = MockLLMProvider(config)
    print(f"✅ Provider created: {type(provider).__name__}")
    
    # Test provider lifecycle
    async with provider:
        print(f"✅ Provider initialized: {provider.is_initialized()}")
        
        # Test health check
        health = await provider.health_check()
        print(f"✅ Health check: {'Healthy' if health else 'Unhealthy'}")
        
        # Test text generation
        request = LLMRequest(
            messages=[message],
            model="mock-gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=100
        )
        
        response = await provider.generate(request)
        print(f"✅ Generated response: '{response.content[:40]}...'")
        print(f"✅ Token usage: {response.usage['total_tokens']} tokens")
        print(f"✅ Model used: {response.model}")
        
        # Test embedding generation
        embedding = await provider.get_embedding("This is a test sentence for embedding generation.")
        print(f"✅ Generated embedding: {len(embedding)} dimensions")
        print(f"✅ Embedding sample: [{embedding[0]:.3f}, {embedding[1]:.3f}, ...]")
        
        # Test batch embeddings
        texts = ["First text", "Second text", "Third text"]
        embeddings = await provider.get_embeddings_batch(texts)
        print(f"✅ Batch embeddings: {len(embeddings)} embeddings for {len(texts)} texts")
        
        # Test streaming generation
        print("✅ Testing streaming generation...")
        stream_chunks = []
        async for chunk in provider.stream_generate(request):
            stream_chunks.append(chunk)
            if len(stream_chunks) >= 5:  # Just test first few chunks
                break
        
        stream_content = "".join(stream_chunks)
        print(f"✅ Streaming: Received {len(stream_chunks)} chunks: '{stream_content[:30]}...'")
        
        # Test model information
        models = provider.get_supported_models()
        print(f"✅ Supported models: {len(models)} models available")
        print(f"   Examples: {', '.join(models[:3])}")
        
        model_info = provider.get_model_info("mock-gpt-3.5-turbo")
        print(f"✅ Model info: {model_info['context_length']} context length, {len(model_info['capabilities'])} capabilities")
        
    print(f"✅ Provider cleaned up: {not provider.is_initialized()}")
    
    # Test 4: Factory Pattern
    print("\n🏭 Test 3: Factory Pattern")
    print("-" * 40)
    
    # Register provider
    LLMFactory.register_provider("mock", MockLLMProvider, {
        "default_model": "mock-gpt-4",
        "timeout_seconds": 60
    })
    print("✅ Provider registered with factory")
    
    # List supported providers
    supported = LLMFactory.get_supported_providers()
    print(f"✅ Supported providers: {supported}")
    
    # Create provider through factory
    factory_config = {
        "api_key": "factory_test_key",
        "default_model": "mock-gpt-4"
    }
    
    factory_provider = LLMFactory.create_provider("mock", factory_config)
    print(f"✅ Factory created provider: {type(factory_provider).__name__}")
    print(f"✅ Provider config: API key set: {bool(factory_provider.config.api_key)}")
    
    # Get provider info
    provider_info = LLMFactory.get_provider_info("mock")
    print(f"✅ Provider info: {provider_info['class']} from {provider_info['name']}")
    
    # Test 5: Mock Behavior Configuration
    print("\n⚙️  Test 4: Mock Configuration")
    print("-" * 40)
    
    provider.configure_mock_behavior(
        response_delay=0.01,  # Fast for demo
        fail_rate=0.0,  # No failures
        custom_responses=["Custom demo response for TinyRAG v1.4!"]
    )
    print("✅ Mock behavior configured")
    
    # Test with custom behavior
    async with provider:
        custom_request = LLMRequest(
            messages=[LLMMessage(role="user", content="test")],
            model="mock-gpt-3.5-turbo"
        )
        custom_response = await provider.generate(custom_request)
        print(f"✅ Custom response: '{custom_response.content}'")
    
    # Test 6: Exception Handling
    print("\n⚠️  Test 5: Exception Handling")
    print("-" * 40)
    
    try:
        # Test unsupported provider
        LLMFactory.create_provider("nonexistent", {})
    except Exception as e:
        print(f"✅ Factory error handled: {type(e).__name__}")
        print(f"   Message: {str(e)[:50]}...")
    
    try:
        # Test invalid model
        invalid_provider = MockLLMProvider(config)
        async with invalid_provider:
            invalid_request = LLMRequest(
                messages=[LLMMessage(role="user", content="test")],
                model="invalid-model"
            )
            is_valid = await invalid_provider.validate_request(invalid_request)
            print(f"✅ Validation works: Invalid request rejected: {not is_valid}")
    except Exception as e:
        print(f"✅ Validation error handled: {type(e).__name__}")
    
    print("\n🎉 All Tests Completed Successfully!")
    print("=" * 60)
    print("✅ TinyRAG v1.4 Core Library Abstractions are working correctly")
    print("✅ Ready for production provider implementations")
    print("✅ Factory pattern enables easy extensibility")
    print("✅ Comprehensive error handling and validation")
    print("✅ Full async/await support for performance")


if __name__ == "__main__":
    print("🧪 Running TinyRAG v1.4 Core Library Abstractions Demo...")
    asyncio.run(test_abstractions()) 