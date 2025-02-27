"""
API Integration example for Promptix library.

This example demonstrates how to use Promptix with the OpenAI and Anthropic APIs,
showing how to prepare model configurations and send them to the respective APIs.
"""

from promptix import Promptix
import openai
import anthropic
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def openai_example():
    """Example of using Promptix with OpenAI's API."""
    print("\n=== OpenAI Integration Example ===")
    
    try:
        # Initialize OpenAI client (uses OPENAI_API_KEY from environment)
        client = openai.OpenAI()

        # Example conversation history
        memory = [
            {"role": "user", "content": "Can you help me understand Python decorators?"}
        ]
        
        # Prepare model configuration using Promptix
        model_config = Promptix.prepare_model_config(
            prompt_template="SimpleChat",
            user_name="Sarah",
            assistant_name="CodeHelper",
            memory=memory
        )
        
        print("Model Configuration:")
        print(model_config)
        print("-" * 50)
        
        # Make the API call to OpenAI
        response = client.chat.completions.create(**model_config)
        
        # Print the response
        print("\nOpenAI Response:")
        print(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error in OpenAI example: {str(e)}")


def anthropic_example():
    """Example of using Promptix with Anthropic's API."""
    print("\n=== Anthropic Integration Example ===")
    
    # Skip this example if Anthropic API key is not available
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Skipping Anthropic example: ANTHROPIC_API_KEY not found in environment")
        return
    
    try:
        # Initialize Anthropic client (uses ANTHROPIC_API_KEY from environment)
        client = anthropic.Anthropic()
        
        # Example conversation history
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
        
        # Prepare model configuration using Promptix with the Anthropic-compatible version
        model_config = (
            Promptix.builder("CodeReviewer")
            .with_version("v2")  # v2 is Anthropic-compatible
            .with_code_snippet(code_snippet)
            .with_programming_language("Python")
            .with_review_focus("code efficiency")
            .with_severity("medium")
            .with_memory(memory)
            .for_client("anthropic")  # Specify Anthropic as the client
            .build()
        )
        
        print("Model Configuration:")
        print(model_config)
        print("-" * 50)
        
        # Make the API call to Anthropic
        response = client.messages.create(**model_config)
        
        # Print the response
        print("\nAnthropic Response:")
        print(response.content[0].text)
        
    except Exception as e:
        print(f"Error in Anthropic example: {str(e)}")


def main():
    """Run both OpenAI and Anthropic examples."""
    openai_example()
    anthropic_example()


if __name__ == "__main__":
    main() 