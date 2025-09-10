"""
VersionManager component for handling prompt version management.

This component is responsible for finding live versions, managing
version data, and handling version-related operations.
"""

from typing import Any, Dict, List, Optional
from ..exceptions import (
    NoLiveVersionError, 
    MultipleLiveVersionsError, 
    VersionNotFoundError
)


class VersionManager:
    """Handles prompt version management operations."""
    
    def __init__(self, logger=None):
        """Initialize the version manager.
        
        Args:
            logger: Optional logger instance for dependency injection.
        """
        self._logger = logger
    
    def find_live_version(self, versions: Dict[str, Any], prompt_name: str) -> str:
        """Find the live version from a versions dictionary.
        
        Args:
            versions: Dictionary of version data.
            prompt_name: Name of the prompt for error reporting.
            
        Returns:
            The key of the live version.
            
        Raises:
            NoLiveVersionError: If no live version is found.
            MultipleLiveVersionsError: If multiple live versions are found.
        """
        # Find versions where is_live == True
        live_versions = [k for k, v in versions.items() if v.get("is_live", False)]
        
        if not live_versions:
            available_versions = list(versions.keys())
            raise NoLiveVersionError(
                prompt_name=prompt_name,
                available_versions=available_versions
            )
            
        if len(live_versions) > 1:
            raise MultipleLiveVersionsError(
                prompt_name=prompt_name,
                live_versions=live_versions
            )
        
        return live_versions[0]
    
    def get_version_data(
        self, 
        versions: Dict[str, Any], 
        version: Optional[str], 
        prompt_name: str
    ) -> Dict[str, Any]:
        """Get version data, either specific version or live version.
        
        Args:
            versions: Dictionary of all versions.
            version: Specific version to get, or None for live version.
            prompt_name: Name of the prompt for error reporting.
            
        Returns:
            The version data dictionary.
            
        Raises:
            VersionNotFoundError: If the specified version is not found.
            NoLiveVersionError: If no live version is found when version is None.
            MultipleLiveVersionsError: If multiple live versions are found.
        """
        if version:
            # Use explicitly requested version
            if version not in versions:
                available_versions = list(versions.keys())
                raise VersionNotFoundError(
                    version=version,
                    prompt_name=prompt_name,
                    available_versions=available_versions
                )
            return versions[version]
        else:
            # Find the live version
            live_version_key = self.find_live_version(versions, prompt_name)
            return versions[live_version_key]
    
    def get_system_instruction(self, version_data: Dict[str, Any], prompt_name: str) -> str:
        """Extract system instruction from version data.
        
        Args:
            version_data: The version data dictionary.
            prompt_name: Name of the prompt for error reporting.
            
        Returns:
            The system instruction text.
            
        Raises:
            ValueError: If system instruction is not found in version data.
        """
        template_text = version_data.get("config", {}).get("system_instruction")
        if not template_text:
            raise ValueError(
                f"Version data for '{prompt_name}' does not contain 'config.system_instruction'."
            )
        return template_text
    
    def list_versions(self, versions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List all versions with their metadata.
        
        Args:
            versions: Dictionary of version data.
            
        Returns:
            List of version information dictionaries.
        """
        version_list = []
        for version_key, version_data in versions.items():
            version_info = {
                "version": version_key,
                "is_live": version_data.get("is_live", False),
                "provider": version_data.get("provider", "unknown"),
                "model": version_data.get("config", {}).get("model", "unknown"),
                "has_tools": bool(version_data.get("tools_config", {})),
                "description": version_data.get("description", "")
            }
            version_list.append(version_info)
        
        return version_list
    
    def validate_version_data(self, version_data: Dict[str, Any], prompt_name: str, version: str) -> bool:
        """Validate that version data contains required fields.
        
        Args:
            version_data: The version data to validate.
            prompt_name: Name of the prompt for error reporting.
            version: Version identifier for error reporting.
            
        Returns:
            True if version data is valid.
            
        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = [
            ("config", "Configuration section is missing"),
            ("config.system_instruction", "System instruction is missing from config"),
            ("config.model", "Model is missing from config")
        ]
        
        for field_path, error_msg in required_fields:
            if self._get_nested_field(version_data, field_path) is None:
                raise ValueError(
                    f"Invalid version data for '{prompt_name}' version '{version}': {error_msg}"
                )
        
        return True
    
    def _get_nested_field(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get a nested field from a dictionary using dot notation.
        
        Args:
            data: The dictionary to search in.
            field_path: Dot-separated path to the field (e.g., "config.model").
            
        Returns:
            The value at the field path, or None if not found.
        """
        keys = field_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
