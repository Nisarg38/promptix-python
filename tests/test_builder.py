import pytest
from promptix import Promptix
import openai
import anthropic


def test_customer_support_builder():
    """Test the CustomerSupport builder configuration."""
    memory = [
        {"role": "user", "content": "I'm having trouble with my account settings"},
    ]

    # Test basic OpenAI configuration
    model_config = (
        Promptix.builder("CustomerSupport")
        .with_user_name("John Doe")
        .with_issue_type("account_settings")
        .with_issue_description("User cannot access account settings page")
        .with_technical_level("intermediate")
        .with_priority("medium")
        .with_memory(memory)
        .build()
    )

    # Verify the configuration
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert len(model_config["messages"]) > 1  # Should have system message + memory
    assert model_config["messages"][0]["role"] == "system"  # First message should be system


def test_code_review_builder():
    """Test the CodeReview builder configuration."""
    memory = [
        {"role": "user", "content": "Can you review this code for security issues?"},
    ]

    code_snippet = '''
    def process_user_input(data):
        query = f"SELECT * FROM users WHERE id = {data['user_id']}"
        return execute_query(query)
    '''

    model_config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(code_snippet)
        .with_programming_language("Python")
        .with_review_focus("Security and SQL Injection")
        .with_severity("high")
        .with_memory(memory)
        .build()
    )

    # Verify the configuration
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert len(model_config["messages"]) > 1
    assert code_snippet in str(model_config["messages"][0]["content"])


def test_anthropic_builder():
    """Test the builder configuration for Anthropic."""
    memory = [
        {"role": "user", "content": "I'm having trouble with my account settings"},
    ]

    model_config = (
        Promptix.builder("CustomerSupport")
        .with_version("v5")
        .with_user_name("John Doe")
        .with_issue_type("account_settings")
        .with_issue_description("User cannot access account settings page")
        .with_technical_level("intermediate")
        .with_priority("medium")
        .with_memory(memory)
        .for_client("anthropic")
        .build()
    )

    # Verify Anthropic-specific configuration
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert model_config.get("model", "").startswith("claude")  # Anthropic models start with "claude"


def test_builder_validation():
    """Test builder validation and error cases."""
    with pytest.raises(ValueError):
        # Should raise error for invalid template name
        Promptix.builder("NonExistentTemplate").build()

    with pytest.raises(ValueError):
        # Should raise error for invalid client type
        (Promptix.builder("CustomerSupport")
         .for_client("invalid_client")
         .build())

    # Test required fields
    with pytest.raises(Exception):
        # CodeReview builder should require code_snippet
        (Promptix.builder("CodeReview")
         .with_programming_language("Python")
         .build()) 