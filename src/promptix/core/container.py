"""
Dependency Injection Container for Promptix.

This module provides a simple dependency injection container to manage
dependencies and improve testability of the Promptix system.
"""

from typing import Any, Dict, Optional, Type, TypeVar, Generic, Callable
from ..enhancements.logging import setup_logging
from .components import (
    PromptLoader,
    VariableValidator,
    TemplateRenderer,
    VersionManager,
    ModelConfigBuilder
)
from .adapters.openai import OpenAIAdapter
from .adapters.anthropic import AnthropicAdapter
from .adapters._base import ModelAdapter
from .exceptions import MissingDependencyError, InvalidDependencyError

T = TypeVar('T')


class Container:
    """Simple dependency injection container for Promptix components."""
    
    def __init__(self):
        """Initialize the container with default dependencies."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._setup_defaults()
    
    def _setup_defaults(self) -> None:
        """Setup default dependencies."""
        # Setup logger as singleton
        self.register_singleton("logger", setup_logging())
        
        # Register component factories
        self.register_factory("prompt_loader", lambda: PromptLoader(
            logger=self.get("logger")
        ))
        
        self.register_factory("variable_validator", lambda: VariableValidator(
            logger=self.get("logger")
        ))
        
        self.register_factory("template_renderer", lambda: TemplateRenderer(
            logger=self.get("logger")
        ))
        
        self.register_factory("version_manager", lambda: VersionManager(
            logger=self.get("logger")
        ))
        
        self.register_factory("model_config_builder", lambda: ModelConfigBuilder(
            logger=self.get("logger")
        ))
        
        # Register adapters as singletons
        self.register_singleton("openai_adapter", OpenAIAdapter())
        self.register_singleton("anthropic_adapter", AnthropicAdapter())
        
        # Register adapter registry
        self.register_singleton("adapters", {
            "openai": self.get("openai_adapter"),
            "anthropic": self.get("anthropic_adapter")
        })
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """Register a singleton instance.
        
        Args:
            name: Name of the service.
            instance: The singleton instance.
        """
        self._singletons[name] = instance
    
    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """Register a factory function that creates instances.
        
        Args:
            name: Name of the service.
            factory: Function that creates the service instance.
        """
        self._factories[name] = factory
    
    def register_transient(self, name: str, service_type: Type[T], *args, **kwargs) -> None:
        """Register a transient service (new instance each time).
        
        Args:
            name: Name of the service.
            service_type: Type of the service to instantiate.
            *args: Arguments to pass to the constructor.
            **kwargs: Keyword arguments to pass to the constructor.
        """
        self._services[name] = (service_type, args, kwargs)
    
    def get(self, name: str) -> Any:
        """Get a service instance by name.
        
        Args:
            name: Name of the service to retrieve.
            
        Returns:
            The service instance.
            
        Raises:
            MissingDependencyError: If the service is not registered.
        """
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]
        
        # Check factories
        if name in self._factories:
            return self._factories[name]()
        
        # Check transient services
        if name in self._services:
            service_type, args, kwargs = self._services[name]
            return service_type(*args, **kwargs)
        
        raise MissingDependencyError(
            dependency_name=name,
            component="Container"
        )
    
    def get_typed(self, name: str, expected_type: Type[T]) -> T:
        """Get a service instance with type checking.
        
        Args:
            name: Name of the service to retrieve.
            expected_type: Expected type of the service.
            
        Returns:
            The service instance cast to the expected type.
            
        Raises:
            MissingDependencyError: If the service is not registered.
            InvalidDependencyError: If the service is not of the expected type.
        """
        service = self.get(name)
        if not isinstance(service, expected_type):
            raise InvalidDependencyError(
                dependency_name=name,
                expected_type=expected_type.__name__,
                actual_type=type(service).__name__
            )
        return service
    
    def override(self, name: str, instance: Any) -> None:
        """Override a service with a new instance (useful for testing).
        
        Args:
            name: Name of the service to override.
            instance: The new service instance.
        """
        self._singletons[name] = instance
    
    def clear_overrides(self) -> None:
        """Clear all service overrides and restore defaults."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._setup_defaults()
    
    def register_adapter(self, name: str, adapter: ModelAdapter) -> None:
        """Register a new model adapter.
        
        Args:
            name: Name of the adapter (e.g., "claude", "gpt4").
            adapter: The adapter instance.
            
        Raises:
            InvalidDependencyError: If the adapter is not a ModelAdapter instance.
        """
        if not isinstance(adapter, ModelAdapter):
            raise InvalidDependencyError(
                dependency_name=name,
                expected_type="ModelAdapter",
                actual_type=type(adapter).__name__
            )
        
        # Add to adapters registry
        adapters = self.get("adapters")
        adapters[name] = adapter
    
    def create_scope(self) -> 'ContainerScope':
        """Create a new scope with isolated overrides.
        
        Returns:
            A new container scope.
        """
        return ContainerScope(self)


class ContainerScope:
    """A scoped container that can have isolated overrides."""
    
    def __init__(self, parent_container: Container):
        """Initialize the scoped container.
        
        Args:
            parent_container: The parent container to inherit from.
        """
        self._parent = parent_container
        self._overrides: Dict[str, Any] = {}
    
    def override(self, name: str, instance: Any) -> None:
        """Override a service in this scope only.
        
        Args:
            name: Name of the service to override.
            instance: The new service instance.
        """
        self._overrides[name] = instance
    
    def get(self, name: str) -> Any:
        """Get a service, checking overrides first.
        
        Args:
            name: Name of the service to retrieve.
            
        Returns:
            The service instance.
        """
        if name in self._overrides:
            return self._overrides[name]
        return self._parent.get(name)
    
    def get_typed(self, name: str, expected_type: Type[T]) -> T:
        """Get a service with type checking.
        
        Args:
            name: Name of the service to retrieve.
            expected_type: Expected type of the service.
            
        Returns:
            The service instance cast to the expected type.
        """
        service = self.get(name)
        if not isinstance(service, expected_type):
            raise InvalidDependencyError(
                dependency_name=name,
                expected_type=expected_type.__name__,
                actual_type=type(service).__name__
            )
        return service


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container instance.
    
    Returns:
        The global container instance.
    """
    global _container
    if _container is None:
        _container = Container()
    return _container


def set_container(container: Container) -> None:
    """Set the global container instance (useful for testing).
    
    Args:
        container: The container instance to set as global.
    """
    global _container
    _container = container


def reset_container() -> None:
    """Reset the global container to defaults."""
    global _container
    _container = None
