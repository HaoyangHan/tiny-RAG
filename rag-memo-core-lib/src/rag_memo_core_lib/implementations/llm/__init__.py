"""
LLM Provider Implementations

Concrete implementations of LLM providers.
"""

from .mock_provider import MockLLMProvider

# Auto-register providers with factory
from ...factories.llm_factory import LLMFactory

# Register mock provider
LLMFactory.register_provider("mock", MockLLMProvider, {
    "default_model": "mock-gpt-3.5-turbo",
    "embedding_model": "mock-embedding"
})

__all__ = [
    "MockLLMProvider",
] 