"""
Refactored PromptixBuilder class using dependency injection and focused components.

This module provides the PromptixBuilder class that has been refactored to use
focused components and dependency injection for better testability and modularity.
"""

from typing import Any, Dict, List, Optional, Union
from .container import get_container
from .components import (
    PromptLoader,
    VariableValidator,
    TemplateRenderer,
    VersionManager,
    ModelConfigBuilder
)
from .adapters._base import ModelAdapter
from .exceptions import (
    PromptNotFoundError,
    VersionNotFoundError,
    UnsupportedClientError,
    ToolNotFoundError,
    ToolProcessingError,
    ValidationError,
    StorageError,
    RequiredVariableError,
    VariableValidationError,
    TemplateRenderError
)


class PromptixBuilder:
    """Builder class for creating model configurations using dependency injection."""
    
    def __init__(self, prompt_template: str, container=None):
        """Initialize the builder with dependency injection.
        
        Args:
            prompt_template: The name of the prompt template to use.
            container: Optional container for dependency injection. If None, uses global container.
            
        Raises:
            PromptNotFoundError: If the prompt template is not found.
        """
        self._container = container or get_container()
        self.prompt_template = prompt_template
        self.custom_version = None
        self._data = {}          # Holds all variables
        self._memory = []        # Conversation history
        self._client = "openai"  # Default client
        self._model_params = {}  # Holds direct model parameters
        
        # Get dependencies from container
        self._prompt_loader = self._container.get_typed("prompt_loader", PromptLoader)
        self._variable_validator = self._container.get_typed("variable_validator", VariableValidator)
        self._template_renderer = self._container.get_typed("template_renderer", TemplateRenderer)
        self._version_manager = self._container.get_typed("version_manager", VersionManager)
        self._model_config_builder = self._container.get_typed("model_config_builder", ModelConfigBuilder)
        self._logger = self._container.get("logger")
        self._adapters = self._container.get("adapters")
        
        # Initialize prompt data
        self._initialize_prompt_data()

    def _initialize_prompt_data(self) -> None:
        """Initialize prompt data and find live version.
        
        Raises:
            PromptNotFoundError: If the prompt template is not found.
        """
        try:
            self.prompt_data = self._prompt_loader.get_prompt_data(self.prompt_template)
        except StorageError as err:
            try:
                available_prompts = list(self._prompt_loader.get_prompts().keys())
            except StorageError:
                available_prompts = []
            raise PromptNotFoundError(
                prompt_name=self.prompt_template,
                available_prompts=available_prompts
            ) from err
        versions = self.prompt_data.get("versions", {})
        live_version_key = self._version_manager.find_live_version(versions, self.prompt_template)
        self.version_data = versions[live_version_key]
        
        # Extract schema properties
        schema = self.version_data.get("schema", {})
        self.properties = schema.get("properties", {})
        self.allow_additional = schema.get("additionalProperties", False)

    @classmethod
    def register_adapter(cls, client_name: str, adapter: ModelAdapter, container=None) -> None:
        """Register a new adapter for a client.
        
        Args:
            client_name: Name of the client.
            adapter: The adapter instance.
            container: Optional container. If None, uses global container.
            
        Raises:
            InvalidDependencyError: If the adapter is not a ModelAdapter instance.
        """
        _container = container or get_container()
        _container.register_adapter(client_name, adapter)

    def _validate_type(self, field: str, value: Any) -> None:
        """Validate that a value matches its schema-defined type.
        
        Args:
            field: Name of the field to validate.
            value: Value to validate.
            
        Raises:
            ValidationError: If validation fails.
        """
        if field not in self.properties:
            if not self.allow_additional:
                raise ValidationError(
                    f"Field '{field}' is not defined in the schema and additional properties are not allowed.",
                    details={"field": field, "value": value}
                )
            return

        self._variable_validator.validate_builder_type(field, value, self.properties)

    def __getattr__(self, name: str):
        """Dynamically handle chainable with_<variable>() methods.
        
        Args:
            name: Name of the method being called.
            
        Returns:
            A setter function for chainable method calls.
            
        Raises:
            AttributeError: If the method is not a valid with_* method.
        """
        if name.startswith("with_"):
            field = name[5:]
            
            def setter(value: Any):
                self._validate_type(field, value)
                self._data[field] = value
                return self
            return setter
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def with_data(self, **kwargs: Dict[str, Any]):
        """Set multiple variables at once using keyword arguments.
        
        Args:
            **kwargs: Variables to set.
            
        Returns:
            Self for method chaining.
        """
        for field, value in kwargs.items():
            self._validate_type(field, value)
            self._data[field] = value
        return self
    
    def with_var(self, variables: Dict[str, Any]):
        """Set multiple variables at once using a dictionary.
        
        This method allows passing a dictionary of variables to be used in prompt templates
        and tools configuration. All variables are made available to the tools_template 
        Jinja2 template for conditional tool selection.
        
        Args:
            variables: Dictionary of variable names and their values to be set
            
        Returns:
            Self for method chaining
            
        Example:
            ```python
            config = (Promptix.builder("ComplexCodeReviewer")
                      .with_var({
                          'programming_language': 'Python',
                          'severity': 'high',
                          'review_focus': 'security and performance'
                      })
                      .build())
            ```
        """
        for field, value in variables.items():
            self._validate_type(field, value)
            self._data[field] = value
        return self
    
    def with_extra(self, extra_params: Dict[str, Any]):
        """Set additional/extra parameters to be passed directly to the model API.
        
        Args:
            extra_params: Dictionary containing model parameters to be passed directly
                         to the API (e.g., temperature, top_p, max_tokens).
            
        Returns:
            Self reference for method chaining.
        """
        self._model_params.update(extra_params)
        return self
    
    def with_memory(self, memory: List[Dict[str, str]]):
        """Set the conversation memory.
        
        Args:
            memory: List of message dictionaries.
            
        Returns:
            Self for method chaining.
            
        Raises:
            InvalidMemoryFormatError: If memory format is invalid.
        """
        # Use the model config builder to validate memory format
        self._model_config_builder.validate_memory_format(memory)
        self._memory = memory
        return self
    
    def for_client(self, client: str):
        """Set the client to use for building the configuration.
        
        Args:
            client: Name of the client to use.
            
        Returns:
            Self for method chaining.
            
        Raises:
            UnsupportedClientError: If the client is not supported.
        """
        # Check if we have an adapter for this client
        if client not in self._adapters:
            available_clients = list(self._adapters.keys())
            raise UnsupportedClientError(
                client_name=client,
                available_clients=available_clients
            )
        
        # Check compatibility and warn if necessary
        self._check_client_compatibility(client)
        
        self._client = client
        return self
    
    def _check_client_compatibility(self, client: str) -> None:
        """Check if the client is compatible with the prompt version.
        
        Args:
            client: Name of the client to check.
        """
        provider = self.version_data.get("provider", "").lower()
        config_provider = self.version_data.get("config", {}).get("provider", "").lower()
        
        # Use either provider field
        effective_provider = provider or config_provider
        
        # Issue warning if providers don't match
        if effective_provider and effective_provider != client:
            warning_msg = (
                f"Client '{client}' may not be fully compatible with this prompt version. "
                f"This prompt version is configured for '{effective_provider}'. "
                f"Some features may not work as expected."
            )
            if self._logger:
                self._logger.warning(warning_msg)
    
    def with_version(self, version: str):
        """Set a specific version of the prompt template to use.
        
        Args:
            version: Version identifier to use.
            
        Returns:
            Self for method chaining.
            
        Raises:
            VersionNotFoundError: If the version is not found.
        """
        versions = self.prompt_data.get("versions", {})
        if version not in versions:
            available_versions = list(versions.keys())
            raise VersionNotFoundError(
                version=version,
                prompt_name=self.prompt_template,
                available_versions=available_versions
            )
        
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
            *args: Additional tool names to activate
            
        Returns:
            Self for method chaining
        """
        # First handle the primary tool_name
        self._activate_tool(tool_name)
        
        # Handle any additional tool names passed as positional arguments
        for tool in args:
            self._activate_tool(tool)
                
        return self
        
    def _activate_tool(self, tool_name: str) -> None:
        """Internal helper to activate a single tool.
        
        Args:
            tool_name: Name of the tool to activate.
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
            if self._logger:
                self._logger.warning(
                    f"Tool '{tool_name}' not found. Available tools: {available_tools}"
                )
    
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
            if self._logger:
                self._logger.warning(
                    f"Tool '{tool_name}' not found. Available tools: {available_tools}"
                )
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
        """Process the tools template and return the configured tools.
        
        Returns:
            List of configured tools.
        """
        tools_config = self.version_data.get("tools_config", {})
        available_tools = tools_config.get("tools", {})
        
        if not tools_config or not available_tools:
            return []

        # Track both template-selected and explicitly activated tools
        selected_tools = {}
        
        # First, find explicitly activated tools (via with_tool)
        for tool_name in available_tools.keys():
            prefixed_name = f"use_{tool_name}"
            if (tool_name in self._data and self._data[tool_name]) or \
               (prefixed_name in self._data and self._data[prefixed_name]):
                selected_tools[tool_name] = available_tools[tool_name]
        
        # Process tools template if available
        tools_template = tools_config.get("tools_template")
        if tools_template:
            try:
                template_result = self._template_renderer.render_tools_template(
                    tools_template=tools_template,
                    variables=self._data,
                    available_tools=available_tools,
                    prompt_name=self.prompt_template
                )
                if template_result:
                    self._process_template_result(template_result, available_tools, selected_tools)
            except TemplateRenderError as e:
                if self._logger:
                    self._logger.warning(f"Error processing tools template: {e!s}")
            # Let unexpected exceptions bubble up
        # If no tools selected, return empty list
        if not selected_tools:
            return []
            
        try:
            # Convert to the format expected by the adapter
            adapter = self._adapters[self._client]
            return adapter.process_tools(selected_tools)
            
        except Exception as e:
            if self._logger:
                self._logger.warning(f"Error processing tools: {str(e)}")
            return []
    
    def _process_template_result(
        self, 
        template_result: Any, 
        available_tools: Dict[str, Any], 
        selected_tools: Dict[str, Any]
    ) -> None:
        """Process the result from tools template rendering.
        
        Args:
            template_result: Result from template rendering.
            available_tools: Available tools configuration.
            selected_tools: Dictionary to update with selected tools.
        """
        # Handle different return types from template
        if isinstance(template_result, list):
            # If it's a list of tool names (new format)
            if all(isinstance(item, str) for item in template_result):
                for tool_name in template_result:
                    if tool_name in available_tools and tool_name not in selected_tools:
                        selected_tools[tool_name] = available_tools[tool_name]
            # If it's a list of tool objects (old format for backward compatibility)
            elif all(isinstance(item, dict) for item in template_result):
                for tool in template_result:
                    if isinstance(tool, dict) and 'name' in tool:
                        tool_name = tool['name']
                        if tool_name in available_tools and tool_name not in selected_tools:
                            selected_tools[tool_name] = available_tools[tool_name]
        # If it's a dictionary of tools (old format for backward compatibility)
        elif isinstance(template_result, dict):
            for tool_name, tool_config in template_result.items():
                if tool_name not in selected_tools:
                    selected_tools[tool_name] = tool_config

    def build(self, system_only: bool = False) -> Union[Dict[str, Any], str]:
        """Build the final configuration using the appropriate adapter.
        
        Args:
            system_only: If True, returns only the system instruction string.
            
        Returns:
            Either the full model configuration dictionary or just the system instruction string.
        """
        # Validate all required fields are present
        missing_fields = []
        for field, props in self.properties.items():
            if props.get("required", False) and field not in self._data:
                missing_fields.append(field)
                if self._logger:
                    self._logger.warning(f"Required field '{field}' is missing from prompt parameters")

        try:
            # Generate the system message using the template renderer
            from .base import Promptix  # Import here to avoid circular dependency
            promptix_instance = Promptix(self._container)
            system_message = promptix_instance.render_prompt(self.prompt_template, self.custom_version, **self._data)
        except (ValueError, ImportError, RuntimeError, RequiredVariableError, VariableValidationError) as e:
            if self._logger:
                self._logger.warning(f"Error generating system message: {e!s}")
            # Provide a fallback basic message when template rendering fails
            system_message = f"You are an AI assistant for {self.prompt_template}."
        
        # If system_only is True, just return the system message
        if system_only:
            return system_message
            
        # Build configuration based on client type
        if self._client == "anthropic":
            model_config = self._model_config_builder.prepare_anthropic_config(
                system_message=system_message,
                memory=self._memory,
                version_data=self.version_data,
                prompt_name=self.prompt_template
            )
        else:
            # For OpenAI and others
            model_config = self._model_config_builder.build_model_config(
                system_message=system_message,
                memory=self._memory,
                version_data=self.version_data,
                prompt_name=self.prompt_template
            )
        
        # Add any direct model parameters from with_extra
        model_config.update(self._model_params)
        
        # Process tools configuration
        try:
            tools = self._process_tools_template()
            if tools:
                model_config["tools"] = tools
        except Exception as e:
            if self._logger:
                self._logger.warning(f"Error processing tools: {str(e)}")
        
        # Get the appropriate adapter and adapt the configuration
        adapter = self._adapters[self._client]
        try:
            model_config = adapter.adapt_config(model_config, self.version_data)
        except Exception as e:
            if self._logger:
                self._logger.warning(f"Error adapting configuration for client {self._client}: {str(e)}")
        
        return model_config

    def system_instruction(self) -> str:
        """Get only the system instruction/prompt as a string.
        
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
        
        # Create context for template rendering
        template_context = {
            "tools_config": tools_config,
            "tools": tools,
            **self._data
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
