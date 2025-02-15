from typing import Any, Dict, List
from ._base import ModelAdapter

class AnthropicAdapter(ModelAdapter):
    """Adapter for Anthropic's API."""
    
    def adapt_config(self, model_config: Dict[str, Any], version_data: Dict[str, Any]) -> Dict[str, Any]:
        # Initialize Anthropic-specific config
        anthropic_config = {}
        
        # Use the model directly from version_data
        anthropic_config["model"] = version_data["model"]
        
        # Map supported parameters with Anthropic-specific names
        param_mapping = {
            "temperature": "temperature",
            "max_tokens": "max_tokens",
            "top_p": "top_p"
        }

        for source_param, target_param in param_mapping.items():
            if source_param in version_data and version_data[source_param] is not None:
                value = version_data[source_param]
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