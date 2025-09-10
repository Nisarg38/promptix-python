"""
PromptLoader component for loading and managing prompts from storage.

This component is responsible for loading prompts from the storage system
and managing the prompt data in memory.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from ..exceptions import StorageError, StorageFileNotFoundError, UnsupportedFormatError
from ..storage.loaders import PromptLoaderFactory
from ..storage.utils import create_default_prompts_file
from ..config import config


class PromptLoader:
    """Handles loading and managing prompts from storage."""
    
    def __init__(self, logger=None):
        """Initialize the prompt loader.
        
        Args:
            logger: Optional logger instance for dependency injection.
        """
        self._prompts: Dict[str, Any] = {}
        self._logger = logger
        self._loaded = False
    
    def load_prompts(self, force_reload: bool = False) -> Dict[str, Any]:
        """Load prompts from storage.
        
        Args:
            force_reload: If True, reload prompts even if already loaded.
            
        Returns:
            Dictionary containing all loaded prompts.
            
        Raises:
            StorageError: If loading fails.
            UnsupportedFormatError: If JSON format is detected.
        """
        if self._loaded and not force_reload:
            return self._prompts
            
        try:
            # Check for unsupported JSON files first
            unsupported_files = config.check_for_unsupported_files()
            if unsupported_files:
                json_file = unsupported_files[0]  # Get the first JSON file found
                raise UnsupportedFormatError(
                    file_path=str(json_file),
                    unsupported_format="json",
                    supported_formats=["yaml"]
                )
            
            # Use centralized configuration to find prompt file
            prompt_file = config.get_prompt_file_path()
            
            if prompt_file is None:
                # No existing prompts file found, create default
                prompt_file = config.get_default_prompt_file_path()
                self._prompts = create_default_prompts_file(prompt_file)
                if self._logger:
                    self._logger.info(f"Created new prompts file at {prompt_file} with a sample prompt")
                self._loaded = True
                return self._prompts
            
            loader = PromptLoaderFactory.get_loader(prompt_file)
            self._prompts = loader.load(prompt_file)
            if self._logger:
                self._logger.info(f"Successfully loaded prompts from {prompt_file}")
            self._loaded = True
            return self._prompts

        except UnsupportedFormatError:
            # Bubble up as-is per public contract.
            raise
        except StorageError:
            # Already a Promptix storage error; preserve type.
            raise
        except ValueError as e:
            # Normalize unknown-extension errors from factory into a structured error.
            if 'Unsupported file format' in str(e) and 'prompt_file' in locals():
                ext = str(getattr(prompt_file, "suffix", "")).lstrip('.')
                raise UnsupportedFormatError(
                    file_path=str(prompt_file),
                    unsupported_format=ext or "unknown",
                    supported_formats=["yaml", "yml"]
                ) from e
            raise StorageError("Failed to load prompts", {"cause": str(e)}) from e
        except Exception as e:
            # Catch-all for anything else, with proper chaining.
            raise StorageError("Failed to load prompts", {"cause": str(e)}) from e
    
    def get_prompts(self) -> Dict[str, Any]:
        """Get the loaded prompts.
        
        Returns:
            Dictionary containing all loaded prompts.
        """
        if not self._loaded:
            return self.load_prompts()
        return self._prompts
    
    def get_prompt_data(self, prompt_template: str) -> Dict[str, Any]:
        """Get data for a specific prompt template.
        
        Args:
            prompt_template: Name of the prompt template.
            
        Returns:
            Dictionary containing the prompt data.
            
        Raises:
            StorageError: If prompt is not found.
        """
        prompts = self.get_prompts()
        if prompt_template not in prompts:
            from ..exceptions import PromptNotFoundError
            available_prompts = list(prompts.keys())
            raise PromptNotFoundError(prompt_template, available_prompts)
        return prompts[prompt_template]
    
    def is_loaded(self) -> bool:
        """Check if prompts have been loaded.
        
        Returns:
            True if prompts are loaded, False otherwise.
        """
        return self._loaded
    
    def reload_prompts(self) -> Dict[str, Any]:
        """Force reload prompts from storage.
        
        Returns:
            Dictionary containing all reloaded prompts.
            
        Raises:
            StorageError: If reloading fails.
        """
        return self.load_prompts(force_reload=True)
