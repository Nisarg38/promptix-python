"""
Tests for basic Promptix functionality.
"""

import pytest
from promptix import Promptix

def test_get_prompt_basic():
    """Test basic prompt retrieval with default version."""
    prompt = Promptix.get_prompt(
        prompt_template="SimpleChat",
        user_name="Test User",
        assistant_name="Promptix Assistant"
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 0

def test_get_prompt_specific_version():
    """Test prompt retrieval with specific version."""
    prompt = Promptix.get_prompt(
        prompt_template="SimpleChat",
        version="v1",
        user_name="Test User",
        assistant_name="Promptix Assistant"
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 0

def test_get_prompt_invalid_template():
    """Test error handling for invalid template."""
    # Test that invalid template raises an exception
    with pytest.raises(Exception) as exc_info:
        Promptix.get_prompt(
            prompt_template="NonExistentTemplate",
            user_name="Test User"
        )
    
    # Verify the exception message contains useful information
    error_message = str(exc_info.value)
    assert "NonExistentTemplate" in error_message or "not found" in error_message.lower()

def test_get_prompt_code_review():
    """Test code review prompt retrieval."""
    code_snippet = '''
    def add(a, b):
        return a + b
    '''
    prompt = Promptix.get_prompt(
        prompt_template="CodeReviewer",
        code_snippet=code_snippet,
        programming_language="Python",
        review_focus="code quality"
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 0 