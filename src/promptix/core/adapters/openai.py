from typing import Any, Dict, List
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
                    tools_list.append({
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            **tool_config
                        }
                    })
                if tools_list:  # Only set if non-empty
                    model_config["tools"] = tools_list
                else:
                    del model_config["tools"]
            elif not isinstance(tools, list):
                raise ValueError("Tools must be either a dictionary or a list")
            elif not tools:  # Empty list case
                del model_config["tools"]
        
        return model_config

    def adapt_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        # OpenAI's message format is already our base format
        return messages 