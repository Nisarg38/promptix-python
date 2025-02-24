from promptix import Promptix
from typing import Dict, Any
import json

def print_config(config: Dict[str, Any]):
    """Helper function to pretty print the configuration"""
    print(json.dumps(config, indent=2))
    print("-" * 80)

def main():
    # Example 1: Basic usage with default tools
    print("Example 1: Basic usage with default tools")
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
    print_config(config)

    # Example 2: Using complexity analyzer
    print("Example 2: Using complexity analyzer")
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
        .with_tool("complexity_analyzer")  # Enable complexity analysis 
        .build()
    )
    print_config(config)

    # Example 3: Using both style checker and benchmark function
    print("Example 3: Using style checker and benchmark function")
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(complex_code)
        .with_programming_language("Python")
        .with_review_focus("Code Quality")
        .with_severity("medium")
        .with_tool("style_checker")
        .with_function("benchmark_code")
        .build()
    )
    print_config(config)

    # Example 4: Using Anthropic with dependency scanner
    print("Example 4: Using Anthropic with dependency scanner")
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
    print_config(config)

    # Example 5: Conversation with memory and multiple tools
    print("Example 5: Conversation with memory and multiple tools")
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
    print_config(config)

    # Example 6: Error handling for invalid tool/function selection
    print("Example 6: Error handling demonstration")
    try:
        config = (
            Promptix.builder("CodeReview")
            .with_code_snippet(code_snippet)
            .with_programming_language("Python")
            .with_review_focus("Security")
            .with_severity("high")
            .with_tool("invalid_tool")  # This should raise an error
            .build()
        )
    except ValueError as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    main()