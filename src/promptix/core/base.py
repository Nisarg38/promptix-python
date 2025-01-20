from pathlib import Path
import json
import re
from typing import Optional, Dict, Any, Union
from jinja2 import Environment, BaseLoader, TemplateError

class Promptix:
    _prompts: Dict[str, Any] = {}
    _jinja_env = Environment(loader=BaseLoader())
    
    @classmethod
    def _load_prompts(cls) -> None:
        """Load prompts from local prompts.json file."""
        try:
            prompts_file = Path("prompts.json")
            if prompts_file.exists():
                with open(prompts_file, 'r') as f:
                    cls._prompts = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load prompts: {str(e)}")
    
    @classmethod
    def _validate_schema(cls, template_schema: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Validate context against template schema."""
        if not template_schema:
            return

        # Check required fields
        required = set(template_schema.get("required", []))
        missing = required - set(context.keys())
        if missing:
            raise ValueError(f"Missing required variables: {', '.join(missing)}")

        # Validate types
        type_specs = template_schema.get("types", {})
        for var_name, var_type in type_specs.items():
            if var_name in context:
                value = context[var_name]
                if isinstance(var_type, list):  # Enum validation
                    if value not in var_type:
                        raise ValueError(f"Invalid value for {var_name}. Must be one of: {', '.join(var_type)}")
                elif var_type == "object":
                    if not isinstance(value, dict):
                        raise ValueError(f"{var_name} must be an object/dictionary")

    @classmethod
    def _render_template(cls, template: str, context: Dict[str, Any]) -> str:
        """Render template with Jinja2 for advanced template features."""
        try:
            template_obj = cls._jinja_env.from_string(template)
            return template_obj.render(**context)
        except TemplateError as e:
            raise ValueError(f"Template rendering error: {str(e)}")

    @classmethod
    def get_prompt(
        cls,
        prompt_template: str,
        context: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None,
        **variables
    ) -> str:
        """Get a prompt by name and fill in the variables.
        
        Args:
            prompt_template (str): The name of the prompt template to use
            context (Optional[Dict[str, Any]]): Context dictionary with all variables
            version (Optional[str]): Specific version to use (e.g. "v1"). If None, uses latest live version
            **variables: Legacy support for direct variable passing
            
        Returns:
            str: The rendered prompt template
            
        Raises:
            ValueError: If template not found, schema validation fails, or rendering fails
        """
        if not cls._prompts:
            cls._load_prompts()
            
        if prompt_template not in cls._prompts:
            raise ValueError(f"Prompt template '{prompt_template}' not found")
            
        prompt_data = cls._prompts[prompt_template]
        versions = prompt_data.get("versions", {})
        
        # Handle version selection
        if version:
            if version not in versions:
                raise ValueError(f"Version '{version}' not found for prompt '{prompt_template}'")
            template_data = versions[version]
        else:
            # Get the latest live version
            live_versions = {k: v for k, v in versions.items() if v.get("is_live", False)}
            if not live_versions:
                raise ValueError(f"No live version found for prompt '{prompt_template}'")
            latest_version = max(live_versions.keys())
            template_data = live_versions[latest_version]
        
        template = template_data.get("system_message")
        if not template:
            raise ValueError(f"No system message found for prompt '{prompt_template}'")

        # Merge context and variables
        merged_context = {**variables}
        if context:
            merged_context.update(context)

        # Validate against schema
        schema = prompt_data.get("schema", {})
        cls._validate_schema(schema, merged_context)
            
        # Render template with Jinja2
        return cls._render_template(template, merged_context) 