from typing import Any, Dict, List, Optional, Union
from .base import Promptix
from .adapters.openai import OpenAIAdapter
from .adapters.anthropic import AnthropicAdapter
from .adapters._base import ModelAdapter

class PromptixBuilder:
    """Builder class for creating model configurations."""
    
    # Map of client names to their adapters
    _adapters = {
        "openai": OpenAIAdapter(),
        "anthropic": AnthropicAdapter()
    }
    
    def __init__(self, prompt_template: str):
        self.prompt_template = prompt_template
        self.custom_version = None
        self._data = {}          # Holds all variables
        self._memory = []        # Conversation history
        self._client = "openai"  # Default client
        
        # Tool selection
        self._selected_tool = "default"
        
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
        if client not in self._adapters:
            raise ValueError(f"Unsupported client: {client}. Available clients: {list(self._adapters.keys())}")
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
    
    def with_tool(self, tool_type: Optional[str] = None):
        """Select which tool configuration to use."""
        if tool_type:
            # Validate tool exists in prompts configuration
            tools_config = self.version_data.get("tools", {})
            if tool_type in tools_config:
                self._selected_tool = tool_type
            else:
                raise ValueError(f"Tool type '{tool_type}' not found in configuration")
        return self

    def build(self) -> Dict[str, Any]:
        """Build the final configuration using the appropriate adapter."""
        # Validate all required fields are present and have correct types
        for field, props in self.properties.items():
            if props.get("required", False):
                if field not in self._data:
                    raise ValueError(f"Required field '{field}' is missing")
                self._validate_type(field, self._data[field])

        try:
            # Generate the system message using the existing logic
            system_message = Promptix.get_prompt(self.prompt_template, self.custom_version, **self._data)
        except Exception as e:
            raise ValueError(f"Error generating system message: {str(e)}")
        
        # Initialize the base configuration
        model_config = {}
        
        # Set the model from version data
        if "model" not in self.version_data:
            raise ValueError(f"Model must be specified in the prompt version data for '{self.prompt_template}'")
        model_config["model"] = self.version_data["model"]
        
        # Handle system message differently for different providers
        if self._client == "anthropic":
            model_config["system"] = system_message
            model_config["messages"] = self._memory

        # if self._client == "openai":
        else:
            # For OpenAI and others, include system message in messages array
            model_config["messages"] = [{"role": "system", "content": system_message}]
            model_config["messages"].extend(self._memory)
        
        # Add tools if they exist in version data
        if "tools" in self.version_data:
            if isinstance(self.version_data["tools"], dict):
                tools_config = self.version_data["tools"].get(self._selected_tool, {})
                if tools_config:
                    model_config["tools"] = tools_config
            elif isinstance(self.version_data["tools"], list):
                model_config["tools"] = self.version_data["tools"]
            else:
                raise ValueError("Tools must be either a dictionary or a list")
        
        # Get the appropriate adapter and adapt the configuration
        adapter = self._adapters[self._client]
        model_config = adapter.adapt_config(model_config, self.version_data)
        
        return model_config 