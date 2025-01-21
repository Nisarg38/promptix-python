import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, List, Union
from jinja2 import BaseLoader, Environment, TemplateError
from ..enhancements.logging import setup_logging


class Promptix:
    """Main class for managing and using prompts with schema validation and template rendering."""
    
    _prompts: Dict[str, Any] = {}
    _jinja_env = Environment(loader=BaseLoader())
    _logger = setup_logging()
    
    @classmethod
    def _load_prompts(cls) -> None:
        """Load prompts from local prompts.json file."""
        try:
            prompts_file = Path("prompts.json")
            if prompts_file.exists():
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    cls._prompts = json.load(f)
            else:
                cls._logger.warning("No prompts.json file found; _prompts will be empty.")
        except Exception as e:
            raise ValueError(f"Failed to load prompts: {str(e)}")
    
    @classmethod
    def _validate_variables(
        cls, 
        schema: Dict[str, Any], 
        user_vars: Dict[str, Any],
        template_name: str
    ) -> None:
        """
        Validate user variables against the prompt's schema:
        1. Check required variables are present.
        2. (Optional) Check that each variable matches the expected type or enumeration.
        """
        required = schema.get("required", [])
        optional = schema.get("optional", [])
        types_dict = schema.get("types", {})

        # --- 1) Check required variables ---
        missing_required = [r for r in required if r not in user_vars]
        if missing_required:
            raise ValueError(
                f"Prompt '{template_name}' is missing required variables: {', '.join(missing_required)}"
            )

        # --- 2) Check for unknown variables (optional) ---
        # If you want to strictly disallow extra variables not in required/optional, uncomment below:
        # allowed_vars = set(required + optional)
        # unknown_vars = [k for k in user_vars if k not in allowed_vars]
        # if unknown_vars:
        #     raise ValueError(
        #         f"Prompt '{template_name}' got unknown variables: {', '.join(unknown_vars)}"
        #     )
        
        # --- 3) Basic type checking / enumeration checks ---
        # The "types" block can define:
        #   - a list of valid strings (for enumerations),
        #   - "string", "integer", "boolean", "array", "object", etc. 
        # We'll do partial checks here:
        for var_name, var_value in user_vars.items():
            if var_name not in types_dict:
                # Not specified in the schema, skip type check for now
                continue

            expected_type = types_dict[var_name]
            
            # 3.1) If it's a list, we treat it like an enum of allowed values
            if isinstance(expected_type, list):
                # user_vars[var_name] must be one of these enumerations
                if var_value not in expected_type:
                    raise ValueError(
                        f"Variable '{var_name}' must be one of {expected_type}, got '{var_value}'"
                    )
            
            # 3.2) If it's a string specifying a type name
            elif isinstance(expected_type, str):
                if expected_type == "string" and not isinstance(var_value, str):
                    raise TypeError(f"Variable '{var_name}' must be a string.")
                elif expected_type == "integer" and not isinstance(var_value, int):
                    raise TypeError(f"Variable '{var_name}' must be an integer.")
                elif expected_type == "boolean" and not isinstance(var_value, bool):
                    raise TypeError(f"Variable '{var_name}' must be a boolean.")
                elif expected_type == "array" and not isinstance(var_value, list):
                    raise TypeError(f"Variable '{var_name}' must be a list/array.")
                elif expected_type == "object" and not isinstance(var_value, dict):
                    raise TypeError(f"Variable '{var_name}' must be an object/dict.")
                # else: we ignore unrecognized type hints for now

            # 3.3) If it's something else, skip or handle as needed
            # e.g., a more complex structure or nested checks (not implemented here)
    
    @classmethod
    def _find_live_version(cls, versions: Dict[str, Any]) -> Optional[str]:
        """Find the 'latest' live version based on 'last_modified' or version naming."""
        # Filter only versions where is_live == True
        live_versions = {k: v for k, v in versions.items() if v.get("is_live", False)}
        if not live_versions:
            return None
        
        # Strategy: pick the version with the largest "last_modified" timestamp
        # (Alternate: pick the lexicographically largest version name, etc.)
        # We'll parse the "last_modified" as an ISO string if possible.
        def parse_iso(dt_str: str) -> float:
            # Convert "YYYY-MM-DDTHH:MM:SS" into a float (timestamp) for easy comparison
            import datetime
            try:
                return datetime.datetime.fromisoformat(dt_str).timestamp()
            except Exception:
                # fallback if parse fails
                return 0.0

        live_versions_list = list(live_versions.items())
        live_versions_list.sort(
            key=lambda x: parse_iso(x[1].get("last_modified", "1970-01-01T00:00:00")), 
            reverse=True
        )
        # Return the key of the version with the newest last_modified
        return live_versions_list[0][0]  # (version_key, version_data)
    
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
            ValueError: If the prompt template is not found or required variables are missing
            TypeError: If a variable doesn't match the schema type
        """
        if not cls._prompts:
            cls._load_prompts()
        
        if prompt_template not in cls._prompts:
            raise ValueError(f"Prompt template '{prompt_template}' not found in prompts.json.")
        
        prompt_data = cls._prompts[prompt_template]
        versions = prompt_data.get("versions", {})
        
        # --- 1) Determine which version to use ---
        version_data = None
        if version:
            # Use explicitly requested version
            if version not in versions:
                raise ValueError(
                    f"Version '{version}' not found for prompt '{prompt_template}'."
                )
            version_data = versions[version]
        else:
            # Find the "latest" live version
            live_version_key = cls._find_live_version(versions)
            if not live_version_key:
                raise ValueError(
                    f"No live version found for prompt '{prompt_template}'."
                )
            version_data = versions[live_version_key]
        
        if not version_data:
            raise ValueError(f"No valid version data found for prompt '{prompt_template}'.")
        
        template_text = version_data.get("system_message")
        if not template_text:
            raise ValueError(
                f"Version data for '{prompt_template}' does not contain 'system_message'."
            )
        
        # --- 2) Validate variables against schema ---
        schema = version_data.get("schema", {})
        cls._validate_variables(schema, variables, prompt_template)
        
        # --- 3) Render with Jinja2 to handle conditionals, loops, etc. ---
        try:
            template_obj = cls._jinja_env.from_string(template_text)
            result = template_obj.render(**variables)
        except TemplateError as e:
            raise ValueError(f"Error rendering template for '{prompt_template}': {str(e)}")

        return result
