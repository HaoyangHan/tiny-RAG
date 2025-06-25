"""
Base Abstractions for TinyRAG Core Library

Provides fundamental abstract base classes following SOLID principles.
All concrete implementations should inherit from these abstractions.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, Dict, Optional, List
from pydantic import BaseModel, Field
import asyncio
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


class BaseConfig(BaseModel):
    """
    Base configuration for all components.
    
    Provides common configuration structure with strict validation
    and extensibility for component-specific settings.
    """
    
    # Component identification
    component_name: str = Field(description="Component name for logging and identification")
    component_version: str = Field(default="1.4.0", description="Component version")
    
    # Common settings
    timeout_seconds: int = Field(default=30, ge=1, le=300, description="Operation timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    retry_delay_seconds: float = Field(default=1.0, ge=0.1, le=10.0, description="Delay between retries")
    
    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    enable_debug: bool = Field(default=False, description="Enable debug mode")
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        extra = "forbid"
        validate_assignment = True
        use_enum_values = True


class BaseProvider(ABC, Generic[T]):
    """
    Base provider class for all service providers.
    
    Implements common patterns for initialization, health checking,
    and resource management with async context manager support.
    """
    
    def __init__(self, config: BaseConfig) -> None:
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self._initialized = False
        self._logger = logging.getLogger(f"{__name__}.{config.component_name}")
        
        # Set logging level
        if config.enable_debug:
            self._logger.setLevel(logging.DEBUG)
        else:
            self._logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))
    
    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize the provider.
        
        Should be called before any operations. Must be idempotent.
        
        Raises:
            ProviderError: If initialization fails
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check provider health status.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """
        Cleanup provider resources.
        
        Should gracefully release all resources and be idempotent.
        """
        pass
    
    async def __aenter__(self) -> 'BaseProvider[T]':
        """Async context manager entry."""
        if not self._initialized:
            await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.cleanup()
    
    def is_initialized(self) -> bool:
        """Check if provider is initialized."""
        return self._initialized
    
    async def _retry_operation(
        self, 
        operation: callable, 
        *args, 
        **kwargs
    ) -> Any:
        """
        Retry operation with exponential backoff.
        
        Args:
            operation: Async operation to retry
            *args: Operation arguments
            **kwargs: Operation keyword arguments
            
        Returns:
            Any: Operation result
            
        Raises:
            Exception: Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay_seconds * (2 ** attempt)
                    self._logger.warning(
                        f"Operation failed (attempt {attempt + 1}), retrying in {delay}s: {str(e)}"
                    )
                    await asyncio.sleep(delay)
                else:
                    self._logger.error(f"Operation failed after {attempt + 1} attempts: {str(e)}")
        
        raise last_exception


class BaseProcessor(ABC, Generic[T, K]):
    """
    Base processor for transforming data.
    
    Provides abstract interface for data transformation operations
    with support for both single and batch processing.
    """
    
    def __init__(self, config: BaseConfig) -> None:
        """
        Initialize processor with configuration.
        
        Args:
            config: Processor configuration
        """
        self.config = config
        self._logger = logging.getLogger(f"{__name__}.{config.component_name}")
    
    @abstractmethod
    async def process(self, input_data: T) -> K:
        """
        Process input data and return transformed output.
        
        Args:
            input_data: Input data to process
            
        Returns:
            K: Processed output data
            
        Raises:
            ProcessingError: If processing fails
        """
        pass
    
    @abstractmethod
    async def batch_process(self, input_batch: List[T]) -> List[K]:
        """
        Process multiple inputs in batch.
        
        Default implementation processes items individually.
        Override for optimized batch processing.
        
        Args:
            input_batch: List of input data to process
            
        Returns:
            List[K]: List of processed outputs
            
        Raises:
            ProcessingError: If batch processing fails
        """
        pass
    
    async def validate_input(self, input_data: T) -> bool:
        """
        Validate input data before processing.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return input_data is not None
    
    async def process_with_validation(self, input_data: T) -> K:
        """
        Process input with validation.
        
        Args:
            input_data: Input data to process
            
        Returns:
            K: Processed output
            
        Raises:
            ValidationError: If input validation fails
            ProcessingError: If processing fails
        """
        if not await self.validate_input(input_data):
            raise ValueError(f"Invalid input data for {self.config.component_name}")
        
        return await self.process(input_data)


class Configurable:
    """Mixin for configurable components."""
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration with new values.
        
        Args:
            **kwargs: Configuration updates
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                self._logger.warning(f"Unknown configuration key: {key}")


class HealthCheckMixin:
    """Mixin for health checking capabilities."""
    
    async def detailed_health_check(self) -> Dict[str, Any]:
        """
        Perform detailed health check.
        
        Returns:
            Dict[str, Any]: Health check results with details
        """
        return {
            "healthy": await self.health_check(),
            "component": self.config.component_name,
            "version": self.config.component_version,
            "initialized": getattr(self, '_initialized', False),
            "timestamp": asyncio.get_event_loop().time()
        } 