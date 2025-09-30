import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from promptix.enhancements.logging import setup_logging

# Set up logger for this module
logger = setup_logging()

from .loaders import PromptLoaderFactory
import yaml

def create_default_prompts_folder(prompts_dir: Path) -> Dict[str, Any]:
    """
    Create a default prompts folder structure with a sample prompt.
    
    Args:
        prompts_dir: Directory where the prompts folder structure should be created
        
    Returns:
        Dict containing the default prompts data
    """
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    # Get current timestamp
    current_time = datetime.now().isoformat()
    
    # Create welcome_prompt folder
    welcome_dir = prompts_dir / "welcome_prompt"
    welcome_dir.mkdir(exist_ok=True)
    (welcome_dir / "versions").mkdir(exist_ok=True)
    
    # Create config.yaml
    config_data = {
        "metadata": {
            "name": "Welcome to Promptix",
            "description": "A sample prompt to help you get started with Promptix",
            "author": "Promptix",
            "version": "1.0.0",
            "created_at": current_time,
            "last_modified": current_time,
            "last_modified_by": "Promptix"
        },
        "schema": {
            "type": "object",
            "required": ["query"],
            "optional": ["context"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The user's question or request"
                },
                "context": {
                    "type": "string",
                    "description": "Optional additional context for the query"
                }
            },
            "additionalProperties": False
        },
        "config": {
            "model": "gpt-4o",
            "provider": "openai",
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 1.0
        }
    }
    
    # Write config.yaml if it doesn't already exist
    config_path = welcome_dir / "config.yaml"
    try:
        with config_path.open("x", encoding="utf-8") as f:
            yaml.dump(config_data, f, sort_keys=False, allow_unicode=True)
    except FileExistsError:
        logger.warning("config.yaml already exists in %s; skipping scaffold write", welcome_dir)
    
    # Create current.md
    template_content = "You are a helpful AI assistant that provides clear and concise responses to {{query}}."
    if 'context' in template_content:
        template_content += " Use the following context if provided: {{context}}"
    
    current_path = welcome_dir / "current.md"
    try:
        with current_path.open("x", encoding="utf-8") as f:
            f.write(template_content)
    except FileExistsError:
        logger.warning("current.md already exists in %s; skipping scaffold write", welcome_dir)
    
    # Create v1.md
    version_path = welcome_dir / "versions" / "v1.md"
    try:
        with version_path.open("x", encoding="utf-8") as f:
            f.write(template_content)
    except FileExistsError:
        logger.warning("versions/v1.md already exists in %s; skipping scaffold write", welcome_dir)
    logger.info(f"Created new prompts folder structure at {prompts_dir} with a sample prompt")
    
    # Return equivalent structure for backward compatibility
    return {
        "schema": 1.0,
        "welcome_prompt": {
            "name": "Welcome to Promptix",
            "description": "A sample prompt to help you get started with Promptix",
            "versions": {
                "v1": {
                    "is_live": True,
                    "config": {
                        "system_instruction": template_content,
                        "model": "gpt-4o",
                        "provider": "openai",
                        "temperature": 0.7,
                        "max_tokens": 1024,
                        "top_p": 1.0
                    },
                    "created_at": current_time,
                    "metadata": config_data["metadata"],
                    "schema": config_data["schema"]
                }
            },
            "created_at": current_time,
            "last_modified": current_time
        }
    }

def create_default_prompts_file(file_path: Path) -> Dict[str, Any]:
    """
    Create a default prompts file with a sample prompt.
    
    Args:
        file_path: Path where the prompts file should be created
        
    Returns:
        Dict containing the default prompts data
    """
    # Create the file if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure the file has a valid extension (default to .yaml if none)
    original_path = file_path
    if file_path.suffix.lower() not in ['.yaml', '.yml', '.json']:
        # If no valid extension is provided, prefer YAML
        file_path = file_path.with_suffix('.yaml')
        logger.info(f"No valid extension provided, defaulting to YAML format: {file_path}")
    
    # Get current timestamp
    current_time = datetime.now().isoformat()
    
    # Create default prompts structure
    default_prompts = {
        "schema": 1.0,
        "welcome_prompt": {
            "name": "Welcome to Promptix",
            "description": "A sample prompt to help you get started with Promptix",
            "versions": {
                "v1": {
                    "is_live": True,
                    "config": {
                        "system_instruction": "You are a helpful AI assistant that provides clear and concise responses.",
                        "model": "gpt-4o",
                        "provider": "openai",
                        "temperature": 0.7,
                        "max_tokens": 1024,
                        "top_p": 1.0
                    },
                    "created_at": current_time,
                    "metadata": {
                        "created_at": current_time,
                        "author": "Promptix",
                        "last_modified": current_time,
                        "last_modified_by": "Promptix"
                    },
                    "schema": {
                        "required": ["query"],
                        "optional": ["context"],
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The user's question or request"
                            },
                            "context": {
                                "type": "string",
                                "description": "Optional additional context for the query"
                            }
                        },
                        "additionalProperties": False
                    }
                }
            },
            "created_at": current_time,
            "last_modified": current_time
        }
    }
    
    # Save the default prompts
    loader = PromptLoaderFactory.get_loader(file_path)
    loader.save(default_prompts, file_path)
    
    logger.info(f"Created new prompts file at {file_path} with a sample prompt")
    
    return default_prompts 