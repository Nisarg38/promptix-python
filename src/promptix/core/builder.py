from typing import Any, Dict, List, Optional, Union
from .base import Promptix
from .adapters.openai import OpenAIAdapter
from .adapters.anthropic import AnthropicAdapter
from .adapters._base import ModelAdapter
from ..enhancements.logging import setup_logging

class PromptixBuilder:
    """Builder class for creating model configurations."""
    
    # Map of client names to their adapters
    _adapters = {
        "openai": OpenAIAdapter(),
        "anthropic": AnthropicAdapter()
    }
    
    # Setup logger
    _logger = setup_logging()
    
    def __init__(self, prompt_template: str):
        self.prompt_template = prompt_template
        self.custom_version = None
        self._data = {}          # Holds all variables
        self._memory = []        # Conversation history
        self._client = "openai"  # Default client
        
        # Ensure prompts are loaded
        if not Promptix._prompts:
            Promptix._load_prompts()
        
        if prompt_template not in Promptix._prompts:
            raise ValueError(f"Prompt template '{prompt_template}' not found in prompts.json.")
        
        self.prompt_data = Promptix._prompts[prompt_template]
        versions = self.prompt_data.get("versions", {})
        live_version_key = Promptix._find_live_version(versions)
        if live_version_key is None:
            raise ValueError(f"No live version found for prompt '{prompt_template}'.")
        self.version_data = versions[live_version_key]
        
        # Extract schema properties
        schema = self.version_data.get("schema", {})
        self.properties = schema.get("properties", {})
        self.allow_additional = schema.get("additionalProperties", False)

    @classmethod
    def register_adapter(cls, client_name: str, adapter: ModelAdapter) -> None:
        """Register a new adapter for a client."""
        if not isinstance(adapter, ModelAdapter):
            raise ValueError("Adapter must be an instance of ModelAdapter")
        cls._adapters[client_name] = adapter

    def _validate_type(self, field: str, value: Any) -> None:
        """Validate that a value matches its schema-defined type."""
        if field not in self.properties:
            if not self.allow_additional:
                raise ValueError(f"Field '{field}' is not defined in the schema and additional properties are not allowed.")
            return

        prop = self.properties[field]
        expected_type = prop.get("type")
        enum_values = prop.get("enum")

        if expected_type == "string":
            if not isinstance(value, str):
                raise TypeError(f"Field '{field}' must be a string, got {type(value).__name__}")
        elif expected_type == "number":
            if not isinstance(value, (int, float)):
                raise TypeError(f"Field '{field}' must be a number, got {type(value).__name__}")
        elif expected_type == "integer":
            if not isinstance(value, int):
                raise TypeError(f"Field '{field}' must be an integer, got {type(value).__name__}")
        elif expected_type == "boolean":
            if not isinstance(value, bool):
                raise TypeError(f"Field '{field}' must be a boolean, got {type(value).__name__}")

        if enum_values is not None and value not in enum_values:
            raise ValueError(f"Field '{field}' must be one of {enum_values}, got '{value}'")

    def __getattr__(self, name: str):
        # Dynamically handle chainable with_<variable>() methods
        if name.startswith("with_"):
            field = name[5:]
            
            def setter(value: Any):
                self._validate_type(field, value)
                self._data[field] = value
                return self
            return setter
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def with_data(self, **kwargs: Dict[str, Any]):
        """Set multiple variables at once using keyword arguments."""
        for field, value in kwargs.items():
            self._validate_type(field, value)
            self._data[field] = value
        return self
    
    def with_memory(self, memory: List[Dict[str, str]]):
        """Set the conversation memory."""
        if not isinstance(memory, list):
            raise TypeError("Memory must be a list of message dictionaries")
        for msg in memory:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                raise TypeError("Each memory item must be a dict with 'role' and 'content'")
        self._memory = memory
        return self
    
    def for_client(self, client: str):
        """Set the client to use for building the configuration."""
        # First check if we have an adapter for this client
        if client not in self._adapters:
            raise ValueError(f"Unsupported client: {client}. Available clients: {list(self._adapters.keys())}")
        
        # Check if the prompt version supports this client
        provider = self.version_data.get("provider", "").lower()
        config_provider = self.version_data.get("config", {}).get("provider", "").lower()
        
        # Use either provider field - some prompts use top-level provider, others put it in config
        effective_provider = provider or config_provider
        
        # If a provider is specified and doesn't match the requested client, issue a warning
        if effective_provider and effective_provider != client:
            warning_msg = (
                f"Client '{client}' may not be fully compatible with this prompt version. "
                f"This prompt version is configured for '{effective_provider}'. "
                f"Some features may not work as expected. "
                f"Consider using a prompt version designed for {client} or use the compatible client."
            )
            self._logger.warning(warning_msg)
        
        self._client = client
        return self
    
    def with_version(self, version: str):
        """Set a specific version of the prompt template to use."""
        versions = self.prompt_data.get("versions", {})
        if version not in versions:
            raise ValueError(f"Version '{version}' not found in prompt template '{self.prompt_template}'")
        
        self.custom_version = version
        self.version_data = versions[version]
        
        # Update schema properties for the new version
        schema = self.version_data.get("schema", {})
        self.properties = schema.get("properties", {})
        self.allow_additional = schema.get("additionalProperties", False)
        
        # Set the client based on the provider in version_data
        provider = self.version_data.get("provider", "openai").lower()
        if provider in self._adapters:
            self._client = provider
        
        return self
    
    def with_tool(self, tool_name: str, *args, **kwargs) -> "PromptixBuilder":
        """Activate a tool by name.
        
        Args:
            tool_name: Name of the tool to activate
            
        Returns:
            Self for method chaining
        """
        # Validate tool exists in prompts configuration
        tools_config = self.version_data.get("tools_config", {})
        tools = tools_config.get("tools", {})
        
        if tool_name in tools:
            # Store tool activation as a template variable
            tool_var = f"use_{tool_name}"
            self._data[tool_var] = True
        else:
            available_tools = list(tools.keys()) if tools else []
            warning_msg = (
                f"Tool type '{tool_name}' not found in configuration. "
                f"Available tools: {available_tools}. "
                f"This tool will be ignored."
            )
            self._logger.warning(warning_msg)
                
        return self
        
    def with_tool_parameter(self, tool_name: str, param_name: str, param_value: Any) -> "PromptixBuilder":
        """Set a parameter value for a specific tool.
        
        Args:
            tool_name: Name of the tool to configure
            param_name: Name of the parameter to set
            param_value: Value to set for the parameter
            
        Returns:
            Self for method chaining
        """
        # Validate tool exists
        tools_config = self.version_data.get("tools_config", {})
        tools = tools_config.get("tools", {})
        
        if tool_name not in tools:
            available_tools = list(tools.keys()) if tools else []
            warning_msg = (
                f"Tool '{tool_name}' not found in configuration. "
                f"Available tools: {available_tools}. "
                f"Parameter will be ignored."
            )
            self._logger.warning(warning_msg)
            return self
            
        # Make sure the tool is activated
        tool_var = f"use_{tool_name}"
        if tool_var not in self._data or not self._data[tool_var]:
            self._data[tool_var] = True
            
        # Store parameter in a dedicated location
        param_key = f"tool_params_{tool_name}"
        if param_key not in self._data:
            self._data[param_key] = {}
            
        self._data[param_key][param_name] = param_value
        return self
        
    def enable_tools(self, *tool_names: str) -> "PromptixBuilder":
        """Enable multiple tools at once.
        
        Args:
            *tool_names: Names of tools to enable
            
        Returns:
            Self for method chaining
        """
        for tool_name in tool_names:
            self.with_tool(tool_name)
        return self
        
    def disable_tools(self, *tool_names: str) -> "PromptixBuilder":
        """Disable specific tools.
        
        Args:
            *tool_names: Names of tools to disable
            
        Returns:
            Self for method chaining
        """
        for tool_name in tool_names:
            tool_var = f"use_{tool_name}"
            self._data[tool_var] = False
        return self
        
    def disable_all_tools(self) -> "PromptixBuilder":
        """Disable all available tools.
        
        Returns:
            Self for method chaining
        """
        tools_config = self.version_data.get("tools_config", {})
        tools = tools_config.get("tools", {})
        
        for tool_name in tools.keys():
            tool_var = f"use_{tool_name}"
            self._data[tool_var] = False
            
        return self

    def _process_tools_template(self) -> List[Dict[str, Any]]:
        """Process the tools template and return the configured tools."""
        tools_config = self.version_data.get("tools_config", {})
        available_tools = tools_config.get("tools", {})
        
        if not tools_config or not available_tools:
            return []

        # Get the selected tools
        selected_tools = {}
        
        # Check which tools are activated (either with or without the "use_" prefix)
        for tool_name in available_tools.keys():
            prefixed_name = f"use_{tool_name}"
            # Check if tool is activated directly or with "use_" prefix
            if (tool_name in self._data and self._data[tool_name]) or \
               (prefixed_name in self._data and self._data[prefixed_name]):
                selected_tools[tool_name] = available_tools[tool_name]
        
        # If no tools selected, return empty list
        if not selected_tools:
            return []
            
        try:
            # Convert to the format expected by the adapter
            adapter = self._adapters[self._client]
            return adapter.process_tools(selected_tools)
            
        except Exception as e:
            # Log the error with detailed information
            import traceback
            error_details = traceback.format_exc()
            self._logger.warning(f"Error processing tools: {str(e)}\nDetails: {error_details}")
            return []  # Return empty list on error

    def build(self, system_only: bool = False) -> Union[Dict[str, Any], str]:
        """Build the final configuration using the appropriate adapter.
        
        Args:
            system_only: If True, returns only the system instruction string instead of the full model config.
            
        Returns:
            Either the full model configuration dictionary or just the system instruction string,
            depending on the value of system_only.
        """
        # Validate all required fields are present and have correct types
        missing_fields = []
        for field, props in self.properties.items():
            if props.get("required", False):
                if field not in self._data:
                    missing_fields.append(field)
                    warning_msg = f"Required field '{field}' is missing from prompt parameters"
                    self._logger.warning(warning_msg)
                else:
                    try:
                        self._validate_type(field, self._data[field])
                    except (TypeError, ValueError) as e:
                        self._logger.warning(str(e))
        
        # Only raise an error if ALL required fields are missing
        if missing_fields and len(missing_fields) == len([f for f, p in self.properties.items() if p.get("required", False)]):
            raise ValueError(f"All required fields are missing: {missing_fields}")

        try:
            # Generate the system message using the existing logic
            system_message = Promptix.get_prompt(self.prompt_template, self.custom_version, **self._data)
        except Exception as e:
            self._logger.warning(f"Error generating system message: {str(e)}")
            # Provide a fallback basic message when template rendering fails
            system_message = f"You are an AI assistant for {self.prompt_template}."
        
        # If system_only is True, just return the system message
        if system_only:
            return system_message
            
        # Initialize the base configuration
        model_config = {}
        
        # Set the model from version data
        if "model" not in self.version_data.get("config", {}):
            raise ValueError(f"Model must be specified in the prompt version data config for '{self.prompt_template}'")
        model_config["model"] = self.version_data["config"]["model"]
        
        # Handle system message differently for different providers
        if self._client == "anthropic":
            model_config["system"] = system_message
            model_config["messages"] = self._memory
        else:
            # For OpenAI and others, include system message in messages array
            model_config["messages"] = [{"role": "system", "content": system_message}]
            model_config["messages"].extend(self._memory)
        
        # Process tools configuration
        try:
            tools = self._process_tools_template()
            if tools:
                model_config["tools"] = tools
        except Exception as e:
            self._logger.warning(f"Error processing tools: {str(e)}")
        
        # Get the appropriate adapter and adapt the configuration
        adapter = self._adapters[self._client]
        try:
            model_config = adapter.adapt_config(model_config, self.version_data)
        except Exception as e:
            self._logger.warning(f"Error adapting configuration for client {self._client}: {str(e)}")
        
        return model_config

    def system_instruction(self) -> str:
        """Get only the system instruction/prompt as a string.
        
        This is a convenient shorthand for build(system_only=True).
        
        Returns:
            The rendered system instruction string
        """
        return self.build(system_only=True)
        
    def debug_tools(self) -> Dict[str, Any]:
        """Debug method to inspect the tools configuration.
        
        Returns:
            Dict containing tools configuration information for debugging.
        """
        tools_config = self.version_data.get("tools_config", {})
        tools = tools_config.get("tools", {})
        tools_template = tools_config.get("tools_template") if tools_config else None
        
        # Create context for template rendering (same as in _process_tools_template)
        template_context = {
            "tools_config": tools_config,
            "tools": tools,
            **self._data  # All variables including tool activation flags
        }
        
        # Return debug information
        return {
            "has_tools_config": bool(tools_config),
            "has_tools": bool(tools),
            "has_tools_template": bool(tools_template),
            "available_tools": list(tools.keys()) if tools else [],
            "template_context_keys": list(template_context.keys()),
            "tool_activation_flags": {k: v for k, v in self._data.items() if k.startswith("use_")}
        } 