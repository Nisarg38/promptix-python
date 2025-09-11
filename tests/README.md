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

## Test Organization

- `test_01_basic.py`: Basic prompt retrieval tests
- `test_02_builder.py`: Builder pattern tests
- `test_03_template_features.py`: Template rendering tests
- `test_04_complex.py`: Complex prompt scenarios
- `test_05_api_integration.py`: OpenAI & Anthropic integration
- `test_06_conditional_tools.py`: Conditional tools tests
- `test_07_architecture_refactor.py`: Tests for future architecture (skipped)
- `test_components.py`: Component-level tests (storage, config, adapters, utils)
- `test_edge_cases.py`: Edge case and error condition tests
- `test_integration_advanced.py`: Advanced end-to-end integration tests
- `test_performance.py`: Performance benchmarks

## Markers and Skips

- Tests marked `@pytest.mark.skip` are for future features or components not yet implemented.
- Use `-v` for verbose output and `--tb=line` for concise tracebacks.
- Slow tests can be deselected with:
  ```bash
  pytest -m "not slow"
  ```
