# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Promptix is a local-first prompt management system for production LLM applications. It provides version-controlled prompt storage, dynamic Jinja2 templating, a Streamlit-based visual editor (Studio), and multi-provider support (OpenAI, Anthropic).

**Version**: 0.2.0 (folder-based prompt structure)
**Python**: 3.9, 3.10, 3.11, 3.12

## Common Commands

```bash
# Development setup
make setup-dev          # Install deps + pre-commit hooks

# Development cycle
make dev-cycle          # format, lint, type-check, test
make quality            # Full check: format, lint, type-check, test-coverage, security, docs

# Testing
make test               # Run pytest
make test-coverage      # Coverage report (HTML)
pytest tests/functional # Fast API tests
pytest tests/unit       # Fast component tests
pytest tests/integration # Slow (needs API keys)
pytest -m "not slow"    # Skip slow tests

# Code quality
make format             # Auto-format (black + isort)
make lint               # flake8, pydocstyle, isort, black checks
make type-check         # mypy strict mode

# Run single test
pytest tests/unit/test_specific.py::test_function_name -v

# Launch Studio
make studio             # Opens Promptix Studio at localhost:8501
```

## Architecture

### Core Components

The library uses **dependency injection** via `container.py` for loose coupling between components:

```
src/promptix/
├── core/
│   ├── base.py              # Main Promptix class
│   ├── builder.py           # PromptixBuilder (fluent API)
│   ├── container.py         # Dependency injection container
│   ├── config.py            # Configuration management
│   ├── exceptions.py        # Custom exception hierarchy (17 types)
│   ├── components/          # Single-responsibility components
│   │   ├── prompt_loader.py      # Load prompts from disk
│   │   ├── template_renderer.py  # Jinja2 rendering
│   │   ├── variable_validator.py # JSON Schema validation
│   │   ├── version_manager.py    # Version tracking
│   │   └── model_config_builder.py
│   ├── adapters/            # LLM provider adapters
│   │   ├── _base.py         # Base adapter interface
│   │   ├── openai.py
│   │   └── anthropic.py
│   └── storage/             # Prompt file management
│       ├── manager.py
│       ├── loaders.py
│       └── utils.py
├── tools/                   # CLI and Studio
│   ├── cli.py               # Click-based CLI
│   └── studio/              # Streamlit web UI
└── enhancements/
    └── logging.py           # Structured logging
```

### Prompt Folder Structure

```
prompts/
└── PromptName/
    ├── config.yaml       # Metadata & current_version
    ├── current.md        # Active version content
    └── versions/
        ├── v001.md
        ├── v002.md
        └── v003.md
```

### Key Patterns

- **Builder Pattern**: `Promptix.builder("Name").with_var(...).for_client("openai").build()`
- **Adapter Pattern**: Provider-agnostic LLM integrations via adapters
- **Exception Hierarchy**: All exceptions inherit from `PromptixError` with context details dict

## Code Standards

- **Formatter**: Black (88 char line length)
- **Import sorting**: isort (black profile)
- **Type hints**: Required on all function signatures (mypy strict mode)
- **Docstrings**: Google format, 80% coverage required (interrogate)
- **Complexity**: Max cyclomatic complexity A (xenon)

### Docstring Format

```python
def example(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Brief description.

    Args:
        param1: Description of first parameter.
        param2: Description of second parameter. Defaults to None.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is empty.
    """
```

### Named Parameters

When calling functions with 3+ parameters, use explicit named arguments:
```python
# Good
function(param1=value1, param2=value2, param3=None)

# Avoid
function(value1, value2, None)
```

## Test Structure

Tests are organized into 5 categories in `tests/`:

| Directory | Purpose | Speed |
|-----------|---------|-------|
| `functional/` | Public API from user perspective | Fast |
| `unit/` | Individual components in isolation | Fast |
| `integration/` | External system integration (API calls) | Slow |
| `quality/` | Edge cases, performance, reliability | Variable |
| `architecture/` | Design patterns, DI, component structure | Fast |

Shared fixtures are in `tests/conftest.py`.

## Exception Handling

Use specific exception types from `promptix.core.exceptions`:

```python
from promptix.core.exceptions import PromptNotFoundError, ValidationError

# Exceptions include context details
raise PromptNotFoundError(
    "Prompt 'X' not found",
    details={"available_prompts": [...]}
)
```

## Pre-commit Hooks

14 hooks run automatically on commit: black, isort, flake8, mypy, pydocstyle, bandit, safety, codespell, xenon, markdownlint, pyupgrade, and standard file checks.

Run manually: `pre-commit run --all-files`
