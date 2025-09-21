# Contributing to Promptix

Welcome to the Promptix project! We're excited to have you contribute. This document provides guidelines and best practices for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Documentation](#documentation)
- [Testing](#testing)
- [Security](#security)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Make (optional, but recommended)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nisarg38/promptix-python.git
   cd promptix-python
   ```

2. **Set up development environment:**
   ```bash
   # Using Make (recommended)
   make setup-dev
   
   # Or manually:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   pre-commit install
   ```

3. **Verify setup:**
   ```bash
   make ci-check  # Runs all quality checks
   ```

### Development Commands

We provide a comprehensive Makefile for development tasks:

```bash
# Show all available commands
make help

# Quick development cycle
make dev-cycle  # format, lint, type-check, test

# Full quality check
make quality    # format, lint, type-check, test-coverage, security-audit, docs

# Run tests
make test              # Basic tests
make test-coverage     # With coverage report
make test-watch        # Watch mode for TDD

# Code quality
make lint              # All linting
make format            # Auto-format code
make type-check        # Type checking with mypy
make security-audit    # Security scanning

# Documentation
make docs              # Build documentation
make docs-serve        # Serve docs locally
```

## Code Standards

### Code Style

We use strict code formatting and quality standards:

- **Black** for code formatting (88 character line length)
- **isort** for import sorting
- **flake8** with plugins for linting
- **mypy** for type checking
- **pydocstyle** for docstring style (Google format)

### Docstring Format

All public functions, classes, and modules must have docstrings in **Google format**:

```python
def example_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Brief description of the function.
    
    Longer description if needed. Explain the purpose, behavior,
    and any important details about the function.
    
    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter. Defaults to None.
        
    Returns:
        Description of the return value and its structure.
        
    Raises:
        ValueError: When param1 is empty.
        TypeError: When param2 is not an integer.
        
    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        {'status': 'success', 'data': 'test'}
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    return {"status": "success", "data": param1}
```

### Type Hints

- All function signatures must include type hints
- Use `from typing import` for complex types
- Prefer specific types over `Any` when possible
- Use `Optional[T]` for optional parameters

```python
from typing import Dict, List, Optional, Union
from pathlib import Path

def process_files(
    file_paths: List[Path], 
    config: Optional[Dict[str, Any]] = None
) -> Union[str, None]:
    """Process multiple files with optional configuration."""
    # Implementation here
    pass
```

### Error Handling

- Use specific exception types, not generic `Exception`
- Provide meaningful error messages
- Log errors appropriately using the structured logging system
- Document all exceptions in docstrings

```python
from promptix.core.exceptions import PromptNotFoundError
from promptix.enhancements.logging import get_logger

logger = get_logger(__name__)

def load_prompt(name: str) -> str:
    """
    Load a prompt by name.
    
    Args:
        name: The name of the prompt to load.
        
    Returns:
        The prompt content.
        
    Raises:
        PromptNotFoundError: If the prompt doesn't exist.
        ValueError: If name is empty or invalid.
    """
    if not name or not name.strip():
        raise ValueError("Prompt name cannot be empty")
    
    try:
        # Load prompt logic here
        pass
    except FileNotFoundError as e:
        logger.error("Prompt file not found", extra={"prompt_name": name})
        raise PromptNotFoundError(f"Prompt '{name}' not found") from e
```

### Code Organization

- Follow the existing project structure
- Group related functionality in modules
- Use dependency injection where appropriate
- Minimize circular dependencies
- Keep functions and classes focused (Single Responsibility Principle)

## Documentation

### API Documentation

We use Sphinx for generating API documentation:

- All public APIs must be documented
- Include examples in docstrings
- Keep documentation up-to-date with code changes

### README and Guides

- Update README.md for user-facing changes
- Add examples for new features
- Create guides for complex functionality

## Testing

### Test Requirements

- All new features must include tests
- Aim for >80% test coverage
- Test both happy paths and error conditions
- Use meaningful test names that describe the scenario

### Test Structure

```python
import pytest
from promptix.core.exceptions import PromptNotFoundError
from promptix import Promptix

class TestPromptix:
    """Test suite for Promptix core functionality."""
    
    def test_render_prompt_with_valid_template_returns_rendered_content(self):
        """Test that rendering a valid template returns the expected content."""
        # Arrange
        promptix = Promptix()
        template_name = "greeting"
        variables = {"name": "Alice"}
        
        # Act
        result = promptix.render_prompt(template_name, **variables)
        
        # Assert
        assert "Hello, Alice" in result
    
    def test_render_prompt_with_missing_template_raises_prompt_not_found_error(self):
        """Test that rendering a non-existent template raises PromptNotFoundError."""
        # Arrange
        promptix = Promptix()
        
        # Act & Assert
        with pytest.raises(PromptNotFoundError, match="Template 'nonexistent' not found"):
            promptix.render_prompt("nonexistent")
```

### Test Categories

Use pytest markers to categorize tests:

```python
@pytest.mark.slow
def test_performance_with_large_dataset():
    """Test performance with a large dataset (marked as slow)."""
    pass

@pytest.mark.integration
def test_api_integration():
    """Test integration with external APIs."""
    pass
```

Run specific test categories:
```bash
# Skip slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration
```

## Security

### Security Best Practices

- Never commit secrets, API keys, or sensitive data
- Use environment variables for configuration
- Validate all inputs
- Follow secure coding practices
- Regularly update dependencies

### Security Tools

We use several tools for security scanning:

- **bandit** - Python security linter
- **safety** - Dependency vulnerability scanner
- **pip-audit** - Package vulnerability checker

Run security checks:
```bash
make security-audit
```

### Reporting Security Issues

If you discover a security vulnerability, please:

1. **Do not** create a public issue
2. Email security@promptix.io with details
3. Include steps to reproduce if possible
4. Wait for acknowledgment before public disclosure

## Pull Request Process

### Before Submitting

1. **Run quality checks:**
   ```bash
   make quality
   ```

2. **Update documentation** if needed

3. **Add tests** for new functionality

4. **Update CHANGELOG.md** with your changes

### PR Guidelines

1. **Clear title and description:**
   - Use descriptive titles
   - Explain what and why, not just how
   - Reference related issues

2. **Small, focused changes:**
   - One feature/fix per PR
   - Break large changes into smaller PRs
   - Keep PRs reviewable (< 500 lines when possible)

3. **Code review process:**
   - Address all review comments
   - Update tests if implementation changes
   - Ensure CI passes

### PR Template

```markdown
## Description
Brief description of changes and why they're needed.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated documentation

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## Release Process

### Version Management

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

### Release Steps

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create release PR** and get approval
4. **Tag release** after merge
5. **GitHub Actions** automatically publishes to PyPI

### Release Notes

Include in CHANGELOG.md:
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Now removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

## Getting Help

- **Questions**: Open a [Discussion](https://github.com/your-org/promptix-python/discussions)
- **Bug Reports**: Open an [Issue](https://github.com/your-org/promptix-python/issues)
- **Feature Requests**: Open an [Issue](https://github.com/your-org/promptix-python/issues) with the "enhancement" label

## License

By contributing to Promptix, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in our [Contributors](https://github.com/your-org/promptix-python/graphs/contributors) page and in release notes for significant contributions.

Thank you for contributing to Promptix! 🚀
