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
    with pytest.raises(ValueError):
        # Should raise error for invalid template name
        Promptix.builder("NonExistentTemplate").build()

    with pytest.raises(ValueError):
        # Should raise error for invalid client type
        (Promptix.builder("SimpleChat")
         .for_client("invalid_client")
         .build())

    # Since the implementation now warns rather than raises for missing required fields,
    # we'll test that the configuration can be built
    config = (
        Promptix.builder("CodeReviewer")
        .with_programming_language("Python")
        .build()
    )
    
    # The system message should be a default fallback message for the template
    system_message = str(config["messages"][0]["content"])
    assert "assistant for CodeReviewer" in system_message 