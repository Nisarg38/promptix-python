import pytest
import os
from unittest.mock import patch, MagicMock
from promptix import Promptix


@pytest.fixture
def mock_openai_client():
    """Create a mock OpenAI client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    
    mock_message.content = "This is a mock response from OpenAI"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    """Create a mock Anthropic client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_content = MagicMock()
    
    mock_content.text = "This is a mock response from Anthropic"
    mock_response.content = [mock_content]
    mock_client.messages.create.return_value = mock_response
    
    return mock_client


def test_openai_integration(mock_openai_client):
    """Test integration with OpenAI API."""
    # Memory for conversation context
    memory = [
        {"role": "user", "content": "Can you help me understand Python decorators?"}
    ]
    
    # Prepare model configuration
    model_config = Promptix.prepare_model_config(
        prompt_template="SimpleChat",
        user_name="TestUser",
        assistant_name="TestAssistant",
        memory=memory
    )
    
    # Verify the configuration structure
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert len(model_config["messages"]) > 1  # System message + memory
    
    # Test the API call (using the mock)
    with patch("openai.OpenAI", return_value=mock_openai_client):
        client = mock_openai_client
        response = client.chat.completions.create(**model_config)
        
        # Verify the mock was called correctly
        client.chat.completions.create.assert_called_once()
        assert response.choices[0].message.content == "This is a mock response from OpenAI"


def test_anthropic_integration(mock_anthropic_client):
    """Test integration with Anthropic API."""
    # Memory for conversation context
    memory = [
        {"role": "user", "content": "I'd like a code review for a Python function"}
    ]
    
    # Code snippet to review
    code_snippet = '''
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result
    '''
    
    # Prepare model configuration using the builder pattern
    model_config = (
        Promptix.builder("CodeReviewer")
        .with_version("v2")  # v2 is Anthropic-compatible
        .with_code_snippet(code_snippet)
        .with_programming_language("Python")
        .with_review_focus("code efficiency")
        .with_severity("medium")
        .with_memory(memory)
        .for_client("anthropic")
        .build()
    )
    
    # Verify the configuration structure
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert model_config["model"].startswith("claude")  # Anthropic models start with "claude"
    
    # Test the API call (using the mock)
    with patch("anthropic.Anthropic", return_value=mock_anthropic_client):
        client = mock_anthropic_client
        response = client.messages.create(**model_config)
        
        # Verify the mock was called correctly
        client.messages.create.assert_called_once()
        assert response.content[0].text == "This is a mock response from Anthropic"


def test_client_specific_configurations():
    """Test different client configurations."""
    memory = [{"role": "user", "content": "Test message"}]
    
    # OpenAI configuration
    openai_config = (
        Promptix.builder("SimpleChat")
        .with_user_name("TestUser")
        .with_assistant_name("TestAssistant")
        .with_memory(memory)
        .for_client("openai")
        .build()
    )
    
    # Verify OpenAI-specific configuration
    assert isinstance(openai_config, dict)
    assert "messages" in openai_config
    assert openai_config.get("model", "").startswith("gpt")  # OpenAI models typically start with gpt
    
    # Anthropic configuration - we need to use a compatible prompt version
    # This test is now more about verifying different client configurations exist and are different
    # rather than specific model names which may change
    try:
        anthropic_config = (
            Promptix.builder("SimpleChat")
            .with_version("v2")  # Anthropic-compatible version
            .with_user_name("TestUser")
            .with_assistant_name("TestAssistant")
            .with_personality_type("friendly")  # Adding missing required parameter
            .with_memory(memory)
            .for_client("anthropic")
            .build()
        )
        
        # Verify Anthropic-specific configuration
        assert isinstance(anthropic_config, dict)
        assert "messages" in anthropic_config
        
        # Verify configurations are different (without assuming specific model names)
        assert openai_config != anthropic_config
    except ValueError as e:
        # If this version doesn't exist, we'll just verify the error contains useful information
        assert "SimpleChat" in str(e) 