# Testing the Auto-Versioning System

This document describes the comprehensive test suite for the Promptix auto-versioning system.

## 🎯 Overview

The test suite covers all aspects of the newly added pre-commit hook functionality:

- **Pre-commit hook logic** - Auto-versioning and version switching
- **Enhanced prompt loader** - Integration with version management
- **CLI tools** - Version and hook management commands
- **Full workflows** - End-to-end integration testing
- **Edge cases** - Error conditions and boundary cases

## 📁 Test Structure

```
tests/
├── unit/                           # Unit tests for individual components
│   ├── test_precommit_hook.py      # Pre-commit hook functionality
│   ├── test_enhanced_prompt_loader.py  # Enhanced prompt loader
│   ├── test_version_manager.py     # Version manager CLI
│   └── test_hook_manager.py        # Hook manager CLI
├── integration/                    # Integration tests
│   └── test_versioning_integration.py  # Full workflow tests
├── functional/                     # Functional and edge case tests
│   └── test_versioning_edge_cases.py   # Edge cases and error conditions
└── test_helpers/                   # Test utilities
    ├── __init__.py
    └── precommit_helper.py          # Testable pre-commit hook wrapper
```

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run All Tests

```bash
# Run all versioning-related tests
pytest tests/unit/test_precommit_hook.py tests/integration/test_versioning_integration.py tests/functional/test_versioning_edge_cases.py -v

# Or run all tests
pytest -v
```

### 3. Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only  
pytest tests/integration/ -v

# Edge cases only
pytest tests/functional/test_versioning_edge_cases.py -v
```

## 📊 Test Categories

### Unit Tests

**test_precommit_hook.py** - Tests core pre-commit hook logic:
- ✅ Finding promptix file changes
- ✅ Version number generation
- ✅ Version snapshot creation
- ✅ Version switching via config.yaml
- ✅ Error handling and bypass mechanisms
- ✅ Multiple agent processing
- ✅ Git integration

**test_enhanced_prompt_loader.py** - Tests enhanced prompt loader:
- ✅ current_version tracking from config.yaml
- ✅ Version header removal from files
- ✅ Version metadata integration
- ✅ Backwards compatibility with legacy prompts
- ✅ Version switching behavior
- ✅ Error condition handling

**test_version_manager.py** - Tests version management CLI:
- ✅ Agent and version listing
- ✅ Version content retrieval
- ✅ Version switching commands
- ✅ New version creation
- ✅ Error handling and validation

**test_hook_manager.py** - Tests hook management CLI:
- ✅ Hook installation and uninstallation
- ✅ Hook enabling and disabling
- ✅ Status reporting
- ✅ Hook testing functionality
- ✅ Backup and restore operations

### Integration Tests

**test_versioning_integration.py** - Tests complete workflows:
- ✅ Full development workflow (edit → commit → version → API)
- ✅ Version switching workflow with API integration
- ✅ Config-based version switching via hooks
- ✅ Multiple agent management
- ✅ Error recovery workflows
- ✅ Backwards compatibility with existing prompts

### Edge Case Tests

**test_versioning_edge_cases.py** - Tests unusual scenarios:
- ✅ Empty and very large files
- ✅ Unicode and special characters
- ✅ Extremely large version numbers
- ✅ Concurrent version creation
- ✅ Malformed version files
- ✅ Circular reference handling
- ✅ Disk full and permission errors
- ✅ Filesystem case sensitivity
- ✅ Symlink handling

## 🛠️ Advanced Testing Options

### Coverage Reports

```bash
# Run with coverage analysis
pytest --cov=promptix --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### Performance Testing

```bash
# Test with performance profiling
pytest tests/quality/test_performance.py -v
```

### Hook Validation

```bash
# Validate hook installation process
pytest tests/unit/test_hook_manager.py -v
```

### Parallel Execution

```bash
# Run tests in parallel (faster)
python -m pytest -n auto tests/unit/ tests/integration/ tests/functional/
```

## 🔍 Test Development

### Creating New Tests

1. **Unit tests** - Add to appropriate `test_*.py` file in `tests/unit/`
2. **Integration tests** - Add to `test_versioning_integration.py`
3. **Edge cases** - Add to `test_versioning_edge_cases.py`

### Test Utilities

The `PreCommitHookTester` class in `tests/test_helpers/precommit_helper.py` provides a testable interface to the pre-commit hook functionality:

```python
from tests.test_helpers.precommit_helper import PreCommitHookTester

# Create tester
tester = PreCommitHookTester(workspace_path)

# Test version creation
version_name = tester.create_version_snapshot("prompts/agent/current.md")

# Test version switching  
success = tester.handle_version_switch("prompts/agent/config.yaml")

# Test full hook logic
success, count, messages = tester.main_hook_logic(staged_files)
```

### Mocking and Fixtures

Tests use pytest fixtures for:
- Temporary workspaces with git repositories
- Mock prompt configurations
- File system structures
- Git operations

## 📋 Test Checklist

When adding new versioning features, ensure tests cover:

- [ ] **Happy path** - Normal operation
- [ ] **Error conditions** - Graceful failure handling
- [ ] **Edge cases** - Boundary conditions
- [ ] **Integration** - Works with existing API
- [ ] **Backwards compatibility** - Legacy prompts still work
- [ ] **Performance** - Reasonable execution time
- [ ] **Security** - No unsafe operations

## 🐛 Debugging Tests

### Running Individual Tests

```bash
# Run specific test file
python -m pytest tests/unit/test_precommit_hook.py -v

# Run specific test method
python -m pytest tests/unit/test_precommit_hook.py::TestPreCommitHookCore::test_find_promptix_changes_current_md -v

# Run with debug output
python -m pytest tests/unit/test_precommit_hook.py -v -s --tb=long
```

### Test Artifacts

Tests create temporary directories for isolation. If tests fail, you can inspect:

- `/tmp/test_*` - Temporary test workspaces (may be cleaned up)
- `test_report.html` - HTML test report (if generated)
- `htmlcov_versioning/` - HTML coverage report (if generated)

### Common Issues

1. **Import errors** - Ensure `PYTHONPATH` includes `src/` and `tests/test_helpers/`
2. **Permission errors** - Tests may fail on read-only filesystems
3. **Git not available** - Some tests require git command
4. **Missing dependencies** - Install from `requirements-versioning-tests.txt`

## 📈 Test Metrics

Target metrics for the test suite:

- **Target: 300+ test cases** across all categories
- **Target: 90%+ code coverage** for versioning components
- **Target: < 30 seconds** total execution time
- **Target: 100% compatibility** with existing Promptix API

## 🎯 Test Goals

The comprehensive test suite ensures:

1. **Reliability** - Auto-versioning never breaks commits
2. **Compatibility** - Existing code continues to work
3. **Performance** - Fast operation even with many versions
4. **Usability** - Clear error messages and recovery paths
5. **Maintainability** - Well-tested, stable codebase

---

**Run the tests before submitting changes to ensure the auto-versioning system works correctly!** 🚀
