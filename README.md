# Promptix

[![PyPI version](https://badge.fury.io/py/promptix.svg)](https://badge.fury.io/py/promptix)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/promptix.svg)](https://pypi.org/project/promptix/)
[![PyPI Downloads](https://static.pepy.tech/badge/promptix)](https://pepy.tech/projects/promptix)

A Python library for managing and using prompts with Promptix Studio integration. Promptix makes it easy to manage, version, and use prompts in your applications with a built-in web interface.

## Features

- 🎯 **Built-in Promptix Studio** - Visual prompt management interface (access via `promptix studio`)
- 🔄 **Version Control** - Track changes with live/draft states for each prompt
- 🔌 **Simple Integration** - Easy-to-use Python interface
- 📝 **Variable Substitution** - Dynamic prompts using `{{variable_name}}` syntax
- 🤖 **LLM Integration** - Direct integration with OpenAI and other LLM providers
- 🏃 **Local First** - No external API dependencies
- 🎨 **Web Interface** - Edit and manage prompts through a modern UI
- 🔍 **Schema Validation** - Automatic validation of prompt variables and structure

## Installation

```bash
# Install from PyPI
pip install promptix
```

## Quick Start

1. Launch Promptix Studio to manage your prompts:

```bash
promptix studio
```

This opens Promptix Studio in your default browser at `localhost:8501`.

2. Use prompts in your code:

```python
from promptix import Promptix

# Simple prompt with variables
prompt = Promptix.get_prompt(
    prompt_template="Greeting",
    user_name="John Doe"
)
print(prompt)  # Output: Hello John Doe! How can I help you today?

# Advanced prompt with multiple variables
support_prompt = Promptix.get_prompt(
    prompt_template="CustomerSupport",
    user_name="Jane Smith",
    issue_type="password reset",
    technical_level="intermediate",
    interaction_history="2 previous tickets about 2FA setup"
)
```

## OpenAI Integration

Promptix provides seamless integration with OpenAI's chat models:

```python
from promptix import Promptix
import openai

client = openai.OpenAI()

# Prepare model configuration with conversation memory
memory = [
    {"role": "user", "content": "I'm having trouble resetting my password"},
    {"role": "assistant", "content": "I understand you're having password reset issues. Could you tell me what happens when you try?"}
]

model_config = Promptix.prepare_model_config(
    prompt_template="CustomerSupport",
    user_name="John Doe",
    issue_type="password reset",
    technical_level="intermediate",
    interaction_history="2 previous tickets about 2FA setup",
    issue_description="User is unable to reset their password after multiple attempts",
    custom_data={"product_version": "2.1.0", "subscription_tier": "standard"},
    memory=memory,
)

# Use the configuration with OpenAI
response = client.chat.completions.create(**model_config)
```

## Builder Pattern

Promptix provides a fluent builder pattern interface for creating model configurations:

```python
# OpenAI Integration
from promptix import Promptix
import openai

client = openai.OpenAI()

# Using builder pattern for CustomerSupport
model_config = (
    Promptix.builder("CustomerSupport")
    .with_user_name("John Doe")
    .with_issue_type("account_settings")
    .with_issue_description("User cannot access account settings page")
    .with_technical_level("intermediate")
    .with_priority("medium")
    .with_memory([
        {"role": "user", "content": "I'm having trouble with my account settings"}
    ])
    .build()
)

response = client.chat.completions.create(**model_config)

# Using builder pattern for Code Review
code_config = (
    Promptix.builder("CodeReview")
    .with_code_snippet(code_snippet)
    .with_programming_language("Python")
    .with_review_focus("Security and SQL Injection")
    .with_severity("high")
    .build()
)

response = client.chat.completions.create(**code_config)


# Anthropic Integration
from promptix import Promptix
import anthropic

client = Anthropic()

anthropic_config = (
    Promptix.builder("CustomerSupport")
    .with_version("v5")
    .with_user_name("John Doe")
    .with_issue_type("account_settings")
    .with_memory(memory)
    .for_client("anthropic")
    .build()
)

response = client.messages.create(**anthropic_config)


```

The builder pattern provides:
- Type-safe configuration building
- Fluent interface for better code readability
- Automatic validation of required fields
- Support for multiple LLM providers
- Clear separation of configuration concerns

## Tools and Functions Support

Promptix supports adding tools and functions to your LLM configurations, making it easy to enable specific capabilities for different use cases:

```python
# OpenAI Integration
from promptix import Promptix
import openai

client = openai.OpenAI()

# Tools with conversation memory
conversation_memory = [
    {"role": "user", "content": "Can you review this API endpoint code?"},
    {"role": "assistant", "content": "I'll analyze the code for security and performance issues."}
]

# Using both tools and functions for comprehensive review
config = (
    Promptix.builder("CodeReview")
    .with_code_snippet(code)
    .with_programming_language("Python")
    .with_review_focus("Performance")
    .with_tool("complexity_analyzer")  # Tool for code complexity analysis
    .with_function("benchmark_code")   # Function to run performance tests
    .with_memory(conversation_memory)
    .build()
)

response = client.chat.completions.create(**config)

# Using tools with different LLM providers
from promptix import Promptix
import anthropic

client = Anthropic()

# Tools with conversation memory
conversation_memory = [
    {"role": "user", "content": "Can you review this API endpoint code?"},
    {"role": "assistant", "content": "I'll analyze the code for security and performance issues."}
]

anthropic_config = (
    Promptix.builder("CodeReview")
    .with_code_snippet(code)
    .with_review_focus("Best Practices")
    .with_tool("style_checker")        # Tool for code style analysis
    .with_tool("dependency_scanner")   # Tool for dependency analysis
    .for_client("anthropic")          # Switch to Anthropic
    .with_memory(conversation_memory)
    .build()
)


response = client.messages.create(**anthropic_config)

```

Key features of Tools and Functions support:
- 🛠 **Specialized Tools** - Enable specific analysis capabilities like security scanning and performance testing
- 🔄 **Function Integration** - Add custom functions for enhanced code analysis
- 🤝 **Multi-Provider Support** - Tools work across different LLM providers
- 🧠 **Memory Compatible** - Use tools alongside conversation memory
- ⚠️ **Validation** - Automatic validation of tool and function configurations
- 🔌 **Extensible** - Easy to add new tools and functions for your specific review needs

## Advanced Usage

### Version Control

```python
# Get specific version of a prompt
prompt_v1 = Promptix.get_prompt(
    prompt_template="CustomerSupport",
    version="v1",
    user_name="John"
)

# Get latest live version (default behavior)
prompt_latest = Promptix.get_prompt(
    prompt_template="CustomerSupport",
    user_name="John"
)
```

### Schema Validation

Promptix automatically validates your prompt variables against defined schemas:

```python
# Schema validation ensures correct variable types and values
try:
    prompt = Promptix.get_prompt(
        prompt_template="CustomerSupport",
        user_name="John",
        technical_level="expert"  # Will raise error if not in ["beginner", "intermediate", "advanced"]
    )
except ValueError as e:
    print(f"Validation Error: {str(e)}")
```

### Error Handling

```python
try:
    prompt = Promptix.get_prompt(
        prompt_template="NonExistentTemplate",
        user_name="John"
    )
except ValueError as e:
    print(f"Error: {str(e)}")
```

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/promptix/promptix-python.git
cd promptix-python
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Style

We use `black` for code formatting and `isort` for import sorting:

```bash
black .
isort .
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 