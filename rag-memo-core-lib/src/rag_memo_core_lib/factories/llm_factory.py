"""
LLM Factory for TinyRAG Core Library

Factory class for creating LLM provider instances with
proper configuration and registration support.
"""

from typing import Dict, Type, Any, List
from ..abstractions.llm import LLMProvider, LLMConfig
from ..exceptions import FactoryError
import logging

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory for creating LLM provider instances.
    
    Manages registration and creation of LLM providers with
    support for dynamic provider registration and configuration.
    """
    
    _providers: Dict[str, Type[LLMProvider]] = {}
    _provider_configs: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_provider(
        cls, 
        name: str, 
        provider_class: Type[LLMProvider],
        default_config: Dict[str, Any] = None
    ) -> None:
        """
        Register a new LLM provider type.
        
        Args:
            name: Provider name/identifier
            provider_class: Provider class implementing LLMProvider
            default_config: Default configuration for the provider
        """
        if not issubclass(provider_class, LLMProvider):
            raise FactoryError(
                f"Provider class must inherit from LLMProvider",
                factory_type="LLMFactory",
                requested_type=name
            )
        
        cls._providers[name] = provider_class
        cls._provider_configs[name] = default_config or {}
        
        logger.info(f"Registered LLM provider: {name}")
    
    @classmethod
    def create_provider(cls, provider_type: str, config: Dict[str, Any]) -> LLMProvider:
        """
        Create LLM provider instance.
        
        Args:
            provider_type: Type of provider to create
            config: Provider configuration
            
        Returns:
            LLMProvider: Configured provider instance
            
        Raises:
            FactoryError: If provider type is not supported
        """
        if provider_type not in cls._providers:
            raise FactoryError(
                f"Unsupported LLM provider: {provider_type}",
                factory_type="LLMFactory",
                requested_type=provider_type,
                available_types=list(cls._providers.keys())
            )
        
        provider_class = cls._providers[provider_type]
        
        # Merge default config with provided config
        merged_config = {**cls._provider_configs.get(provider_type, {}), **config}
        merged_config['component_name'] = f"llm_{provider_type}"
        
        try:
            provider_config = LLMConfig(**merged_config)
            return provider_class(provider_config)
        except Exception as e:
            raise FactoryError(
                f"Failed to create LLM provider {provider_type}: {str(e)}",
                factory_type="LLMFactory",
                requested_type=provider_type,
                cause=e
            )
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """
        Get list of supported provider types.
        
        Returns:
            List[str]: Supported provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def get_provider_info(cls, provider_type: str) -> Dict[str, Any]:
        """
        Get information about a specific provider.
        
        Args:
            provider_type: Provider type
            
        Returns:
            Dict[str, Any]: Provider information
            
        Raises:
            FactoryError: If provider type not found
        """
        if provider_type not in cls._providers:
            raise FactoryError(
                f"Unknown provider type: {provider_type}",
                factory_type="LLMFactory",
                requested_type=provider_type
            )
        
        provider_class = cls._providers[provider_type]
        return {
            "name": provider_type,
            "class": provider_class.__name__,
            "module": provider_class.__module__,
            "default_config": cls._provider_configs.get(provider_type, {}),
            "docstring": provider_class.__doc__
        }
    
    @classmethod
    def unregister_provider(cls, provider_type: str) -> bool:
        """
        Unregister a provider type.
        
        Args:
            provider_type: Provider type to unregister
            
        Returns:
            bool: True if unregistered successfully
        """
        if provider_type in cls._providers:
            del cls._providers[provider_type]
            cls._provider_configs.pop(provider_type, None)
            logger.info(f"Unregistered LLM provider: {provider_type}")
            return True
        return False
    
    @classmethod
    def clear_providers(cls) -> None:
        """Clear all registered providers."""
        cls._providers.clear()
        cls._provider_configs.clear()
        logger.info("Cleared all LLM providers") 