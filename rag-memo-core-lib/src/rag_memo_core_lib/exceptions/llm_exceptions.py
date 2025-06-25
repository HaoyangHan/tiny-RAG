"""
LLM Exception Classes for TinyRAG Core Library

Specific exceptions for LLM provider operations.
"""

from typing import Optional, Dict, Any
from .base import ProviderError


class LLMError(ProviderError):
    """Base exception for LLM provider errors."""
    
    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if model:
            context['model'] = model
        if provider:
            context['provider'] = provider
        
        super().__init__(message, provider_type="llm", context=context, **kwargs)


class LLMTimeoutError(LLMError):
    """Exception raised when LLM request times out."""
    
    def __init__(
        self,
        message: str,
        timeout_seconds: Optional[float] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if timeout_seconds:
            context['timeout_seconds'] = timeout_seconds
        
        super().__init__(message, error_code="LLM_TIMEOUT", context=context, **kwargs)


class LLMQuotaError(LLMError):
    """Exception raised when LLM quota/rate limit is exceeded."""
    
    def __init__(
        self,
        message: str,
        quota_type: Optional[str] = None,
        reset_time: Optional[float] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if quota_type:
            context['quota_type'] = quota_type
        if reset_time:
            context['reset_time'] = reset_time
        
        super().__init__(message, error_code="LLM_QUOTA_EXCEEDED", context=context, **kwargs)


class LLMAuthenticationError(LLMError):
    """Exception raised for LLM authentication failures."""
    
    def __init__(
        self,
        message: str,
        auth_type: Optional[str] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if auth_type:
            context['auth_type'] = auth_type
        
        super().__init__(message, error_code="LLM_AUTH_FAILED", context=context, **kwargs)


class LLMModelError(LLMError):
    """Exception raised for model-specific errors."""
    
    def __init__(
        self,
        message: str,
        requested_model: Optional[str] = None,
        available_models: Optional[list] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if requested_model:
            context['requested_model'] = requested_model
        if available_models:
            context['available_models'] = available_models
        
        super().__init__(message, error_code="LLM_MODEL_ERROR", context=context, **kwargs) 