from typing import Any, Dict, List, Union
from ._base import ModelAdapter

class AnthropicAdapter(ModelAdapter):
    """Adapter for Anthropic's API."""
    
    def adapt_config(self, model_config: Dict[str, Any], version_data: Dict[str, Any]) -> Dict[str, Any]:
        # Initialize Anthropic-specific config
        anthropic_config = {}
        
        # Use the model from version_data config
        anthropic_config["model"] = version_data.get("config", {}).get("model")
        if not anthropic_config["model"]:
            raise ValueError("Model must be specified in the version data config")
        
        # Map supported parameters with Anthropic-specific names
        param_mapping = {
            "temperature": "temperature",
            "max_tokens": "max_tokens",
            "top_p": "top_p"
        }

        config = version_data.get("config", {})
        for source_param, target_param in param_mapping.items():
            if source_param in config and config[source_param] is not None:
                value = config[source_param]
                if isinstance(value, (int, float)):
                    anthropic_config[target_param] = value
        
        # Copy system and messages directly
        if "system" in model_config:
            anthropic_config["system"] = model_config["system"]
        if "messages" in model_config:
            anthropic_config["messages"] = model_config["messages"]
        
        # Handle tools if supported by the model
        if "tools" in model_config and model_config["tools"]:
            tools = model_config["tools"]
            if isinstance(tools, dict):
                # Convert to Anthropic's tool format
                tools_list = []
                for tool_name, tool_config in tools.items():
                    tool_spec = {
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            **tool_config
                        }
                    }
                    tools_list.append(tool_spec)
                anthropic_config["tools"] = tools_list
            elif isinstance(tools, list):
                anthropic_config["tools"] = tools
        
        return anthropic_config

    def adapt_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        anthropic_messages = []
        
        # Convert messages to Anthropic format
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                # For Claude, system messages are supported directly
                anthropic_messages.append({
                    "role": "system",
                    "content": content
                })
            elif role in ["assistant", "user"]:
                anthropic_messages.append({
                    "role": role,
                    "content": content
                })
        
        return anthropic_messages

    def process_tools(self, tools_data: Union[Dict, List]) -> List[Dict[str, Any]]:
        """Convert tools data to Anthropic's format.
        
        Anthropic uses a different format for tools compared to OpenAI:
        - Name and description are at the top level
        - Parameters are under "input_schema" instead of "parameters"
        """
        anthropic_tools = []
        
        # Handle if tools_data is a dictionary of tool_name -> tool_config
        if isinstance(tools_data, dict):
            for tool_name, tool_config in tools_data.items():
                # Create an Anthropic-compatible tool
                anthropic_tool = {
                    "name": tool_name,
                    "description": tool_config.get("description", "")
                }
                
                # Extract parameters from tool_config
                parameters = tool_config.get("parameters", {})
                if parameters:
                    # Anthropic uses "input_schema" instead of "parameters"
                    anthropic_tool["input_schema"] = parameters
                
                anthropic_tools.append(anthropic_tool)
        
        # Handle if tools_data is already a list (possibly from OpenAI format)
        elif isinstance(tools_data, list):
            for tool in tools_data:
                # Handle OpenAI-style function tools
                if isinstance(tool, dict) and tool.get("type") == "function" and "function" in tool:
                    function = tool["function"]
                    anthropic_tool = {
                        "name": function.get("name", ""),
                        "description": function.get("description", "")
                    }
                    
                    # Convert parameters to input_schema
                    if "parameters" in function:
                        anthropic_tool["input_schema"] = function["parameters"]
                    
                    anthropic_tools.append(anthropic_tool)
                # Handle already formatted Anthropic tools
                elif isinstance(tool, dict) and "name" in tool:
                    # Already in Anthropic format, just add it
                    anthropic_tools.append(tool)
        
        return anthropic_tools 