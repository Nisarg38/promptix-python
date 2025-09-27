"""
Tests to verify the folder-based prompt system works correctly.

This module tests that the new folder-based prompt structure functions
properly and provides the same functionality as the old YAML-based system.
"""

import pytest
from pathlib import Path
import yaml


class TestFolderBasedPromptStructure:
    """Test the folder-based prompt structure."""

    def test_test_prompts_directory_exists(self, test_prompts_dir):
        """Test that the test prompts directory exists."""
        assert test_prompts_dir.exists()
        assert test_prompts_dir.is_dir()

    def test_prompt_folders_exist(self, test_prompts_dir):
        """Test that all expected prompt folders exist."""
        expected_prompts = ["SimpleChat", "CodeReviewer", "TemplateDemo"]
        
        for prompt_name in expected_prompts:
            prompt_dir = test_prompts_dir / prompt_name
            assert prompt_dir.exists(), f"Prompt directory {prompt_name} should exist"
            assert prompt_dir.is_dir(), f"Prompt {prompt_name} should be a directory"

    def test_prompt_config_files_exist(self, test_prompts_dir):
        """Test that config.yaml files exist for all prompts."""
        expected_prompts = ["SimpleChat", "CodeReviewer", "TemplateDemo"]
        
        for prompt_name in expected_prompts:
            config_file = test_prompts_dir / prompt_name / "config.yaml"
            assert config_file.exists(), f"Config file for {prompt_name} should exist"

    def test_prompt_template_files_exist(self, test_prompts_dir):
        """Test that template files exist for all prompts."""
        expected_prompts = ["SimpleChat", "CodeReviewer", "TemplateDemo"]
        
        for prompt_name in expected_prompts:
            # Check current.md
            current_file = test_prompts_dir / prompt_name / "current.md"
            assert current_file.exists(), f"Current template for {prompt_name} should exist"
            
            # Check versions directory
            versions_dir = test_prompts_dir / prompt_name / "versions"
            assert versions_dir.exists(), f"Versions directory for {prompt_name} should exist"
            
            # Check at least one versioned file exists
            version_files = list(versions_dir.glob("*.md"))
            assert len(version_files) > 0, f"At least one versioned template for {prompt_name} should exist"


class TestFolderBasedPromptLoading:
    """Test loading prompts from folder structure."""

    def test_mock_prompt_loader_loads_from_folders(self, mock_prompt_loader):
        """Test that MockPromptLoader can load from folder structure."""
        prompts_data = mock_prompt_loader.load_prompts()
        
        assert isinstance(prompts_data, dict)
        assert len(prompts_data) > 0
        
        # Check expected prompts are loaded
        expected_prompts = ["SimpleChat", "CodeReviewer", "TemplateDemo"]
        for prompt_name in expected_prompts:
            assert prompt_name in prompts_data, f"{prompt_name} should be loaded"

    def test_loaded_prompt_structure(self, mock_prompt_loader):
        """Test that loaded prompts have expected structure."""
        prompts_data = mock_prompt_loader.load_prompts()
        
        for prompt_name, prompt_data in prompts_data.items():
            assert "versions" in prompt_data, f"{prompt_name} should have versions"
            assert isinstance(prompt_data["versions"], dict), f"{prompt_name} versions should be dict"
            
            for version_name, version_data in prompt_data["versions"].items():
                assert "is_live" in version_data, f"{prompt_name} v{version_name} should have is_live"
                assert "config" in version_data, f"{prompt_name} v{version_name} should have config"
                assert "schema" in version_data, f"{prompt_name} v{version_name} should have schema"
                
                config = version_data["config"]
                assert "system_instruction" in config, f"{prompt_name} v{version_name} should have system_instruction"
                assert "model" in config, f"{prompt_name} v{version_name} should have model"

    def test_simple_chat_template_content(self, mock_prompt_loader):
        """Test SimpleChat template content is loaded correctly."""
        prompts_data = mock_prompt_loader.load_prompts()
        
        simple_chat = prompts_data["SimpleChat"]
        versions = simple_chat["versions"]
        
        # Check that template variables are present
        for version_name, version_data in versions.items():
            system_instruction = version_data["config"]["system_instruction"]
            assert "{{assistant_name}}" in system_instruction
            assert "{{user_name}}" in system_instruction

    def test_code_reviewer_template_content(self, mock_prompt_loader):
        """Test CodeReviewer template content is loaded correctly."""
        prompts_data = mock_prompt_loader.load_prompts()
        
        code_reviewer = prompts_data["CodeReviewer"]
        versions = code_reviewer["versions"]
        
        # Check that template variables are present
        for version_name, version_data in versions.items():
            system_instruction = version_data["config"]["system_instruction"]
            assert "{{programming_language}}" in system_instruction
            assert "{{code_snippet}}" in system_instruction
            assert "{{review_focus}}" in system_instruction


class TestFolderBasedPromptCompatibility:
    """Test that folder-based prompts work with existing test fixtures."""

    def test_sample_prompts_data_fixture_compatibility(self, sample_prompts_data):
        """Test that sample_prompts_data fixture works with folder structure."""
        assert isinstance(sample_prompts_data, dict)
        assert len(sample_prompts_data) > 0
        
        # Should contain expected prompts
        expected_prompts = ["SimpleChat", "CodeReviewer", "TemplateDemo"]
        for prompt_name in expected_prompts:
            assert prompt_name in sample_prompts_data

    def test_temp_prompts_file_returns_directory(self, temp_prompts_file):
        """Test that temp_prompts_file fixture returns directory path."""
        path = Path(temp_prompts_file)
        assert path.exists()
        # Should be a directory containing prompt folders
        assert path.is_dir()

    def test_temp_prompts_dir_structure(self, temp_prompts_dir):
        """Test that temp_prompts_dir creates proper structure."""
        assert temp_prompts_dir.exists()
        assert temp_prompts_dir.is_dir()
        
        # Should contain expected prompt folders
        expected_prompts = ["SimpleChat", "CodeReviewer", "TemplateDemo"]
        for prompt_name in expected_prompts:
            prompt_dir = temp_prompts_dir / prompt_name
            assert prompt_dir.exists()


class TestFolderBasedPromptValidation:
    """Test validation of folder-based prompt structure."""

    def test_config_yaml_valid_structure(self, test_prompts_dir):
        """Test that config.yaml files have valid structure."""
        expected_prompts = ["SimpleChat", "CodeReviewer", "TemplateDemo"]
        
        for prompt_name in expected_prompts:
            config_file = test_prompts_dir / prompt_name / "config.yaml"
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check expected sections
            assert "metadata" in config, f"{prompt_name} config should have metadata"
            assert "schema" in config, f"{prompt_name} config should have schema"
            assert "config" in config, f"{prompt_name} config should have config section"
            
            # Check metadata
            metadata = config["metadata"]
            assert "name" in metadata
            assert "description" in metadata
            
            # Check schema
            schema = config["schema"]
            assert "type" in schema
            assert "properties" in schema or "required" in schema
            
            # Check config section
            config_section = config["config"]
            assert "model" in config_section
            assert "provider" in config_section

    def test_template_files_not_empty(self, test_prompts_dir):
        """Test that template files are not empty."""
        expected_prompts = ["SimpleChat", "CodeReviewer", "TemplateDemo"]
        
        for prompt_name in expected_prompts:
            # Check current.md
            current_file = test_prompts_dir / prompt_name / "current.md"
            with open(current_file, 'r') as f:
                content = f.read().strip()
            assert len(content) > 0, f"Current template for {prompt_name} should not be empty"
            
            # Check versioned templates
            versions_dir = test_prompts_dir / prompt_name / "versions"
            for version_file in versions_dir.glob("*.md"):
                with open(version_file, 'r') as f:
                    content = f.read().strip()
                assert len(content) > 0, f"Version template {version_file.name} for {prompt_name} should not be empty"
