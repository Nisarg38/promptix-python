"""
Basic usage example for Promptix library.

This example demonstrates how to use the SimpleChat prompt template with different versions,
showing the basic functionality of Promptix for managing prompt versions.
"""

from promptix import Promptix

def main():
    print("SimpleChat Example:\n")
    
    # Default behavior - Gets the live version (v1)
    print("Default (Live Version v1):")
    chat_prompt = Promptix.get_prompt(
        prompt_template="SimpleChat",
        user_name="John",
        assistant_name="Alex"
    )
    print(chat_prompt)
    print("\n" + "-"*50 + "\n")

    # Explicitly requesting version 2
    print("Explicitly requesting v2:")
    try:
        chat_prompt_v2 = Promptix.get_prompt(
            prompt_template="SimpleChat",
            version="v2",  # Explicitly requesting v2
            user_name="John",
            assistant_name="Alex",
            personality_type="friendly"
        )
        print(chat_prompt_v2)
    except ValueError as e:
        print(f"Error: {str(e)}")
    print("\n" + "-"*50 + "\n")

    # Incomplete parameters example (missing required parameter)
    print("Error Handling Example (Missing Required Parameter):")
    try:
        incomplete_prompt = Promptix.get_prompt(
            prompt_template="SimpleChat",
            user_name="John"
            # Missing assistant_name parameter
        )
    except ValueError as e:
        print(f"Error: {str(e)}")
    print("\n" + "-"*50 + "\n")
    
    # Non-existent template example
    print("Error Handling Example (Non-existent Template):")
    try:
        non_existent_prompt = Promptix.get_prompt(
            prompt_template="NonExistentTemplate",
            user_name="John"
        )
    except ValueError as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 