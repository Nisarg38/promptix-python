from pathlib import Path
import json
import re
from typing import Optional, Dict, Any

class Promptix:
    _prompts: Dict[str, Any] = {}
    
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
    def _extract_variables(cls, text: str) -> set:
        """Extract variables of the form {{variable_name}} from text."""
        pattern = r'\{\{(\w+)\}\}'
        return set(re.findall(pattern, text))
    
    @classmethod
    def get_prompt(cls, prompt_template: str, version: Optional[str] = None, **variables) -> str:
        """Get a prompt by name and fill in the variables.
        
        Args:
            prompt_template (str): The name of the prompt template to use
            version (Optional[str]): Specific version to use (e.g. "v1"). If None, uses latest live version.
            **variables: Variable key-value pairs to fill in the prompt template
            
        Returns:
            str: The filled prompt template
            
        Raises:
            ValueError: If the prompt template is not found or required variables are missing
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
            template = versions[version].get("system_message")
        else:
            # Get the latest live version (default behavior)
            live_versions = {k: v for k, v in versions.items() if v.get("is_live", False)}
            if not live_versions:
                raise ValueError(f"No live version found for prompt '{prompt_template}'")
            latest_version = max(live_versions.keys())
            template = live_versions[latest_version].get("system_message")
        
        if not template:
            raise ValueError(f"No system message found for prompt '{prompt_template}'")
            
        # Extract required variables
        required_vars = cls._extract_variables(template)
        
        # Check for missing variables
        missing_vars = required_vars - set(variables.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        # Replace variables in template
        result = template
        for var, value in variables.items():
            if var in required_vars:
                result = result.replace(f"{{{{{var}}}}}", str(value))
                
        return result 