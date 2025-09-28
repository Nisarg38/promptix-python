"""
Unit tests for the HookManager CLI tool.

Tests the command-line interface for managing pre-commit hooks.
"""

import pytest
import tempfile
import shutil
import subprocess
import io
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from promptix.tools.hook_manager import HookManager


class TestHookManager:
    """Test the HookManager CLI functionality"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace with git repository"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_hook_manager_"))
        
        # Initialize git repository
        git_dir = temp_dir / ".git"
        git_dir.mkdir()
        
        # Create hooks directory
        hooks_git_dir = git_dir / "hooks"
        hooks_git_dir.mkdir()
        
        # Create promptix hooks directory with hook script
        promptix_hooks_dir = temp_dir / "hooks"
        promptix_hooks_dir.mkdir()
        
        # Create a mock pre-commit hook
        hook_content = """#!/usr/bin/env python3
'''
Promptix pre-commit hook
'''
import sys
print("Mock Promptix hook running")
sys.exit(0)
"""
        
        with open(promptix_hooks_dir / "pre-commit", "w") as f:
            f.write(hook_content)
        
        # Make it executable
        (promptix_hooks_dir / "pre-commit").chmod(0o755)
        
        yield temp_dir
        
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def non_git_workspace(self):
        """Create a workspace without git"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_non_git_"))
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_initialization_valid_git_repo(self, temp_workspace):
        """Test HookManager initialization with valid git repo"""
        hm = HookManager(str(temp_workspace))
        
        assert hm.workspace_path == temp_workspace
        assert hm.git_dir == temp_workspace / ".git"
        assert hm.hooks_dir == temp_workspace / ".git" / "hooks"
        assert hm.pre_commit_hook == temp_workspace / ".git" / "hooks" / "pre-commit"
        assert hm.promptix_hook == temp_workspace / "hooks" / "pre-commit"
    
    def test_initialization_invalid_git_repo(self, non_git_workspace):
        """Test HookManager initialization with invalid git repo"""
        with pytest.raises(ValueError, match="Not a git repository"):
            HookManager(str(non_git_workspace))
    
    def test_is_git_repo_true(self, temp_workspace):
        """Test git repository detection - positive case"""
        hm = HookManager(str(temp_workspace))
        assert hm.is_git_repo() is True
    
    def test_is_git_repo_false(self, non_git_workspace):
        """Test git repository detection - negative case"""
        # Add .git directory manually for initialization, then remove
        git_dir = non_git_workspace / ".git"
        git_dir.mkdir()
        
        hm = HookManager(str(non_git_workspace))
        
        # Remove .git directory
        shutil.rmtree(git_dir)
        
        assert hm.is_git_repo() is False
    
    def test_has_existing_hook_false(self, temp_workspace):
        """Test detecting no existing hook"""
        hm = HookManager(str(temp_workspace))
        assert hm.has_existing_hook() is False
    
    def test_has_existing_hook_true(self, temp_workspace):
        """Test detecting existing hook"""
        hm = HookManager(str(temp_workspace))
        
        # Create existing hook
        with open(hm.pre_commit_hook, "w") as f:
            f.write("#!/bin/bash\necho 'existing hook'")
        
        assert hm.has_existing_hook() is True
    
    def test_is_promptix_hook_false(self, temp_workspace):
        """Test detecting non-Promptix hook"""
        hm = HookManager(str(temp_workspace))
        
        # Create non-Promptix hook
        with open(hm.pre_commit_hook, "w") as f:
            f.write("#!/bin/bash\necho 'some other hook'")
        
        assert hm.is_promptix_hook() is False
    
    def test_is_promptix_hook_true(self, temp_workspace):
        """Test detecting Promptix hook"""
        hm = HookManager(str(temp_workspace))
        
        # Create Promptix hook
        with open(hm.pre_commit_hook, "w") as f:
            f.write("#!/usr/bin/env python3\n# Promptix pre-commit hook\nprint('hello')")
        
        assert hm.is_promptix_hook() is True
    
    def test_backup_existing_hook_success(self, temp_workspace):
        """Test successful backup of existing hook"""
        hm = HookManager(str(temp_workspace))
        
        # Create existing hook
        hook_content = "#!/bin/bash\necho 'original hook'"
        with open(hm.pre_commit_hook, "w") as f:
            f.write(hook_content)
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            result = hm.backup_existing_hook()
        
        assert result is True
        assert hm.backup_hook.exists()
        
        # Verify backup content
        with open(hm.backup_hook, "r") as f:
            backed_up_content = f.read()
        
        assert backed_up_content == hook_content
        
        output = captured_output.getvalue()
        assert "Backed up existing hook" in output
    
    def test_backup_existing_hook_no_hook(self, temp_workspace):
        """Test backup when no existing hook"""
        hm = HookManager(str(temp_workspace))
        
        result = hm.backup_existing_hook()
        assert result is True
        assert not hm.backup_hook.exists()
    
    def test_backup_existing_hook_promptix_hook(self, temp_workspace):
        """Test backup when existing hook is already Promptix"""
        hm = HookManager(str(temp_workspace))
        
        # Create Promptix hook
        with open(hm.pre_commit_hook, "w") as f:
            f.write("# Promptix pre-commit hook\nprint('promptix')")
        
        result = hm.backup_existing_hook()
        assert result is True
        assert not hm.backup_hook.exists()  # No backup needed
    
    def test_install_hook_success(self, temp_workspace):
        """Test successful hook installation"""
        hm = HookManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.install_hook()
        
        output = captured_output.getvalue()
        
        # Check hook was installed
        assert hm.pre_commit_hook.exists()
        assert hm.pre_commit_hook.stat().st_mode & 0o755  # Executable
        
        # Check output
        assert "installed successfully" in output
        assert "SKIP_PROMPTIX_HOOK" in output
    
    def test_install_hook_missing_source(self, temp_workspace):
        """Test hook installation when source hook is missing"""
        hm = HookManager(str(temp_workspace))
        
        # Remove source hook
        hm.promptix_hook.unlink()
        
        captured_output = io.StringIO()
        with patch('sys.stderr', captured_output):
            hm.install_hook()
        
        output = captured_output.getvalue()
        assert "not found" in output.lower()
    
    def test_install_hook_existing_non_promptix(self, temp_workspace):
        """Test hook installation with existing non-Promptix hook"""
        hm = HookManager(str(temp_workspace))
        
        # Create existing non-Promptix hook
        with open(hm.pre_commit_hook, "w") as f:
            f.write("#!/bin/bash\necho 'existing hook'")
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.install_hook()
        
        output = captured_output.getvalue()
        assert "Existing pre-commit hook detected" in output
        assert "Use --force" in output
        
        # Hook should not be overwritten
        with open(hm.pre_commit_hook, "r") as f:
            content = f.read()
        assert "existing hook" in content
    
    def test_install_hook_force_overwrite(self, temp_workspace):
        """Test hook installation with force overwrite"""
        hm = HookManager(str(temp_workspace))
        
        # Create existing hook
        with open(hm.pre_commit_hook, "w") as f:
            f.write("#!/bin/bash\necho 'existing hook'")
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.install_hook(force=True)
        
        output = captured_output.getvalue()
        assert "installed successfully" in output
        
        # Check hook was overwritten
        with open(hm.pre_commit_hook, "r") as f:
            content = f.read()
        assert "Promptix hook" in content
    
    def test_install_hook_already_installed(self, temp_workspace):
        """Test installing hook when already installed"""
        hm = HookManager(str(temp_workspace))
        
        # Install hook first
        hm.install_hook()
        
        # Try to install again
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.install_hook()
        
        output = captured_output.getvalue()
        assert "already installed" in output
    
    def test_uninstall_hook_success(self, temp_workspace):
        """Test successful hook uninstallation"""
        hm = HookManager(str(temp_workspace))
        
        # Install hook first
        hm.install_hook()
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.uninstall_hook()
        
        output = captured_output.getvalue()
        
        # Check hook was removed
        assert not hm.pre_commit_hook.exists()
        assert "uninstalled" in output
    
    def test_uninstall_hook_no_hook(self, temp_workspace):
        """Test uninstalling when no hook exists"""
        hm = HookManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.uninstall_hook()
        
        output = captured_output.getvalue()
        assert "No pre-commit hook found" in output
    
    def test_uninstall_hook_non_promptix(self, temp_workspace):
        """Test uninstalling when hook is not Promptix"""
        hm = HookManager(str(temp_workspace))
        
        # Create non-Promptix hook
        with open(hm.pre_commit_hook, "w") as f:
            f.write("#!/bin/bash\necho 'other hook'")
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.uninstall_hook()
        
        output = captured_output.getvalue()
        assert "not a Promptix hook" in output
    
    def test_disable_hook_success(self, temp_workspace):
        """Test successful hook disabling"""
        hm = HookManager(str(temp_workspace))
        
        # Install hook first
        hm.install_hook()
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.disable_hook()
        
        output = captured_output.getvalue()
        
        # Check hook was disabled
        assert not hm.pre_commit_hook.exists()
        assert (hm.hooks_dir / "pre-commit.disabled").exists()
        assert "disabled" in output
    
    def test_enable_hook_success(self, temp_workspace):
        """Test successful hook enabling"""
        hm = HookManager(str(temp_workspace))
        
        # Install and disable hook first
        hm.install_hook()
        hm.disable_hook()
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.enable_hook()
        
        output = captured_output.getvalue()
        
        # Check hook was enabled
        assert hm.pre_commit_hook.exists()
        assert not (hm.hooks_dir / "pre-commit.disabled").exists()
        assert "enabled" in output
    
    def test_enable_hook_no_disabled_hook(self, temp_workspace):
        """Test enabling when no disabled hook exists"""
        hm = HookManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.enable_hook()
        
        output = captured_output.getvalue()
        assert "No disabled hook found" in output
    
    def test_status_complete(self, temp_workspace):
        """Test status display with all conditions"""
        hm = HookManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.status()
        
        output = captured_output.getvalue()
        
        # Check status components
        assert "Hook Status" in output
        assert "Git repository detected" in output
        assert "Promptix hook found" in output
        assert "No pre-commit hook installed" in output
    
    def test_status_hook_installed(self, temp_workspace):
        """Test status display with hook installed"""
        hm = HookManager(str(temp_workspace))
        
        # Install hook
        hm.install_hook()
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.status()
        
        output = captured_output.getvalue()
        assert "Promptix hook is active" in output
    
    def test_test_hook_success(self, temp_workspace):
        """Test running hook test successfully"""
        hm = HookManager(str(temp_workspace))
        
        # Install hook
        hm.install_hook()
        
        # Mock successful subprocess run
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Hook test output"
            
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                hm.test_hook()
        
        output = captured_output.getvalue()
        assert "completed successfully" in output
        assert "Hook test output" in output
    
    def test_test_hook_failure(self, temp_workspace):
        """Test running hook test with failure"""
        hm = HookManager(str(temp_workspace))
        
        # Install hook
        hm.install_hook()
        
        # Mock failed subprocess run
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Hook test error"
            
            captured_output = io.StringIO()
            with patch('sys.stderr', captured_output):
                hm.test_hook()
        
        output = captured_output.getvalue()
        assert "test failed" in output
        assert "Hook test error" in output
    
    def test_test_hook_no_hook(self, temp_workspace):
        """Test running hook test when no hook installed"""
        hm = HookManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stderr', captured_output):
            hm.test_hook()
        
        output = captured_output.getvalue()
        assert "No pre-commit hook installed" in output


class TestHookManagerErrorHandling:
    """Test error handling in HookManager"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create minimal workspace"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_hook_error_"))
        
        # Create .git directory
        git_dir = temp_dir / ".git"
        git_dir.mkdir()
        
        yield temp_dir
        
        shutil.rmtree(temp_dir)
    
    def test_permission_denied_hook_installation(self, temp_workspace):
        """Test handling permission denied during hook installation"""
        hm = HookManager(str(temp_workspace))
        
        # Create source hook
        hooks_dir = temp_workspace / "hooks"
        hooks_dir.mkdir()
        with open(hooks_dir / "pre-commit", "w") as f:
            f.write("#!/usr/bin/env python3\nprint('test')")
        
        # Mock permission error
        with patch('shutil.copy2', side_effect=PermissionError("Access denied")):
            captured_output = io.StringIO()
            with patch('sys.stderr', captured_output):
                hm.install_hook()
            
            output = captured_output.getvalue()
            # Should handle error gracefully
    
    def test_corrupted_hook_file(self, temp_workspace):
        """Test handling corrupted hook files"""
        hm = HookManager(str(temp_workspace))
        
        # Create corrupted hook file
        with open(hm.pre_commit_hook, "w") as f:
            f.write("")  # Empty file
        
        # Should not crash when checking if it's a Promptix hook
        result = hm.is_promptix_hook()
        assert result is False
    
    def test_git_hooks_directory_missing(self, temp_workspace):
        """Test handling missing git hooks directory"""
        hm = HookManager(str(temp_workspace))
        
        # Create source hook
        hooks_dir = temp_workspace / "hooks"  
        hooks_dir.mkdir()
        with open(hooks_dir / "pre-commit", "w") as f:
            f.write("#!/usr/bin/env python3\nprint('test')")
        
        # Install hook (should create hooks directory)
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            hm.install_hook()
        
        output = captured_output.getvalue()
        assert "installed successfully" in output
        assert hm.hooks_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
