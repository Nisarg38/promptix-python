from typing import Any, Dict, List, Union
from ._base import ModelAdapter

class AnthropicAdapter(ModelAdapter):
    """Adapter for Anthropic's API."""
    
    def adapt_config(self, model_config: Dict[str, Any], version_data: Dict[str, Any]) -> Dict[str, Any]:
        # Initialize Anthropic-specific config
        anthropic_config = {}
        
        # Get the model from version data config
        anthropic_config["model"] = self.get_model_from_config(version_data)
        
        # Add common parameters (Anthropic uses same parameter names as common ones)
        common_params = self.validate_and_extract_parameters(version_data)
        anthropic_config.update(common_params)
        
        # Copy system and messages directly
        if "system" in model_config:
            anthropic_config["system"] = model_config["system"]
        if "messages" in model_config:
            anthropic_config["messages"] = model_config["messages"]
        
        # Handle tools if supported by the model
        if self.has_tools(model_config):
            tools = model_config["tools"]
            if isinstance(tools, dict):
                # Convert to Anthropic's tool format with tool parameters
                tools_list = self._convert_dict_tools_to_anthropic_format(tools, model_config)
                anthropic_config["tools"] = tools_list
            elif isinstance(tools, list):
                anthropic_config["tools"] = tools
        
        # Clean up temporary tool parameter entries
        self.cleanup_tool_parameters(anthropic_config)
        
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
        """Convert tools data to Anthropic's format with support for custom parameters."""
        anthropic_tools = []
        
        # Handle if tools_data is a dictionary of tool_name -> tool_config
        if isinstance(tools_data, dict):
            for tool_name, tool_config in tools_data.items():
                anthropic_tool = self._create_anthropic_tool_definition(tool_name, tool_config)
                anthropic_tools.append(anthropic_tool)
        
        # Handle if tools_data is already a list
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
    
    def _convert_dict_tools_to_anthropic_format(
        self, 
        tools: Dict[str, Any], 
        model_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert dictionary-format tools to Anthropic format."""
        tools_list = []
        tool_params_map = self.extract_tool_parameters(model_config)
        
        for tool_name, tool_config in tools.items():
            tool_params = tool_params_map.get(tool_name, {})
            
            # Create base tool definition
            tool_spec = {
                "name": tool_name,
                "description": tool_config.get("description", "")
            }
            
            # Handle input schema (parameters)
            if "parameters" in tool_config:
                input_schema = self.apply_custom_parameters_to_schema(
                    tool_config["parameters"], 
                    tool_params
                )
                tool_spec["input_schema"] = input_schema
            
            tools_list.append(tool_spec)
        
        return tools_list
    
    def _create_anthropic_tool_definition(self, tool_name: str, tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create an Anthropic-format tool definition."""
        # Extract tool parameters if present
        tool_params = {}
        if "params" in tool_config:
            tool_params = tool_config.pop("params")
        
        # Create an Anthropic-compatible tool
        anthropic_tool = {
            "name": tool_name,
            "description": tool_config.get("description", "")
        }
        
        # Extract parameters from tool_config
        parameters = tool_config.get("parameters", {})
        if parameters:
            # Apply custom parameters and convert to Anthropic's input_schema format
            input_schema = self.apply_custom_parameters_to_schema(parameters, tool_params)
            anthropic_tool["input_schema"] = input_schema
        
        return anthropic_tool 