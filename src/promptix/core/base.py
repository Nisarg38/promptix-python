"""
Refactored Promptix main class using dependency injection and focused components.

This module provides the main Promptix class that has been refactored to use
focused components and dependency injection for better testability and modularity.
"""

from typing import Any, Dict, Optional, List
from .container import get_container
from .components import (
    PromptLoader,
    VariableValidator,
    TemplateRenderer,
    VersionManager,
    ModelConfigBuilder
)
from .exceptions import PromptNotFoundError, ConfigurationError, StorageError

class Promptix:
    """Main class for managing and using prompts with schema validation and template rendering."""
    
    def __init__(self, container=None):
        """Initialize Promptix with dependency injection.
        
        Args:
            container: Optional container for dependency injection. If None, uses global container.
        """
        self._container = container or get_container()
        
        # Get dependencies from container
        self._prompt_loader = self._container.get_typed("prompt_loader", PromptLoader)
        self._variable_validator = self._container.get_typed("variable_validator", VariableValidator)
        self._template_renderer = self._container.get_typed("template_renderer", TemplateRenderer)
        self._version_manager = self._container.get_typed("version_manager", VersionManager)
        self._model_config_builder = self._container.get_typed("model_config_builder", ModelConfigBuilder)
        self._logger = self._container.get("logger")
    
    @classmethod
    def get_prompt(cls, prompt_template: str, version: Optional[str] = None, **variables) -> str:
        """Get a prompt by name and fill in the variables.
        
        Args:
            prompt_template (str): The name of the prompt template to use
            version (Optional[str]): Specific version to use (e.g. "v1"). 
                                     If None, uses the latest live version.
            **variables: Variable key-value pairs to fill in the prompt template
            
        Returns:
            str: The rendered prompt
            
        Raises:
            PromptNotFoundError: If the prompt template is not found
            RequiredVariableError: If required variables are missing
            VariableValidationError: If a variable doesn't match the schema type
            TemplateRenderError: If template rendering fails
        """
        instance = cls()
        return instance.render_prompt(prompt_template, version, **variables)
    
    def render_prompt(self, prompt_template: str, version: Optional[str] = None, **variables) -> str:
        """Render a prompt with the provided variables.
        
        Args:
            prompt_template: The name of the prompt template to use.
            version: Specific version to use. If None, uses the live version.
            **variables: Variable key-value pairs to fill in the prompt template.
            
        Returns:
            The rendered prompt string.
            
        Raises:
            PromptNotFoundError: If the prompt template is not found.
            RequiredVariableError: If required variables are missing.
            VariableValidationError: If a variable doesn't match the schema type.
            TemplateRenderError: If template rendering fails.
        """
        # Load prompt data
        try:
            prompt_data = self._prompt_loader.get_prompt_data(prompt_template)
        except StorageError as err:
            try:
                available_prompts = list(self._prompt_loader.get_prompts().keys())
            except StorageError:
                available_prompts = []
            raise PromptNotFoundError(
                prompt_name=prompt_template,
                available_prompts=available_prompts
            ) from err
        versions = prompt_data.get("versions", {})
        
        # Get the appropriate version data
        version_data = self._version_manager.get_version_data(versions, version, prompt_template)
        
        # Get the system instruction template
        try:
            template_text = self._version_manager.get_system_instruction(version_data, prompt_template)
        except ValueError as err:
            raise ConfigurationError(
                config_issue="Missing 'config.system_instruction'",
                config_path=f"{prompt_template}.versions"
            ) from err
        
        # Validate variables against schema
        schema = version_data.get("schema", {})
        self._variable_validator.validate_variables(schema, variables, prompt_template)
        
        # Render the template
        result = self._template_renderer.render_template(template_text, variables, prompt_template)
        
        return result
    
    @classmethod
    def prepare_model_config(
        cls, 
        prompt_template: str, 
        memory: List[Dict[str, str]], 
        version: Optional[str] = None, 
        **variables
    ) -> Dict[str, Any]:
        """Prepare a model configuration ready for OpenAI chat completion API.
        
        Args:
            prompt_template (str): The name of the prompt template to use
            memory (List[Dict[str, str]]): List of previous messages in the conversation
            version (Optional[str]): Specific version to use (e.g. "v1"). 
                                     If None, uses the latest live version.
            **variables: Variable key-value pairs to fill in the prompt template
            
        Returns:
            Dict[str, Any]: Configuration dictionary for OpenAI chat completion API
            
        Raises:
            PromptNotFoundError: If the prompt template is not found
            InvalidMemoryFormatError: If memory format is invalid
            RequiredVariableError: If required variables are missing
            VariableValidationError: If a variable doesn't match the schema type
            ConfigurationError: If required configuration is missing
        """
        instance = cls()
        return instance.build_model_config(prompt_template, memory, version, **variables)
    
    def build_model_config(
        self, 
        prompt_template: str, 
        memory: List[Dict[str, str]], 
        version: Optional[str] = None,
        **variables
    ) -> Dict[str, Any]:
        """Build a model configuration.
        
        Args:
            prompt_template: The name of the prompt template to use.
            memory: List of previous messages in the conversation.
            version: Specific version to use. If None, uses the live version.
            **variables: Variable key-value pairs to fill in the prompt template.
            
        Returns:
            Configuration dictionary for the model API.
            
        Raises:
            PromptNotFoundError: If the prompt template is not found.
            InvalidMemoryFormatError: If memory format is invalid.
            RequiredVariableError: If required variables are missing.
            VariableValidationError: If a variable doesn't match the schema type.
            ConfigurationError: If required configuration is missing.
        """
        # Get the prompt data for version information
        try:
            prompt_data = self._prompt_loader.get_prompt_data(prompt_template)
        except StorageError as err:
            try:
                available_prompts = list(self._prompt_loader.get_prompts().keys())
            except StorageError:
                available_prompts = []
            raise PromptNotFoundError(
                prompt_name=prompt_template,
                available_prompts=available_prompts
            ) from err

        versions = prompt_data.get("versions", {})
        version_data = self._version_manager.get_version_data(versions, version, prompt_template)
        
        # Render the system message
        system_message = self.render_prompt(prompt_template, version, **variables)
        
        # Build the model configuration
        return self._model_config_builder.build_model_config(
            system_message=system_message,
            memory=memory,
            version_data=version_data,
            prompt_name=prompt_template
        )
    
    @staticmethod
    def builder(prompt_template: str, container=None):
        """Create a new PromptixBuilder instance for building model configurations.
        
        Args:
            prompt_template (str): The name of the prompt template to use
            container: Optional container for dependency injection
            
        Returns:
            PromptixBuilder: A builder instance for configuring the model
        """
        from .builder import PromptixBuilder
        return PromptixBuilder(prompt_template, container)
    
    def list_prompts(self) -> Dict[str, Any]:
        """List all available prompts.
        
        Returns:
            Dictionary of all available prompts.
        """
        return self._prompt_loader.get_prompts()
    
    def list_versions(self, prompt_template: str) -> List[Dict[str, Any]]:
        """List all versions for a specific prompt.
        
        Args:
            prompt_template: Name of the prompt template.
            
        Returns:
            List of version information.
            
        Raises:
            PromptNotFoundError: If the prompt template is not found.
        """
        try:
            prompt_data = self._prompt_loader.get_prompt_data(prompt_template)
        except StorageError as err:
            try:
                available_prompts = list(self._prompt_loader.get_prompts().keys())
            except StorageError:
                available_prompts = []
            raise PromptNotFoundError(
                prompt_name=prompt_template,
                available_prompts=available_prompts
            ) from err

        versions = prompt_data.get("versions", {})
        return self._version_manager.list_versions(versions)
    def validate_template(self, template_text: str) -> bool:
        """Validate that a template is syntactically correct.
        
        Args:
            template_text: The template text to validate.
            
        Returns:
            True if the template is valid, False otherwise.
        """
        return self._template_renderer.validate_template(template_text)
    
    def reload_prompts(self) -> None:
        """Force reload prompts from storage."""
        self._prompt_loader.reload_prompts()
        if self._logger:
            self._logger.info("Prompts reloaded successfully")
