"""
Integration tests for the complete auto-versioning workflow.

Tests the full end-to-end workflow from pre-commit hooks to API integration.
"""

import pytest
import tempfile
import shutil
import subprocess
import yaml
import os
import sys
import stat
from pathlib import Path
from unittest.mock import patch

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "tests" / "test_helpers"))

from promptix import Promptix
from promptix.core.components.prompt_loader import PromptLoader
from promptix.tools.version_manager import VersionManager
from promptix.tools.hook_manager import HookManager
from precommit_helper import PreCommitHookTester


def remove_readonly(func, path, excinfo):
    """
    Error handler for Windows read-only file removal.
    
    This is needed because Git creates read-only files in .git/objects/
    that can't be deleted on Windows without changing permissions first.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def safe_rmtree(path):
    """
    Safely remove a directory tree, handling Windows permission issues.
    
    On Windows, Git repositories contain read-only files that need
    special handling to delete.
    """
    try:
        if sys.platform == 'win32':
            # On Windows, use onerror callback to handle read-only files
            shutil.rmtree(path, onerror=remove_readonly)
        else:
            shutil.rmtree(path)
    except Exception as e:
        # If all else fails, try one more time with ignore_errors
        try:
            shutil.rmtree(path, ignore_errors=True)
        except:
            # Last resort: just pass and let the OS clean up temp files
            pass


class TestVersioningIntegration:
    """Integration tests for the complete versioning workflow"""
    
    @pytest.fixture
    def git_workspace(self):
        """Create a complete git workspace with Promptix structure"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_integration_"))
        prev_cwd = Path.cwd()
        
        # Initialize git repo
        os.chdir(temp_dir)
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
        
        # Create promptix structure
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        
        # Create test agent
        agent_dir = prompts_dir / "test_agent"
        agent_dir.mkdir()
        
        config_content = {
            'metadata': {
                'name': 'TestAgent',
                'description': 'Integration test agent',
                'author': 'Test Team',
            },
            'schema': {
                'type': 'object',
                'properties': {
                    'user_name': {'type': 'string'},
                    'task_type': {'type': 'string'}
                },
                'required': ['user_name']
            },
            'config': {
                'model': 'gpt-4',
                'temperature': 0.7,
                'max_tokens': 1000
            }
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f, default_flow_style=False)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("You are an assistant. Help {{user_name}} with {{task_type}} tasks.")
        
        (agent_dir / "versions").mkdir()
        
        # Create and install hook
        hooks_dir = temp_dir / "hooks"
        hooks_dir.mkdir()
        
        # Copy pre-commit hook from project
        hook_source = project_root / "hooks" / "pre-commit"
        hook_dest = hooks_dir / "pre-commit"
        
        if hook_source.exists():
            shutil.copy2(hook_source, hook_dest)
            os.chmod(hook_dest, 0o755)
        
        yield temp_dir
        
        # Cleanup
        os.chdir(prev_cwd)
        safe_rmtree(temp_dir)
    
    def test_complete_development_workflow(self, git_workspace):
        """Test complete development workflow: edit → commit → version → API"""
        os.chdir(git_workspace)
        
        # Step 1: Initial commit
        subprocess.run(["git", "add", "."], capture_output=True)
        result = subprocess.run(["git", "commit", "-m", "Initial commit"], 
                              capture_output=True, text=True)
        
        # Should succeed
        assert result.returncode == 0
        
        # Check that hook didn't create version yet (no current.md changes)
        versions_dir = git_workspace / "prompts" / "test_agent" / "versions"
        version_files = list(versions_dir.glob("v*.md"))
        # Might or might not create version on initial commit
        
        # Step 2: Edit current.md and commit
        current_md = git_workspace / "prompts" / "test_agent" / "current.md"
        with open(current_md, "w") as f:
            f.write("You are a helpful assistant. Help {{user_name}} with {{task_type}} tasks efficiently.")
        
        subprocess.run(["git", "add", "prompts/test_agent/current.md"], capture_output=True)
        
        # Install hook first
        hm = HookManager(str(git_workspace))
        hm.install_hook()
        
        result = subprocess.run(["git", "commit", "-m", "Improved assistance message"], 
                              capture_output=True, text=True)
        
        # Should succeed and create version
        assert result.returncode == 0
        
        # Check version was created
        version_files = list(versions_dir.glob("v*.md"))
        assert len(version_files) >= 1
        
        # Check config was updated
        with open(git_workspace / "prompts" / "test_agent" / "config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        assert 'versions' in config
        # current_version should NOT be set automatically - it's only set when explicitly switching
        # The API will use current.md when current_version is not set
        
        # Step 3: Test API integration
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=git_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            # Basic prompt retrieval should work
            prompt = Promptix.get_prompt("test_agent", user_name="Alice", task_type="coding")
            assert "Alice" in prompt
            assert "coding" in prompt
            assert "efficiently" in prompt  # Should use updated version
            
            # Builder should work
            builder = Promptix.builder("test_agent")
            config_result = builder.with_data(user_name="Bob", task_type="testing").build()
            assert isinstance(config_result, dict)
            assert 'messages' in config_result
    
    def test_version_switching_workflow(self, git_workspace):
        """Test version switching workflow: create versions → switch → API reflects change"""
        os.chdir(git_workspace)
        
        # Setup: Create multiple versions
        tester = PreCommitHookTester(git_workspace)
        
        # Version 1: Initial
        current_md = git_workspace / "prompts" / "test_agent" / "current.md"
        with open(current_md, "w") as f:
            f.write("Version 1: Basic assistant for {{user_name}}")
        
        version1 = tester.create_version_snapshot("prompts/test_agent/current.md")
        assert version1 is not None
        
        # Version 2: Enhanced
        with open(current_md, "w") as f:
            f.write("Version 2: Enhanced assistant helping {{user_name}} with {{task_type}}")
        
        version2 = tester.create_version_snapshot("prompts/test_agent/current.md")
        assert version2 is not None
        
        # Version 3: Advanced
        with open(current_md, "w") as f:
            f.write("Version 3: Advanced assistant specializing in {{task_type}} for {{user_name}}")
        
        version3 = tester.create_version_snapshot("prompts/test_agent/current.md")
        assert version3 is not None
        
        # Test API with latest version
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=git_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            prompt = Promptix.get_prompt("test_agent", user_name="Alice", task_type="debugging")
            assert "Advanced assistant" in prompt
            assert "specializing" in prompt
        
        # Switch to version 1 using VersionManager
        vm = VersionManager(str(git_workspace))
        vm.switch_version("test_agent", version1)
        
        # Test API reflects the change
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=git_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            # Force reload
            loader = PromptLoader()
            prompts = loader.load_prompts(force_reload=True)
            
            prompt = Promptix.get_prompt("test_agent", user_name="Bob")
            assert "Version 1" in prompt
            assert "Basic assistant" in prompt
            assert "specializing" not in prompt  # Should not have v3 content
        
        # Test specific version requests
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=git_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            # Request specific version
            prompt_v2 = Promptix.get_prompt("test_agent", version=version2, 
                                          user_name="Carol", task_type="testing")
            assert "Version 2" in prompt_v2
            assert "Enhanced assistant" in prompt_v2
    
    def test_config_based_version_switching(self, git_workspace):
        """Test version switching via config.yaml changes (hook-based)"""
        os.chdir(git_workspace)
        
        # Setup: Create versions first
        tester = PreCommitHookTester(git_workspace)
        
        current_md = git_workspace / "prompts" / "test_agent" / "current.md"
        
        # Create v001
        with open(current_md, "w") as f:
            f.write("Original assistant content")
        version1 = tester.create_version_snapshot("prompts/test_agent/current.md")
        
        # Create v002  
        with open(current_md, "w") as f:
            f.write("Updated assistant content with improvements")
        version2 = tester.create_version_snapshot("prompts/test_agent/current.md")
        
        # Verify current state
        with open(current_md, "r") as f:
            content = f.read()
        assert "improvements" in content
        
        # Switch to v001 via config.yaml
        config_path = git_workspace / "prompts" / "test_agent" / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        config['current_version'] = version1
        
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Trigger hook via version switch handling
        success = tester.handle_version_switch(str(config_path))
        assert success is True
        
        # Verify current.md was updated
        with open(current_md, "r") as f:
            content = f.read()
        assert "Original assistant" in content
        assert "improvements" not in content
        
        # Test API reflects the change
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=git_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            prompts = loader.load_prompts(force_reload=True)
            
            prompt = Promptix.get_prompt("test_agent", user_name="TestUser")
            assert "Original assistant" in prompt
    
    def test_multiple_agents_workflow(self, git_workspace):
        """Test workflow with multiple agents"""
        os.chdir(git_workspace)
        
        # Create second agent
        agent2_dir = git_workspace / "prompts" / "agent2"
        agent2_dir.mkdir()
        
        config2_content = {
            'metadata': {'name': 'Agent2', 'description': 'Second test agent'},
            'schema': {'type': 'object', 'properties': {'topic': {'type': 'string'}}},
            'config': {'model': 'gpt-3.5-turbo'}
        }
        
        with open(agent2_dir / "config.yaml", "w") as f:
            yaml.dump(config2_content, f)
        
        with open(agent2_dir / "current.md", "w") as f:
            f.write("Agent2 helps with {{topic}} discussions")
        
        (agent2_dir / "versions").mkdir()
        
        # Test hook handles multiple agents
        tester = PreCommitHookTester(git_workspace)
        
        # Simulate changes to both agents
        current_md1 = git_workspace / "prompts" / "test_agent" / "current.md"
        current_md2 = git_workspace / "prompts" / "agent2" / "current.md"
        
        with open(current_md1, "w") as f:
            f.write("Updated test agent content for {{user_name}} with {{task_type}}")
        
        with open(current_md2, "w") as f:
            f.write("Updated agent2 helps with {{topic}} in detail")
        
        # Process both changes
        staged_files = [
            "prompts/test_agent/current.md",
            "prompts/agent2/current.md"
        ]
        
        success, processed_count, messages = tester.main_hook_logic(staged_files)
        
        assert success is True
        assert processed_count == 2
        
        # Verify versions created for both agents
        test_agent_versions = list((git_workspace / "prompts" / "test_agent" / "versions").glob("v*.md"))
        agent2_versions = list((git_workspace / "prompts" / "agent2" / "versions").glob("v*.md"))
        assert test_agent_versions
        assert agent2_versions
        # Test API can access both agents
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=git_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            prompt1 = Promptix.get_prompt("test_agent", user_name="Alice", task_type="coding")
            prompt2 = Promptix.get_prompt("agent2", topic="Python")
            
            assert "Alice" in prompt1
            assert "Python" in prompt2
    
    def test_error_recovery_workflow(self, git_workspace):
        """Test error recovery in the complete workflow"""
        os.chdir(git_workspace)
        
        # Test hook bypassing
        os.environ['SKIP_PROMPTIX_HOOK'] = '1'
        
        try:
            tester = PreCommitHookTester(git_workspace)
            success, processed_count, messages = tester.main_hook_logic([])
            
            assert success is True
            assert processed_count == 0
            assert any("skipped" in msg for msg in messages)
            
        finally:
            del os.environ['SKIP_PROMPTIX_HOOK']
        
        # Test corrupted config handling
        config_path = git_workspace / "prompts" / "test_agent" / "config.yaml"
        with open(config_path, "w") as f:
            f.write("invalid: yaml: [content")
        
        tester = PreCommitHookTester(git_workspace)
        
        # Should not crash
        success, processed_count, messages = tester.main_hook_logic(["prompts/test_agent/current.md"])
        
        assert success is True  # Always succeeds
        # Might have processed_count == 0 due to error
        
        # Test API graceful handling
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=git_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            # Should handle corrupted config gracefully
            try:
                loader = PromptLoader()
                prompts = loader.load_prompts()
                # Might raise StorageError or skip the corrupted agent
            except Exception:
                # Error handling depends on implementation
                pass


class TestVersioningBackwardsCompatibility:
    """Test backwards compatibility with existing prompts"""
    
    @pytest.fixture 
    def legacy_workspace(self):
        """Create workspace with legacy prompt structure"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_legacy_integration_"))
        
        # Create legacy prompt structure (no current_version tracking)
        prompts_dir = temp_dir / "prompts"
        agent_dir = prompts_dir / "legacy_agent"
        agent_dir.mkdir(parents=True)
        
        # Legacy config without current_version
        config_content = {
            'metadata': {'name': 'LegacyAgent'},
            'schema': {'type': 'object', 'properties': {'user': {'type': 'string'}}},
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Legacy agent prompt for {{user}}")
        
        # Legacy versions without headers
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        with open(versions_dir / "v1.md", "w") as f:
            f.write("Legacy version 1 for {{user}}")
        
        with open(versions_dir / "v2.md", "w") as f:
            f.write("Legacy version 2 for {{user}}")
        
        yield temp_dir
        
        safe_rmtree(temp_dir)
    
    def test_legacy_prompt_api_compatibility(self, legacy_workspace):
        """Test that legacy prompts still work with the API"""
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=legacy_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            # Should load legacy prompts
            loader = PromptLoader()
            prompts = loader.load_prompts()
            
            assert 'legacy_agent' in prompts
            
            # API should work
            prompt = Promptix.get_prompt("legacy_agent", user="TestUser")
            assert "TestUser" in prompt
    
    def test_legacy_prompt_version_requests(self, legacy_workspace):
        """Test version requests on legacy prompts"""
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=legacy_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            # Should be able to request specific versions
            prompt_v1 = Promptix.get_prompt("legacy_agent", version="v1", user="TestUser")
            assert "TestUser" in prompt_v1
            
            prompt_v2 = Promptix.get_prompt("legacy_agent", version="v2", user="TestUser") 
            assert "TestUser" in prompt_v2
    
    def test_legacy_to_new_migration(self, legacy_workspace):
        """Test migration from legacy to new version management"""
        # Add current_version to legacy config
        config_path = legacy_workspace / "prompts" / "legacy_agent" / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        config['current_version'] = 'v2'
        config['versions'] = {
            'v1': {'notes': 'Legacy version 1'},
            'v2': {'notes': 'Legacy version 2'}
        }
        
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        
        # Should now use new version management
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=legacy_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            prompts = loader.load_prompts()
            
            agent_data = prompts['legacy_agent']
            versions = agent_data['versions']
            
            # v2 should be live
            live_versions = [k for k, v in versions.items() if v.get('is_live', False)]
            assert 'v2' in live_versions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
