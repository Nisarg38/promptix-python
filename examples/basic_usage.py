"""
Basic usage example for Promptix library.

This example demonstrates how Promptix manages prompt versions through Promptix Studio,
showing how only the 'live' version is served by default while maintaining access to previous versions.
"""

from promptix import Promptix


def main():
    print("Customer Support Prompt Example:\n")

    # Default behavior - Gets the live version (v3)
    print("Default (Live Version):")
    support_prompt = Promptix.get_prompt(
        prompt_template="CustomerSupport",
        user_name="John Doe",
        issue_type="password reset",
        technical_level="intermediate",
        interaction_history="2 previous tickets about 2FA setup",
        product_version="2.1.0",
    )
    print(support_prompt)
    print("\n" + "-" * 50 + "\n")

    # Explicitly requesting an older version (v1)
    print("Explicitly requesting v1:")
    support_prompt_v1 = Promptix.get_prompt(
        prompt_template="CustomerSupport",
        version="v1",  # Explicitly requesting v1
        user_name="John Doe",
        issue_type="password reset",
        technical_level="intermediate",
        interaction_history="2 previous tickets about 2FA setup",
        product_version="2.1.0",
    )
    print(support_prompt_v1)
    print("\n" + "-" * 50 + "\n")

    # Code Review Example (using live version)
    print("Code Review Example (Live Version):")
    code_snippet = """
    def calculate_total(items):
        return sum(item.price for item in items)
    """

    code_review_prompt = Promptix.get_prompt(
        prompt_template="CodeReview",
        code_snippet=code_snippet,
        programming_language="Python",
        review_focus="code readability and error handling",
        severity="medium",
    )
    print(code_review_prompt)
    print("\n" + "-" * 50 + "\n")

    # Error Handling Example
    print("Error Handling Example:")
    try:
        prompt = Promptix.get_prompt(
            prompt_template="NonExistentTemplate", user_name="John Doe"
        )
    except ValueError as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
