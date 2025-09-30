import json
import warnings
from pathlib import Path
from typing import Dict, Any, Optional
from .loaders import PromptLoaderFactory
from .utils import create_default_prompts_file, create_default_prompts_folder
from ...enhancements.logging import setup_logging
from ..config import config

class PromptManager:
    """Manages prompts from local storage using centralized configuration."""
    
    def __init__(self, format: str = None):
        self.prompts: Dict[str, Any] = {}
        self._folder_based = False
        self._prompts_directory = None
        # Legacy format parameter is ignored in favor of centralized config
        if format:
            self._logger = setup_logging()
            self._logger.warning(
                f"Format parameter '{format}' is deprecated. "
                f"Use PROMPTIX_STORAGE_FORMAT environment variable instead."
            )
        self._logger = setup_logging()
        self._load_prompts()
    
    def _get_prompt_file(self) -> Optional[Path]:
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
            # No existing YAML file found, check for prompts/ directory
            prompts_dir = config.working_directory / "prompts"
            if prompts_dir.exists() and prompts_dir.is_dir():
                # Prompts directory exists, use folder-based approach
                self._logger.info(f"Found prompts directory at {prompts_dir}, using folder-based structure")
                # Don't create YAML file, just indicate folder-based approach
                self._folder_based = True
                self._prompts_directory = prompts_dir
                return None  # Indicate folder-based mode
            else:
                # No prompts directory found, create folder structure
                self._logger.info(f"Creating new folder-based prompts structure at {prompts_dir}")
                create_default_prompts_folder(prompts_dir)
                # Use folder-based approach
                self._folder_based = True
                self._prompts_directory = prompts_dir
                return None  # Indicate folder-based mode
            
        return prompt_file
    
    def _load_prompts(self) -> None:
        """Load prompts from YAML file or folder structure."""
        try:
            prompt_file = self._get_prompt_file()
            
            if prompt_file is None and self._folder_based:
                # Load from folder structure
                self._load_from_folder_structure()
            elif prompt_file is not None:
                # Load from YAML file
                loader = PromptLoaderFactory.get_loader(prompt_file)
                self.prompts = loader.load(prompt_file)
                self._logger.info(f"Successfully loaded prompts from {prompt_file}")
            else:
                # No prompts found, create empty structure
                self.prompts = {"schema": 1.0}
                
        except Exception as e:
            raise ValueError(f"Failed to load prompts: {str(e)}")
    
    def _load_from_folder_structure(self) -> None:
        """Load prompts from folder-based structure."""
        from ..components.prompt_loader import PromptLoader
        
        # Use the folder-based prompt loader
        folder_loader = PromptLoader(logger=self._logger)
        # Temporarily change config to use our prompts directory
        original_dir = config.working_directory
        config.set_working_directory(self._prompts_directory.parent)
        
        try:
            self.prompts = folder_loader.load_prompts()
            self._logger.info(f"Successfully loaded prompts from folder structure at {self._prompts_directory}")
        finally:
            # Restore original directory
            config.set_working_directory(original_dir)
    
    def get_prompt(self, prompt_id: str) -> Dict[str, Any]:
        """Get a specific prompt by ID."""
        if prompt_id not in self.prompts:
            raise ValueError(f"Prompt not found: {prompt_id}")
        return self.prompts[prompt_id]
    
    def list_prompts(self) -> Dict[str, Any]:
        """Return all available prompts."""
        return self.prompts
    
    def load_prompts(self) -> None:
        """Public method to reload prompts from storage."""
        self._load_prompts()

    def _format_prompt_for_storage(self, prompt_data: Any) -> Any:
        """Convert multiline prompts to single line with escaped newlines."""
        # Handle non-dict values (like schema float) directly
        if not isinstance(prompt_data, dict):
            return prompt_data
            
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
            
            # Handle folder-based mode
            if prompt_file is None and self._folder_based:
                # In folder-based mode, create a fallback YAML file in the prompts directory
                prompt_file = self._prompts_directory / "prompts.yaml"
                self._logger.info(f"Folder-based mode detected. Saving to fallback file: {prompt_file}")
            elif prompt_file is None:
                # Shouldn't happen, but provide a safe fallback
                raise ValueError("No valid prompt file path found. Unable to save prompts.")
            
            loader = PromptLoaderFactory.get_loader(prompt_file)
            formatted_prompts = {
                prompt_id: self._format_prompt_for_storage(prompt_data)
                for prompt_id, prompt_data in self.prompts.items()
            }
            loader.save(formatted_prompts, prompt_file)
            self._logger.info(f"Successfully saved prompts to {prompt_file}")
        except Exception as e:
            raise ValueError(f"Failed to save prompts: {str(e)}") 