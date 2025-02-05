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
    def calculate_speed(distance: float, time: float) -> float:
        return distance / time
    """
    
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(code_snippet)
        .with_programming_language("Python")
        .with_review_focus("Security and SQL Injection")
        .with_severity("high")
        .build()
    )
    print_config(config)

    # Example 2: Using vehicle-specific tools
    print("Example 2: Using vehicle-specific tools")
    vehicle_code = """
    class CarEngine:
        def __init__(self, fuel_type: str):
            self.fuel_type = fuel_type
            
        def start(self):
            if self.fuel_type not in ['gasoline', 'diesel']:
                raise ValueError('Invalid fuel type')
            return f'Starting {self.fuel_type} engine'
    """
    
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(vehicle_code)
        .with_programming_language("Python")
        .with_review_focus("Vehicle Safety")
        .with_severity("high")
        .with_tool("vehicle_selection")  # Enable vehicle-specific tools
        .build()
    )
    print_config(config)

    # Example 3: Using both vehicle-specific tools and functions
    print("Example 3: Using both vehicle-specific tools and functions")
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(vehicle_code)
        .with_programming_language("Python")
        .with_review_focus("Vehicle Safety")
        .with_severity("high")
        .with_tool("vehicle_selection")
        .with_function("vehicle_selection")
        .build()
    )
    print_config(config)

    # Example 4: Using Anthropic with tools
    print("Example 4: Using Anthropic with tools")
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(vehicle_code)
        .with_programming_language("Python")
        .with_review_focus("Vehicle Safety")
        .with_severity("high")
        .with_tool("vehicle_selection")
        .for_client("anthropic")  # Switch to Anthropic
        .build()
    )
    print_config(config)

    # Example 5: Conversation with memory and tools
    print("Example 5: Conversation with memory and tools")
    conversation_memory = [
        {"role": "user", "content": "Can you review this vehicle code?"},
        {"role": "assistant", "content": "I'll analyze the code for vehicle safety."}
    ]
    
    config = (
        Promptix.builder("CodeReview")
        .with_code_snippet(vehicle_code)
        .with_programming_language("Python")
        .with_review_focus("Vehicle Safety")
        .with_severity("high")
        .with_tool("vehicle_selection")
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