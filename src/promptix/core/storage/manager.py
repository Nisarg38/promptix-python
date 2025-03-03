import json
from pathlib import Path
from typing import Dict, Any
from .loaders import PromptLoaderFactory
from .utils import create_default_prompts_file

class PromptManager:
    """Manages prompts from local storage."""
    
    DEFAULT_FORMAT = '.yaml'  # Change default to YAML
    
    def __init__(self, format: str = None):
        self.prompts: Dict[str, Any] = {}
        self.format = format or self.DEFAULT_FORMAT
        self._load_prompts()
    
    def _get_prompt_file(self) -> Path:
        # Try YAML first (default), then JSON
        yaml_file = Path("prompts.yaml")
        yml_file = Path("prompts.yml")
        json_file = Path("prompts.json")
        
        if yaml_file.exists():
            return yaml_file
        elif yml_file.exists():
            return yml_file
        elif json_file.exists():
            return json_file
        else:
            # Create new file with preferred format
            default_file = Path(f"prompts{self.format}")
            create_default_prompts_file(default_file)
            return default_file
    
    def _load_prompts(self) -> None:
        """Load prompts from local prompts.json file."""
        try:
            prompt_file = self._get_prompt_file()
            loader = PromptLoaderFactory.get_loader(prompt_file)
            self.prompts = loader.load(prompt_file)
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
        """Save prompts to local prompts.json file."""
        try:
            prompt_file = self._get_prompt_file()
            loader = PromptLoaderFactory.get_loader(prompt_file)
            formatted_prompts = {
                prompt_id: self._format_prompt_for_storage(prompt_data)
                for prompt_id, prompt_data in self.prompts.items()
            }
            loader.save(formatted_prompts, prompt_file)
        except Exception as e:
            raise ValueError(f"Failed to save prompts: {str(e)}") 