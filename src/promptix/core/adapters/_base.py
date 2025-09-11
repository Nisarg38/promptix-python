from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union, Optional, Tuple


class ModelAdapter(ABC):
    """Base adapter class for different model providers with common functionality."""
    
    # Common parameter types and their validation
    COMMON_PARAMETERS = {
        "temperature": (int, float),
        "max_tokens": int,
        "top_p": (int, float),
    }
    
    @abstractmethod
    def adapt_config(self, model_config: Dict[str, Any], version_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt the configuration for specific provider."""
        pass

    @abstractmethod
    def adapt_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Adapt message format for specific provider."""
        pass

    @abstractmethod
    def process_tools(self, tools_data: Union[Dict, List]) -> List[Dict[str, Any]]:
        """Process tools data into the appropriate format for the specific adapter."""
        pass
    
    # Common helper methods
    
    def validate_and_extract_parameters(
        self, 
        version_data: Dict[str, Any], 
        parameter_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Validate and extract common configuration parameters.
        
        Args:
            version_data: The version data containing configuration
            parameter_mapping: Optional mapping from source to target parameter names
                             If None, uses direct mapping (source = target)
        
        Returns:
            Dict of validated parameters
            
        Raises:
            ValueError: If parameter validation fails
        """
        parameter_mapping = parameter_mapping or {}
        validated_params = {}
        config = version_data.get("config", {})
        
        for source_param, expected_type in self.COMMON_PARAMETERS.items():
            if source_param in config and config[source_param] is not None:
                value = config[source_param]
                
                # Validate parameter type
                if not isinstance(value, expected_type):
                    type_name = expected_type.__name__ if hasattr(expected_type, '__name__') else str(expected_type)
                    raise ValueError(f"{source_param} must be of type {type_name}, got {type(value).__name__}")
                
                # Map to target parameter name
                target_param = parameter_mapping.get(source_param, source_param)
                validated_params[target_param] = value
        
        return validated_params
    
    def extract_tool_parameters(self, model_config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract custom tool parameters from model config.
        
        Args:
            model_config: The model configuration dictionary
            
        Returns:
            Dict mapping tool names to their custom parameters
        """
        tool_params = {}
        
        for key in model_config:
            if key.startswith("tool_params_"):
                tool_name = key[len("tool_params_"):]
                tool_params[tool_name] = model_config[key]
        
        return tool_params
    
    def cleanup_tool_parameters(self, model_config: Dict[str, Any]) -> None:
        """
        Remove temporary tool parameter entries from model config.
        
        Args:
            model_config: The model configuration dictionary to clean
        """
        keys_to_remove = [key for key in model_config.keys() if key.startswith("tool_params_")]
        for key in keys_to_remove:
            del model_config[key]
    
    def apply_custom_parameters_to_schema(
        self, 
        input_schema: Dict[str, Any], 
        custom_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply custom parameters to a tool's input schema.
        
        Args:
            input_schema: The original input schema
            custom_params: Custom parameters to apply
            
        Returns:
            Modified input schema with custom parameters applied
        """
        if not custom_params:
            return input_schema
        
        # Create a copy to avoid modifying the original
        modified_schema = input_schema.copy()
        
        # Apply custom parameters to properties if they exist
        if "properties" in modified_schema and custom_params:
            if "properties" not in modified_schema:
                modified_schema["properties"] = {}
                
            properties = modified_schema["properties"]
            for param_name, param_value in custom_params.items():
                if param_name in properties:
                    if not isinstance(properties[param_name], dict):
                        properties[param_name] = {}
                    properties[param_name]["default"] = param_value
        
        return modified_schema
    
    def has_tools(self, model_config: Dict[str, Any]) -> bool:
        """
        Check if model config has non-empty tools.
        
        Args:
            model_config: The model configuration dictionary
            
        Returns:
            True if tools exist and are non-empty
        """
        tools = model_config.get("tools")
        if not tools:
            return False
        
        if isinstance(tools, list):
            return len(tools) > 0
        elif isinstance(tools, dict):
            return len(tools) > 0
        
        return False
    
    def get_model_from_config(self, version_data: Dict[str, Any]) -> str:
        """
        Extract model name from version data configuration.
        
        Args:
            version_data: The version data containing configuration
            
        Returns:
            Model name
            
        Raises:
            ValueError: If model is not specified
        """
        model = version_data.get("config", {}).get("model")
        if not model:
            raise ValueError("Model must be specified in the version data config")
        return model 