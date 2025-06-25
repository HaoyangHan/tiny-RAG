"""
Base Exception Classes for TinyRAG Core Library

Provides hierarchical exception structure with context and error codes.
"""

from typing import Optional, Dict, Any
import traceback
import time


class TinyRAGError(Exception):
    """
    Base exception for all TinyRAG core library errors.
    
    Provides structured error information with context,
    error codes, and debugging information.
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        """
        Initialize TinyRAG error.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            context: Additional context information
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self._get_default_error_code()
        self.context = context or {}
        self.cause = cause
        self.timestamp = time.time()
        self.traceback_str = traceback.format_exc() if cause else None
    
    def _get_default_error_code(self) -> str:
        """Get default error code based on exception class."""
        return self.__class__.__name__.upper()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary format.
        
        Returns:
            Dict[str, Any]: Exception as dictionary
        """
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp,
            "cause": str(self.cause) if self.cause else None,
            "traceback": self.traceback_str
        }
    
    def __str__(self) -> str:
        """String representation of the error."""
        parts = [f"{self.error_code}: {self.message}"]
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        
        return " | ".join(parts)


class ConfigurationError(TinyRAGError):
    """Exception raised for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if config_key:
            context['config_key'] = config_key
        if config_value is not None:
            context['config_value'] = config_value
        
        super().__init__(message, context=context, **kwargs)


class ValidationError(TinyRAGError):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if field_name:
            context['field_name'] = field_name
        if field_value is not None:
            context['field_value'] = field_value
        if validation_rule:
            context['validation_rule'] = validation_rule
        
        super().__init__(message, context=context, **kwargs)


class InitializationError(TinyRAGError):
    """Exception raised during component initialization."""
    
    def __init__(
        self,
        message: str,
        component_name: Optional[str] = None,
        initialization_stage: Optional[str] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if component_name:
            context['component_name'] = component_name
        if initialization_stage:
            context['initialization_stage'] = initialization_stage
        
        super().__init__(message, context=context, **kwargs)


class ProviderError(TinyRAGError):
    """Exception raised by service providers."""
    
    def __init__(
        self,
        message: str,
        provider_type: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if provider_type:
            context['provider_type'] = provider_type
        if operation:
            context['operation'] = operation
        
        super().__init__(message, context=context, **kwargs)


class ProcessingError(TinyRAGError):
    """Exception raised during data processing operations."""
    
    def __init__(
        self,
        message: str,
        processor_type: Optional[str] = None,
        input_type: Optional[str] = None,
        processing_stage: Optional[str] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if processor_type:
            context['processor_type'] = processor_type
        if input_type:
            context['input_type'] = input_type
        if processing_stage:
            context['processing_stage'] = processing_stage
        
        super().__init__(message, context=context, **kwargs)


class FactoryError(TinyRAGError):
    """Exception raised by factory classes."""
    
    def __init__(
        self,
        message: str,
        factory_type: Optional[str] = None,
        requested_type: Optional[str] = None,
        available_types: Optional[list] = None,
        **kwargs
    ) -> None:
        context = kwargs.get('context', {})
        if factory_type:
            context['factory_type'] = factory_type
        if requested_type:
            context['requested_type'] = requested_type
        if available_types:
            context['available_types'] = available_types
        
        super().__init__(message, context=context, **kwargs) 