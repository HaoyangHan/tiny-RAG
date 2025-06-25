"""
Vector Store Factory for TinyRAG Core Library

Factory class for creating vector store instances with
proper configuration and registration support.
"""

from typing import Dict, Type, Any, List
from ..abstractions.vector_store import VectorStore, VectorStoreConfig
from ..exceptions import FactoryError
import logging

logger = logging.getLogger(__name__)


class VectorStoreFactory:
    """
    Factory for creating vector store instances.
    
    Manages registration and creation of vector stores with
    support for dynamic provider registration and configuration.
    """
    
    _stores: Dict[str, Type[VectorStore]] = {}
    _store_configs: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_store(
        cls, 
        name: str, 
        store_class: Type[VectorStore],
        default_config: Dict[str, Any] = None
    ) -> None:
        """
        Register a new vector store type.
        
        Args:
            name: Store name/identifier
            store_class: Store class implementing VectorStore
            default_config: Default configuration for the store
        """
        if not issubclass(store_class, VectorStore):
            raise FactoryError(
                f"Store class must inherit from VectorStore",
                factory_type="VectorStoreFactory",
                requested_type=name
            )
        
        cls._stores[name] = store_class
        cls._store_configs[name] = default_config or {}
        
        logger.info(f"Registered vector store: {name}")
    
    @classmethod
    def create_store(cls, store_type: str, config: Dict[str, Any]) -> VectorStore:
        """
        Create vector store instance.
        
        Args:
            store_type: Type of store to create
            config: Store configuration
            
        Returns:
            VectorStore: Configured store instance
            
        Raises:
            FactoryError: If store type is not supported
        """
        if store_type not in cls._stores:
            raise FactoryError(
                f"Unsupported vector store: {store_type}",
                factory_type="VectorStoreFactory",
                requested_type=store_type,
                available_types=list(cls._stores.keys())
            )
        
        store_class = cls._stores[store_type]
        
        # Merge default config with provided config
        merged_config = {**cls._store_configs.get(store_type, {}), **config}
        merged_config['component_name'] = f"vector_store_{store_type}"
        
        try:
            store_config = VectorStoreConfig(**merged_config)
            return store_class(store_config)
        except Exception as e:
            raise FactoryError(
                f"Failed to create vector store {store_type}: {str(e)}",
                factory_type="VectorStoreFactory",
                requested_type=store_type,
                cause=e
            )
    
    @classmethod
    def get_supported_stores(cls) -> List[str]:
        """
        Get list of supported store types.
        
        Returns:
            List[str]: Supported store names
        """
        return list(cls._stores.keys())
    
    @classmethod
    def get_store_info(cls, store_type: str) -> Dict[str, Any]:
        """
        Get information about a specific store.
        
        Args:
            store_type: Store type
            
        Returns:
            Dict[str, Any]: Store information
            
        Raises:
            FactoryError: If store type not found
        """
        if store_type not in cls._stores:
            raise FactoryError(
                f"Unknown store type: {store_type}",
                factory_type="VectorStoreFactory",
                requested_type=store_type
            )
        
        store_class = cls._stores[store_type]
        return {
            "name": store_type,
            "class": store_class.__name__,
            "module": store_class.__module__,
            "default_config": cls._store_configs.get(store_type, {}),
            "docstring": store_class.__doc__
        }
    
    @classmethod
    def unregister_store(cls, store_type: str) -> bool:
        """
        Unregister a store type.
        
        Args:
            store_type: Store type to unregister
            
        Returns:
            bool: True if unregistered successfully
        """
        if store_type in cls._stores:
            del cls._stores[store_type]
            cls._store_configs.pop(store_type, None)
            logger.info(f"Unregistered vector store: {store_type}")
            return True
        return False
    
    @classmethod
    def clear_stores(cls) -> None:
        """Clear all registered stores."""
        cls._stores.clear()
        cls._store_configs.clear()
        logger.info("Cleared all vector stores") 