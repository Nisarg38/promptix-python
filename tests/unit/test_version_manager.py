"""
Unit tests for the VersionManager CLI tool.

Tests the command-line interface for manual version management.
"""

import pytest
import tempfile
import shutil
import yaml
import io
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from promptix.tools.version_manager import VersionManager


class TestVersionManager:
    """Test the VersionManager CLI functionality"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace with multiple agents and versions"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_version_manager_"))
        
        # Create prompts directory
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        
        # Agent 1: test_agent with multiple versions
        agent1_dir = prompts_dir / "test_agent"
        agent1_dir.mkdir()
        
        config1_content = {
            'metadata': {
                'name': 'TestAgent',
                'description': 'Test agent for version management',
                'author': 'Test Team',
            },
            'current_version': 'v002',
            'versions': {
                'v001': {
                    'created_at': '2024-01-01T10:00:00',
                    'author': 'developer',
                    'notes': 'Initial version'
                },
                'v002': {
                    'created_at': '2024-01-02T11:00:00', 
                    'author': 'developer',
                    'notes': 'Updated version'
                }
            },
            'schema': {'type': 'object', 'properties': {'user': {'type': 'string'}}},
            'config': {'model': 'gpt-4', 'temperature': 0.7}
        }
        
        with open(agent1_dir / "config.yaml", "w") as f:
            yaml.dump(config1_content, f, default_flow_style=False)
        
        with open(agent1_dir / "current.md", "w") as f:
            f.write("Current version of test agent")
        
        # Create versions
        versions1_dir = agent1_dir / "versions"
        versions1_dir.mkdir()
        
        with open(versions1_dir / "v001.md", "w") as f:
            f.write("Version 1 content")
        
        with open(versions1_dir / "v002.md", "w") as f:
            f.write("Version 2 content")
        
        # Agent 2: simple_agent with fewer versions
        agent2_dir = prompts_dir / "simple_agent"
        agent2_dir.mkdir()
        
        config2_content = {
            'metadata': {'name': 'SimpleAgent', 'description': 'Simple test agent'},
            'current_version': 'v001',
            'versions': {
                'v001': {
                    'created_at': '2024-01-01T15:00:00',
                    'author': 'developer',
                    'notes': 'Only version'
                }
            },
            'config': {'model': 'gpt-3.5-turbo'}
        }
        
        with open(agent2_dir / "config.yaml", "w") as f:
            yaml.dump(config2_content, f)
        
        with open(agent2_dir / "current.md", "w") as f:
            f.write("Simple agent content")
        
        versions2_dir = agent2_dir / "versions"
        versions2_dir.mkdir()
        
        with open(versions2_dir / "v001.md", "w") as f:
            f.write("Simple agent version 1")
        
        yield temp_dir
        
        shutil.rmtree(temp_dir)
    
    def test_initialization(self, temp_workspace):
        """Test VersionManager initialization"""
        vm = VersionManager(str(temp_workspace))
        
        assert vm.workspace_path == temp_workspace
        assert vm.prompts_dir == temp_workspace / "prompts"
        assert vm.prompts_dir.exists()
    
    def test_find_agent_dirs(self, temp_workspace):
        """Test finding agent directories"""
        vm = VersionManager(str(temp_workspace))
        
        agent_dirs = vm.find_agent_dirs()
        
        assert len(agent_dirs) == 2
        agent_names = [d.name for d in agent_dirs]
        assert "test_agent" in agent_names
        assert "simple_agent" in agent_names
    
    def test_list_agents(self, temp_workspace):
        """Test listing all agents with their current versions"""
        vm = VersionManager(str(temp_workspace))
        
        # Capture stdout
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.list_agents()
        
        output = captured_output.getvalue()
        
        # Check output contains agent information
        assert "TestAgent" in output
        assert "SimpleAgent" in output
        assert "Current Version: v002" in output
        assert "Current Version: v001" in output
        assert "Test agent for version management" in output
    
    def test_list_versions(self, temp_workspace):
        """Test listing versions for a specific agent"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.list_versions("test_agent")
        
        output = captured_output.getvalue()
        
        # Check output contains version information
        assert "Versions for test_agent" in output
        assert "Current Version: v002" in output
        assert "v001" in output
        assert "v002" in output
        assert "← CURRENT" in output  # Should mark current version
        assert "Initial version" in output
        assert "Updated version" in output
    
    def test_list_versions_nonexistent_agent(self, temp_workspace):
        """Test listing versions for non-existent agent"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.list_versions("nonexistent_agent")
        
        output = captured_output.getvalue()
        assert "not found" in output.lower()
    
    def test_get_version(self, temp_workspace):
        """Test getting content of a specific version"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.get_version("test_agent", "v001")
        
        output = captured_output.getvalue()
        
        # Should display version content
        assert "Content of test_agent/v001" in output
        assert "Version 1 content" in output
    
    def test_get_version_nonexistent(self, temp_workspace):
        """Test getting content of non-existent version"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.get_version("test_agent", "v999")
        
        output = captured_output.getvalue()
        assert "not found" in output.lower()
    
    def test_switch_version_success(self, temp_workspace):
        """Test successful version switching"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.switch_version("test_agent", "v001")
        
        output = captured_output.getvalue()
        
        # Should indicate success
        assert "Switched test_agent to v001" in output
        
        # Check that config was updated
        config_path = temp_workspace / "prompts" / "test_agent" / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        assert config['current_version'] == 'v001'
        
        # Check that current.md was updated
        current_path = temp_workspace / "prompts" / "test_agent" / "current.md"
        with open(current_path, "r") as f:
            content = f.read()
        
        assert content.strip() == "Version 1 content"
    
    def test_switch_version_nonexistent_agent(self, temp_workspace):
        """Test switching version for non-existent agent"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.switch_version("nonexistent_agent", "v001")
        
        output = captured_output.getvalue()
        assert "not found" in output.lower()
    
    def test_switch_version_nonexistent_version(self, temp_workspace):
        """Test switching to non-existent version"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.switch_version("test_agent", "v999")
        
        output = captured_output.getvalue()
        assert "not found" in output.lower()
    
    def test_create_version_auto_name(self, temp_workspace):
        """Test creating new version with auto-generated name"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.create_version("test_agent", None, "Test creation")
        
        output = captured_output.getvalue()
        
        # Should create v003 (next in sequence)
        assert "Created version v003 for test_agent" in output
        
        # Check version file was created
        version_file = temp_workspace / "prompts" / "test_agent" / "versions" / "v003.md"
        assert version_file.exists()
        
        # Check content
        with open(version_file, "r") as f:
            content = f.read()
        
        assert "Current version of test agent" in content
        
        # Check config was updated
        config_path = temp_workspace / "prompts" / "test_agent" / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        assert 'v003' in config['versions']
        assert config['versions']['v003']['notes'] == 'Test creation'
        assert config['current_version'] == 'v003'
    
    def test_create_version_explicit_name(self, temp_workspace):
        """Test creating new version with explicit name"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.create_version("test_agent", "v010", "Custom version")
        
        output = captured_output.getvalue()
        
        assert "Created version v010 for test_agent" in output
        
        # Check version file was created
        version_file = temp_workspace / "prompts" / "test_agent" / "versions" / "v010.md"
        assert version_file.exists()
    
    def test_create_version_duplicate_name(self, temp_workspace):
        """Test creating version with duplicate name"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.create_version("test_agent", "v001", "Duplicate")
        
        output = captured_output.getvalue()
        assert "already exists" in output.lower()
    
    def test_create_version_nonexistent_agent(self, temp_workspace):
        """Test creating version for non-existent agent"""
        vm = VersionManager(str(temp_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.create_version("nonexistent_agent", None, "Test")
        
        output = captured_output.getvalue()
        assert "not found" in output.lower()
    
    def test_create_version_missing_current_md(self, temp_workspace):
        """Test creating version when current.md doesn't exist"""
        vm = VersionManager(str(temp_workspace))
        
        # Remove current.md
        current_path = temp_workspace / "prompts" / "test_agent" / "current.md"
        current_path.unlink()
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.create_version("test_agent", None, "Test")
        
        output = captured_output.getvalue()
        assert "current.md" in output.lower()


class TestVersionManagerErrorHandling:
    """Test error handling in VersionManager"""
    
    @pytest.fixture
    def broken_workspace(self):
        """Create workspace with error conditions"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_broken_version_manager_"))
        
        # Create prompts directory but no agents
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        
        yield temp_dir
        
        shutil.rmtree(temp_dir)
    
    def test_no_agents_found(self, broken_workspace):
        """Test behavior when no agents are found"""
        vm = VersionManager(str(broken_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.list_agents()
        
        output = captured_output.getvalue()
        assert "No agents found" in output
    
    def test_invalid_workspace_path(self):
        """Test initialization with invalid workspace path"""
        with pytest.raises(ValueError):
            vm = VersionManager("/nonexistent/path")
    
    def test_corrupted_config_file(self, broken_workspace):
        """Test handling corrupted config files"""
        # Create agent with corrupted config
        agent_dir = broken_workspace / "prompts" / "broken_agent"
        agent_dir.mkdir()
        
        with open(agent_dir / "config.yaml", "w") as f:
            f.write("invalid: yaml: [content")
        
        vm = VersionManager(str(broken_workspace))
        
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            vm.list_agents()
        
        # Should handle error gracefully
        output = captured_output.getvalue()
        # Should not crash, might show warning or skip the agent
    
    def test_permission_denied_file_operations(self, broken_workspace):
        """Test handling permission denied errors"""
        # Create agent
        agent_dir = broken_workspace / "prompts" / "test_agent"
        agent_dir.mkdir()
        
        config_content = {
            'metadata': {'name': 'TestAgent'},
            'current_version': 'v001',
            'versions': {},
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        vm = VersionManager(str(broken_workspace))
        
        # Mock file operations to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            captured_output = io.StringIO()
            with patch('sys.stdout', captured_output):
                vm.create_version("test_agent", None, "Test")
            
            output = captured_output.getvalue()
            # Should handle error gracefully
            # Exact message depends on implementation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
