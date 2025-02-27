import pytest
from unittest.mock import patch, MagicMock
from promptix import Promptix
from typing import Dict, Any, List


def test_code_reviewer_basic():
    """Test basic code reviewer functionality."""
    code_snippet = '''
def calculate_total(items):
    return sum(item.price for item in items)
    '''
    
    prompt = Promptix.get_prompt(
        prompt_template="CodeReviewer",
        code_snippet=code_snippet,
        programming_language="Python",
        review_focus="code readability and error handling"
    )
    
    # Verify prompt contains expected content
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert code_snippet in prompt
    assert "Python" in prompt
    assert "code readability" in prompt.lower()
    assert "error handling" in prompt.lower()


def test_code_reviewer_review_focus():
    """Test code reviewer with different review focus."""
    code_snippet = '''
def process_user_data(data):
    query = f"SELECT * FROM users WHERE id = {data['user_id']}"
    conn = get_db_connection()
    result = conn.execute(query)
    return result.fetchall()
    '''
    
    # Since severity might not be supported directly, we'll test with different review focus
    security_prompt = Promptix.get_prompt(
        prompt_template="CodeReviewer",
        code_snippet=code_snippet,
        programming_language="Python",
        review_focus="security vulnerabilities"
    )
    
    performance_prompt = Promptix.get_prompt(
        prompt_template="CodeReviewer",
        code_snippet=code_snippet,
        programming_language="Python",
        review_focus="performance optimization"
    )
    
    # Verify prompts are different based on review focus
    assert security_prompt != performance_prompt
    
    # Verify prompts contain expected content
    assert isinstance(security_prompt, str)
    assert len(security_prompt) > 0
    assert code_snippet in security_prompt
    assert "Python" in security_prompt
    assert "security vulnerabilities" in security_prompt.lower()
    
    assert "performance optimization" in performance_prompt.lower()


def test_code_reviewer_builder():
    """Test code reviewer with builder pattern."""
    code_snippet = '''
def process_user_data(data):
    query = f"SELECT * FROM users WHERE id = {data['user_id']}"
    conn = get_db_connection()
    result = conn.execute(query)
    return result.fetchall()
    '''
    
    config = (
        Promptix.builder("CodeReviewer")
        .with_code_snippet(code_snippet)
        .with_programming_language("Python")
        .with_review_focus("Performance and Security")
        .build()
    )
    
    # Verify configuration contains expected content
    assert isinstance(config, dict)
    assert "messages" in config
    assert "model" in config
    assert len(config["messages"]) > 0
    
    # The content can be in different formats depending on the client
    messages_str = str(config["messages"])
    
    # Check for key parts of the code rather than exact matching to handle escaping
    assert "process_user_data" in messages_str
    assert "SELECT * FROM users" in messages_str
    assert "Python" in messages_str
    assert "Performance" in messages_str
    assert "Security" in messages_str


def test_memory_integration():
    """Test integration of memory (conversation history)."""
    code_snippet = "def test(): pass"
    
    # Conversation memory
    memory = [
        {"role": "user", "content": "Can you review this code for security issues?"},
        {"role": "assistant", "content": "I'll analyze the code for security vulnerabilities."}
    ]
    
    # Create configuration with memory
    config = (
        Promptix.builder("CodeReviewer")
        .with_code_snippet(code_snippet)
        .with_programming_language("Python")
        .with_review_focus("security")
        .with_memory(memory)
        .build()
    )
    
    # Verify memory is integrated
    assert "messages" in config
    messages = config["messages"]
    
    # Convert to string to handle different message formats
    messages_str = str(messages)
    assert "Can you review this code for security issues?" in messages_str
    assert "I'll analyze the code for security vulnerabilities." in messages_str


def test_different_programming_languages():
    """Test code reviewer with different programming languages."""
    code_snippet = "function add(a, b) { return a + b; }"
    
    # Test with JavaScript
    js_prompt = Promptix.get_prompt(
        prompt_template="CodeReviewer",
        code_snippet=code_snippet,
        programming_language="JavaScript",
        review_focus="code quality"
    )
    
    # Test with TypeScript
    ts_prompt = Promptix.get_prompt(
        prompt_template="CodeReviewer",
        code_snippet=code_snippet,
        programming_language="TypeScript",
        review_focus="code quality"
    )
    
    # Verify prompts reflect the different programming languages
    assert "JavaScript" in js_prompt
    assert "TypeScript" in ts_prompt
    assert js_prompt != ts_prompt 