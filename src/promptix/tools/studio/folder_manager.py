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
from promptix.core.storage.loaders import PromptLoaderFactory
from promptix.core.config import config
from promptix.enhancements.logging import setup_logging
import traceback
import shutil


class FolderBasedPromptManager:
    """
    Manages prompts using folder-based structure for Studio.
    
    This manager automatically handles migration from legacy YAML prompt files
    to the new folder-based structure on first initialization. The migration:
    
    - Preserves all existing prompts and their versions
    - Creates a backup of the original YAML file (prompts.yaml.backup)
    - Creates a migration marker (.promptix_migrated) to prevent re-migration
    - Logs all migration activity for transparency
    
    If you have an existing prompts.yaml, it will be safely migrated to the
    prompts/ folder structure without data loss.
    """
    
    def __init__(self) -> None:
        # Set up logging
        self._logger = setup_logging()
        
        # Get the prompts directory from configuration
        self.prompts_dir = self._get_prompts_directory()
        
        # Check for and perform migration if needed
        self._migrate_yaml_to_folder_if_needed()
        
        # Ensure prompts directory exists
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
    
    def _migrate_yaml_to_folder_if_needed(self) -> None:
        """Check for existing YAML prompt files and migrate them to folder structure."""
        # Look for existing YAML prompt files
        legacy_yaml = config.get_prompt_file_path()
        
        if not legacy_yaml or not legacy_yaml.exists():
            # No legacy YAML file found, nothing to migrate
            return
            
        # Check if we already have a folder structure with prompts
        if self.prompts_dir.exists() and any(self.prompts_dir.iterdir()):
            # Folder structure already exists and has content, don't migrate
            self._logger.info(f"Folder-based prompts already exist at {self.prompts_dir}, skipping migration")
            return
        
        # Check for migration marker to avoid re-migrating
        migration_marker = legacy_yaml.parent / ".promptix_migrated"
        if migration_marker.exists():
            self._logger.info(f"YAML migration already completed (marker found)")
            return
            
        try:
            self._logger.info(f"Found legacy YAML prompt file at {legacy_yaml}")
            self._logger.info("Starting migration from YAML to folder-based structure...")
            
            # Load the existing YAML file
            loader = PromptLoaderFactory.get_loader(legacy_yaml)
            yaml_data = loader.load(legacy_yaml)
            
            # Create prompts directory
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            
            # Track migration statistics
            migrated_count = 0
            
            # Migrate each prompt from YAML to folder structure
            for prompt_id, prompt_data in yaml_data.items():
                if prompt_id == "schema":  # Skip schema metadata
                    continue
                    
                try:
                    self._migrate_single_prompt(prompt_id, prompt_data)
                    migrated_count += 1
                    self._logger.info(f"Migrated prompt: {prompt_id}")
                except Exception as e:
                    self._logger.error(f"Failed to migrate prompt {prompt_id}: {str(e)}")
            
            # Create migration marker to prevent re-migration
            # Create backup of original YAML file
            backup_file = legacy_yaml.parent / f"{legacy_yaml.name}.backup"
            shutil.copy2(legacy_yaml, backup_file)
            
            # Create migration marker to prevent re-migration (after successful backup)
            migration_marker.touch()
            self._logger.info(f"Migration completed successfully!")
            self._logger.info(f"Migrated {migrated_count} prompts to folder structure")
            self._logger.info(f"Original YAML file backed up to: {backup_file}")
            self._logger.info(f"You can safely delete {legacy_yaml} after verifying the migration")
            
        except Exception as e:
            self._logger.error(f"Failed to migrate YAML prompts: {str(e)}")
            self._logger.error("Your existing YAML file is unchanged. Please report this issue.")
            raise
    
    def _migrate_single_prompt(self, prompt_id: str, prompt_data: Dict) -> None:
        """Migrate a single prompt from YAML structure to folder structure."""
        current_time = datetime.now().isoformat()
        
        # Create directory structure
        prompt_dir = self.prompts_dir / prompt_id
        prompt_dir.mkdir(exist_ok=True)
        versions_dir = prompt_dir / "versions"
        versions_dir.mkdir(exist_ok=True)
        
        # Extract metadata
        metadata = {
            "name": prompt_data.get("name", prompt_id),
            "description": prompt_data.get("description", "Migrated from YAML"),
            "author": "Migrated User",
            "version": "1.0.0",
            "created_at": prompt_data.get("created_at", current_time),
            "last_modified": prompt_data.get("last_modified", current_time),
            "last_modified_by": "Promptix Migration"
        }
        
        # Create config.yaml structure
        config_data = {
            "metadata": metadata,
            "schema": prompt_data.get("schema", {
                "type": "object",
                "required": [],
                "optional": [],
                "properties": {},
                "additionalProperties": False
            }),
            "config": {}
        }
        
        # Process versions - handle both old and new version structures
        versions_data = prompt_data.get("versions", {})
        if not versions_data:
            # If no versions, create a default v1 from prompt data
            versions_data = {
                "v1": {
                    "is_live": True,
                    "config": prompt_data.get("config", {
                        "model": "gpt-4o",
                        "provider": "openai",
                        "temperature": 0.7,
                        "max_tokens": 1024
                    }),
                    "created_at": current_time,
                    "metadata": metadata.copy(),
                    "schema": config_data["schema"].copy()
                }
            }
            # Add system_instruction if present at prompt level
            if "system_instruction" in prompt_data:
                versions_data["v1"]["config"]["system_instruction"] = prompt_data["system_instruction"]
            elif "template" in prompt_data:
                versions_data["v1"]["config"]["system_instruction"] = prompt_data["template"]
        
        # Find live version and extract common config
        live_version = None
        for version_id, version_data in versions_data.items():
            if version_data.get("is_live", False):
                live_version = version_data
                break
        
        if live_version:
            # Extract config excluding system_instruction
            version_config = live_version.get("config", {})
            config_data["config"] = {k: v for k, v in version_config.items() if k != "system_instruction"}
        
        # Write config.yaml
        with open(prompt_dir / "config.yaml", "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, sort_keys=False, allow_unicode=True)
        
        # Write version files and current.md
        current_content = ""
        for version_id, version_data in versions_data.items():
            system_instruction = version_data.get("config", {}).get("system_instruction", "")
            
            # Write version file
            version_file = versions_dir / f"{version_id}.md"
            with open(version_file, "w", encoding="utf-8") as f:
                f.write(system_instruction)
            
            # If this is the live version, save as current.md
            if version_data.get("is_live", False):
                current_content = system_instruction
        
        # Write current.md (fallback to first version content if none marked live)
        if not current_content and versions_data:
            first_version_id = next(iter(versions_data))
            current_content = versions_data[first_version_id].get("config", {}).get("system_instruction", "")
        with open(prompt_dir / "current.md", "w", encoding="utf-8") as f:
            f.write(current_content)
    
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
                    
                    # Determine if this version is live by comparing with current.md
                    is_live = template.strip() == current_template.strip()
                    
                    versions[version_name] = {
                        "is_live": is_live,
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
                # Load the full live version config dict, preserving all fields
                config_data["config"] = version_config.copy()
                # Remove only the system_instruction key if present
                if "system_instruction" in config_data["config"]:
                    del config_data["config"]["system_instruction"]
            
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
