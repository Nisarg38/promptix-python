"""
TemplateRenderer component for rendering templates with Jinja2.

This component handles rendering of prompt templates using Jinja2,
including variable substitution and template processing.
"""

from typing import Any, Dict, Optional, List, Union
from jinja2 import BaseLoader, Environment, TemplateError
from ..exceptions import TemplateRenderError


class TemplateRenderer:
    """Handles template rendering with Jinja2."""
    
    def __init__(self, logger: Optional[Any] = None) -> None:
        """Initialize the template renderer.
        
        Args:
            logger: Optional logger instance for dependency injection.
        """
        self._jinja_env = Environment(
            loader=BaseLoader(),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._logger = logger
    
    def render_template(
        self, 
        template_text: str, 
        variables: Dict[str, Any], 
        prompt_name: str = "unknown"
    ) -> str:
        """Render a template with the provided variables.
        
        Args:
            template_text: The template text to render.
            variables: Variables to substitute in the template.
            prompt_name: Name of the prompt for error reporting.
            
        Returns:
            The rendered template as a string.
            
        Raises:
            TemplateRenderError: If template rendering fails.
        """
        try:
            template_obj = self._jinja_env.from_string(template_text)
            result = template_obj.render(**variables)
            
            # Convert escaped newlines (\n) to actual line breaks
            result = result.replace("\\n", "\n")
            
            return result
            
        except TemplateError as e:
            raise TemplateRenderError(
                prompt_name=prompt_name,
                template_error=str(e),
                variables=variables
            )
        except Exception as e:
            # Catch any other rendering errors
            raise TemplateRenderError(
                prompt_name=prompt_name,
                template_error=f"Unexpected error: {str(e)}",
                variables=variables
            )
    
    def render_tools_template(
        self, 
        tools_template: str, 
        variables: Dict[str, Any],
        available_tools: Dict[str, Any],
        prompt_name: str = "unknown"
    ) -> Any:
        """Render a tools template and parse the result.
        
        Args:
            tools_template: The tools template to render.
            variables: Variables available to the template.
            available_tools: Available tools configuration.
            prompt_name: Name of the prompt for error reporting.
            
        Returns:
            Parsed template result (typically a list or dict).
            
        Raises:
            TemplateRenderError: If template rendering or parsing fails.
        """
        try:
            # Make a copy of variables to avoid modifying the original
            template_vars = dict(variables)
            
            # Add the tools configuration to the template variables
            template_vars['tools'] = available_tools
            
            # Render the template with the variables
            template = self._jinja_env.from_string(tools_template)
            rendered_template = template.render(**template_vars)
            
            # Skip empty template output
            if not rendered_template.strip():
                return None
                
            # Parse the rendered template (assuming it returns JSON-like string)
            import json
            try:
                return json.loads(rendered_template)
            except json.JSONDecodeError as json_error:
                raise TemplateRenderError(
                    prompt_name=prompt_name,
                    template_error=f"Tools template rendered invalid JSON: {str(json_error)}",
                    variables=template_vars
                )
                
        except TemplateError as e:
            raise TemplateRenderError(
                prompt_name=prompt_name,
                template_error=f"Tools template rendering failed: {str(e)}",
                variables=variables
            )
        except Exception as e:
            raise TemplateRenderError(
                prompt_name=prompt_name,
                template_error=f"Unexpected error in tools template: {str(e)}",
                variables=variables
            )
    
    def validate_template(self, template_text: str) -> bool:
        """Validate that a template is syntactically correct.
        
        Args:
            template_text: The template text to validate.
            
        Returns:
            True if the template is valid, False otherwise.
        """
        try:
            self._jinja_env.from_string(template_text)
            return True
        except TemplateError:
            return False
        except Exception:
            return False
