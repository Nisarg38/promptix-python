"""
Folder-based prompt manager for Studio.

This module provides a PromptManager that works with the folder-based prompt structure
instead of a single YAML file.
"""

import os
import yaml
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from promptix.core.storage.utils import create_default_prompts_folder
from promptix.core.config import config
import traceback


class FolderBasedPromptManager:
    """Manages prompts using folder-based structure for Studio."""
    
    def __init__(self) -> None:
        # Get the prompts directory from configuration
        self.prompts_dir = self._get_prompts_directory()
        self._ensure_prompts_directory_exists()
    
    def _get_prompts_directory(self) -> Path:
        """Get the prompts directory path."""
        # Look for existing prompts directory first
        base_dir = config.working_directory
        prompts_dir = base_dir / "prompts"
        
        if prompts_dir.exists():
            return prompts_dir
        
        # Check if legacy prompts.yaml exists
        legacy_yaml = config.get_prompt_file_path()
        if legacy_yaml and legacy_yaml.exists():
            # Use the same directory as the YAML file
            return legacy_yaml.parent / "prompts"
        
        # Default to prompts/ in current directory
        return base_dir / "prompts"
    
    def _ensure_prompts_directory_exists(self) -> None:
        """Ensure the prompts directory exists with at least one sample prompt."""
        if not self.prompts_dir.exists() or not any(self.prompts_dir.iterdir()):
            create_default_prompts_folder(self.prompts_dir)
    
    def load_prompts(self) -> Dict:
        """Load all prompts from folder structure."""
        try:
            prompts_data = {"schema": 1.0}
            
            if not self.prompts_dir.exists():
                return prompts_data
            
            for prompt_dir in self.prompts_dir.iterdir():
                if not prompt_dir.is_dir():
                    continue
                
                prompt_id = prompt_dir.name
                prompt_data = self._load_single_prompt(prompt_dir)
                if prompt_data:
                    prompts_data[prompt_id] = prompt_data
            
            return prompts_data
            
        except Exception as e:
            print(f"Warning: Error loading prompts: {e}")
            return {"schema": 1.0}
    
    def _load_single_prompt(self, prompt_dir: Path) -> Optional[Dict]:
        """Load a single prompt from its directory."""
        try:
            config_file = prompt_dir / "config.yaml"
            if not config_file.exists():
                return None
            
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Read current template
            current_file = prompt_dir / "current.md"
            current_template = ""
            if current_file.exists():
                with open(current_file, 'r') as f:
                    current_template = f.read()
            
            # Read versioned templates
            versions = {}
            versions_dir = prompt_dir / "versions"
            if versions_dir.exists():
                for version_file in versions_dir.glob("*.md"):
                    version_name = version_file.stem
                    with open(version_file, 'r') as f:
                        template = f.read()
                    
                    versions[version_name] = {
                        "is_live": version_name == "v1",  # Assume v1 is live
                        "config": {
                            "system_instruction": template,
                            **config_data.get("config", {})
                        },
                        "created_at": config_data.get("metadata", {}).get("created_at", datetime.now().isoformat()),
                        "metadata": config_data.get("metadata", {}),
                        "schema": config_data.get("schema", {})
                    }
            
            # Add current as live version if no versions found
            if not versions:
                versions["v1"] = {
                    "is_live": True,
                    "config": {
                        "system_instruction": current_template,
                        **config_data.get("config", {})
                    },
                    "created_at": config_data.get("metadata", {}).get("created_at", datetime.now().isoformat()),
                    "metadata": config_data.get("metadata", {}),
                    "schema": config_data.get("schema", {})
                }
            
            return {
                "name": config_data.get("metadata", {}).get("name", prompt_dir.name),
                "description": config_data.get("metadata", {}).get("description", ""),
                "versions": versions,
                "created_at": config_data.get("metadata", {}).get("created_at", datetime.now().isoformat()),
                "last_modified": config_data.get("metadata", {}).get("last_modified", datetime.now().isoformat())
            }
        
        except Exception as e:
            print(f"Warning: Error loading prompt from {prompt_dir}: {e}")
            return None
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict]:
        """Get a specific prompt by ID."""
        prompt_dir = self.prompts_dir / prompt_id
        if not prompt_dir.exists():
            return None
        return self._load_single_prompt(prompt_dir)
    
    def save_prompt(self, prompt_id: str, prompt_data: Dict):
        """Save or update a prompt."""
        try:
            prompt_dir = self.prompts_dir / prompt_id
            prompt_dir.mkdir(exist_ok=True)
            (prompt_dir / "versions").mkdir(exist_ok=True)
            
            current_time = datetime.now().isoformat()
            
            # Update last_modified
            prompt_data['last_modified'] = current_time
            if 'metadata' not in prompt_data:
                prompt_data['metadata'] = {}
            prompt_data['metadata']['last_modified'] = current_time
            
            # Prepare config data
            config_data = {
                "metadata": {
                    "name": prompt_data.get("name", prompt_id),
                    "description": prompt_data.get("description", ""),
                    "author": prompt_data.get("metadata", {}).get("author", "Promptix User"),
                    "version": "1.0.0",
                    "created_at": prompt_data.get("created_at", current_time),
                    "last_modified": current_time,
                    "last_modified_by": prompt_data.get("metadata", {}).get("last_modified_by", "Promptix User")
                }
            }
            
            # Extract schema and config from the first live version
            versions = prompt_data.get('versions', {})
            live_version = None
            for version_id, version_data in versions.items():
                if version_data.get('is_live', False):
                    live_version = version_data
                    break
            
            if live_version:
                config_data["schema"] = live_version.get("schema", {})
                version_config = live_version.get("config", {})
                config_data["config"] = {
                    "model": version_config.get("model", "gpt-4o"),
                    "provider": version_config.get("provider", "openai"),
                    "temperature": version_config.get("temperature", 0.7),
                    "max_tokens": version_config.get("max_tokens", 1024),
                    "top_p": version_config.get("top_p", 1.0)
                }
            
            # Save config.yaml
            with open(prompt_dir / "config.yaml", 'w') as f:
                yaml.dump(config_data, f, sort_keys=False, allow_unicode=True)
            
            # Save templates
            for version_id, version_data in versions.items():
                system_instruction = version_data.get("config", {}).get("system_instruction", "")
                
                # Save version file
                with open(prompt_dir / "versions" / f"{version_id}.md", 'w') as f:
                    f.write(system_instruction)
                
                # Update current.md if this is the live version
                if version_data.get('is_live', False):
                    with open(prompt_dir / "current.md", 'w') as f:
                        f.write(system_instruction)
                        
        except Exception as e:
            print(f"Error in save_prompt: {str(e)}")
            print(traceback.format_exc())
            raise
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt by ID."""
        try:
            prompt_dir = self.prompts_dir / prompt_id
            if prompt_dir.exists():
                import shutil
                shutil.rmtree(prompt_dir)
                return True
            return False
        except Exception as e:
            print(f"Error deleting prompt {prompt_id}: {e}")
            return False
    
    def get_recent_prompts(self, limit: int = 5) -> List[Dict]:
        """Get recent prompts sorted by last modified date."""
        prompts = self.load_prompts()
        # Filter out the schema key
        prompt_dict = {k: v for k, v in prompts.items() if k != "schema"}
        sorted_prompts = sorted(
            [{'id': k, **v} for k, v in prompt_dict.items()],
            key=lambda x: x.get('last_modified', ''),
            reverse=True
        )
        return sorted_prompts[:limit]
    
    def create_new_prompt(self, name: str, description: str = "") -> str:
        """Create a new prompt and return its ID."""
        # Generate unique ID based on name
        prompt_id = name.lower().replace(" ", "_").replace("-", "_")
        
        # Ensure unique ID
        counter = 1
        original_id = prompt_id
        while (self.prompts_dir / prompt_id).exists():
            prompt_id = f"{original_id}_{counter}"
            counter += 1
        
        current_time = datetime.now().isoformat()
        
        # Create prompt data structure
        prompt_data = {
            "name": name,
            "description": description,
            "versions": {
                "v1": {
                    "is_live": True,
                    "config": {
                        "system_instruction": "You are a helpful AI assistant.",
                        "model": "gpt-4o",
                        "provider": "openai",
                        "temperature": 0.7,
                        "max_tokens": 1024,
                        "top_p": 1.0
                    },
                    "created_at": current_time,
                    "metadata": {
                        "created_at": current_time,
                        "author": "Promptix User",
                        "last_modified": current_time,
                        "last_modified_by": "Promptix User"
                    },
                    "schema": {
                        "required": [],
                        "optional": [],
                        "properties": {},
                        "additionalProperties": False
                    }
                }
            },
            "created_at": current_time,
            "last_modified": current_time
        }
        
        self.save_prompt(prompt_id, prompt_data)
        return prompt_id
    
    def add_version(self, prompt_id: str, version: str, content: Dict):
        """Add a new version to a prompt."""
        try:
            prompt = self.get_prompt(prompt_id)
            if not prompt:
                raise ValueError(f"Prompt with ID {prompt_id} not found")
            
            if 'versions' not in prompt:
                prompt['versions'] = {}
            
            current_time = datetime.now().isoformat()
            
            # Ensure version has required structure
            if 'config' not in content:
                content['config'] = {
                    "system_instruction": "You are a helpful AI assistant.",
                    "model": "gpt-4o",
                    "provider": "openai",
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "top_p": 1.0
                }
            
            # Ensure metadata
            if 'metadata' not in content:
                content['metadata'] = {
                    "created_at": current_time,
                    "author": "Promptix User",
                    "last_modified": current_time,
                    "last_modified_by": "Promptix User"
                }
            
            if 'created_at' not in content:
                content['created_at'] = current_time
            
            if 'schema' not in content:
                content['schema'] = {
                    "required": [],
                    "optional": [],
                    "properties": {},
                    "additionalProperties": False
                }
            
            # Update the version
            prompt['versions'][version] = content
            prompt['last_modified'] = current_time
            
            # Save the updated prompt
            self.save_prompt(prompt_id, prompt)
            
            return True
            
        except Exception as e:
            print(f"Error in add_version: {str(e)}")
            print(traceback.format_exc())
            raise
