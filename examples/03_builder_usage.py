"""
Builder Pattern example for Promptix library.

This example demonstrates how to use the builder pattern in Promptix
to construct prompt configurations in a fluent, chainable manner.
"""

from promptix import Promptix
import json

def print_config(config):
    """Helper function to pretty print a configuration."""
    print(json.dumps(config, indent=2))
    print("-" * 50)

def main():
    print("Builder Pattern Examples:\n")
    
    # Example 1: Basic builder usage with SimpleChat
    print("Example 1: Basic Builder (SimpleChat)")
    config1 = (
        Promptix.builder("SimpleChat")
        .with_user_name("Alice")
        .with_assistant_name("Helper")
        .build()
    )
    print_config(config1)

    # Example 2: Builder with version specification
    print("Example 2: Builder with Version (SimpleChat v2)")
    config2 = (
        Promptix.builder("SimpleChat")
        .with_version("v2")
        .with_user_name("Bob")
        .with_assistant_name("Advisor")
        .with_personality_type("professional")
        .build()
    )
    print_config(config2)

    # Example 3: Builder with memory (conversation history)
    print("Example 3: Builder with Memory")
    memory = [
        {"role": "user", "content": "How can I improve my code?"},
        {"role": "assistant", "content": "I'd be happy to help! Could you share some code with me?"}
    ]
    
    config3 = (
        Promptix.builder("CodeReviewer")
        .with_code_snippet("def add(a, b): return a + b")
        .with_programming_language("Python")
        .with_review_focus("Best practices")
        .with_memory(memory)
        .build()
    )
    print_config(config3)

    
    # Example 4: Builder for specific client
    print("Example 4: Builder for Specific Client (Anthropic)")
    try:
        config5 = (
            Promptix.builder("CodeReviewer")
            .with_version("v2")  # Anthropic-compatible version
            .with_code_snippet("def process(data): return [x for x in data if x > 0]")
            .with_programming_language("Python")
            .with_review_focus("Readability")
            .with_severity("low")
            .for_client("anthropic")  # Specify client type
            .build()
        )
        print_config(config5)
    except ValueError as e:
        print(f"Error: {str(e)}")

    # Example 5: Complex tool configuration
    print("Example 5: Complex Tool Configuration")
    config5 = (
        Promptix.builder("ComplexCodeReviewer")
        .with_programming_language("Python")
        .with_severity("high")
        .with_review_focus("security and performance")
        .with_tool("complexity_analyzer")
        .with_tool_parameter("complexity_analyzer", "thresholds", {"cyclomatic": 8, "cognitive": 5})
        .with_tool("security_scanner")  
        .with_tool_parameter("security_scanner", "cwe_list", ["CWE-78", "CWE-89", "CWE-862"])
        .with_tool("test_coverage")
        .disable_tools("style_checker")
        .build()
    )
    print_config(config5)

if __name__ == "__main__":
    main() 