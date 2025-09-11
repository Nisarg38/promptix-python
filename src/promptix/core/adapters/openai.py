from typing import Any, Dict, List, Union
from ._base import ModelAdapter

class OpenAIAdapter(ModelAdapter):
    """Adapter for OpenAI's API."""
    
    # OpenAI-specific parameters beyond the common ones
    OPENAI_SPECIFIC_PARAMETERS = {
        "frequency_penalty": (int, float),
        "presence_penalty": (int, float)
    }
    
    def adapt_config(self, model_config: Dict[str, Any], version_data: Dict[str, Any]) -> Dict[str, Any]:
        # Add common configuration parameters
        common_params = self.validate_and_extract_parameters(version_data)
        model_config.update(common_params)
        
        # Add OpenAI-specific parameters
        config = version_data.get("config", {})
        for param_name, expected_type in self.OPENAI_SPECIFIC_PARAMETERS.items():
            if param_name in config and config[param_name] is not None:
                value = config[param_name]
                if not isinstance(value, expected_type):
                    raise ValueError(f"{param_name} must be of type {expected_type}")
                model_config[param_name] = value
        
        # Handle tools - only include if non-empty
        if self.has_tools(model_config):
            tools = model_config["tools"]
            if isinstance(tools, dict):
                # Convert dict to list format expected by OpenAI
                tools_list = self._convert_dict_tools_to_openai_format(tools, model_config)
                
                if tools_list:  # Only set if non-empty
                    model_config["tools"] = tools_list
                else:
                    del model_config["tools"]
            elif not isinstance(tools, list):
                raise ValueError("Tools must be either a dictionary or a list")
            elif not tools:  # Empty list case
                del model_config["tools"]
        elif "tools" in model_config:
            del model_config["tools"]  # Remove empty tools
        
        # Clean up temporary tool parameter entries
        self.cleanup_tool_parameters(model_config)
        
        return model_config

    def adapt_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        # OpenAI's message format is already our base format
        return messages 

    def process_tools(self, tools_data: Union[Dict, List]) -> List[Dict[str, Any]]:
        """Convert tools data to OpenAI function format."""
        formatted_tools = []
        
        if isinstance(tools_data, dict):
            # If template returns a dict of tool configurations
            for tool_name, tool_config in tools_data.items():
                tool_def = self._create_openai_tool_definition(tool_name, tool_config)
                formatted_tools.append(tool_def)
        elif isinstance(tools_data, list):
            # If template returns a list of tool configurations
            for tool_config in tools_data:
                if isinstance(tool_config, dict) and "name" in tool_config:
                    formatted_tools.append({
                        "type": "function",
                        "function": tool_config
                    })
                
        return formatted_tools
    
    def _convert_dict_tools_to_openai_format(
        self, 
        tools: Dict[str, Any], 
        model_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert dictionary-format tools to OpenAI list format."""
        tools_list = []
        tool_params_map = self.extract_tool_parameters(model_config)
        
        for tool_name, tool_config in tools.items():
            tool_params = tool_params_map.get(tool_name, {})
            
            # Create base tool config
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    **tool_config
                }
            }
            
            # Apply any custom parameters
            if tool_params and "parameters" in tool_def["function"]:
                modified_params = self.apply_custom_parameters_to_schema(
                    tool_def["function"]["parameters"], 
                    tool_params
                )
                tool_def["function"]["parameters"] = modified_params
            
            tools_list.append(tool_def)
        
        return tools_list
    
    def _create_openai_tool_definition(self, tool_name: str, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create an OpenAI-format tool definition."""
        # Extract tool parameters if present
        tool_params = {}
        if "params" in tool_config:
            tool_params = tool_config.pop("params")
        
        # Create the base tool definition
        tool_def = {
            "type": "function",
            "function": {
                "name": tool_name,
            }
        }
        
        # Copy all other properties to the function
        for key, value in tool_config.items():
            if key != "params":
                tool_def["function"][key] = value
        
        # Apply custom parameters if needed
        if tool_params and "parameters" in tool_def["function"]:
            modified_params = self.apply_custom_parameters_to_schema(
                tool_def["function"]["parameters"], 
                tool_params
            )
            tool_def["function"]["parameters"] = modified_params
        
        return tool_def 