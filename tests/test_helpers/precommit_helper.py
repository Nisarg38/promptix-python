"""
Test helper for pre-commit hook functionality.

This module provides a testable interface to the pre-commit hook functions
by wrapping them in a class that can be easily mocked and tested.
"""

import os
import sys
import shutil
import subprocess
import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


class PreCommitHookTester:
    """
    Testable wrapper for pre-commit hook functionality.
    
    This class replicates the core logic from the pre-commit hook
    in a way that can be easily unit tested.
    """
    
    def __init__(self, workspace_path: Path):
        """Initialize with workspace path"""
        self.workspace_path = Path(workspace_path)
    
    def print_status(self, message: str, status: str = "info"):
        """Print status messages (can be mocked in tests)"""
        icons = {
            "info": "📝",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌",
            "version": "🔄"
        }
        print(f"{icons.get(status, '📝')} {message}")
    
    def is_hook_bypassed(self) -> bool:
        """Check if user wants to bypass the hook"""
        return os.getenv('SKIP_PROMPTIX_HOOK') == '1'
    
    def get_staged_files(self) -> List[str]:
        """Get list of staged files from git"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'], 
                capture_output=True, 
                text=True, 
                check=True,
                cwd=self.workspace_path
            )
            return [f for f in result.stdout.strip().split('\n') if f]
        except subprocess.CalledProcessError:
            return []
    
    def find_promptix_changes(self, staged_files: List[str]) -> Dict[str, List[str]]:
        """
        Find promptix-related changes, categorized by type
        Returns dict with 'current_md' and 'config_yaml' file lists
        """
        changes = {
            'current_md': [],
            'config_yaml': []
        }
        
        for file_path in staged_files:
            path = Path(file_path)
            
            # Check if it's in a prompts directory
            if len(path.parts) >= 2 and path.parts[0] == 'prompts':
                if path.name == 'current.md' and (self.workspace_path / file_path).exists():
                    changes['current_md'].append(file_path)
                elif path.name == 'config.yaml' and (self.workspace_path / file_path).exists():
                    changes['config_yaml'].append(file_path)
        
        return changes
    
    def load_config(self, config_path: Path) -> Optional[Dict[str, Any]]:
        """Load YAML config file safely"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.print_status(f"Failed to load {config_path}: {e}", "warning")
            return None
    
    def save_config(self, config_path: Path, config: Dict[str, Any]) -> bool:
        """Save YAML config file safely"""
        try:
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            self.print_status(f"Failed to save {config_path}: {e}", "warning")
            return False
    
    def get_next_version_number(self, versions_dir: Path) -> int:
        """Get the next sequential version number"""
        if not versions_dir.exists():
            return 1
        
        version_files = list(versions_dir.glob('v*.md'))
        if not version_files:
            return 1
        
        version_numbers = []
        for file in version_files:
            match = re.match(r'v(\d+)\.md', file.name)
            if match:
                version_numbers.append(int(match.group(1)))
        
        return max(version_numbers) + 1 if version_numbers else 1
    
    def create_version_snapshot(self, current_md_path: str) -> Optional[str]:
        """
        Create a new version snapshot from current.md
        Returns the new version name (e.g., 'v005') or None if failed
        """
        current_path = self.workspace_path / current_md_path
        prompt_dir = current_path.parent
        config_path = prompt_dir / 'config.yaml'
        versions_dir = prompt_dir / 'versions'
        
        # Skip if no config file
        if not config_path.exists():
            self.print_status(f"No config.yaml found for {current_md_path}", "warning")
            return None
        
        # Load config
        config = self.load_config(config_path)
        if not config:
            return None
        
        # Create versions directory if it doesn't exist
        versions_dir.mkdir(exist_ok=True)
        
        # Get next version number
        version_num = self.get_next_version_number(versions_dir)
        version_name = f'v{version_num:03d}'
        version_file = versions_dir / f'{version_name}.md'
        
        try:
            # Copy current.md to new version file
            shutil.copy2(current_path, version_file)
            
            # Add version header to the file
            with open(version_file, 'r') as f:
                content = f.read()
            
            version_header = f"<!-- Version {version_name} - Created {datetime.now().isoformat()} -->\n"
            with open(version_file, 'w') as f:
                f.write(version_header)
                f.write(content)
            
            # Update config with new version info
            if 'versions' not in config:
                config['versions'] = {}
            
            config['versions'][version_name] = {
                'created_at': datetime.now().isoformat(),
                'author': os.getenv('USER', 'unknown'),
                'commit': self.get_current_commit_hash()[:7],
                'notes': 'Auto-versioned on commit'
            }
            
            # Set as current version if not already set
            if 'current_version' not in config:
                config['current_version'] = version_name
            
            # Update metadata
            if 'metadata' not in config:
                config['metadata'] = {}
            config['metadata']['last_modified'] = datetime.now().isoformat()
            
            # Save updated config
            if self.save_config(config_path, config):
                # Stage the new files
                self.stage_files([str(version_file), str(config_path)])
                return version_name
            
        except Exception as e:
            self.print_status(f"Failed to create version {version_name}: {e}", "warning")
            return None
        
        return None
    
    def handle_version_switch(self, config_path: str) -> bool:
        """
        Handle version switching in config.yaml
        If current_version changed, deploy that version to current.md
        """
        config_path = Path(config_path)
        prompt_dir = config_path.parent
        current_md = prompt_dir / 'current.md'
        versions_dir = prompt_dir / 'versions'
        
        # Load config
        config = self.load_config(config_path)
        if not config:
            return False
        
        # Check if current_version is specified
        current_version = config.get('current_version')
        if not current_version:
            return False
        
        # Check if the version file exists
        version_file = versions_dir / f'{current_version}.md'
        if not version_file.exists():
            self.print_status(f"Version {current_version} not found in {versions_dir}", "warning")
            return False
        
        try:
            # Check if current.md differs from the specified version
            if current_md.exists():
                with open(current_md, 'r') as f:
                    current_content = f.read()
                with open(version_file, 'r') as f:
                    version_content = f.read()
                    # Remove version header if present
                    version_content = re.sub(r'^<!-- Version.*? -->\n', '', version_content)
                
                if current_content.strip() == version_content.strip():
                    return False  # Already matches, no need to deploy
            
            # Deploy the version to current.md
            shutil.copy2(version_file, current_md)
            
            # Remove version header from current.md
            with open(current_md, 'r') as f:
                content = f.read()
            
            # Remove version header
            content = re.sub(r'^<!-- Version.*? -->\n', '', content)
            with open(current_md, 'w') as f:
                f.write(content)
            
            # Stage current.md
            self.stage_files([str(current_md)])
            
            self.print_status(f"Deployed {current_version} to current.md", "version")
            return True
            
        except Exception as e:
            self.print_status(f"Failed to deploy version {current_version}: {e}", "warning")
            return False
    
    def get_current_commit_hash(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'], 
                capture_output=True, 
                text=True, 
                check=True,
                cwd=self.workspace_path
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return 'unknown'
    
    def stage_files(self, files: List[str]):
        """Stage files for git commit"""
        try:
            subprocess.run(['git', 'add'] + files, check=True, cwd=self.workspace_path)
        except subprocess.CalledProcessError as e:
            self.print_status(f"Failed to stage files: {e}", "warning")
    
    def main_hook_logic(self, staged_files: Optional[List[str]] = None):
        """
        Main hook logic - returns (success, processed_count, messages)
        
        This replicates the main() function from the pre-commit hook
        for testing purposes.
        """
        # Check for bypass
        if self.is_hook_bypassed():
            return True, 0, ["Promptix hook skipped (SKIP_PROMPTIX_HOOK=1)"]
        
        # Get staged files
        if staged_files is None:
            staged_files = self.get_staged_files()
        
        if not staged_files:
            return True, 0, []
        
        # Find promptix-related changes
        promptix_changes = self.find_promptix_changes(staged_files)
        
        if not promptix_changes['current_md'] and not promptix_changes['config_yaml']:
            # No promptix changes
            return True, 0, []
        
        messages = ["Promptix: Processing version management..."]
        processed_count = 0
        
        # Handle current.md changes (auto-versioning)
        for current_md_path in promptix_changes['current_md']:
            try:
                version_name = self.create_version_snapshot(current_md_path)
                if version_name:
                    messages.append(f"{current_md_path} → {version_name}")
                    processed_count += 1
                else:
                    messages.append(f"{current_md_path} (skipped)")
            except Exception as e:
                messages.append(f"{current_md_path} (error: {e})")
        
        # Handle config.yaml changes (version switching)
        for config_path in promptix_changes['config_yaml']:
            try:
                if self.handle_version_switch(config_path):
                    processed_count += 1
            except Exception as e:
                messages.append(f"{config_path} version switch failed: {e}")
        
        if processed_count > 0:
            messages.append(f"Processed {processed_count} version operation(s)")
        
        # Always return success - never block commits
        return True, processed_count, messages
