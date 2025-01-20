"""
Example demonstrating the dynamic prompt generation functionality in Promptix.

This example shows how to use:
1. Dynamic templates with conditional logic
2. Schema validation
3. Nested data structures
4. Version control
5. Error handling
"""

from promptix import Promptix
from typing import Dict, Any

def print_prompt_result(title: str, context: Dict[str, Any], version: str = None):
    """Helper function to print prompt results with consistent formatting."""
    print(f"\n{title}:")
    print("-" * 50)
    
    try:
        prompt = Promptix.get_prompt(
            prompt_template="CustomerSupport",
            context=context,
            version=version
        )
        print("Generated Prompt:")
        print(prompt)
        
    except ValueError as e:
        print(f"Error: {str(e)}")
    
    print("-" * 50)

def main():
    # Example 1: High-priority premium customer (using all dynamic features)
    premium_context = {
        "user_name": "Alice Smith",
        "issue_type": "API integration",
        "issue_description": "Unable to authenticate API calls after recent update",
        "technical_level": "advanced",
        "priority": "high",
        "custom_data": {
            "product_version": "2.1.0",
            "subscription_tier": "premium"
        }
    }
    print_prompt_result(
        "1. High-Priority Premium Customer",
        premium_context
    )

    # Example 2: Regular customer (different conditional paths)
    regular_context = {
        "user_name": "Bob Johnson",
        "issue_type": "account access",
        "issue_description": "Need help resetting 2FA",
        "technical_level": "beginner",
        "priority": "medium",
        "custom_data": {
            "product_version": "2.0.0",
            "subscription_tier": "basic"
        }
    }
    print_prompt_result(
        "2. Regular Customer Support Request",
        regular_context
    )

    # Example 3: Schema validation error - missing required field
    invalid_context_1 = {
        "user_name": "Charlie Brown",
        "issue_type": "billing",
        # Missing required field: issue_description
        "technical_level": "beginner"
    }
    print_prompt_result(
        "3. Schema Validation Error - Missing Required Field",
        invalid_context_1
    )

    # Example 4: Schema validation error - invalid enum value
    invalid_context_2 = {
        "user_name": "Diana Prince",
        "issue_type": "login",
        "issue_description": "Password reset not working",
        "technical_level": "expert",  # Invalid enum value
        "priority": "critical"  # Invalid enum value
    }
    print_prompt_result(
        "4. Schema Validation Error - Invalid Enum Values",
        invalid_context_2
    )

    # Example 5: Using a specific version
    print_prompt_result(
        "5. Using Specific Version (v2)",
        regular_context,
        version="v2"
    )

    # Example 6: Code Review Example
    code_review_context = {
        "code_snippet": '''
def calculate_total(items):
    return sum(item.price for item in items)
        ''',
        "programming_language": "Python",
        "review_focus": "code readability and error handling",
        "severity": "medium"
    }
    
    try:
        prompt = Promptix.get_prompt(
            prompt_template="CodeReview",
            context=code_review_context
        )
        print("\n6. Code Review Example:")
        print("-" * 50)
        print("Generated Prompt:")
        print(prompt)
        print("-" * 50)
        
    except ValueError as e:
        print(f"\n6. Code Review Example:")
        print("-" * 50)
        print(f"Error: {str(e)}")
        print("-" * 50)

if __name__ == "__main__":
    main() 