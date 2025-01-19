# Promptix

[![PyPI version](https://badge.fury.io/py/promptix.svg)](https://badge.fury.io/py/promptix)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/promptix.svg)](https://pypi.org/project/promptix/)

A Python library for managing and using prompts with Promptix Studio integration. Promptix makes it easy to manage, version, and use prompts in your applications with a built-in web interface.

## Features

- 🎯 **Built-in Promptix Studio** - Visual prompt management interface (access via `promptix studio`)
- 🔄 **Version Control** - Track changes with live/draft states for each prompt
- 🔌 **Simple Integration** - Easy-to-use Python interface
- 📝 **Variable Substitution** - Dynamic prompts using `{{variable_name}}` syntax
- 🏃 **Local First** - No external API dependencies
- 🎨 **Web Interface** - Edit and manage prompts through a modern UI

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