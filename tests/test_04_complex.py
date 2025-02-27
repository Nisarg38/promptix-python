"""
Tests for advanced Promptix functionality with complex templates.
"""

import pytest
from typing import Dict, List, Any
from promptix import Promptix

def test_complex_code_reviewer_basic():
    """Test basic complex code reviewer functionality."""
    code_snippet = '''
def calculate_total(items):
    return sum(item.price for item in items)
    '''
    
    prompt = Promptix.get_prompt(
        prompt_template="ComplexCodeReviewer",
        code_snippet=code_snippet,
        programming_language="Python",
        review_focus="code quality",
        severity="low",
        active_tools="complexity_analyzer"
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "Python" in prompt
    assert "code quality" in prompt.lower()

def test_complex_code_reviewer_with_multiple_tools():
    """Test complex code reviewer with multiple tools."""
    code_snippet = '''
def process_user_data(data):
    query = f"SELECT * FROM users WHERE id = {data['user_id']}"
    conn = get_db_connection()
    result = conn.execute(query)
    return result.fetchall()
    '''
    
    prompt = Promptix.get_prompt(
        prompt_template="ComplexCodeReviewer",
        code_snippet=code_snippet,
        programming_language="Python",
        review_focus="security vulnerabilities",
        severity="high",
        active_tools="complexity_analyzer, security_scanner"
    )
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "Python" in prompt
    assert "security vulnerabilities" in prompt.lower()
    assert "high" in prompt.lower()

def test_complex_code_reviewer_builder():
    """Test complex code reviewer builder pattern."""
    code_snippet = '''
def process_user_data(data):
    query = f"SELECT * FROM users WHERE id = {data['user_id']}"
    return execute_query(query)
    '''
    
    config = (
        Promptix.builder("ComplexCodeReviewer")
        .with_code_snippet(code_snippet)
        .with_programming_language("Python")
        .with_review_focus("Security and Performance")
        .with_severity("high")
        .with_tool("complexity_analyzer")
        .with_tool("security_scanner")
        .build()
    )
    
    assert isinstance(config, dict)
    assert "messages" in config
    assert "model" in config
    assert len(config["messages"]) > 0
    
    messages_str = str(config["messages"])
    assert "process_user_data" in messages_str
    assert "Python" in messages_str
    assert "Security" in messages_str

def test_complex_code_reviewer_with_tool_parameters():
    """Test complex code reviewer with tool parameters."""
    code_snippet = "def test(): pass"
    
    config = (
        Promptix.builder("ComplexCodeReviewer")
        .with_code_snippet(code_snippet)
        .with_programming_language("Python")
        .with_review_focus("code quality")
        .with_severity("medium")
        .with_tool("complexity_analyzer")
        .with_tool_parameter("complexity_analyzer", "thresholds", {"cyclomatic": 5, "cognitive": 3})
        .build()
    )
    
    assert isinstance(config, dict)
    assert "messages" in config
    assert "model" in config

def test_complex_code_reviewer_with_default_configuration():
    """Test complex code reviewer with default tool configuration."""
    code_snippet = "function add(a, b) { return a + b; }"
    
    prompt = Promptix.get_prompt(
        prompt_template="ComplexCodeReviewer",
        code_snippet=code_snippet,
        programming_language="JavaScript",
        review_focus="best practices",
        severity="low",
        active_tools="style_checker"
    )
    
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "JavaScript" in prompt
    assert "best practices" in prompt.lower()
    assert "style_checker" in prompt.lower() 