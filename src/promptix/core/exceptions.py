"""
Custom exception classes for Promptix.

This module provides a standardized exception hierarchy for consistent error handling
throughout the Promptix library. All custom exceptions inherit from PromptixError.
"""

from typing import Any, Dict, List, Optional, Union


class PromptixError(Exception):
    """Base exception class for all Promptix errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message


# === Template and Prompt Related Errors ===

class PromptNotFoundError(PromptixError):
    """Raised when a requested prompt template is not found."""
    
    def __init__(self, prompt_name: str, available_prompts: Optional[List[str]] = None):
        message = f"Prompt template '{prompt_name}' not found"
        details = {
            "prompt_name": prompt_name,
            "available_prompts": available_prompts or []
        }
        super().__init__(message, details)


class VersionNotFoundError(PromptixError):
    """Raised when a requested prompt version is not found."""
    
    def __init__(self, version: str, prompt_name: str, available_versions: Optional[List[str]] = None):
        message = f"Version '{version}' not found for prompt '{prompt_name}'"
        details = {
            "version": version,
            "prompt_name": prompt_name,
            "available_versions": available_versions or []
        }
        super().__init__(message, details)


class NoLiveVersionError(PromptixError):
    """Raised when no live version is found for a prompt."""
    
    def __init__(self, prompt_name: str, available_versions: Optional[List[str]] = None):
        message = f"No live version found for prompt '{prompt_name}'"
        details = {
            "prompt_name": prompt_name,
            "available_versions": available_versions or []
        }
        super().__init__(message, details)


class MultipleLiveVersionsError(PromptixError):
    """Raised when multiple live versions are found for a prompt."""
    
    def __init__(self, prompt_name: str, live_versions: List[str]):
        message = f"Multiple live versions found for prompt '{prompt_name}': {live_versions}. Only one version can be live at a time"
        details = {
            "prompt_name": prompt_name,
            "live_versions": live_versions
        }
        super().__init__(message, details)


class TemplateRenderError(PromptixError):
    """Raised when template rendering fails."""
    
    def __init__(self, prompt_name: str, template_error: str, variables: Optional[Dict[str, Any]] = None):
        message = f"Error rendering template for '{prompt_name}': {template_error}"
        details = {
            "prompt_name": prompt_name,
            "template_error": template_error,
            "variables": variables or {}
        }
        super().__init__(message, details)


# === Validation Errors ===

class ValidationError(PromptixError):
    """Base class for validation-related errors."""
    pass


class VariableValidationError(ValidationError):
    """Raised when variable validation fails."""
    
    def __init__(self, prompt_name: str, variable_name: str, error_message: str, 
                 provided_value: Any = None, expected_type: Optional[str] = None):
        message = f"Variable '{variable_name}' validation failed for prompt '{prompt_name}': {error_message}"
        details = {
            "prompt_name": prompt_name,
            "variable_name": variable_name,
            "provided_value": provided_value,
            "expected_type": expected_type,
            "error_message": error_message
        }
        super().__init__(message, details)


class RequiredVariableError(ValidationError):
    """Raised when required variables are missing."""
    
    def __init__(self, prompt_name: str, missing_variables: List[str], 
                 provided_variables: Optional[List[str]] = None):
        message = f"Prompt '{prompt_name}' is missing required variables: {', '.join(missing_variables)}"
        details = {
            "prompt_name": prompt_name,
            "missing_variables": missing_variables,
            "provided_variables": provided_variables or []
        }
        super().__init__(message, details)


class SchemaValidationError(ValidationError):
    """Raised when schema validation fails."""
    
    def __init__(self, prompt_name: str, schema_errors: List[str]):
        message = f"Schema validation failed for prompt '{prompt_name}': {'; '.join(schema_errors)}"
        details = {
            "prompt_name": prompt_name,
            "schema_errors": schema_errors
        }
        super().__init__(message, details)


# === Configuration and Adapter Errors ===

class ConfigurationError(PromptixError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, config_issue: str, config_path: Optional[str] = None):
        message = f"Configuration error: {config_issue}"
        details = {"config_issue": config_issue}
        if config_path:
            details["config_path"] = config_path
        super().__init__(message, details)


class AdapterError(PromptixError):
    """Base class for adapter-related errors."""
    pass


class UnsupportedClientError(AdapterError):
    """Raised when an unsupported client is requested."""
    
    def __init__(self, client_name: str, available_clients: List[str]):
        message = f"Unsupported client: {client_name}. Available clients: {available_clients}"
        details = {
            "client_name": client_name,
            "available_clients": available_clients
        }
        super().__init__(message, details)


class AdapterConfigurationError(AdapterError):
    """Raised when adapter configuration fails."""
    
    def __init__(self, client_name: str, configuration_error: str):
        message = f"Adapter configuration failed for client '{client_name}': {configuration_error}"
        details = {
            "client_name": client_name,
            "configuration_error": configuration_error
        }
        super().__init__(message, details)


# === Storage and File Errors ===

class StorageError(PromptixError):
    """Base class for storage-related errors."""
    pass


class StorageFileNotFoundError(StorageError):
    """Raised when a required file is not found."""
    
    def __init__(self, file_path: str, file_type: str = "file"):
        message = f"{file_type.capitalize()} not found: {file_path}"
        details = {
            "file_path": file_path,
            "file_type": file_type
        }
        super().__init__(message, details)


class UnsupportedFormatError(StorageError):
    """Raised when an unsupported file format is encountered."""
    
    def __init__(self, file_path: str, unsupported_format: str, supported_formats: List[str]):
        message = f"Unsupported format '{unsupported_format}' for file: {file_path}"
        details = {
            "file_path": file_path,
            "unsupported_format": unsupported_format,
            "supported_formats": supported_formats
        }
        super().__init__(message, details)


class FileParsingError(StorageError):
    """Raised when file parsing fails."""
    
    def __init__(self, file_path: str, parsing_error: str):
        message = f"Error parsing file '{file_path}': {parsing_error}"
        details = {
            "file_path": file_path,
            "parsing_error": parsing_error
        }
        super().__init__(message, details)


# === Memory and Message Errors ===

class PromptixMemoryError(PromptixError):
    """Base class for memory/message-related errors."""
    pass


class InvalidMemoryFormatError(PromptixMemoryError):
    """Raised when memory/message format is invalid."""
    
    def __init__(self, error_description: str, invalid_message: Optional[Dict[str, Any]] = None):
        message = f"Invalid memory format: {error_description}"
        details = {
            "error_description": error_description,
            "invalid_message": invalid_message
        }
        super().__init__(message, details)


# === Tool-related Errors ===

class ToolError(PromptixError):
    """Base class for tool-related errors."""
    pass


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not found."""
    
    def __init__(self, tool_name: str, available_tools: Optional[List[str]] = None):
        message = f"Tool '{tool_name}' not found in configuration"
        details = {
            "tool_name": tool_name,
            "available_tools": available_tools or []
        }
        super().__init__(message, details)


class ToolProcessingError(ToolError):
    """Raised when tool processing fails."""
    
    def __init__(self, tool_name: str, processing_error: str):
        message = f"Error processing tool '{tool_name}': {processing_error}"
        details = {
            "tool_name": tool_name,
            "processing_error": processing_error
        }
        super().__init__(message, details)


# === Dependency Injection Errors ===

class DependencyError(PromptixError):
    """Base class for dependency injection errors."""
    pass


class MissingDependencyError(DependencyError):
    """Raised when a required dependency is not provided."""
    
    def __init__(self, dependency_name: str, component: str):
        message = f"Missing required dependency '{dependency_name}' for component '{component}'"
        details = {
            "dependency_name": dependency_name,
            "component": component
        }
        super().__init__(message, details)


class InvalidDependencyError(DependencyError):
    """Raised when a dependency does not meet requirements."""
    
    def __init__(self, dependency_name: str, expected_type: str, actual_type: str):
        message = f"Invalid dependency '{dependency_name}': expected {expected_type}, got {actual_type}"
        details = {
            "dependency_name": dependency_name,
            "expected_type": expected_type,
            "actual_type": actual_type
        }
        super().__init__(message, details)


# Convenience function to create appropriate exceptions
def create_validation_error(prompt_name: str, field: str, value: Any, 
                          expected_type: Optional[str] = None, 
                          enum_values: Optional[List[Any]] = None) -> ValidationError:
    """Create appropriate validation error based on the validation failure type."""
    if enum_values and value not in enum_values:
        return VariableValidationError(
            prompt_name=prompt_name,
            variable_name=field,
            error_message=f"must be one of {enum_values}",
            provided_value=value,
            expected_type=f"enum: {enum_values}"
        )
    elif expected_type:
        return VariableValidationError(
            prompt_name=prompt_name,
            variable_name=field,
            error_message=f"must be of type {expected_type}",
            provided_value=value,
            expected_type=expected_type
        )
    else:
        return VariableValidationError(
            prompt_name=prompt_name,
            variable_name=field,
            error_message="validation failed",
            provided_value=value
        )
