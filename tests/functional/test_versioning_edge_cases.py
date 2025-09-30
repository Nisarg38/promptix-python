"""
Edge case and error condition tests for the auto-versioning system.

Tests unusual scenarios, error conditions, and boundary cases
to ensure robust operation.
"""

import pytest
import tempfile
import shutil
import yaml
import os
import stat
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add test helpers
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "tests" / "test_helpers"))

from precommit_helper import PreCommitHookTester


class TestVersioningEdgeCases:
    """Test edge cases in the versioning system"""
    
    @pytest.fixture
    def edge_case_workspace(self):
        """Create workspace for edge case testing"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_edge_cases_"))
        
        # Create basic structure
        prompts_dir = temp_dir / "prompts"
        prompts_dir.mkdir()
        
        yield temp_dir
        
        shutil.rmtree(temp_dir)
    
    def test_empty_current_md_file(self, edge_case_workspace):
        """Test handling completely empty current.md files"""
        agent_dir = edge_case_workspace / "prompts" / "empty_agent"
        agent_dir.mkdir()
        
        # Create empty current.md
        (agent_dir / "current.md").touch()
        
        # Create minimal config
        config_content = {
            'metadata': {'name': 'EmptyAgent'},
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        (agent_dir / "versions").mkdir()
        
        tester = PreCommitHookTester(edge_case_workspace)
        
        # Should handle empty file gracefully
        version_name = tester.create_version_snapshot("prompts/empty_agent/current.md")
        
        # Should still create version (with empty content)
        assert version_name is not None
    
    def test_very_large_current_md_file(self, edge_case_workspace):
        """Test handling very large current.md files"""
        agent_dir = edge_case_workspace / "prompts" / "large_agent"
        agent_dir.mkdir()
        
        # Create very large current.md (1MB)
        large_content = "This is a large prompt. " * 50000  # ~1MB
        with open(agent_dir / "current.md", "w") as f:
            f.write(large_content)
        
        config_content = {
            'metadata': {'name': 'LargeAgent'},
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        (agent_dir / "versions").mkdir()
        
        tester = PreCommitHookTester(edge_case_workspace)
        
        # Should handle large file
        version_name = tester.create_version_snapshot("prompts/large_agent/current.md")
        assert version_name is not None
        
        # Check version file exists and has correct size
        version_file = agent_dir / "versions" / f"{version_name}.md"
        assert version_file.exists()
        
        with open(version_file, "r") as f:
            content = f.read()
        
        # Should contain the large content plus version header
        assert len(content) > 1000000  # Should be larger than 1MB due to header
    
    def test_unicode_and_special_characters(self, edge_case_workspace):
        """Test handling Unicode and special characters in prompts"""
        agent_dir = edge_case_workspace / "prompts" / "unicode_agent"
        agent_dir.mkdir()
        
        # Create current.md with Unicode and special characters
        unicode_content = """You are an assistant that speaks multiple languages: 
        
        English: Hello {{user_name}}! 
        Spanish: ¡Hola {{user_name}}!
        Chinese: 你好 {{user_name}}!
        Japanese: こんにちは {{user_name}}!
        Arabic: مرحبا {{user_name}}!
        Russian: Привет {{user_name}}!
        
        Special characters: @#$%^&*()_+-=[]{}|;:,.<>?
        
        Emoji: 🚀 🎯 ✅ ❌ 📝 🔄"""
        
        with open(agent_dir / "current.md", "w", encoding='utf-8') as f:
            f.write(unicode_content)
        
        config_content = {
            'metadata': {'name': 'UnicodeAgent', 'description': 'Multi-language agent'},
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        (agent_dir / "versions").mkdir()
        
        tester = PreCommitHookTester(edge_case_workspace)
        
        version_name = tester.create_version_snapshot("prompts/unicode_agent/current.md")
        assert version_name is not None
        
        # Verify Unicode content is preserved
        version_file = agent_dir / "versions" / f"{version_name}.md"
        with open(version_file, "r", encoding='utf-8') as f:
            content = f.read()
        
        assert "你好" in content
        assert "🚀" in content
        assert "مرحبا" in content
    
    def test_extremely_long_version_names(self, edge_case_workspace):
        """Test handling when version numbers get extremely large"""
        agent_dir = edge_case_workspace / "prompts" / "long_version_agent"
        agent_dir.mkdir()
        
        config_content = {
            'metadata': {'name': 'LongVersionAgent'},
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        # Create many existing versions to push version number high
        for i in range(1, 1000, 100):  # Create v001, v101, v201, etc.
            (versions_dir / f"v{i:03d}.md").touch()
        
        tester = PreCommitHookTester(edge_case_workspace)
        
        # Should handle large version numbers
        version_name = tester.create_version_snapshot("prompts/long_version_agent/current.md")
        assert version_name is not None
        
        # Should be v901 or similar
        assert version_name.startswith('v')
        version_num = int(version_name[1:])
        assert version_num >= 901
    
    def test_concurrent_version_creation(self, edge_case_workspace):
        """Test behavior when multiple processes try to create versions simultaneously"""
        agent_dir = edge_case_workspace / "prompts" / "concurrent_agent"
        agent_dir.mkdir()
        
        config_content = {
            'metadata': {'name': 'ConcurrentAgent'},
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Concurrent test content")
        
        (agent_dir / "versions").mkdir()
        
        # Simulate race condition by creating multiple testers
        tester1 = PreCommitHookTester(edge_case_workspace)
        tester2 = PreCommitHookTester(edge_case_workspace)
        
        # Both try to create versions
        version1 = tester1.create_version_snapshot("prompts/concurrent_agent/current.md")
        version2 = tester2.create_version_snapshot("prompts/concurrent_agent/current.md")
        
        # Both should succeed with different version numbers
        assert version1 is not None
        assert version2 is not None
        assert version1 != version2  # Should be different versions
    
    def test_malformed_version_files(self, edge_case_workspace):
        """Test handling of malformed existing version files"""
        agent_dir = edge_case_workspace / "prompts" / "malformed_agent"
        agent_dir.mkdir()
        
        config_content = {
            'metadata': {'name': 'MalformedAgent'},
            'current_version': 'v002',
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        # Create malformed version files
        with open(versions_dir / "invalid_name.md", "w") as f:
            f.write("Invalid version name")
        
        with open(versions_dir / "v.md", "w") as f:  # Missing number
            f.write("Missing version number")
        
        with open(versions_dir / "vabc.md", "w") as f:  # Non-numeric
            f.write("Non-numeric version")
        
        # Create valid version that should be used
        with open(versions_dir / "v002.md", "w") as f:
            f.write("Valid version 2")
        
        tester = PreCommitHookTester(edge_case_workspace)
        
        # Should handle malformed versions gracefully and switch to v002
        success = tester.handle_version_switch(str(agent_dir / "config.yaml"))
        assert success is True
        
        # current.md should contain v002 content
        with open(agent_dir / "current.md", "r") as f:
            content = f.read()
        
        assert "Valid version 2" in content
    
    def test_circular_version_references(self, edge_case_workspace):
        """Test handling potential circular references in version switching"""
        agent_dir = edge_case_workspace / "prompts" / "circular_agent"
        agent_dir.mkdir()
        
        # Create versions that might reference each other
        config_content = {
            'metadata': {'name': 'CircularAgent'},
            'current_version': 'v001',
            'versions': {
                'v001': {'notes': 'Points to v002'},
                'v002': {'notes': 'Points to v001'}
            },
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Original content")
        
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        with open(versions_dir / "v001.md", "w") as f:
            f.write("Version 1 content")
        
        with open(versions_dir / "v002.md", "w") as f:
            f.write("Version 2 content")
        
        tester = PreCommitHookTester(edge_case_workspace)
        
        # Switch to v001
        success = tester.handle_version_switch(str(agent_dir / "config.yaml"))
        assert success is True
        
        # Should contain v001 content, not get stuck in loop
        with open(agent_dir / "current.md", "r") as f:
            content = f.read()
        
        assert "Version 1 content" in content


class TestVersioningErrorConditions:
    """Test error conditions and recovery"""
    
    @pytest.fixture
    def error_workspace(self):
        """Create workspace for error testing"""
        temp_dir = Path(tempfile.mkdtemp(prefix="test_error_conditions_"))
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_disk_full_simulation(self, error_workspace):
        """Test behavior when disk is full"""
        agent_dir = error_workspace / "prompts" / "disk_full_agent"
        agent_dir.mkdir(parents=True)
        
        config_content = {'metadata': {'name': 'DiskFullAgent'}, 'config': {'model': 'gpt-4'}}
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        (agent_dir / "versions").mkdir()
        
        tester = PreCommitHookTester(error_workspace)
        
        # Mock file operations to raise OSError (disk full)
        with patch('shutil.copy2', side_effect=OSError("No space left on device")):
            version_name = tester.create_version_snapshot("prompts/disk_full_agent/current.md")
        
        # Should fail gracefully
        assert version_name is None
    
    def test_permission_denied_directories(self, error_workspace):
        """Test behavior with permission denied on directories"""
        agent_dir = error_workspace / "prompts" / "permission_agent"
        agent_dir.mkdir(parents=True)
        
        config_content = {'metadata': {'name': 'PermissionAgent'}, 'config': {'model': 'gpt-4'}}
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        tester = PreCommitHookTester(error_workspace)

        # Simulate permission denied when copying into versions directory
        with patch('shutil.copy2', side_effect=PermissionError("Permission denied")):
            version_name = tester.create_version_snapshot("prompts/permission_agent/current.md")

        # Should fail gracefully
        assert version_name is None
    def test_corrupted_git_repository(self, error_workspace):
        """Test behavior with corrupted git repository"""
        agent_dir = error_workspace / "prompts" / "git_corrupt_agent"
        agent_dir.mkdir(parents=True)
        
        config_content = {'metadata': {'name': 'GitCorruptAgent'}, 'config': {'model': 'gpt-4'}}
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        (agent_dir / "versions").mkdir()
        
        tester = PreCommitHookTester(error_workspace)
        
        # Mock git operations to fail
        with patch.object(tester, 'get_current_commit_hash', side_effect=Exception("Git error")):
            version_name = tester.create_version_snapshot("prompts/git_corrupt_agent/current.md")
        
        # Should still create version, just without git info
        assert version_name is not None
    
    def test_yaml_encoding_issues(self, error_workspace):
        """Test handling YAML files with encoding issues"""
        agent_dir = error_workspace / "prompts" / "encoding_agent"
        agent_dir.mkdir(parents=True)
        
        # Create config with unusual encoding
        config_content = "metadata:\n  name: EncodingAgent\n  special: 'ñoño'\nconfig:\n  model: gpt-4"
        with open(agent_dir / "config.yaml", "wb") as f:
            f.write(config_content.encode('latin1'))  # Non-UTF8 encoding
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        (agent_dir / "versions").mkdir()
        
        tester = PreCommitHookTester(error_workspace)
        
        # Should handle encoding issues gracefully
        version_name = tester.create_version_snapshot("prompts/encoding_agent/current.md")
        
        # Might fail or succeed depending on implementation
        # Main thing is it shouldn't crash
    
    def test_filesystem_case_sensitivity(self, error_workspace):
        """Test behavior on case-insensitive filesystems"""
        agent_dir = error_workspace / "prompts" / "case_agent"
        agent_dir.mkdir(parents=True)
        
        config_content = {'metadata': {'name': 'CaseAgent'}, 'config': {'model': 'gpt-4'}}
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Test content")
        
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        # Create versions with potential case conflicts
        (versions_dir / "V001.md").touch()  # Uppercase V
        (versions_dir / "v001.MD").touch()  # Uppercase extension
        
        tester = PreCommitHookTester(error_workspace)
        
        # Should handle case sensitivity issues
        version_name = tester.create_version_snapshot("prompts/case_agent/current.md")
        
        # Should create a version that doesn't conflict
        assert version_name is not None
    
    def test_symlink_handling(self, error_workspace):
        """Test behavior with symbolic links"""
        agent_dir = error_workspace / "prompts" / "symlink_agent"
        agent_dir.mkdir(parents=True)
        
        # Create actual config in different location
        actual_config_dir = error_workspace / "actual_config"
        actual_config_dir.mkdir()
        
        config_content = {'metadata': {'name': 'SymlinkAgent'}, 'config': {'model': 'gpt-4'}}
        actual_config = actual_config_dir / "config.yaml"
        with open(actual_config, "w") as f:
            yaml.dump(config_content, f)
        
        # Create symlink to config
        try:
            os.symlink(actual_config, agent_dir / "config.yaml")
        except OSError:
            # Skip test if symlinks not supported (e.g., Windows without admin)
            pytest.skip("Symlinks not supported on this system")
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Symlink test content")
        
        (agent_dir / "versions").mkdir()
        
        tester = PreCommitHookTester(error_workspace)
        
        # Should handle symlinked config
        version_name = tester.create_version_snapshot("prompts/symlink_agent/current.md")
        
        # Should work or fail gracefully
        # Main thing is it shouldn't crash
    
    def test_version_rollback_edge_cases(self, error_workspace):
        """Test edge cases in version rollback"""
        agent_dir = error_workspace / "prompts" / "rollback_agent"
        agent_dir.mkdir(parents=True)
        
        # Create config pointing to non-existent version
        config_content = {
            'metadata': {'name': 'RollbackAgent'},
            'current_version': 'v999',  # Doesn't exist
            'versions': {'v001': {'notes': 'Exists'}},
            'config': {'model': 'gpt-4'}
        }
        
        with open(agent_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)
        
        with open(agent_dir / "current.md", "w") as f:
            f.write("Current content")
        
        versions_dir = agent_dir / "versions"
        versions_dir.mkdir()
        
        with open(versions_dir / "v001.md", "w") as f:
            f.write("Version 1 exists")
        
        tester = PreCommitHookTester(error_workspace)
        
        # Should handle non-existent version gracefully
        success = tester.handle_version_switch(str(agent_dir / "config.yaml"))
        
        assert success is False  # Should fail gracefully
        
        # current.md should remain unchanged
        with open(agent_dir / "current.md", "r") as f:
            content = f.read()
        
        assert "Current content" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
