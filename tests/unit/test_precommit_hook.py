"""
Unit tests for the pre-commit hook auto-versioning functionality.

Tests the core logic of the pre-commit hook without requiring git setup.
"""

import pytest
import tempfile
import shutil
import yaml
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call

# Add the hooks directory to the Python path
project_root = Path(__file__).parent.parent.parent
hooks_dir = project_root / "hooks"
sys.path.insert(0, str(hooks_dir))

# Import the pre-commit hook functions (we'll need to modify the hook to make functions importable)
from test_helpers.precommit_helper import PreCommitHookTester


class TestPreCommitHookCore:
    """Test the core functionality of the pre-commit hook"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_precommit_"))
        
        # Create basic structure
        agent_dir = temp_dir / "prompts" / "test_agent"
        agent_dir.mkdir(parents=True)
        
        # Create config.yaml
        config_content = {
            'metadata': {
                'name': 'TestAgent',
                'description': 'Test agent',
                'author': 'Test',
            },
            'schema': {
                'type': 'object',
                'properties': {'user_name': {'type': 'string'}},
                'required': ['user_name']
            },
            'config': {
                'model': 'gpt-4',
                'temperature': 0.7
            }
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        # Create current.md
        with open(agent_dir / "current.md", "w") as f:
            f.write("Initial prompt content for {{user_name}}")
        
        # Create versions directory
        (agent_dir / "versions").mkdir()
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_find_promptix_changes_current_md(self, temp_workspace):
        """Test finding changes to current.md files"""
        tester = PreCommitHookTester(temp_workspace)
        
        # Mock git diff output for current.md change
        staged_files = ["prompts/test_agent/current.md", "other_file.py"]
        
        changes = tester.find_promptix_changes(staged_files)
        
        assert "prompts/test_agent/current.md" in changes['current_md']
        assert len(changes['current_md']) == 1
        assert len(changes['config_yaml']) == 0
    
    def test_find_promptix_changes_config_yaml(self, temp_workspace):
        """Test finding changes to config.yaml files"""
        tester = PreCommitHookTester(temp_workspace)
        
        staged_files = ["prompts/test_agent/config.yaml", "README.md"]
        
        changes = tester.find_promptix_changes(staged_files)
        
        assert "prompts/test_agent/config.yaml" in changes['config_yaml']
        assert len(changes['config_yaml']) == 1
        assert len(changes['current_md']) == 0
    
    def test_find_promptix_changes_both(self, temp_workspace):
        """Test finding changes to both current.md and config.yaml"""
        tester = PreCommitHookTester(temp_workspace)
        
        staged_files = [
            "prompts/test_agent/current.md",
            "prompts/test_agent/config.yaml",
            "prompts/other_agent/current.md",
            "unrelated_file.txt"
        ]
        
        changes = tester.find_promptix_changes(staged_files)
        
        assert len(changes['current_md']) == 2
        assert len(changes['config_yaml']) == 1
        assert "prompts/test_agent/current.md" in changes['current_md']
        assert "prompts/other_agent/current.md" in changes['current_md']
        assert "prompts/test_agent/config.yaml" in changes['config_yaml']
    
    def test_get_next_version_number_first_version(self, temp_workspace):
        """Test getting version number when no versions exist"""
        tester = PreCommitHookTester(temp_workspace)
        
        versions_dir = temp_workspace / "prompts" / "test_agent" / "versions"
        version_num = tester.get_next_version_number(versions_dir)
        
        assert version_num == 1
    
    def test_get_next_version_number_existing_versions(self, temp_workspace):
        """Test getting version number when versions exist"""
        tester = PreCommitHookTester(temp_workspace)
        
        versions_dir = temp_workspace / "prompts" / "test_agent" / "versions"
        
        # Create some version files
        (versions_dir / "v001.md").touch()
        (versions_dir / "v003.md").touch()
        (versions_dir / "v002.md").touch()
        
        version_num = tester.get_next_version_number(versions_dir)
        
        assert version_num == 4  # Should be max + 1
    
    def test_create_version_snapshot_success(self, temp_workspace):
        """Test successful version snapshot creation"""
        tester = PreCommitHookTester(temp_workspace)
        
        current_md_path = "prompts/test_agent/current.md"
        
        # Update current.md content
        with open(temp_workspace / current_md_path, "w") as f:
            f.write("Updated prompt content for {{user_name}}")
        
        # Mock git operations
        with patch.object(tester, 'stage_files'), \
             patch.object(tester, 'get_current_commit_hash', return_value='abc123'):
            
            version_name = tester.create_version_snapshot(current_md_path)
        
        assert version_name == "v001"
        
        # Check version file was created
        version_file = temp_workspace / "prompts" / "test_agent" / "versions" / "v001.md"
        assert version_file.exists()
        
        # Check version content
        with open(version_file, "r") as f:
            content = f.read()
        
        assert "<!-- Version v001" in content
        assert "Updated prompt content for {{user_name}}" in content
        
        # Check config was updated
        with open(temp_workspace / "prompts" / "test_agent" / "config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        assert 'versions' in config
        assert 'v001' in config['versions']
        assert config['versions']['v001']['notes'] == 'Auto-versioned on commit'
    
    def test_handle_version_switch_success(self, temp_workspace):
        """Test successful version switching"""
        tester = PreCommitHookTester(temp_workspace)
        
        # Create a version to switch to
        versions_dir = temp_workspace / "prompts" / "test_agent" / "versions"
        version_content = "Version 1 content for {{user_name}}"
        
        with open(versions_dir / "v001.md", "w") as f:
            f.write(f"<!-- Version v001 -->\n{version_content}")
        
        # Update config to specify current_version
        config_path = temp_workspace / "prompts" / "test_agent" / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        config['current_version'] = 'v001'
        
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        
        # Mock git operations
        with patch.object(tester, 'stage_files'):
            success = tester.handle_version_switch(str(config_path))
        
        assert success is True
        
        # Check current.md was updated
        current_md = temp_workspace / "prompts" / "test_agent" / "current.md"
        with open(current_md, "r") as f:
            content = f.read()
        
        assert content.strip() == version_content
    
    def test_handle_version_switch_version_not_found(self, temp_workspace):
        """Test version switching when version doesn't exist"""
        tester = PreCommitHookTester(temp_workspace)
        
        # Update config to specify non-existent version
        config_path = temp_workspace / "prompts" / "test_agent" / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        config['current_version'] = 'v999'
        
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        
        success = tester.handle_version_switch(str(config_path))
        
        assert success is False
    
    @patch.dict(os.environ, {'SKIP_PROMPTIX_HOOK': '1'})
    def test_bypass_hook_with_environment(self, temp_workspace):
        """Test bypassing hook with environment variable"""
        tester = PreCommitHookTester(temp_workspace)
        
        assert tester.is_hook_bypassed() is True
    
    def test_bypass_hook_without_environment(self, temp_workspace):
        """Test hook not bypassed without environment variable"""
        tester = PreCommitHookTester(temp_workspace)
        
        with patch.dict(os.environ, {}, clear=True):
            assert tester.is_hook_bypassed() is False


class TestPreCommitHookIntegration:
    """Test integration scenarios for the pre-commit hook"""
    
    @pytest.fixture
    def git_workspace(self):
        """Create a temporary workspace with git initialized"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_git_precommit_"))
        
        # Initialize git repo
        os.chdir(temp_dir)
        os.system("git init")
        os.system("git config user.name 'Test User'")
        os.system("git config user.email 'test@example.com'")
        
        # Create promptix structure
        agent_dir = temp_dir / "prompts" / "test_agent"
        agent_dir.mkdir(parents=True)
        
        config_content = {
            'metadata': {'name': 'TestAgent'},
            'schema': {'type': 'object', 'properties': {'user': {'type': 'string'}}},
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Initial prompt for {{user}}")
        
        (agent_dir / "versions").mkdir()
        
        yield temp_dir
        
        # Cleanup
        os.chdir("/")
        shutil.rmtree(temp_dir)
    
    def test_multiple_agents_same_commit(self, git_workspace):
        """Test handling multiple agent changes in same commit"""
        tester = PreCommitHookTester(git_workspace)
        
        # Create second agent
        agent2_dir = git_workspace / "prompts" / "agent2"
        agent2_dir.mkdir()
        
        with open(agent2_dir / "config.yaml", "w") as f:
            yaml.dump({'metadata': {'name': 'Agent2'}, 'config': {'model': 'gpt-4'}}, f)
        
        with open(agent2_dir / "current.md", "w") as f:
            f.write("Agent2 prompt")
        
        (agent2_dir / "versions").mkdir()
        
        # Mock staged files for both agents
        staged_files = [
            "prompts/test_agent/current.md",
            "prompts/agent2/current.md"
        ]
        
        changes = tester.find_promptix_changes(staged_files)
        
        assert len(changes['current_md']) == 2
        
        # Mock successful processing
        with patch.object(tester, 'stage_files'), \
             patch.object(tester, 'get_current_commit_hash', return_value='abc123'):
            
            processed_count = 0
            for current_md_path in changes['current_md']:
                version_name = tester.create_version_snapshot(current_md_path)
                if version_name:
                    processed_count += 1
        
        assert processed_count == 2
    
    def test_config_only_changes(self, git_workspace):
        """Test that config-only changes don't trigger versioning"""
        tester = PreCommitHookTester(git_workspace)
        
        staged_files = ["prompts/test_agent/config.yaml"]
        changes = tester.find_promptix_changes(staged_files)
        
        assert len(changes['current_md']) == 0
        assert len(changes['config_yaml']) == 1
        
        # Should handle version switch if current_version changed
        config_path = git_workspace / "prompts" / "test_agent" / "config.yaml"
        
        # First create a version to switch to
        with open(git_workspace / "prompts" / "test_agent" / "versions" / "v001.md", "w") as f:
            f.write("Test version content")
        
        # Update config with current_version
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        config['current_version'] = 'v001'
        
        with open(config_path, "w") as f:
            yaml.dump(config, f)
        
        with patch.object(tester, 'stage_files'):
            success = tester.handle_version_switch(str(config_path))
        
        assert success is True


class TestPreCommitHookErrorHandling:
    """Test error handling and edge cases in the pre-commit hook"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a minimal workspace for error testing"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_error_precommit_"))
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_missing_config_file(self, temp_workspace):
        """Test handling missing config.yaml file"""
        tester = PreCommitHookTester(temp_workspace)
        
        # Create current.md without config.yaml
        agent_dir = temp_workspace / "prompts" / "test_agent"
        agent_dir.mkdir(parents=True)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        version_name = tester.create_version_snapshot("prompts/test_agent/current.md")
        
        assert version_name is None  # Should fail gracefully
    
    def test_invalid_yaml_config(self, temp_workspace):
        """Test handling invalid YAML in config file"""
        tester = PreCommitHookTester(temp_workspace)
        
        agent_dir = temp_workspace / "prompts" / "test_agent"
        agent_dir.mkdir(parents=True)
        
        # Create invalid YAML
        with open(agent_dir / "config.yaml", "w") as f:
            f.write("invalid: yaml: content: [unclosed")
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        version_name = tester.create_version_snapshot("prompts/test_agent/current.md")
        
        assert version_name is None  # Should fail gracefully
    
    def test_permission_denied_version_creation(self, temp_workspace):
        """Test handling permission denied when creating versions"""
        tester = PreCommitHookTester(temp_workspace)
        
        agent_dir = temp_workspace / "prompts" / "test_agent"
        agent_dir.mkdir(parents=True)
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump({'metadata': {'name': 'Test'}}, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        # Mock permission error
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            version_name = tester.create_version_snapshot("prompts/test_agent/current.md")
        
        assert version_name is None  # Should fail gracefully
    
    def test_empty_current_md_file(self, temp_workspace):
        """Test handling empty current.md file"""
        tester = PreCommitHookTester(temp_workspace)
        
        agent_dir = temp_workspace / "prompts" / "test_agent"
        agent_dir.mkdir(parents=True)
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump({'metadata': {'name': 'Test'}}, f)
        
        # Create empty current.md
        (agent_dir / "current.md").touch()
        (agent_dir / "versions").mkdir()
        
        with patch.object(tester, 'stage_files'), \
             patch.object(tester, 'get_current_commit_hash', return_value='abc123'):
            
            version_name = tester.create_version_snapshot("prompts/test_agent/current.md")
        
        # Should still work with empty content
        assert version_name == "v001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
