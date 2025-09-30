import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from promptix.core.storage.loaders import PromptLoaderFactory, InvalidPromptSchemaError
from promptix.core.exceptions import UnsupportedFormatError
from promptix.core.config import config
from .folder_manager import FolderBasedPromptManager
import traceback

class PromptManager:
    def __init__(self) -> None:
        # Check for unsupported JSON files first
        unsupported_files = config.check_for_unsupported_files()
        if unsupported_files:
            json_file = unsupported_files[0]
            raise UnsupportedFormatError(
                str(json_file),
                "json",
                ["yaml", "yml"]
            )
        
        # Use folder-based prompt management
        # Note: FolderBasedPromptManager automatically handles migration
        # from existing YAML files to folder structure on first initialization.
        # Your existing prompts.yaml will be backed up and migrated safely.
        self._folder_manager = FolderBasedPromptManager()
    
    def load_prompts(self) -> Dict:
        """Load all prompts from folder structure."""
        return self._folder_manager.load_prompts()
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict]:
        """Get a specific prompt by ID."""
        return self._folder_manager.get_prompt(prompt_id)
    
    def save_prompt(self, prompt_id: str, prompt_data: Dict):
        """Save or update a prompt."""
        return self._folder_manager.save_prompt(prompt_id, prompt_data)
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt by ID."""
        return self._folder_manager.delete_prompt(prompt_id)
    
    def get_recent_prompts(self, limit: int = 5) -> List[Dict]:
        """Get recent prompts sorted by last modified date."""
        return self._folder_manager.get_recent_prompts(limit)
    
    def create_new_prompt(self, name: str, description: str = "") -> str:
        """Create a new prompt and return its ID."""
        return self._folder_manager.create_new_prompt(name, description)
    
    def add_version(self, prompt_id: str, version: str, content: Dict):
        """Add a new version to a prompt."""
        return self._folder_manager.add_version(prompt_id, version, content) 