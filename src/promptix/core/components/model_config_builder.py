"""
ModelConfigBuilder component for building model configurations.

This component handles building model configurations for different
providers, including message formatting and parameter validation.
"""

from typing import Any, Dict, List, Optional, Union
from ..exceptions import InvalidMemoryFormatError, ConfigurationError


class ModelConfigBuilder:
    """Handles building model configurations for API calls."""
    
    def __init__(self, logger=None):
        """Initialize the model config builder.
        
        Args:
            logger: Optional logger instance for dependency injection.
        """
        self._logger = logger
    
    def build_model_config(
        self,
        system_message: str,
        memory: List[Dict[str, str]],
        version_data: Dict[str, Any],
        prompt_name: str
    ) -> Dict[str, Any]:
        """Build a complete model configuration.
        
        Args:
            system_message: The system message/instruction.
            memory: List of conversation history messages.
            version_data: Version configuration data.
            prompt_name: Name of the prompt for error reporting.
            
        Returns:
            Complete model configuration dictionary.
            
        Raises:
            InvalidMemoryFormatError: If memory format is invalid.
            ConfigurationError: If required configuration is missing.
        """
        # Validate memory format
        self.validate_memory_format(memory)
        
        # Validate system message
        if not system_message.strip():
            raise ConfigurationError("System message cannot be empty")
        
        # Initialize the base configuration
        model_config = {
            "messages": [{"role": "system", "content": system_message}]
        }
        model_config["messages"].extend(memory)

        # Get configuration from version data
        config = version_data.get("config", {})
        
        # Model is required
        if "model" not in config:
            raise ConfigurationError(
                f"Model must be specified in the version data config for prompt '{prompt_name}'"
            )
        model_config["model"] = config["model"]

        # Add optional configuration parameters
        self._add_optional_parameters(model_config, config)
        
        # Add tools configuration if present
        self._add_tools_configuration(model_config, config)
        
        return model_config
    
    def validate_memory_format(self, memory: List[Dict[str, str]]) -> None:
        """Validate the format of conversation memory.
        
        Args:
            memory: List of message dictionaries to validate.
            
        Raises:
            InvalidMemoryFormatError: If memory format is invalid.
        """
        if not isinstance(memory, list):
            raise InvalidMemoryFormatError("Memory must be a list of message dictionaries")
        
        for i, msg in enumerate(memory):
            if not isinstance(msg, dict):
                raise InvalidMemoryFormatError(
                    f"Message at index {i} must be a dictionary",
                    invalid_message=msg
                )
            
            if "role" not in msg or "content" not in msg:
                raise InvalidMemoryFormatError(
                    f"Message at index {i} must have 'role' and 'content' keys",
                    invalid_message=msg
                )
            
            if msg["role"] not in ["user", "assistant", "system"]:
                raise InvalidMemoryFormatError(
                    f"Message role at index {i} must be 'user', 'assistant', or 'system'",
                    invalid_message=msg
                )
            
            if not isinstance(msg["content"], str):
                raise InvalidMemoryFormatError(
                    f"Message content at index {i} must be a string",
                    invalid_message=msg
                )
            
            if not msg["content"].strip():
                raise InvalidMemoryFormatError(
                    f"Message content at index {i} cannot be empty",
                    invalid_message=msg
                )
    
    def _add_optional_parameters(self, model_config: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Add optional parameters to model configuration.
        
        Args:
            model_config: The model configuration to update.
            config: The source configuration data.
        """
        optional_params = [
            ("temperature", (int, float)),
            ("max_tokens", int),
            ("top_p", (int, float)),
            ("frequency_penalty", (int, float)),
            ("presence_penalty", (int, float))
        ]

        for param_name, expected_type in optional_params:
            if param_name in config and config[param_name] is not None:
                value = config[param_name]
                if not isinstance(value, expected_type):
                    if self._logger:
                        self._logger.warning(
                            f"{param_name} must be of type {expected_type}, got {type(value)}"
                        )
                    continue
                model_config[param_name] = value
    
    def _add_tools_configuration(self, model_config: Dict[str, Any], config: Dict[str, Any]) -> None:
        """Add tools configuration to model configuration.
        
        Args:
            model_config: The model configuration to update.
            config: The source configuration data.
        """
        if "tools" in config and config["tools"]:
            tools = config["tools"]
            if not isinstance(tools, list):
                if self._logger:
                    self._logger.warning("Tools configuration must be a list")
                return
            
            model_config["tools"] = tools
            
            # If tools are present, also set tool_choice if specified
            if "tool_choice" in config:
                model_config["tool_choice"] = config["tool_choice"]
    
    def prepare_anthropic_config(
        self,
        system_message: str,
        memory: List[Dict[str, str]],
        version_data: Dict[str, Any],
        prompt_name: str
    ) -> Dict[str, Any]:
        """Build configuration specifically for Anthropic API.
        
        Args:
            system_message: The system message/instruction.
            memory: List of conversation history messages.
            version_data: Version configuration data.
            prompt_name: Name of the prompt for error reporting.
            
        Returns:
            Anthropic-specific model configuration dictionary.
        """
        # Validate inputs
        self.validate_memory_format(memory)
        
        if not system_message.strip():
            raise ConfigurationError("System message cannot be empty")
        
        config = version_data.get("config", {})
        
        if "model" not in config:
            raise ConfigurationError(
                f"Model must be specified in the version data config for prompt '{prompt_name}'"
            )
        
        # Anthropic format uses separate system parameter
        model_config = {
            "model": config["model"],
            "system": system_message,
            "messages": memory
        }
        
        # Add optional parameters
        self._add_optional_parameters(model_config, config)
        
        return model_config
    
    def build_system_only_config(self, system_message: str) -> str:
        """Build a configuration that returns only the system message.
        
        Args:
            system_message: The system message to return.
            
        Returns:
            The system message string.
        """
        return system_message
