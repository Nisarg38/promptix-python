import json
import warnings
from pathlib import Path
from typing import Dict, Any
from .loaders import PromptLoaderFactory
from .utils import create_default_prompts_file
from ...enhancements.logging import setup_logging
from ..config import config

class PromptManager:
    """Manages prompts from local storage using centralized configuration."""
    
    def __init__(self, format: str = None):
        self.prompts: Dict[str, Any] = {}
        # Legacy format parameter is ignored in favor of centralized config
        if format:
            self._logger = setup_logging()
            self._logger.warning(
                f"Format parameter '{format}' is deprecated. "
                f"Use PROMPTIX_STORAGE_FORMAT environment variable instead."
            )
        self._logger = setup_logging()
        self._load_prompts()
    
    def _get_prompt_file(self) -> Path:
        """Get the prompt file path using centralized configuration."""
        # Check for unsupported JSON files first
        unsupported_files = config.check_for_unsupported_files()
        if unsupported_files:
            json_file = unsupported_files[0]
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
            # No existing file found, create default
            prompt_file = config.get_default_prompt_file_path()
            create_default_prompts_file(prompt_file)
            return prompt_file
            
        return prompt_file
    
    def _load_prompts(self) -> None:
        """Load prompts from local YAML prompts file (JSON no longer supported)."""
        try:
            prompt_file = self._get_prompt_file()
            loader = PromptLoaderFactory.get_loader(prompt_file)
            self.prompts = loader.load(prompt_file)
            self._logger.info(f"Successfully loaded prompts from {prompt_file}")
        except Exception as e:
            raise ValueError(f"Failed to load prompts: {str(e)}")
    
    def get_prompt(self, prompt_id: str) -> Dict[str, Any]:
        """Get a specific prompt by ID."""
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt not found: {prompt_id}")
        return self.prompts[prompt_id]
    
    def list_prompts(self) -> Dict[str, Any]:
        """Return all available prompts."""
        return self.prompts

    def _format_prompt_for_storage(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert multiline prompts to single line with escaped newlines."""
        formatted_data = prompt_data.copy()
        
        # Process each version's system_message
        if "versions" in formatted_data:
            for version in formatted_data["versions"].values():
                if "config" in version and "system_instruction" in version["config"]:
                    # Convert multiline to single line with \n
                    message = version["config"]["system_instruction"]
                    if isinstance(message, str):
                        lines = [line for line in message.strip().split("\n")]
                        version["config"]["system_instruction"] = "\\n".join(lines)
        
        return formatted_data

    def save_prompts(self) -> None:
        """Save prompts to local YAML prompts file (JSON no longer supported)."""
        try:
            prompt_file = self._get_prompt_file()
            loader = PromptLoaderFactory.get_loader(prompt_file)
            formatted_prompts = {
                prompt_id: self._format_prompt_for_storage(prompt_data)
                for prompt_id, prompt_data in self.prompts.items()
            }
            loader.save(formatted_prompts, prompt_file)
            self._logger.info(f"Successfully saved prompts to {prompt_file}")
        except Exception as e:
            raise ValueError(f"Failed to save prompts: {str(e)}") 