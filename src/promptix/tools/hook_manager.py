#!/usr/bin/env python3
"""
Promptix Hook Manager

Tool for installing, managing, and configuring the Promptix pre-commit hook.
Handles safe installation with backups and easy removal.
"""

import argparse
import os
import shutil
import sys
import subprocess
from pathlib import Path
from typing import Optional


class HookManager:
    """Manager for Promptix git hooks"""
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize with workspace path"""
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd()
        # Locate the git directory, supporting both real dirs and worktree pointer files
        self.git_dir = self.workspace_path / '.git'
        if self.git_dir.is_file():
            gitdir_line = self.git_dir.read_text().strip()
            if gitdir_line.lower().startswith("gitdir:"):
                resolved = (self.git_dir.parent / gitdir_line.split(":", 1)[1].strip()).resolve()
                self.git_dir = resolved
            else:
                raise ValueError(f"Unsupported .git file format in {self.workspace_path}")

        # Now safe to build hook paths off the resolved git directory
        self.hooks_dir = self.git_dir / 'hooks'
        self.pre_commit_hook = self.hooks_dir / 'pre-commit'
        self.backup_hook = self.hooks_dir / 'pre-commit.backup'

        # Path to our hook script in the workspace
        self.promptix_hook = self.workspace_path / 'hooks' / 'pre-commit'

        if not self.git_dir.exists():
            raise ValueError(f"Not a git repository: {self.workspace_path}")
    def print_status(self, message: str, status: str = "info"):
        """Print colored status messages"""
        icons = {
            "info": "📝",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌",
            "install": "🔧",
            "uninstall": "🗑️"
        }
        print(f"{icons.get(status, '📝')} {message}")
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        return self.git_dir.exists()
    
    def has_existing_hook(self) -> bool:
        """Check if there's already a pre-commit hook"""
        return self.pre_commit_hook.exists()
    
    def is_promptix_hook(self) -> bool:
        """Check if existing hook is a Promptix hook"""
        if not self.pre_commit_hook.exists():
            return False
        
        try:
            with open(self.pre_commit_hook, 'r') as f:
                content = f.read()
            return 'Promptix pre-commit hook' in content
        except Exception:
            return False
    
    def backup_existing_hook(self) -> bool:
        """Backup existing pre-commit hook"""
        if not self.has_existing_hook():
            return True
        
        if self.is_promptix_hook():
            # No need to backup if it's already a Promptix hook
            return True
        
        try:
            shutil.copy2(self.pre_commit_hook, self.backup_hook)
            self.print_status(f"Backed up existing hook to {self.backup_hook.name}", "info")
            return True
        except Exception as e:
            self.print_status(f"Failed to backup existing hook: {e}", "error")
            return False
    
    def restore_backup(self) -> bool:
        """Restore backed up pre-commit hook"""
        if not self.backup_hook.exists():
            return True
        
        try:
            shutil.copy2(self.backup_hook, self.pre_commit_hook)
            self.backup_hook.unlink()
            self.print_status("Restored original pre-commit hook", "info")
            return True
        except Exception as e:
            self.print_status(f"Failed to restore backup: {e}", "error")
            return False
    
    def install_hook(self, force: bool = False):
        """Install the Promptix pre-commit hook"""
        if not self.is_git_repo():
            self.print_status("Not a git repository", "error")
            return
        
        if not self.promptix_hook.exists():
            self.print_status(f"Promptix hook not found at {self.promptix_hook}", "error")
            self.print_status("Make sure you're in the Promptix workspace root", "info")
            return
        
        # Check for existing hook
        if self.has_existing_hook() and not force:
            if self.is_promptix_hook():
                self.print_status("Promptix hook is already installed", "info")
                return
            else:
                self.print_status("Existing pre-commit hook detected", "warning")
                self.print_status("Use --force to overwrite, or uninstall first", "info")
                return
        
        # Create hooks directory if it doesn't exist
        self.hooks_dir.mkdir(exist_ok=True)
        
        # Backup existing hook if needed
        if not self.backup_existing_hook():
            return
        
        try:
            # Copy our hook to the git hooks directory
            shutil.copy2(self.promptix_hook, self.pre_commit_hook)
            
            # Make sure it's executable
            os.chmod(self.pre_commit_hook, 0o755)
            
            self.print_status("Promptix pre-commit hook installed successfully", "install")
            self.print_status("💡 Use 'SKIP_PROMPTIX_HOOK=1 git commit' to bypass when needed", "info")
            
        except Exception as e:
            self.print_status(f"Failed to install hook: {e}", "error")
    
    def uninstall_hook(self):
        """Uninstall the Promptix pre-commit hook"""
        if not self.has_existing_hook():
            self.print_status("No pre-commit hook found", "info")
            return
        
        if not self.is_promptix_hook():
            self.print_status("Existing hook is not a Promptix hook", "warning")
            return
        
        try:
            # Remove the hook
            self.pre_commit_hook.unlink()
            
            # Restore backup if it exists
            self.restore_backup()
            
            self.print_status("Promptix pre-commit hook uninstalled", "uninstall")
            
        except Exception as e:
            self.print_status(f"Failed to uninstall hook: {e}", "error")
    
    def disable_hook(self):
        """Disable the hook by renaming it"""
        if not self.has_existing_hook():
            self.print_status("No pre-commit hook found", "info")
            return
        
        if not self.is_promptix_hook():
            self.print_status("Existing hook is not a Promptix hook", "warning")
            return
        
        try:
            disabled_hook = self.hooks_dir / 'pre-commit.disabled'
            shutil.move(self.pre_commit_hook, disabled_hook)
            self.print_status("Promptix hook disabled", "info")
            self.print_status("Use 'enable' command to re-enable", "info")
            
        except Exception as e:
            self.print_status(f"Failed to disable hook: {e}", "error")
    
    def enable_hook(self):
        """Enable a disabled hook"""
        disabled_hook = self.hooks_dir / 'pre-commit.disabled'
        
        if not disabled_hook.exists():
            self.print_status("No disabled hook found", "info")
            return
        
        if self.has_existing_hook():
            self.print_status("Active pre-commit hook already exists", "warning")
            return
        
        try:
            shutil.move(disabled_hook, self.pre_commit_hook)
            self.print_status("Promptix hook enabled", "success")
            
        except Exception as e:
            self.print_status(f"Failed to enable hook: {e}", "error")
    
    def status(self):
        """Show status of Promptix hooks"""
        self.print_status("Promptix Hook Status:", "info")
        print()
        
        # Git repository check
        if not self.is_git_repo():
            print("  ❌ Not a git repository")
            return
        else:
            print("  ✅ Git repository detected")
        
        # Hook file check
        if not self.promptix_hook.exists():
            print(f"  ❌ Promptix hook not found at {self.promptix_hook}")
        else:
            print(f"  ✅ Promptix hook found at {self.promptix_hook}")
        
        # Installation status
        if not self.has_existing_hook():
            print("  📝 No pre-commit hook installed")
        elif self.is_promptix_hook():
            print("  ✅ Promptix hook is active")
        else:
            print("  ⚠️  Non-Promptix pre-commit hook is active")
        
        # Disabled hook check
        disabled_hook = self.hooks_dir / 'pre-commit.disabled'
        if disabled_hook.exists():
            print("  📝 Disabled Promptix hook found (use 'enable' to activate)")
        
        # Backup check
        if self.backup_hook.exists():
            print("  📝 Original hook backup exists")
        
        print()
    
    def test_hook(self):
        """Test the hook without committing"""
        if not self.has_existing_hook():
            self.print_status("No pre-commit hook installed", "error")
            return
        
        if not self.is_promptix_hook():
            self.print_status("Active hook is not a Promptix hook", "error")
            return
        
        self.print_status("Running hook test...", "info")
        
        try:
            # Resolve and validate hook path to prevent symlink attacks
            try:
                resolved_hook = self.pre_commit_hook.resolve(strict=True)
            except (OSError, RuntimeError) as e:
                self.print_status(f"Failed to resolve hook path: {e}", "error")
                return
            
            # Verify the resolved hook is inside the expected hooks directory
            expected_hooks_dir = self.hooks_dir.resolve(strict=True)
            if resolved_hook.parent != expected_hooks_dir:
                self.print_status(
                    f"Security error: Hook path resolves outside hooks directory ({resolved_hook})",
                    "error"
                )
                return
            
            # Run the validated hook directly
            result = subprocess.run([str(resolved_hook)],
                                    capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_status("Hook test completed successfully", "success")
                if result.stdout:
                    print("Output:")
                    print(result.stdout)
            else:
                self.print_status("Hook test failed", "error")
                if result.stderr:
                    print("Error:")
                    print(result.stderr)
                    
        except Exception as e:
            self.print_status(f"Failed to run hook test: {e}", "error")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Promptix Hook Manager - Install and manage git hooks"
    )
    
    parser.add_argument(
        '--workspace', '-w', 
        help="Path to promptix workspace (default: current directory)"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Install command
    install_cmd = subparsers.add_parser('install', help='Install pre-commit hook')
    install_cmd.add_argument('--force', action='store_true',
                             help='Overwrite existing hook')
    
    # Uninstall command
    subparsers.add_parser('uninstall', help='Uninstall pre-commit hook')
    
    # Enable/disable commands
    subparsers.add_parser('enable', help='Enable disabled hook')
    subparsers.add_parser('disable', help='Disable hook temporarily')
    
    # Status command
    subparsers.add_parser('status', help='Show hook status')
    
    # Test command
    subparsers.add_parser('test', help='Test hook without committing')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        hm = HookManager(args.workspace)
        
        if args.command == 'install':
            hm.install_hook(args.force)
        elif args.command == 'uninstall':
            hm.uninstall_hook()
        elif args.command == 'enable':
            hm.enable_hook()
        elif args.command == 'disable':
            hm.disable_hook()
        elif args.command == 'status':
            hm.status()
        elif args.command == 'test':
            hm.test_hook()
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
