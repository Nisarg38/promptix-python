import pytest
from promptix import Promptix
import openai
import anthropic


def test_chat_builder():
    """Test the SimpleChat builder configuration."""
    memory = [
        {"role": "user", "content": "Can you help me with a question?"},
    ]

    # Test basic OpenAI configuration
    model_config = (
        Promptix.builder("SimpleChat")
        .with_user_name("John Doe")
        .with_assistant_name("Promptix Helper")
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
    """Test the CodeReviewer builder configuration."""
    memory = [
        {"role": "user", "content": "Can you review this code for security issues?"},
    ]

    code_snippet = '''
    def process_user_input(data):
        query = f"SELECT * FROM users WHERE id = {data['user_id']}"
        return execute_query(query)
    '''

    model_config = (
        Promptix.builder("CodeReviewer")
        .with_code_snippet(code_snippet)
        .with_programming_language("Python")
        .with_review_focus("Security and SQL Injection")
        .with_memory(memory)
        .build()
    )

    # Verify the configuration
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert len(model_config["messages"]) > 1
    assert code_snippet in str(model_config["messages"][0]["content"])


def test_template_demo_builder():
    """Test the TemplateDemo builder configuration."""
    memory = [
        {"role": "user", "content": "Can you create a tutorial for me?"},
    ]

    model_config = (
        Promptix.builder("TemplateDemo")
        .with_content_type("tutorial")
        .with_theme("Python programming")
        .with_difficulty("intermediate")
        .with_elements(["functions", "classes", "decorators"])
        .with_memory(memory)
        .build()
    )

    # Verify the configuration
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert len(model_config["messages"]) > 1
    assert "tutorial" in str(model_config["messages"][0]["content"])
    # Check for text related to intermediate difficulty, not the literal word
    assert "advanced concepts" in str(model_config["messages"][0]["content"])


def test_builder_validation():
    """Test builder validation and error cases."""
    
    # Test invalid template name raises an exception
    with pytest.raises(Exception) as exc_info:
        Promptix.builder("NonExistentTemplate").build()
    
    error_message = str(exc_info.value)
    assert "NonExistentTemplate" in error_message or "not found" in error_message.lower()

    # Test invalid client type raises an exception
    with pytest.raises(Exception) as exc_info:
        (Promptix.builder("SimpleChat")
         .for_client("invalid_client")
         .build())
    
    error_message = str(exc_info.value)
    assert "invalid_client" in error_message or "unsupported" in error_message.lower() or "client" in error_message.lower()

    # Since the implementation now warns rather than raises for missing required fields,
    # we'll test that the configuration can be built
    config = (
        Promptix.builder("CodeReviewer")
        .with_programming_language("Python")
        .build()
    )
    
    # Verify basic config structure
    assert isinstance(config, dict)
    assert "messages" in config
    assert "model" in config 