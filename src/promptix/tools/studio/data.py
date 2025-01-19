import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class PromptManager:
    def __init__(self, storage_path: str = "prompts.json"):
        self.storage_path = storage_path
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """Ensure the storage file exists"""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({}, f)
    
    def load_prompts(self) -> Dict:
        """Load all prompts from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    
    def save_prompts(self, prompts: Dict):
        """Save prompts to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(prompts, f, indent=2)
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict]:
        """Get a specific prompt by ID"""
        prompts = self.load_prompts()
        return prompts.get(prompt_id)
    
    def save_prompt(self, prompt_id: str, prompt_data: Dict):
        """Save or update a prompt"""
        prompts = self.load_prompts()
        prompt_data['last_modified'] = datetime.now().isoformat()
        prompts[prompt_id] = prompt_data
        self.save_prompts(prompts)
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt by ID"""
        prompts = self.load_prompts()
        if prompt_id in prompts:
            del prompts[prompt_id]
            self.save_prompts(prompts)
            return True
        return False
    
    def get_recent_prompts(self, limit: int = 5) -> List[Dict]:
        """Get recent prompts sorted by last modified date"""
        prompts = self.load_prompts()
        sorted_prompts = sorted(
            [{'id': k, **v} for k, v in prompts.items()],
            key=lambda x: x.get('last_modified', ''),
            reverse=True
        )
        return sorted_prompts[:limit]
    
    def create_new_prompt(self, name: str, description: str = "") -> str:
        """Create a new prompt and return its ID"""
        prompts = self.load_prompts()
        prompt_id = f"prompt_{len(prompts) + 1}"
        
        prompt_data = {
            "name": name,
            "description": description,
            "versions": {},
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }
        
        self.save_prompt(prompt_id, prompt_data)
        return prompt_id
    
    def add_version(self, prompt_id: str, version: str, content: Dict):
        """Add a new version to a prompt"""
        prompt = self.get_prompt(prompt_id)
        if prompt:
            if 'versions' not in prompt:
                prompt['versions'] = {}
            prompt['versions'][version] = {
                **content,
                'created_at': datetime.now().isoformat()
            }
            self.save_prompt(prompt_id, prompt)
            return True
        return False 