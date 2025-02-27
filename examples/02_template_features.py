"""
Template Features example for Promptix library.

This example demonstrates how to use the TemplateDemo prompt to showcase
conditional logic, loops, and other templating features in Promptix.
"""

from promptix import Promptix
from typing import List, Optional

def generate_content(
    content_type: str,
    theme: str,
    difficulty: str,
    elements: Optional[List[str]] = None
) -> str:
    """
    Generate content using the TemplateDemo prompt with various parameters.
    
    Args:
        content_type: Type of content to generate (e.g., 'tutorial', 'article')
        theme: Main theme or topic
        difficulty: Difficulty level ('beginner', 'intermediate', 'advanced')
        elements: Optional list of elements to include
    
    Returns:
        Generated prompt with conditional formatting
    """
    return Promptix.get_prompt(
        prompt_template="TemplateDemo",
        content_type=content_type,
        theme=theme,
        difficulty=difficulty,
        elements=elements or []
    )

def main():
    print("Template Features Example:\n")
    
    # Example 1: Beginner tutorial with no elements
    print("Example 1: Beginner Tutorial (No Elements)")
    print("-" * 50)
    prompt1 = generate_content(
        content_type="tutorial",
        theme="Python functions",
        difficulty="beginner"
    )
    print(prompt1)
    print("\n" + "-"*50 + "\n")

    # Example 2: Intermediate tutorial with elements
    print("Example 2: Intermediate Tutorial (With Elements)")
    print("-" * 50)
    prompt2 = generate_content(
        content_type="tutorial",
        theme="Python decorators",
        difficulty="intermediate",
        elements=["Basic decorator syntax", "Decorators with arguments", "Real-world examples"]
    )
    print(prompt2)
    print("\n" + "-"*50 + "\n")

    # Example 3: Advanced article
    print("Example 3: Advanced Article")
    print("-" * 50)
    prompt3 = generate_content(
        content_type="article",
        theme="Python metaclasses",
        difficulty="advanced",
        elements=["Type theory", "Use cases for metaclasses", "Performance considerations"]
    )
    print(prompt3)

if __name__ == "__main__":
    main() 