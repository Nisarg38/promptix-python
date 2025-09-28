"""
Unit tests for the enhanced prompt loader with auto-versioning support.

Tests the new functionality added to support current_version tracking,
version header removal, and metadata integration.
"""

import pytest
import tempfile
import shutil
import yaml
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from promptix.core.components.prompt_loader import PromptLoader
from promptix.core.exceptions import StorageError


class TestEnhancedPromptLoader:
    """Test the enhanced prompt loader functionality"""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace with versioned prompts"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_enhanced_loader_"))
        
        # Create agent with both old and new version features
        agent_dir = temp_dir / "prompts" / "test_agent"
        agent_dir.mkdir(parents=True)
        
        # Create config.yaml with new version tracking
        config_content = {
            'metadata': {
                'name': 'TestAgent',
                'description': 'Enhanced test agent',
                'author': 'Test Team',
            },
            'current_version': 'v002',  # NEW: current version tracking
            'versions': {  # NEW: version history
                'v001': {
                    'created_at': '2024-01-01T10:00:00',
                    'author': 'developer',
                    'commit': 'abc1234',
                    'notes': 'Initial version'
                },
                'v002': {
                    'created_at': '2024-01-02T11:00:00', 
                    'author': 'developer',
                    'commit': 'def5678',
                    'notes': 'Updated version'
                },
                'v003': {
                    'created_at': '2024-01-03T12:00:00',
                    'author': 'developer', 
                    'commit': 'ghi9012',
                    'notes': 'Latest version'
                }
            },
            'schema': {
                'type': 'object',
                'properties': {'user_name': {'type': 'string'}},
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
        
        # Create current.md (should match v002)
        with open(agent_dir / "current.md", "w") as f:
            f.write("You are a helpful assistant. Help {{user_name}} with tasks.")
        
        # Create versions directory with version files
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        # v001 - Simple version
        with open(versions_dir / "v001.md", "w") as f:
            f.write("<!-- Version v001 - Created 2024-01-01T10:00:00 -->\nYou are an assistant.")
        
        # v002 - With version header (should be live)
        with open(versions_dir / "v002.md", "w") as f:
            f.write("<!-- Version v002 - Created 2024-01-02T11:00:00 -->\nYou are a helpful assistant. Help {{user_name}} with tasks.")
        
        # v003 - Latest but not live
        with open(versions_dir / "v003.md", "w") as f:
            f.write("<!-- Version v003 - Created 2024-01-03T12:00:00 -->\nYou are an expert assistant helping {{user_name}}.")
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def legacy_workspace(self):
        """Create a workspace with legacy version structure (no current_version tracking)"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_legacy_loader_"))
        
        agent_dir = temp_dir / "prompts" / "legacy_agent"
        agent_dir.mkdir(parents=True)
        
        # Config without current_version tracking
        config_content = {
            'metadata': {'name': 'LegacyAgent'},
            'schema': {'type': 'object', 'properties': {'user': {'type': 'string'}}},
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Legacy prompt content")
        
        # Legacy versions without headers
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        with open(versions_dir / "v1.md", "w") as f:
            f.write("Legacy version 1 content")
        
        with open(versions_dir / "v2.md", "w") as f:
            f.write("Legacy version 2 content")
        
        yield temp_dir
        
        shutil.rmtree(temp_dir)
    
    def test_current_version_tracking(self, temp_workspace):
        """Test that current_version from config.yaml controls which version is live"""
        # Mock config to use our test workspace
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=temp_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            prompts = loader.load_prompts()
            
            assert 'test_agent' in prompts
            agent_data = prompts['test_agent']
            
            # Check version structure
            assert 'versions' in agent_data
            versions = agent_data['versions']
            
            # Find live version
            live_versions = [k for k, v in versions.items() if v.get('is_live', False)]
            
            assert len(live_versions) == 1
            assert live_versions[0] == 'v002'  # Should match current_version in config
    
    def test_version_header_removal(self, temp_workspace):
        """Test that version headers are removed from version content"""
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=temp_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            prompts = loader.load_prompts()
            
            versions = prompts['test_agent']['versions']
            
            # Check that headers were removed
            for version_key, version_data in versions.items():
                if version_key != 'current':  # Skip the current version
                    system_instruction = version_data['config']['system_instruction']
                    assert not system_instruction.startswith('<!-- Version')
                    assert '<!-- Version' not in system_instruction
    
    def test_version_metadata_integration(self, temp_workspace):
        """Test that version metadata from config.yaml is integrated"""
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=temp_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            prompts = loader.load_prompts()
            
            versions = prompts['test_agent']['versions']
            
            # Check v001 metadata
            v001 = versions['v001']
            assert 'metadata' in v001
            metadata = v001['metadata']
            
            assert metadata['created_at'] == '2024-01-01T10:00:00'
            assert metadata['author'] == 'developer'
            assert metadata['commit'] == 'abc1234'
            assert metadata['notes'] == 'Initial version'
    
    def test_legacy_compatibility(self, legacy_workspace):
        """Test that legacy prompts without current_version still work"""
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=legacy_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            prompts = loader.load_prompts()
            
            assert 'legacy_agent' in prompts
            agent_data = prompts['legacy_agent']
            
            # Should still have versions
            assert 'versions' in agent_data
            versions = agent_data['versions']
            
            # Should have 'current' version as live (fallback behavior)
            live_versions = [k for k, v in versions.items() if v.get('is_live', False)]
            assert len(live_versions) == 1
            assert 'current' in live_versions or len([k for k in versions.keys() if k != 'current']) > 0
    
    def test_empty_version_files_skipped(self, temp_workspace):
        """Test that empty version files are skipped"""
        # Create empty version file
        versions_dir = temp_workspace / "prompts" / "test_agent" / "versions"
        (versions_dir / "v004.md").touch()  # Create empty file
        
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=temp_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            prompts = loader.load_prompts()
            
            versions = prompts['test_agent']['versions']
            
            # v004 should not be loaded (empty file)
            assert 'v004' not in versions
    
    def test_version_switching_behavior(self, temp_workspace):
        """Test that changing current_version changes which version is live"""
        # First load with v002 as current
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=temp_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            prompts = loader.load_prompts()
            
            live_versions = [k for k, v in prompts['test_agent']['versions'].items() if v.get('is_live', False)]
            assert 'v002' in live_versions
        
        # Update config to switch to v003
        config_path = temp_workspace / "prompts" / "test_agent" / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        config['current_version'] = 'v003'
        
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Reload and check that v003 is now live
        loader = PromptLoader()
        prompts = loader.load_prompts(force_reload=True)
        
        live_versions = [k for k, v in prompts['test_agent']['versions'].items() if v.get('is_live', False)]
        assert 'v003' in live_versions
        assert 'v002' not in live_versions
    
    def test_missing_current_version_fallback(self, temp_workspace):
        """Test fallback behavior when current_version points to non-existent version"""
        # Update config to point to non-existent version
        config_path = temp_workspace / "prompts" / "test_agent" / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        config['current_version'] = 'v999'  # Doesn't exist
        
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=temp_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            prompts = loader.load_prompts()
            
            # Should still have a live version (fallback behavior)
            versions = prompts['test_agent']['versions']
            live_versions = [k for k, v in versions.items() if v.get('is_live', False)]
            
            assert len(live_versions) >= 1  # Should fallback to some version


class TestEnhancedPromptLoaderErrorHandling:
    """Test error handling in the enhanced prompt loader"""
    
    @pytest.fixture
    def broken_workspace(self):
        """Create a workspace with various error conditions"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_broken_loader_"))
        
        # Agent with invalid config
        broken_agent_dir = temp_dir / "prompts" / "broken_agent"
        broken_agent_dir.mkdir(parents=True)
        
        # Invalid YAML
        with open(broken_agent_dir / "config.yaml", "w") as f:
            f.write("invalid: yaml: [unclosed")
        
        with open(broken_agent_dir / "current.md", "w") as f:
            f.write("Broken agent prompt")
        
        yield temp_dir
        
        shutil.rmtree(temp_dir)
    
    def test_invalid_yaml_handling(self, broken_workspace):
        """Test handling of invalid YAML in config files"""
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=broken_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            
            # Should not crash, might log warnings
            with pytest.raises(StorageError):
                prompts = loader.load_prompts()
    
    def test_missing_versions_directory(self, broken_workspace):
        """Test handling when versions directory doesn't exist"""
        # Create agent without versions directory
        good_agent_dir = broken_workspace / "prompts" / "good_agent"
        good_agent_dir.mkdir(parents=True)
        
        config_content = {
            'metadata': {'name': 'GoodAgent'},
            'current_version': 'v001',  # Points to version that doesn't exist
            'config': {'model': 'gpt-4'}
        }
        
        with open(good_agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(good_agent_dir / "current.md", "w") as f:
            f.write("Good agent prompt")
        
        # No versions directory created
        
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=broken_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            loader = PromptLoader()
            prompts = loader.load_prompts()
            
            # Should still work, fallback to 'current' version
            assert 'good_agent' in prompts
            agent_data = prompts['good_agent']
            
            assert 'versions' in agent_data
            versions = agent_data['versions']
            
            # Should have 'current' version from current.md
            assert 'current' in versions
    
    def test_corrupted_version_files(self, broken_workspace):
        """Test handling of corrupted version files"""
        agent_dir = broken_workspace / "prompts" / "test_agent"
        agent_dir.mkdir(parents=True)
        
        config_content = {
            'metadata': {'name': 'TestAgent'},
            'current_version': 'v001',
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test prompt")
        
        # Create versions directory with corrupted file
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        # Create a file that can't be read (simulate permission error)
        version_file = versions_dir / "v001.md"
        version_file.touch()
        
        with patch('promptix.core.config.config.get_prompts_workspace_path', 
                   return_value=broken_workspace / "prompts"), \
             patch('promptix.core.config.config.has_prompts_workspace', return_value=True):
            
            # Mock file read to raise PermissionError for version file
            original_open = open
            def mock_open(*args, **kwargs):
                if 'v001.md' in str(args[0]):
                    raise PermissionError("Access denied")
                return original_open(*args, **kwargs)
            
            with patch('builtins.open', side_effect=mock_open):
                loader = PromptLoader()
                prompts = loader.load_prompts()
                
                # Should still work, just skip the corrupted version
                assert 'test_agent' in prompts
                versions = prompts['test_agent']['versions']
                
                # v001 should not be loaded due to error
                assert 'v001' not in versions or not versions['v001']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
