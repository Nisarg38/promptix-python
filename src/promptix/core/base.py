import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, List, Union
from jinja2 import BaseLoader, Environment, TemplateError
from ..enhancements.logging import setup_logging
from .storage.loaders import PromptLoaderFactory
from .storage.utils import create_default_prompts_file
from .config import config
from .validation import get_validation_engine


class Promptix:
    """Main class for managing and using prompts with schema validation and template rendering."""
    
    _prompts: Dict[str, Any] = {}
    _jinja_env = Environment(
        loader=BaseLoader(),
        trim_blocks=True,
        lstrip_blocks=True
    )
    _logger = setup_logging()
    
    @classmethod
    def _load_prompts(cls) -> None:
        """Load prompts from local prompts file using centralized configuration."""
        try:
            # Check for unsupported JSON files first
            unsupported_files = config.check_for_unsupported_files()
            if unsupported_files:
                json_file = unsupported_files[0]  # Get the first JSON file found
                raise ValueError(
                    f"JSON format is no longer supported. Found unsupported file: {json_file}\n"
                    f"Please convert to YAML format:\n"
                    f"1. Rename {json_file} to {json_file.with_suffix('.yaml')}\n"
                    f"2. Ensure the content follows YAML syntax\n"
                    f"3. Remove the old JSON file"
                )
            
            # Use centralized configuration to find prompt file
            prompt_file = config.get_prompt_file_path()
            
            if prompt_file is None:
                # No existing prompts file found, create default
                prompt_file = config.get_default_prompt_file_path()
                cls._prompts = create_default_prompts_file(prompt_file)
                cls._logger.info(f"Created new prompts file at {prompt_file} with a sample prompt")
                return
            
            loader = PromptLoaderFactory.get_loader(prompt_file)
            cls._prompts = loader.load(prompt_file)
            cls._logger.info(f"Successfully loaded prompts from {prompt_file}")
            
        except Exception as e:
            raise ValueError(f"Failed to load prompts: {str(e)}")
    
    
    @classmethod
    def _find_live_version(cls, versions: Dict[str, Any]) -> Optional[str]:
        """Find the live version. Only one version should be live at a time."""
        # Find versions where is_live == True
        live_versions = [k for k, v in versions.items() if v.get("is_live", False)]
        
        if not live_versions:
            return None
            
        if len(live_versions) > 1:
            raise ValueError(
                f"Multiple live versions found: {live_versions}. Only one version can be live at a time."
            )
        
        return live_versions[0]
    
    @classmethod
    def get_prompt(cls, prompt_template: str, version: Optional[str] = None, **variables) -> str:
        """Get a prompt by name and fill in the variables.
        
        Args:
            prompt_template (str): The name of the prompt template to use
            version (Optional[str]): Specific version to use (e.g. "v1"). 
                                     If None, uses the latest live version.
            **variables: Variable key-value pairs to fill in the prompt template
            
        Returns:
            str: The rendered prompt
            
        Raises:
            ValueError: If the prompt template is not found or required variables are missing
            TypeError: If a variable doesn't match the schema type
        """
        if not cls._prompts:
            cls._load_prompts()
        
        if prompt_template not in cls._prompts:
            raise ValueError(f"Prompt template '{prompt_template}' not found in prompts configuration.")
        
        prompt_data = cls._prompts[prompt_template]
        versions = prompt_data.get("versions", {})
        
        # --- 1) Determine which version to use ---
        version_data = None
        if version:
            # Use explicitly requested version
            if version not in versions:
                raise ValueError(
                    f"Version '{version}' not found for prompt '{prompt_template}'."
                )
            version_data = versions[version]
        else:
            # Find the "latest" live version
            live_version_key = cls._find_live_version(versions)
            if not live_version_key:
                raise ValueError(
                    f"No live version found for prompt '{prompt_template}'."
                )
            version_data = versions[live_version_key]
        
        if not version_data:
            raise ValueError(f"No valid version data found for prompt '{prompt_template}'.")
        
        template_text = version_data.get("config", {}).get("system_instruction")
        if not template_text:
            raise ValueError(
                f"Version data for '{prompt_template}' does not contain 'config.system_instruction'."
            )
        
        # --- 2) Validate variables against schema ---
        schema = version_data.get("schema", {})
        validation_engine = get_validation_engine(cls._logger)
        validation_engine.validate_variables(schema, variables, prompt_template)
        
        # --- 3) Render with Jinja2 to handle conditionals, loops, etc. ---
        try:
            template_obj = cls._jinja_env.from_string(template_text)
            result = template_obj.render(**variables)
        except TemplateError as e:
            raise ValueError(f"Error rendering template for '{prompt_template}': {str(e)}")

        # Convert escaped newlines (\n) to actual line breaks
        result = result.replace("\\n", "\n")
        
        return result

    
    @classmethod
    def prepare_model_config(cls, prompt_template: str, memory: List[Dict[str, str]], version: Optional[str] = None, **variables) -> Dict[str, Any]:
        """Prepare a model configuration ready for OpenAI chat completion API.
        
        Args:
            prompt_template (str): The name of the prompt template to use
            memory (List[Dict[str, str]]): List of previous messages in the conversation
            version (Optional[str]): Specific version to use (e.g. "v1"). 
                                     If None, uses the latest live version.
            **variables: Variable key-value pairs to fill in the prompt template
            
        Returns:
            Dict[str, Any]: Configuration dictionary for OpenAI chat completion API
            
        Raises:
            ValueError: If the prompt template is not found, required variables are missing, or system message is empty
            TypeError: If a variable doesn't match the schema type or memory format is invalid
        """
        # Validate memory format
        if not isinstance(memory, list):
            raise TypeError("Memory must be a list of message dictionaries")
        
        for msg in memory:
            if not isinstance(msg, dict):
                raise TypeError("Each memory item must be a dictionary")
            if "role" not in msg or "content" not in msg:
                raise ValueError("Each memory item must have 'role' and 'content' keys")
            if msg["role"] not in ["user", "assistant", "system"]:
                raise ValueError("Message role must be 'user', 'assistant', or 'system'")
            if not isinstance(msg["content"], str):
                raise TypeError("Message content must be a string")
            if not msg["content"].strip():
                raise ValueError("Message content cannot be empty")

        # Get the system message using existing get_prompt method
        system_message = cls.get_prompt(prompt_template, version, **variables)
        
        if not system_message.strip():
            raise ValueError("System message cannot be empty")

        # Get the prompt configuration
        if not cls._prompts:
            cls._load_prompts()
        
        if prompt_template not in cls._prompts:
            raise ValueError(f"Prompt template '{prompt_template}' not found in prompts configuration.")
        
        prompt_data = cls._prompts[prompt_template]
        versions = prompt_data.get("versions", {})
        
        # Determine which version to use
        version_data = None
        if version:
            if version not in versions:
                raise ValueError(f"Version '{version}' not found for prompt '{prompt_template}'.")
            version_data = versions[version]
        else:
            live_version_key = cls._find_live_version(versions)
            if not live_version_key:
                raise ValueError(f"No live version found for prompt '{prompt_template}'.")
            version_data = versions[live_version_key]
        
        # Initialize the base configuration with required parameters
        model_config = {
            "messages": [{"role": "system", "content": system_message}]
        }
        model_config["messages"].extend(memory)

        # Get configuration from version data
        config = version_data.get("config", {})
        
        # Model is required for OpenAI API
        if "model" not in config:
            raise ValueError(f"Model must be specified in the version data config for prompt '{prompt_template}'")
        model_config["model"] = config["model"]

        # Add optional configuration parameters only if they are present and not null
        optional_params = [
            ("temperature", (int, float)),
            ("max_tokens", int),
            ("top_p", (int, float)),
            ("frequency_penalty", (int, float)),
            ("presence_penalty", (int, float))
        ]

        for param_name, expected_type in optional_params:
            if param_name in config and config[param_name] is not None:
                value = config[param_name]
                if not isinstance(value, expected_type):
                    raise ValueError(f"{param_name} must be of type {expected_type}")
                model_config[param_name] = value
            
        # Add tools configuration if present and non-empty
        if "tools" in config and config["tools"]:
            tools = config["tools"]
            if not isinstance(tools, list):
                raise ValueError("Tools configuration must be a list")
            model_config["tools"] = tools
            
            # If tools are present, also set tool_choice if specified
            if "tool_choice" in config:
                model_config["tool_choice"] = config["tool_choice"]
        
        return model_config

    @staticmethod
    def builder(prompt_template: str):
        """Create a new PromptixBuilder instance for building model configurations.
        
        Args:
            prompt_template (str): The name of the prompt template to use
            
        Returns:
            PromptixBuilder: A builder instance for configuring the model
        """
        from .builder import PromptixBuilder
        return PromptixBuilder(prompt_template)
