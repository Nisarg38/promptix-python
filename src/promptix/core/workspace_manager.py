"""
Workspace manager for creating and managing agents in the prompts/ directory structure.
"""

import os
import yaml
from pathlib import Path
from typing import Optional
from .config import config


class WorkspaceManager:
    """Manages workspace creation and agent management."""
    
    def __init__(self, working_directory: Optional[Path] = None):
        """Initialize workspace manager.
        
        Args:
            working_directory: Optional working directory override
        """
        if working_directory:
            config.set_working_directory(working_directory)
        self.workspace_path = config.get_prompts_workspace_path()
    
    def create_agent(self, agent_name: str, template: str = "basic") -> Path:
        """Create a new agent with the specified template.
        
        Args:
            agent_name: Name of the agent to create
            template: Template type (currently only 'basic' supported)
            
        Returns:
            Path to created agent directory
            
        Raises:
            ValueError: If agent already exists or name is invalid
        """
        # Validate agent name
        if not agent_name or not agent_name.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Agent name must contain only letters, numbers, hyphens, and underscores")
        
        # Create workspace if it doesn't exist
        self._ensure_workspace_exists()
        
        # Check if agent already exists
        agent_dir = self.workspace_path / agent_name
        if agent_dir.exists():
            raise ValueError(f"Agent '{agent_name}' already exists at {agent_dir}")
        
        # Create agent directory
        agent_dir.mkdir(parents=True)
        
        # Create agent files based on template
        if template == "basic":
            self._create_basic_agent(agent_dir, agent_name)
        else:
            raise ValueError(f"Unknown template: {template}")
        
        # Ensure pre-commit hook exists
        self._ensure_precommit_hook()
        
        # Show clean relative paths instead of full paths
        relative_path = f"prompts/{agent_name}"
        print(f"✅ Created agent '{agent_name}' at {relative_path}")
        print(f"📝 Edit your prompt: {relative_path}/current.md")
        print(f"⚙️  Configure variables: {relative_path}/config.yaml")
        
        return agent_dir
    
    def _ensure_workspace_exists(self) -> None:
        """Ensure workspace directory exists."""
        if not self.workspace_path.exists():
            config.create_default_workspace()
            print(f"📁 Created workspace directory: prompts/")
    
    def _create_basic_agent(self, agent_dir: Path, agent_name: str) -> None:
        """Create a basic agent template.
        
        Args:
            agent_dir: Path to agent directory
            agent_name: Name of the agent
        """
        # Create config.yaml
        config_content = {
            'metadata': {
                'name': agent_name.replace('_', ' ').replace('-', ' ').title(),
                'description': f"AI agent for {agent_name}",
                'author': "Promptix User",
                'version': "1.0.0"
            },
            'schema': {
                'type': 'object',
                'properties': {
                    'task': {
                        'type': 'string',
                        'description': 'The task to perform',
                        'default': 'general assistance'
                    },
                    'style': {
                        'type': 'string',
                        'description': 'Communication style',
                        'enum': ['professional', 'casual', 'technical', 'friendly'],
                        'default': 'professional'
                    }
                },
                'additionalProperties': True
            },
            'config': {
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 1000
            }
        }
        
        with open(agent_dir / 'config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config_content, f, default_flow_style=False, sort_keys=False)
        
        # Create current.md with basic template
        prompt_content = f"""You are a {agent_name.replace('_', ' ').replace('-', ' ')} assistant.

Your task is to help with {{{{task}}}} using a {{{{style}}}} communication style.

## Guidelines:
- Provide clear, helpful responses
- Ask clarifying questions when needed
- Stay focused on the user's needs
- Maintain a {{{{style}}}} tone throughout

## Your Role:
As a {agent_name.replace('_', ' ').replace('-', ' ')}, you should:
1. Understand the user's request thoroughly
2. Provide accurate and relevant information
3. Offer practical solutions when appropriate
4. Be responsive to feedback and adjustments

How can I help you today?"""
        
        with open(agent_dir / 'current.md', 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        
        # Create versions directory
        versions_dir = agent_dir / 'versions'
        versions_dir.mkdir()
        
        # Create initial version
        with open(versions_dir / 'v001.md', 'w', encoding='utf-8') as f:
            f.write(prompt_content)
    
    def _ensure_precommit_hook(self) -> None:
        """Ensure pre-commit hook exists for versioning."""
        git_dir = config.working_directory / '.git'
        if not git_dir.exists():
            print("⚠️  Not in a git repository. Pre-commit hook skipped.")
            return
        
        hooks_dir = git_dir / 'hooks'
        hooks_dir.mkdir(exist_ok=True)
        
        precommit_path = hooks_dir / 'pre-commit'
        
        if precommit_path.exists():
            print("📋 Pre-commit hook already exists")
            return
        
        # Create simple pre-commit hook for versioning
        hook_content = '''#!/bin/sh
# Promptix pre-commit hook for automatic versioning

# Detect available comparison tool
if command -v cmp >/dev/null 2>&1; then
    compare_cmd='cmp -s'
elif command -v diff >/dev/null 2>&1; then
    compare_cmd='diff -q'
else
    echo "Error: Neither cmp nor diff found. Cannot compare files." >&2
    exit 1
fi

# Function to create version snapshots
create_version_snapshot() {
    local agent_dir="$1"
    local current_file="$agent_dir/current.md"
    local versions_dir="$agent_dir/versions"
    
    if [ ! -f "$current_file" ]; then
        return 0
    fi
    
    # Create versions directory if it doesn't exist
    mkdir -p "$versions_dir"
    
    # Find next version number
    local max_version=0
    for version_file in "$versions_dir"/v*.md; do
        if [ -f "$version_file" ]; then
            local version_num=$(basename "$version_file" .md | sed 's/v0*//')
            if [ "$version_num" -gt "$max_version" ]; then
                max_version="$version_num"
            fi
        fi
    done
    
    # First check if current.md differs from the latest snapshot
    local should_create_version=false
    if [ "$max_version" -eq 0 ]; then
        # No existing versions, create the first one
        should_create_version=true
    else
        # Compare against the latest existing snapshot
        local latest_snapshot="$versions_dir/$(printf "v%03d.md" "$max_version")"
        if [ ! -f "$latest_snapshot" ] || ! $compare_cmd "$current_file" "$latest_snapshot" 2>/dev/null; then
            should_create_version=true
        fi
    fi
    
    # Only create new version if needed
    if [ "$should_create_version" = true ]; then
        local next_version=$((max_version + 1))
        local version_file="$versions_dir/$(printf "v%03d.md" "$next_version")"
        cp "$current_file" "$version_file"
        git add "$version_file"
        echo "📝 Created version snapshot: $version_file"
    fi
}

# Process all agents in prompts/ directory
if [ -d "prompts" ]; then
    for agent_dir in prompts/*/; do
        if [ -d "$agent_dir" ]; then
            create_version_snapshot "$agent_dir"
        fi
    done
fi

exit 0
'''
        
        with open(precommit_path, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        # Make hook executable
        precommit_path.chmod(0o755)
        
        print(f"🔄 Created pre-commit hook at .git/hooks/pre-commit")
        print("🔄 Hook will automatically create version snapshots on commit")
    
    def list_agents(self) -> list[str]:
        """List all agents in the workspace.
        
        Returns:
            List of agent names
        """
        if not self.workspace_path.exists():
            return []
        
        agents = []
        for item in self.workspace_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                agents.append(item.name)
        
        return sorted(agents)
    
    def agent_exists(self, agent_name: str) -> bool:
        """Check if an agent exists.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if agent exists
        """
        agent_dir = self.workspace_path / agent_name
        return agent_dir.exists() and agent_dir.is_dir()
