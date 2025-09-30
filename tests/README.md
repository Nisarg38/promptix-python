# Tests Directory

This folder contains all pytest test files for the `promptix` library.

## Running Tests

To run all tests against the **source code** and gather coverage:

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests with source path in PYTHONPATH
PYTHONPATH=src python3 -m pytest --cov=promptix --cov-report=html tests/ -v
```

To run tests against the **installed package**:

```bash
pytest --cov=promptix --cov-report=html tests/ -v
```

## Running Tests by Category

You can run specific test categories independently:

```bash
# Run only functional tests (fast, user-facing API)
pytest tests/functional/ -v

# Run only unit tests (fast, isolated components)
pytest tests/unit/ -v

# Run only integration tests (slower, external dependencies)
pytest tests/integration/ -v

# Run only quality tests (includes performance tests)
pytest tests/quality/ -v

# Run only architecture tests
pytest tests/architecture/ -v

# Run fast tests only (exclude performance tests)
pytest tests/functional/ tests/unit/ tests/architecture/ -v
```

## Test Organization

The tests are organized into logical directories for better maintainability and clarity:

### 📁 `functional/` - User-Facing API Tests
Tests that verify the public API works correctly from an end-user perspective:
- `test_prompt_retrieval.py`: Basic get_prompt() functionality
- `test_builder_pattern.py`: Builder pattern API tests
- `test_template_rendering.py`: Template rendering features
- `test_complex_templates.py`: Complex template scenarios
- `test_conditional_features.py`: Conditional tools and features

### 📁 `integration/` - External System Integration
Tests that verify interaction with external systems and APIs:
- `test_api_clients.py`: OpenAI & Anthropic API integration
- `test_workflows.py`: Advanced end-to-end workflow integration

### 📁 `unit/` - Component Unit Tests  
Tests that focus on individual components in isolation:
- `test_individual_components.py`: Storage, config, adapters, utils
- `adapters/`: Client adapter specific unit tests

### 📁 `quality/` - Quality Assurance Tests
Tests for edge cases, performance, and reliability:
- `test_edge_cases.py`: Edge cases and error condition handling
- `test_performance.py`: Performance benchmarks and scalability

### 📁 `architecture/` - Design and Structure Tests
Tests that verify architectural design and component structure:
- `test_components.py`: Dependency injection, architecture patterns

## Markers and Skips

- Tests marked `@pytest.mark.skip` are for future features or components not yet implemented.
- Use `-v` for verbose output and `--tb=line` for concise tracebacks.
- Slow tests can be deselected with:
  ```bash
  pytest -m "not slow"
  ```
