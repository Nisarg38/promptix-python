# Promptix Library

A simple yet powerful library for managing and using prompts locally with Promptix Studio.

## Features

- 🔄 Version Control: Manage multiple versions of your prompts
- 📝 Schema Validation: Ensure prompt variables are correctly used
- 🎨 Template System: Use Jinja2 for dynamic prompt generation
- 🚀 Studio UI: Visual interface for prompt management
- ⚡ CLI Tools: Command-line interface for quick access
- 🛡️ Type Safety: Built-in type checking and validation
- 🔍 Smart Defaults: Intelligent handling of optional fields
- 📊 Flexible Output: Support for various output formats

## Installation

```bash
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

# Simple prompt with required fields
prompt = Promptix.get_prompt(
    prompt_template="Greeting",
    user_name="John Doe"
)
print(prompt)  # Output: Hello John Doe! How can I help you today?

# Advanced prompt with optional fields
support_prompt = Promptix.get_prompt(
    prompt_template="CustomerSupport",
    user_name="Jane Smith",
    issue_type="password reset",
    technical_level="intermediate",
    priority="high",  # Optional field
    custom_data={     # Optional nested data
        "product_version": "2.1.0",
        "subscription_tier": "premium"
    }
)
```

## Schema Validation

Promptix provides robust schema validation with smart handling of required and optional fields:

```python
# Schema example in prompts.json
{
  "CustomerSupport": {
    "schema": {
      "required": ["user_name", "issue_type"],
      "optional": ["priority", "custom_data"],
      "types": {
        "priority": ["high", "medium", "low"],
        "custom_data": "object"
      }
    }
  }
}
```

- Required fields: Warns if missing, continues with empty string
- Optional fields: Automatically initialized with appropriate defaults
- Type validation: Ensures values match defined types
- Nested fields: Proper handling of complex data structures

## Advanced Features

### Version Control

```python
# Get specific version
prompt_v1 = Promptix.get_prompt(
    prompt_template="CustomerSupport",
    version="v1",
    user_name="John"
)

# Get latest live version (default)
prompt_latest = Promptix.get_prompt(
    prompt_template="CustomerSupport",
    user_name="John"
)
```

### Dynamic Templates

```python
# Template with conditional logic
template = """
{% if priority == 'high' %}
URGENT: Immediate attention required!
{% endif %}

User: {{user_name}}
Issue: {{issue_type}}
{% if custom_data.subscription_tier == 'premium' %}
Premium Support Enabled
{% endif %}
"""
```

### Studio UI

Launch Promptix Studio for visual prompt management:

```bash
promptix studio
```

## Development

1. Clone the repository
2. Install development dependencies:
```bash
pip install -e ".[dev]"
```
3. Run tests:
```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
