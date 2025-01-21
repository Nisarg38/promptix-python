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

    def _format_prompt_for_storage(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert multiline prompts to single line with escaped newlines."""
        formatted_data = prompt_data.copy()
        
        # Process each version's system_message
        if "versions" in formatted_data:
            for version in formatted_data["versions"].values():
                if "system_message" in version:
                    # Convert multiline to single line with \n
                    message = version["system_message"]
                    if isinstance(message, str):
                        lines = [line for line in message.strip().split("\n")]
                        version["system_message"] = "\\n".join(lines)
        
        return formatted_data

    def save_prompts(self) -> None:
        """Save prompts to local prompts.json file."""
        try:
            prompts_file = Path("prompts.json")
            
            # Always format prompts before saving
            formatted_prompts = {}
            for prompt_id, prompt_data in self.prompts.items():
                formatted_prompts[prompt_id] = self._format_prompt_for_storage(prompt_data)
            
            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(formatted_prompts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to save prompts: {str(e)}") 