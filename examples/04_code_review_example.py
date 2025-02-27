"""
Code Review example for Promptix library.

This example demonstrates how to use the CodeReviewer prompt template to perform
code reviews with different levels of detail and provider options.
"""

from promptix import Promptix

def main():
    print("CodeReviewer Example:\n")
    
    # Simple code snippet for demonstration
    simple_code = '''
def calculate_total(items):
    return sum(item.price for item in items)
    '''
    
    # More complex code snippet with potential issues
    complex_code = '''
def process_user_data(data):
    query = f"SELECT * FROM users WHERE id = {data['user_id']}"
    conn = get_db_connection()
    result = conn.execute(query)
    return result.fetchall()
    '''
    
    # Basic code review (using v1 - OpenAI)
    print("Basic Code Review (v1 - OpenAI):")
    code_review_basic = Promptix.get_prompt(
        prompt_template="CodeReviewer",
        code_snippet=simple_code,
        programming_language="Python",
        review_focus="code readability and error handling"
    )
    print(code_review_basic)
    print("\n" + "-"*50 + "\n")

    # Advanced code review with severity level (using v2 - Anthropic with tools)
    print("Advanced Code Review (v2 - Anthropic with tools):")
    try:
        code_review_advanced = Promptix.get_prompt(
            prompt_template="CodeReviewer",
            version="v2",
            code_snippet=complex_code,
            programming_language="Python", 
            review_focus="security vulnerabilities",
            severity="high"
        )
        print(code_review_advanced)
    except ValueError as e:
        print(f"Error: {str(e)}")
    print("\n" + "-"*50 + "\n")
    
    # Using builder pattern for code review
    print("Using Builder Pattern:")
    builder_config = (
        Promptix.builder("CodeReviewer")
        .with_code_snippet(complex_code)
        .with_programming_language("Python")
        .with_review_focus("Performance and Security")
        .build()
    )
    print(builder_config)

if __name__ == "__main__":
    main() 