import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from promptix.core.storage.loaders import PromptLoaderFactory, InvalidPromptSchemaError, UnsupportedFormatError
from promptix.core.storage.utils import create_default_prompts_file
from promptix.core.config import config
import traceback

class PromptManager:
    def __init__(self):
        # Use centralized configuration to find the correct YAML file
        # Check for unsupported JSON files first
        unsupported_files = config.check_for_unsupported_files()
        if unsupported_files:
            json_file = unsupported_files[0]
            raise UnsupportedFormatError(
                json_file,
                f"Promptix Studio no longer supports JSON format. "
                f"Please convert '{json_file}' to YAML format. "
                f"You can rename it to '{json_file.with_suffix('.yaml')}' and ensure YAML syntax is correct."
            )
        
        # Get the prompt file path from configuration
        prompt_file = config.get_prompt_file_path()
        if prompt_file is None:
            # Create default YAML file
            prompt_file = config.get_default_prompt_file_path()
            
        self.storage_path = str(prompt_file)
        self._ensure_storage_exists()
        self._loader = PromptLoaderFactory.get_loader(Path(self.storage_path))
    
    def _ensure_storage_exists(self):
        """Ensure the storage file exists"""
        if not os.path.exists(self.storage_path):
            # Create a default prompts file, preferring YAML format
            # But respect the extension if it's already specified
            create_default_prompts_file(Path(self.storage_path))
    
    def load_prompts(self) -> Dict:
        """Load all prompts from YAML storage with schema validation"""
        try:
            return self._loader.load(Path(self.storage_path))
        except InvalidPromptSchemaError as e:
            print(f"Warning: Schema validation error: {e}")
            # Return empty schema-compliant structure
            return {"schema": 1.0}
        except Exception as e:
            print(f"Warning: Error loading prompts: {e}")
            return {"schema": 1.0}
    
    def save_prompts(self, prompts: Dict):
        """Save prompts to YAML storage with validation"""
        try:
            # First validate the data
            self._loader.validate_loaded(prompts)
            # Then save in YAML format
            self._loader.save(prompts, Path(self.storage_path))
        except InvalidPromptSchemaError as e:
            print(f"Warning: Schema validation error during save: {e}")
            # Save without validation but still in YAML format
            import yaml
            with open(self.storage_path, 'w') as f:
                yaml.dump(prompts, f, sort_keys=False, allow_unicode=True)
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict]:
        """Get a specific prompt by ID"""
        prompts = self.load_prompts()
        return prompts.get(prompt_id)
    
    def save_prompt(self, prompt_id: str, prompt_data: Dict):
        """Save or update a prompt"""
        try:
            prompts = self.load_prompts()
            current_time = datetime.now().isoformat()
            prompt_data['last_modified'] = current_time
            
            # Verify the data structure before saving
            versions = prompt_data.get('versions', {})
            for version_id, version_data in versions.items():
                # Ensure config exists and has required fields
                if 'config' not in version_data:
                    version_data['config'] = {
                        "system_instruction": "You are a helpful AI assistant.",
                        "model": "gpt-4o",
                        "provider": "openai",
                        "temperature": 0.7,
                        "max_tokens": 1024,
                        "top_p": 1.0
                    }
                config = version_data['config']
                # Log verification of important fields
                # print(f"Saving version {version_id} with model: {config.get('model')} and provider: {config.get('provider')}")
                
                # Ensure specific fields are preserved
                if 'model' not in config or config['model'] is None:
                    config['model'] = "gpt-4o"
                if 'provider' not in config or config['provider'] is None:
                    config['provider'] = "openai"
            
            prompts[prompt_id] = prompt_data
            self.save_prompts(prompts)
            
            # Verify the save worked correctly
            saved_prompts = self.load_prompts()
            if prompt_id in saved_prompts:
                saved_versions = saved_prompts[prompt_id].get('versions', {})
                for version_id, version_data in saved_versions.items():
                    if 'config' in version_data:
                        config = version_data['config']
                        # print(f"Verified saved version {version_id}: model={config.get('model')}, provider={config.get('provider')}")
                    else:
                        print(f"Warning: No config found in saved version {version_id}")
                        pass
        except Exception as e:
            print(f"Error in save_prompt: {str(e)}")
            print(traceback.format_exc())
            raise
    
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
        # Filter out the schema key
        prompt_dict = {k: v for k, v in prompts.items() if k != "schema"}
        sorted_prompts = sorted(
            [{'id': k, **v} for k, v in prompt_dict.items()],
            key=lambda x: x.get('last_modified', ''),
            reverse=True
        )
        return sorted_prompts[:limit]
    
    def create_new_prompt(self, name: str, description: str = "") -> str:
        """Create a new prompt and return its ID"""
        prompts = self.load_prompts()
        # Filter out the schema key for counting
        prompt_count = sum(1 for k in prompts.keys() if k != "schema")
        prompt_id = f"prompt_{prompt_count + 1}"
        
        current_time = datetime.now().isoformat()
        
        # Create an empty prompt with proper schema structure
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
        """Add a new version to a prompt"""
        try:
            prompt = self.get_prompt(prompt_id)
            if not prompt:
                raise ValueError(f"Prompt with ID {prompt_id} not found")
                
            if 'versions' not in prompt:
                prompt['versions'] = {}
            
            # Get current timestamp    
            current_time = datetime.now().isoformat()
            
            # Debug logging
            print(f"Adding version {version} to prompt {prompt_id}")
            if 'config' in content:
                # print(f"Incoming config: model={content['config'].get('model')}, provider={content['config'].get('provider')}")
                pass
            else:
                print("No config provided in content")
                    
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
            else:
                # Ensure config has all required fields
                config = content['config']
                if 'model' not in config or config['model'] is None:
                    config['model'] = "gpt-4o"
                if 'provider' not in config or config['provider'] is None:
                    config['provider'] = "openai"
                if 'system_instruction' not in config:
                    config['system_instruction'] = "You are a helpful AI assistant."
                if 'temperature' not in config:
                    config['temperature'] = 0.7
                if 'max_tokens' not in config:
                    config['max_tokens'] = 1024
                if 'top_p' not in config:
                    config['top_p'] = 1.0
            
            # Ensure metadata is proper
            if 'metadata' not in content:
                content['metadata'] = {
                    "created_at": current_time,
                    "author": "Promptix User",
                    "last_modified": current_time,
                    "last_modified_by": "Promptix User"
                }
            else:
                content['metadata']['last_modified'] = current_time
            
            # Set created_at if it doesn't exist
            if 'created_at' not in content:
                content['created_at'] = current_time
                
            # Add schema if not present
            if 'schema' not in content:
                content['schema'] = {
                    "required": [],
                    "optional": [],
                    "properties": {},
                    "additionalProperties": False
                }
            
            # Log the final version data
            print(f"Final config: model={content['config'].get('model')}, provider={content['config'].get('provider')}")
            
            # Update the version
            prompt['versions'][version] = content
            
            # Update the prompt's last_modified
            prompt['last_modified'] = current_time
            
            # Save the updated prompt
            self.save_prompt(prompt_id, prompt)
            
            # Verify the save worked
            saved_prompt = self.get_prompt(prompt_id)
            if saved_prompt and version in saved_prompt.get('versions', {}):
                saved_config = saved_prompt['versions'][version]['config']
                # print(f"Verified saved version config: model={saved_config.get('model')}, provider={saved_config.get('provider')}")
            
            return True
        except Exception as e:
            print(f"Error in add_version: {str(e)}")
            print(traceback.format_exc())
            raise 