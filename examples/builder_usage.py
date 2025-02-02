from promptix import Promptix
import openai
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def basic_builder_example() -> None:
    """Basic example of using the builder pattern with OpenAI.
    
    This example demonstrates how to use Promptix with OpenAI's API for a customer support scenario.
    Requires OPENAI_API_KEY to be set in environment variables.
    """
    try:
        client = openai.OpenAI()  # Will automatically use OPENAI_API_KEY from environment

        memory= [
            {"role": "user", "content": "I'm having trouble with my account settings"},
        ]

        # Build configuration using the builder pattern with CustomerSupport
        model_config = (
            Promptix.builder("CustomerSupport")
            .with_user_name("John Doe")
            .with_issue_type("account_settings")
            .with_issue_description("User cannot access account settings page after recent update")
            .with_technical_level("intermediate")
            .with_priority("medium")
            .with_memory(memory)
            .build()
        )

        print("Model Config:", model_config)
        print("\n\n")        

        response = client.chat.completions.create(**model_config)
        print("Basic Example Response:", response.choices[0].message.content)
    except Exception as e:
        print(f"Error in basic builder example: {str(e)}")


def advanced_builder_example() -> None:
    """Advanced example showing code review features with OpenAI.
    
    This example demonstrates how to use Promptix for code review scenarios.
    Requires OPENAI_API_KEY to be set in environment variables.
    """
    try:
        client = openai.OpenAI()

        memory= [
            {"role": "user", "content": "Can you review this code for security issues?"},
        ]

        code_snippet = '''
        def process_user_input(data):
            query = f"SELECT * FROM users WHERE id = {data['user_id']}"
            return execute_query(query)
        '''

        model_config = (
            Promptix.builder("CodeReview")
            .with_code_snippet(code_snippet)
            .with_programming_language("Python")
            .with_review_focus("Security and SQL Injection")
            .with_severity("high")
            .with_memory(memory)
            .build()
        )

        print("Model Config:", model_config)
        print("\n\n")        

        response = client.chat.completions.create(**model_config)
        print("Advanced Example Response:", response.choices[0].message.content)
    except Exception as e:
        print(f"Error in advanced builder example: {str(e)}")


def anthropic_builder_example() -> None:
    """Example of using the builder with Anthropic.
    
    This example demonstrates how to use Promptix with Anthropic's API.
    Requires ANTHROPIC_API_KEY to be set in environment variables.
    """
    try:
        client = anthropic.Anthropic()  # Will automatically use ANTHROPIC_API_KEY from environment

        memory= [
            {"role": "user", "content": "I'm having trouble with my account settings"},
        ]

        model_config = (
            Promptix.builder("CustomerSupport")
            .with_version("v5")
            .with_user_name("John Doe")
            .with_issue_type("account_settings")
            .with_issue_description("User cannot access account settings page after recent update")
            .with_technical_level("intermediate")
            .with_priority("medium")
            .with_memory(memory)
            .for_client("anthropic")
            .build()
        )

        print("Anthropic Model Config:", model_config)
        print("\n\n")        

        message = client.messages.create(**model_config)
        print("Anthropic Response:", message.content)
    except Exception as e:
        print(f"Error in Anthropic builder example: {str(e)}")


if __name__ == "__main__":
    print("\n=== Basic Builder Example (CustomerSupport) ===")
    basic_builder_example()

    print("\n=== Advanced Builder Example (CodeReview) ===")
    advanced_builder_example()

    print("\n=== Anthropic Builder Example ===")
    anthropic_builder_example() 