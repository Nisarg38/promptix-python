import json
from pathlib import Path
from typing import Dict, Any

class PromptManager:
    """Manages prompts from local storage."""
    
    def __init__(self):
        self.prompts: Dict[str, Any] = {}
        self._load_prompts()
    
    def _load_prompts(self) -> None:
        """Load prompts from local prompts.json file."""
        try:
            prompts_file = Path("prompts.json")
            if prompts_file.exists():
                with open(prompts_file, 'r') as f:
                    self.prompts = json.load(f)
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

    def save_prompts(self) -> None:
        """Save prompts to local prompts.json file."""
        try:
            prompts_file = Path("prompts.json")
            with open(prompts_file, 'w') as f:
                json.dump(self.prompts, f, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to save prompts: {str(e)}") 