from typing import Any, Dict, List, Union
from ._base import ModelAdapter

class OpenAIAdapter(ModelAdapter):
    """Adapter for OpenAI's API."""
    
    def adapt_config(self, model_config: Dict[str, Any], version_data: Dict[str, Any]) -> Dict[str, Any]:
        # Add optional configuration parameters if present
        optional_params = [
            ("temperature", (int, float)),
            ("max_tokens", int),
            ("top_p", (int, float)),
            ("frequency_penalty", (int, float)),
            ("presence_penalty", (int, float))
        ]

        for param_name, expected_type in optional_params:
            if param_name in version_data and version_data[param_name] is not None:
                value = version_data[param_name]
                if not isinstance(value, expected_type):
                    raise ValueError(f"{param_name} must be of type {expected_type}")
                model_config[param_name] = value
        
        # Handle tools - only include if non-empty
        if "tools" in model_config:
            tools = model_config["tools"]
            if not tools:  # Remove empty tools array
                del model_config["tools"]
            elif isinstance(tools, dict):
                # Convert dict to list format expected by OpenAI
                tools_list = []
                for tool_name, tool_config in tools.items():
                    # Check if this tool has custom parameters from the builder
                    tool_params = model_config.get(f"tool_params_{tool_name}", {})
                    
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
                        for param_name, param_value in tool_params.items():
                            if param_name in tool_def["function"]["parameters"]:
                                tool_def["function"]["parameters"][param_name]["default"] = param_value
                    
                    tools_list.append(tool_def)
                
                if tools_list:  # Only set if non-empty
                    model_config["tools"] = tools_list
                else:
                    del model_config["tools"]
            elif not isinstance(tools, list):
                raise ValueError("Tools must be either a dictionary or a list")
            elif not tools:  # Empty list case
                del model_config["tools"]
        
        # Clean up temporary tool parameter entries
        for key in list(model_config.keys()):
            if key.startswith("tool_params_"):
                del model_config[key]
        
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
                    parameters = tool_def["function"]["parameters"]
                    for param_name, param_value in tool_params.items():
                        if param_name in parameters:
                            # Set default value to custom parameter
                            if "properties" in parameters and param_name in parameters["properties"]:
                                parameters["properties"][param_name]["default"] = param_value
                            # For simple parameters schema
                            elif isinstance(parameters, dict):
                                parameters[param_name] = param_value
                
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