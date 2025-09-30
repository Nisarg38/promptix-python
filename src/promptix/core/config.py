import os
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class PromptixConfig:
    """
    Centralized configuration management for Promptix.
    
    Provides a unified interface for managing:
    - File paths and storage locations
    - Environment-specific settings
    - API keys and authentication
    - Default values and overrides
    """
    
    # Default configuration values
    _defaults = {
        "prompt_file_extensions": [".yaml", ".yml"],
        "unsupported_extensions": [".json"],  # Completely unsupported now
        "default_prompt_filename": "prompts.yaml",
        "log_level": "INFO",
        "storage_format": "yaml",
        "schema_version": 1.0,
    }
    
    def __init__(self, working_directory: Optional[Union[str, Path]] = None):
        """
        Initialize configuration with optional working directory override.
        
        Args:
            working_directory: Custom working directory (defaults to current directory)
        """
        self.working_directory = Path(working_directory or os.getcwd())
        self._config_cache: Dict[str, Any] = {}
    
    def get_working_directory(self) -> Path:
        """Get the current working directory for Promptix operations."""
        return self.working_directory
    
    def set_working_directory(self, path: Union[str, Path]) -> None:
        """Set a new working directory for Promptix operations."""
        self.working_directory = Path(path)
        self._config_cache.clear()  # Clear cache when working directory changes
    
    def get_prompts_workspace_path(self) -> Path:
        """
        Get the path to the prompts workspace directory.
        
        Returns:
            Path to prompts/ directory
        """
        return self.working_directory / "prompts"
    
    def has_prompts_workspace(self) -> bool:
        """
        Check if prompts workspace directory exists.
        
        Returns:
            True if prompts/ directory exists
        """
        prompts_dir = self.get_prompts_workspace_path()
        return prompts_dir.exists() and prompts_dir.is_dir()
    
    def create_default_workspace(self) -> Path:
        """
        Create the default prompts workspace directory structure.
        
        Returns:
            Path to created prompts/ directory
        """
        prompts_dir = self.get_prompts_workspace_path()
        prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .promptix directory for workspace configuration
        promptix_config_dir = self.working_directory / ".promptix"
        promptix_config_dir.mkdir(parents=True, exist_ok=True)
        return prompts_dir
    
    def get_promptix_key(self) -> str:
        """Get the Promptix API key from environment variables."""
        return os.getenv("PROMPTIX_KEY", "")
    
    def get_log_level(self) -> str:
        """Get the logging level."""
        return os.getenv("PROMPTIX_LOG_LEVEL", self.get("log_level"))
    
    def get_storage_format(self) -> str:
        """Get the preferred storage format (yaml/json)."""
        return os.getenv("PROMPTIX_STORAGE_FORMAT", self.get("storage_format"))
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions (YAML only)."""
        return self.get("prompt_file_extensions")
    
    def get_unsupported_extensions(self) -> List[str]:
        """Get list of unsupported file extensions."""
        return self.get("unsupported_extensions")
    
    def get_schema_version(self) -> float:
        """Get the current schema version."""
        return self.get("schema_version")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # Check environment variables first (with PROMPTIX_ prefix)
        env_key = f"PROMPTIX_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value
        
        # Check defaults
        return self._defaults.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a runtime configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config_cache[key] = value
    
    def get_prompt_file_path(self) -> Optional[Path]:
        """
        Get path to legacy prompts file (backward compatibility).
        
        This method supports the legacy single-file approach for backward compatibility.
        In the new system, we prefer the workspace approach using prompts/ directory.
        
        Returns:
            Path to prompts.yaml file if it exists, None otherwise
        """
        base_dir = self.working_directory
        
        # Check for existing YAML files in the preferred order
        for ext in self.get_supported_extensions():
            file_path = base_dir / f"prompts{ext}"
            if file_path.exists():
                return file_path
        
        return None
    
    def get_default_prompt_file_path(self) -> Path:
        """Get the default path for creating a new prompts file."""
        return self.working_directory / self.get("default_prompt_filename")
    
    def check_for_unsupported_files(self) -> List[Path]:
        """Check working directory for unsupported JSON files."""
        base_dir = self.working_directory
        unsupported_files = []
        
        for ext in self.get_unsupported_extensions():
            pattern = f"prompts{ext}"
            file_path = base_dir / pattern
            if file_path.exists():
                unsupported_files.append(file_path)
        
        return unsupported_files
    
    def to_dict(self) -> Dict[str, Any]:
        """Export current configuration as a dictionary."""
        config = self._defaults.copy()
        config.update(self._config_cache)
        config.update({
            "working_directory": str(self.working_directory),
            "promptix_key": self.get_promptix_key(),
            "log_level": self.get_log_level(),
            "storage_format": self.get_storage_format(),
        })
        return config

# Global configuration instance
config = PromptixConfig()

# Backwards compatibility
class Config:
    """Legacy Config class for backwards compatibility."""
    
    @classmethod
    def get_promptix_key(cls) -> str:
        """Get the Promptix key from environment variables."""
        return config.get_promptix_key()
    