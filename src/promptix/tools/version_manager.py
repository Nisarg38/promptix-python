#!/usr/bin/env python3
"""
Promptix Version Manager CLI

Command-line tool for managing prompt versions manually.
Complements the pre-commit hook with manual version operations.

Usage:
    python -m promptix.tools.version_manager [command] [args]
"""

import argparse
import os
import shutil
import sys
import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


class VersionManager:
    """Main class for version management operations"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize with workspace path"""
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        self.prompts_dir = self.workspace_path / 'prompts'
        
        if not self.prompts_dir.exists():
            raise ValueError(f"No prompts directory found at {self.prompts_dir}")
    
    def print_status(self, message: str, status: str = "info"):
        """Print colored status messages"""
        icons = {
            "info": "📝",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌",
            "version": "🔄",
            "list": "📋"
        }
        print(f"{icons.get(status, '📝')} {message}")
    
    def find_agent_dirs(self) -> List[Path]:
        """Find all agent directories in prompts/"""
        agent_dirs = []
        for item in self.prompts_dir.iterdir():
            if item.is_dir() and (item / 'config.yaml').exists():
                agent_dirs.append(item)
        return agent_dirs
    
    def load_config(self, config_path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML config file safely"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.print_status(f"Failed to load {config_path}: {e}", "error")
            return None
    
    def save_config(self, config_path: Path, config: Dict[str, Any]) -> bool:
        """Save YAML config file safely"""
        try:
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            self.print_status(f"Failed to save {config_path}: {e}", "error")
            return False
    
    def list_agents(self):
        """List all available agents with their current versions"""
        agent_dirs = self.find_agent_dirs()
        
        if not agent_dirs:
            self.print_status("No agents found in prompts directory", "warning")
            return
        
        self.print_status("Available agents:", "list")
        print()
        
        for agent_dir in sorted(agent_dirs):
            config_path = agent_dir / 'config.yaml'
            config = self.load_config(config_path)
            
            if config:
                name = config.get('metadata', {}).get('name', agent_dir.name)
                current_version = config.get('current_version', 'not set')
                description = config.get('metadata', {}).get('description', 'No description')
                
                print(f"  {name}")
                print(f"    📍 Current Version: {current_version}")
                print(f"    📖 {description}")
                print(f"    📁 Location: {agent_dir}")
                print()
    
    def list_versions(self, agent_name: str):
        """List all versions for a specific agent"""
        agent_dir = self.prompts_dir / agent_name
        
        if not agent_dir.exists():
            self.print_status(f"Agent '{agent_name}' not found", "error")
            return
        
        config_path = agent_dir / 'config.yaml'
        versions_dir = agent_dir / 'versions'
        
        config = self.load_config(config_path)
        if not config:
            return
        
        current_version = config.get('current_version', 'not set')
        
        self.print_status(f"Versions for {agent_name}:", "list")
        print(f"📍 Current Version: {current_version}")
        print()
        
        if not versions_dir.exists():
            self.print_status("No versions directory found", "warning")
            return
        
        version_files = sorted(versions_dir.glob('v*.md'), key=lambda x: x.name)
        
        if not version_files:
            self.print_status("No versions found", "warning")
            return
        
        version_info = config.get('versions', {})
        
        for version_file in version_files:
            version_name = version_file.stem
            is_current = version_name == current_version
            marker = " ← CURRENT" if is_current else ""
            
            print(f"  {version_name}{marker}")
            
            if version_name in version_info:
                info = version_info[version_name]
                created_at = info.get('created_at', 'Unknown')
                author = info.get('author', 'Unknown')
                notes = info.get('notes', 'No notes')
                
                print(f"    📅 Created: {created_at}")
                print(f"    👤 Author: {author}")
                print(f"    📝 Notes: {notes}")
            print()
    
    def get_version(self, agent_name: str, version_name: str):
        """Get the content of a specific version"""
        agent_dir = self.prompts_dir / agent_name
        version_file = agent_dir / 'versions' / f'{version_name}.md'
        
        if not version_file.exists():
            self.print_status(f"Version {version_name} not found for {agent_name}", "error")
            return
        
        try:
            with open(version_file, 'r') as f:
                content = f.read()
            
            # Remove version header if present
            content = re.sub(r'^<!-- Version.*? -->\n', '', content)
            
            self.print_status(f"Content of {agent_name}/{version_name}:", "info")
            print("-" * 50)
            print(content)
            print("-" * 50)
            
        except Exception as e:
            self.print_status(f"Failed to read version {version_name}: {e}", "error")
    
    def switch_version(self, agent_name: str, version_name: str):
        """Switch an agent to a specific version"""
        agent_dir = self.prompts_dir / agent_name
        config_path = agent_dir / 'config.yaml'
        current_md = agent_dir / 'current.md'
        version_file = agent_dir / 'versions' / f'{version_name}.md'
        
        if not agent_dir.exists():
            self.print_status(f"Agent '{agent_name}' not found", "error")
            return
        
        if not version_file.exists():
            self.print_status(f"Version {version_name} not found for {agent_name}", "error")
            return
        
        # Load config
        config = self.load_config(config_path)
        if not config:
            return
        
        try:
            # Update current_version in config
            config['current_version'] = version_name
            
            # Update metadata
            if 'metadata' not in config:
                config['metadata'] = {}
            config['metadata']['last_modified'] = datetime.now().isoformat()
            
            # Save config
            if not self.save_config(config_path, config):
                return
            
            # Deploy version to current.md
            shutil.copy2(version_file, current_md)
            
            # Remove version header from current.md
            with open(current_md, 'r') as f:
                content = f.read()
            
            content = re.sub(r'^<!-- Version.*? -->\n', '', content)
            with open(current_md, 'w') as f:
                f.write(content)
            
            self.print_status(f"Switched {agent_name} to {version_name}", "success")
            self.print_status(f"Updated current.md and config.yaml", "info")
            
        except Exception as e:
            self.print_status(f"Failed to switch version: {e}", "error")
    
    def create_version(self, agent_name: str, version_name: Optional[str] = None, notes: str = "Manually created"):
        """Create a new version from current.md"""
        agent_dir = self.prompts_dir / agent_name
        config_path = agent_dir / 'config.yaml'
        current_md = agent_dir / 'current.md'
        versions_dir = agent_dir / 'versions'
        
        if not agent_dir.exists():
            self.print_status(f"Agent '{agent_name}' not found", "error")
            return
        
        if not current_md.exists():
            self.print_status(f"No current.md found for {agent_name}", "error")
            return
        
        # Load config
        config = self.load_config(config_path)
        if not config:
            return
        
        # Create versions directory if needed
        versions_dir.mkdir(exist_ok=True)
        
        # Determine version name
        if not version_name:
            # Auto-generate next version number
            version_files = list(versions_dir.glob('v*.md'))
            version_numbers = []
            
            for file in version_files:
                match = re.match(r'v(\d+)\.md', file.name)
                if match:
                    version_numbers.append(int(match.group(1)))
            
            next_num = max(version_numbers) + 1 if version_numbers else 1
            version_name = f'v{next_num:03d}'
        
        version_file = versions_dir / f'{version_name}.md'
        
        if version_file.exists():
            self.print_status(f"Version {version_name} already exists", "error")
            return
        
        try:
            # Copy current.md to version file
            shutil.copy2(current_md, version_file)
            
            # Add version header
            with open(version_file, 'r') as f:
                content = f.read()
            
            version_header = f"<!-- Version {version_name} - Created {datetime.now().isoformat()} -->\n"
            with open(version_file, 'w') as f:
                f.write(version_header)
                f.write(content)
            
            # Update config
            if 'versions' not in config:
                config['versions'] = {}
            
            config['versions'][version_name] = {
                'created_at': datetime.now().isoformat(),
                'author': os.getenv('USER', 'unknown'),
                'notes': notes
            }
            
            # Set as current version
            config['current_version'] = version_name
            
            # Update metadata
            if 'metadata' not in config:
                config['metadata'] = {}
            config['metadata']['last_modified'] = datetime.now().isoformat()
            
            # Save config
            if self.save_config(config_path, config):
                self.print_status(f"Created version {version_name} for {agent_name}", "success")
            
        except Exception as e:
            self.print_status(f"Failed to create version: {e}", "error")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Promptix Version Manager - Manual version control for prompts"
    )
    
    parser.add_argument(
        '--workspace', '-w', 
        help="Path to promptix workspace (default: current directory)"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List agents command
    list_cmd = subparsers.add_parser('list', help='List all agents')
    
    # List versions command
    versions_cmd = subparsers.add_parser('versions', help='List versions for an agent')
    versions_cmd.add_argument('agent', help='Agent name')
    
    # Get version command
    get_cmd = subparsers.add_parser('get', help='Get content of specific version')
    get_cmd.add_argument('agent', help='Agent name')
    get_cmd.add_argument('version', help='Version name (e.g., v001)')
    
    # Switch version command
    switch_cmd = subparsers.add_parser('switch', help='Switch to specific version')
    switch_cmd.add_argument('agent', help='Agent name')
    switch_cmd.add_argument('version', help='Version name (e.g., v001)')
    
    # Create version command
    create_cmd = subparsers.add_parser('create', help='Create new version from current.md')
    create_cmd.add_argument('agent', help='Agent name')
    create_cmd.add_argument('--name', help='Version name (auto-generated if not provided)')
    create_cmd.add_argument('--notes', default='Manually created', help='Version notes')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        vm = VersionManager(args.workspace)
        
        if args.command == 'list':
            vm.list_agents()
        elif args.command == 'versions':
            vm.list_versions(args.agent)
        elif args.command == 'get':
            vm.get_version(args.agent, args.version)
        elif args.command == 'switch':
            vm.switch_version(args.agent, args.version)
        elif args.command == 'create':
            vm.create_version(args.agent, args.name, args.notes)
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
