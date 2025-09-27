"""
PromptLoader component for loading prompts from workspace structure.

This component provides a unified interface for loading prompts from the
new prompts/ directory structure with comprehensive error handling.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..exceptions import StorageError, PromptNotFoundError
from ..config import config


class PromptLoader:
    """Handles loading and managing prompts from workspace structure."""
    
    def __init__(self, logger=None):
        """Initialize the prompt loader.
        
        Args:
            logger: Optional logger instance for dependency injection.
        """
        self._prompts: Dict[str, Any] = {}
        self._logger = logger
        self._loaded = False
    
    def load_prompts(self, force_reload: bool = False) -> Dict[str, Any]:
        """Load prompts from workspace structure.
        
        Args:
            force_reload: If True, reload prompts even if already loaded.
            
        Returns:
            Dictionary containing all loaded prompts.
            
        Raises:
            StorageError: If loading fails.
        """
        if self._loaded and not force_reload:
            return self._prompts
            
        try:
            # Get or create workspace path
            workspace_path = config.get_prompts_workspace_path()
            
            if not config.has_prompts_workspace():
                # Create default workspace with a sample agent
                if self._logger:
                    self._logger.info(f"Creating new workspace at {workspace_path}")
                config.create_default_workspace()
                self._create_sample_agent(workspace_path)
            
            # Load all agents from workspace directly
            self._prompts = self._load_all_agents(workspace_path)
            
            if self._logger:
                agent_count = len(self._prompts)
                self._logger.info(f"Successfully loaded {agent_count} agents from workspace {workspace_path}")
            
            self._loaded = True
            return self._prompts

        except Exception as e:
            raise StorageError("Failed to load prompts from workspace", {"cause": str(e)}) from e
    
    def get_prompts(self) -> Dict[str, Any]:
        """Get the loaded prompts.
        
        Returns:
            Dictionary containing all loaded prompts.
        """
        if not self._loaded:
            return self.load_prompts()
        return self._prompts
    
    def get_prompt_data(self, prompt_template: str) -> Dict[str, Any]:
        """Get data for a specific prompt template.
        
        Args:
            prompt_template: Name of the prompt template.
            
        Returns:
            Dictionary containing the prompt data.
            
        Raises:
            PromptNotFoundError: If prompt is not found.
        """
        prompts = self.get_prompts()
        if prompt_template not in prompts:
            available_prompts = list(prompts.keys())
            raise PromptNotFoundError(prompt_template, available_prompts)
        return prompts[prompt_template]
    
    def list_agents(self) -> List[str]:
        """List all available agent names.
        
        Returns:
            List of agent names.
        """
        workspace_path = config.get_prompts_workspace_path()
        if not workspace_path.exists():
            return []
            
        return [
            d.name for d in workspace_path.iterdir() 
            if d.is_dir() and not d.name.startswith('.')
        ]
    
    def is_loaded(self) -> bool:
        """Check if prompts have been loaded.
        
        Returns:
            True if prompts are loaded, False otherwise.
        """
        return self._loaded
    
    def reload_prompts(self) -> Dict[str, Any]:
        """Force reload prompts from storage.
        
        Returns:
            Dictionary containing all reloaded prompts.
            
        Raises:
            StorageError: If reloading fails.
        """
        return self.load_prompts(force_reload=True)
    
    def _create_sample_agent(self, workspace_path: Path) -> None:
        """Create a sample agent to get users started.
        
        Args:
            workspace_path: Path to the workspace directory
        """
        sample_agent_dir = workspace_path / "simple_chat"
        sample_agent_dir.mkdir(exist_ok=True)
        
        # Create config.yaml
        config_content = """# Agent configuration
metadata:
  name: "Simple Chat"
  description: "A basic conversational agent"
  author: "Promptix"
  version: "1.0.0"

# Schema for variables
schema:
  type: "object"
  properties:
    personality:
      type: "string"
      description: "The personality type of the assistant"
      default: "helpful"
    domain:
      type: "string"
      description: "Domain of expertise"
      default: "general"
  additionalProperties: true

# Configuration for the prompt
config:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 1000
"""
        
        config_path = sample_agent_dir / "config.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # Create current.md
        prompt_content = """You are a {{personality}} assistant specialized in {{domain}}.

Your role is to provide helpful, accurate, and engaging responses to user questions and requests. Always maintain a professional and friendly tone while adapting to the user's needs.

Key guidelines:
- Be concise but thorough in your explanations
- Ask clarifying questions when needed
- Provide examples when helpful
- Stay focused on the {{domain}} domain when specified

How can I help you today?"""
        
        current_path = sample_agent_dir / "current.md"
        with open(current_path, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        
        # Create versions directory (optional)
        versions_dir = sample_agent_dir / "versions"
        versions_dir.mkdir(exist_ok=True)
        
        if self._logger:
            self._logger.info(f"Created sample agent 'simple_chat' at {sample_agent_dir}")
    
    def _load_all_agents(self, workspace_path: Path) -> Dict[str, Any]:
        """
        Load all agents from the workspace.
        
        Args:
            workspace_path: Path to the prompts/ directory
            
        Returns:
            Dictionary mapping agent names to their complete data structure
        """
        agents = {}
        
        if not workspace_path.exists():
            return agents
            
        for agent_dir in workspace_path.iterdir():
            if agent_dir.is_dir() and not agent_dir.name.startswith('.'):
                try:
                    agent_data = self._load_agent(agent_dir)
                    agents[agent_dir.name] = agent_data
                except Exception as e:
                    if self._logger:
                        self._logger.warning(f"Failed to load agent {agent_dir.name}: {e}")
                    continue
                    
        return agents
    
    def _load_agent(self, agent_dir: Path) -> Dict[str, Any]:
        """
        Load agent data from directory structure.
        
        Args:
            agent_dir: Path to agent directory
            
        Returns:
            Agent data in V1-compatible format with versions structure
        """
        config_path = agent_dir / "config.yaml"
        current_path = agent_dir / "current.md"
        versions_dir = agent_dir / "versions"
        
        # Load configuration
        config_data = {}
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
            except Exception as e:
                raise StorageError(
                    f"Failed to load config for agent {agent_dir.name}",
                    {"config_path": str(config_path), "error": str(e)}
                )
        
        # Load current prompt
        current_prompt = ""
        if current_path.exists():
            try:
                with open(current_path, 'r', encoding='utf-8') as f:
                    current_prompt = f.read().strip()
            except Exception as e:
                raise StorageError(
                    f"Failed to load current prompt for agent {agent_dir.name}",
                    {"current_path": str(current_path), "error": str(e)}
                )
        
        # Load version history
        versions = {}
        if versions_dir.exists():
            versions = self._load_versions(versions_dir, config_data)
        
        # Create current version if we have a prompt
        if current_prompt and 'current' not in versions:
            config_section = config_data.get('config') or {}
            if not isinstance(config_section, dict):
                config_section = {}
            schema_section = config_data.get('schema') or {}
            if not isinstance(schema_section, dict):
                schema_section = {}
            tools_config_section = config_data.get('tools_config') or {}
            if not isinstance(tools_config_section, dict):
                tools_config_section = {}
                
            versions['current'] = {
                'config': {
                    'system_instruction': current_prompt,
                    **config_section,
                },
                'schema': schema_section,
                'tools_config': tools_config_section,
                'is_live': True,
            }
        
        # Ensure at least one version is live
        live_versions = [k for k, v in versions.items() if v.get('is_live', False)]
        if not live_versions and versions:
            # Make 'current' live if it exists, otherwise make the first version live
            live_key = 'current' if 'current' in versions else list(versions.keys())[0]
            versions[live_key]['is_live'] = True
        
        # Return V1-compatible structure
        return {
            'versions': versions,
            'metadata': config_data.get('metadata', {})
        }
    
    def _load_versions(self, versions_dir: Path, base_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Load version history from versions/ directory.
        
        Args:
            versions_dir: Path to versions directory
            base_config: Base configuration to inherit schema and config from
            
        Returns:
            Dictionary of version data
        """
        versions = {}
        base_config = base_config or {}
        
        for version_file in versions_dir.glob("*.md"):
            version_name = version_file.stem
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                # Inherit configuration from base config
                config_section = base_config.get('config', {}).copy()
                config_section['system_instruction'] = content
                
                versions[version_name] = {
                    'config': config_section,
                    'schema': base_config.get('schema', {}),  # Inherit schema from base config
                    'tools_config': base_config.get('tools_config', {}),  # Inherit tools_config from base config
                    'is_live': False  # Historical versions are not live
                }
            except Exception as e:
                if self._logger:
                    self._logger.warning(f"Failed to load version {version_name}: {e}")
                continue
                
        return versions