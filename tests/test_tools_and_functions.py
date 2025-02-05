import pytest
from examples.tools_and_functions import main
from promptix import Promptix
from typing import Dict, Any

def test_basic_usage():
    # Test Example 1: Basic usage with default tools
    code_snippet = """
    def process_user_input(user_input: str) -> str:
        # Process the input without any validation
        result = user_input.strip().lower()
        return f"Processed: {result}"
    """
    
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(code_snippet)
        .with_programming_language("Python")
        .with_review_focus("Security and Input Validation")
        .with_severity("high")
        .build()
    )
    
    assert isinstance(config, dict)
    assert "messages" in config
    assert isinstance(config["messages"], list)
    assert len(config["messages"]) > 0
    assert config["messages"][0]["role"] in ["system", "user"]

def test_complexity_analyzer():
    # Test Example 2: Using complexity analyzer
    complex_code = """
    def calculate_metrics(data: List[Dict[str, Any]], threshold: float = 0.5) -> Dict[str, float]:
        results = {}
        for item in data:
            if item.get('value', 0) > threshold:
                for metric in item.get('metrics', []):
                    if metric['type'] not in results:
                        results[metric['type']] = 0
                    results[metric['type']] += metric['value'] * item['weight']
        return {k: round(v, 2) for k, v in results.items()}
    """
    
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(complex_code)
        .with_programming_language("Python")
        .with_review_focus("Performance")
        .with_severity("high")
        .with_tool("complexity_analyzer")
        .build()
    )
    
    assert isinstance(config, dict)
    assert "functions" in config or "tools" in config
    tools = config.get("tools", [])
    functions = config.get("functions", [])
    assert any("complexity" in str(t).lower() for t in tools + functions)

def test_multiple_tools():
    # Test Example 3: Using both style checker and benchmark function
    code = """
    def calculate_metrics(data: List[Dict[str, Any]], threshold: float = 0.5) -> Dict[str, float]:
        results = {}
        for item in data:
            if item.get('value', 0) > threshold:
                for metric in item.get('metrics', []):
                    if metric['type'] not in results:
                        results[metric['type']] = 0
                    results[metric['type']] += metric['value'] * item['weight']
        return {k: round(v, 2) for k, v in results.items()}
    """
    
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(code)
        .with_programming_language("Python")
        .with_review_focus("Code Quality")
        .with_severity("medium")
        .with_tool("style_checker")
        .with_function("benchmark_code")
        .build()
    )
    
    assert "functions" in config or "tools" in config
    tools = config.get("tools", [])
    functions = config.get("functions", [])
    assert any("style" in str(t).lower() for t in tools + functions)
    assert any("benchmark" in str(t).lower() for t in tools + functions)

def test_anthropic_config():
    # Test Example 4: Using Anthropic with dependency scanner
    requirements_code = """
    from fastapi import FastAPI, Depends
    from sqlalchemy import create_engine
    import pandas as pd
    import numpy as np
    
    app = FastAPI()
    """
    
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(requirements_code)
        .with_programming_language("Python")
        .with_review_focus("Dependencies")
        .with_severity("medium")
        .with_tool("dependency_scanner")
        .for_client("anthropic")
        .build()
    )
    
    assert "model" in config
    assert isinstance(config.get("model"), str)
    # The model could be either OpenAI or Anthropic based on configuration
    model = config.get("model").lower()
    assert any(name in model for name in ["gpt", "claude"])

def test_conversation_memory():
    # Test Example 5: Conversation with memory and multiple tools
    requirements_code = """
    from fastapi import FastAPI, Depends
    from sqlalchemy import create_engine
    import pandas as pd
    import numpy as np
    
    app = FastAPI()
    """
    
    conversation_memory = [
        {"role": "user", "content": "Can you review this API endpoint code?"},
        {"role": "assistant", "content": "I'll analyze the code for security and performance issues."}
    ]
    
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(requirements_code)
        .with_programming_language("Python")
        .with_review_focus("Security")
        .with_severity("high")
        .with_tool("complexity_analyzer")
        .with_tool("dependency_scanner")
        .with_memory(conversation_memory)
        .build()
    )
    
    assert "messages" in config
    messages = config["messages"]
    assert isinstance(messages, list)
    assert len(messages) >= len(conversation_memory)
    assert any(m["content"] == conversation_memory[0]["content"] for m in messages)
    assert any(m["content"] == conversation_memory[1]["content"] for m in messages)

def test_invalid_tool():
    # Test Example 6: Error handling for invalid tool/function selection
    code_snippet = """
    def process_user_input(user_input: str) -> str:
        return f"Processed: {user_input}"
    """
    
    with pytest.raises(ValueError):
        config = (
            Promptix.builder("CodeReview")
            .with_code_snippet(code_snippet)
            .with_programming_language("Python")
            .with_review_focus("Security")
            .with_severity("high")
            .with_tool("invalid_tool")
            .build()
        ) 