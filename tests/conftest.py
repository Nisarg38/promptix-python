"""
Comprehensive test fixtures and mocking strategies for Promptix library.

This module provides reusable fixtures for testing various aspects of the Promptix library,
including mock clients, test data, and helper functions for consistent testing.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import tempfile
import os
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path


# Path to test prompts fixtures
TEST_PROMPTS_DIR = Path(__file__).parent / "fixtures" / "test_prompts"

# Available test prompt names (matching the folder structure)
TEST_PROMPT_NAMES = ["SimpleChat", "CodeReviewer", "TemplateDemo"]

# Edge case test data
EDGE_CASE_DATA = {
    "EmptyTemplate": {
        "versions": {
            "v1": {
                "is_live": True,
                "config": {
                    "system_instruction": "",
                    "model": "gpt-3.5-turbo"
                },
                "schema": {}
            }
        }
    },
    "NoLiveVersion": {
        "versions": {
            "v1": {
                "is_live": False,
                "config": {
                    "system_instruction": "Test",
                    "model": "gpt-3.5-turbo"
                },
                "schema": {}
            }
        }
    },
    "MultipleLiveVersions": {
        "versions": {
            "v1": {
                "is_live": True,
                "config": {
                    "system_instruction": "Test v1",
                    "model": "gpt-3.5-turbo"
                },
                "schema": {}
            },
            "v2": {
                "is_live": True,
                "config": {
                    "system_instruction": "Test v2",
                    "model": "gpt-4"
                },
                "schema": {}
            }
        }
    },
    "InvalidSchema": {
        "versions": {
            "v1": {
                "is_live": True,
                "config": {
                    "system_instruction": "Hello {{required_var}}",
                    "model": "gpt-3.5-turbo"
                },
                "schema": {
                    "required": ["required_var", "missing_var"],
                    "types": {
                        "required_var": "invalid_type"
                    }
                }
            }
        }
    }
}


@pytest.fixture
def test_prompts_dir():
    """Fixture providing path to test prompts directory."""
    return TEST_PROMPTS_DIR

def _load_prompts_from_directory(prompts_dir: Path) -> Dict[str, Any]:
    """Helper function to load prompts from a directory structure.
    
    This shared implementation is used by both sample_prompts_data fixture
    and MockPromptLoader to ensure consistency.
    """
    prompts_data = {}
    
    for prompt_dir in prompts_dir.iterdir():
        if not prompt_dir.is_dir():
            continue
        prompt_name = prompt_dir.name

        config_file = prompt_dir / "config.yaml"
        if not config_file.exists():
            continue
            
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            
        # Read current template
        current_file = prompt_dir / "current.md"
        current_template = ""
        if current_file.exists():
            with open(current_file, 'r') as f:
                current_template = f.read()
        
        # Read versioned templates
        versions = {}
        versions_dir = prompt_dir / "versions"
        if versions_dir.exists():
            for version_file in versions_dir.glob("*.md"):
                version_name = version_file.stem
                with open(version_file, 'r') as f:
                    template = f.read()
                
                versions[version_name] = {
                    "is_live": version_name == "v1",  # Assume v1 is live for testing
                    "config": {
                        "system_instruction": template,
                        "model": config.get("config", {}).get("model", "gpt-3.5-turbo"),
                        "temperature": config.get("config", {}).get("temperature", 0.7)
                    },
                    "schema": config.get("schema", {})
                }
        
        # Add current as live version if no versions found
        if not versions:
            versions["v1"] = {
                "is_live": True,
                "config": {
                    "system_instruction": current_template,
                    "model": config.get("config", {}).get("model", "gpt-3.5-turbo"),
                    "temperature": config.get("config", {}).get("temperature", 0.7)
                },
                "schema": config.get("schema", {})
            }
        
        prompts_data[prompt_name] = {"versions": versions}
    
    return prompts_data


@pytest.fixture
def sample_prompts_data(test_prompts_dir):
    """Fixture providing sample prompt data for testing (legacy compatibility)."""
    # Use the shared helper function
    return _load_prompts_from_directory(test_prompts_dir)

@pytest.fixture
def edge_case_data():
    """Fixture providing edge case prompt data for testing."""
    import copy
    return copy.deepcopy(EDGE_CASE_DATA)

@pytest.fixture
def all_test_data(sample_prompts_data, edge_case_data):
    """Fixture combining all test data."""
    import copy
    combined = copy.deepcopy(sample_prompts_data)
    combined.update(copy.deepcopy(edge_case_data))
    return combined

@pytest.fixture
def temp_prompts_dir_compat(test_prompts_dir):
    """Provide path to test prompts directory for compatibility.
    
    NOTE: Despite the historical name, this returns a DIRECTORY path (not a file path).
    This fixture exists for backward compatibility with tests that were written
    before the workspace-based structure was introduced.
    """
    yield str(test_prompts_dir)

@pytest.fixture
def temp_prompts_dir(test_prompts_dir):
    """Create a temporary copy of the test prompts directory structure."""
    import shutil
    temp_dir = tempfile.mkdtemp()
    prompts_dir = Path(temp_dir) / "prompts"
    
    # Copy test fixtures to temp directory
    shutil.copytree(test_prompts_dir, prompts_dir)
    
    yield prompts_dir
    
    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except OSError:
        pass


@pytest.fixture
def mock_openai_client():
    """Create a comprehensive mock OpenAI client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    
    # Configure the response chain
    mock_message.content = "This is a mock response from OpenAI"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    
    # Configure usage statistics
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 15
    mock_usage.total_tokens = 25
    mock_response.usage = mock_usage
    
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    """Create a comprehensive mock Anthropic client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_content = MagicMock()
    
    # Configure the response
    mock_content.text = "This is a mock response from Anthropic"
    mock_response.content = [mock_content]
    
    # Configure usage statistics
    mock_usage = MagicMock()
    mock_usage.input_tokens = 12
    mock_usage.output_tokens = 18
    mock_response.usage = mock_usage
    
    mock_client.messages.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_config(test_prompts_dir):
    """Mock configuration object for testing."""
    mock = MagicMock()
    mock.get_prompts_dir.return_value = str(test_prompts_dir)
    mock.get_prompt_file_path.return_value = str(test_prompts_dir)  # Backward compatibility
    mock.check_for_unsupported_files.return_value = []
    return mock


@pytest.fixture
def sample_memory():
    """Sample conversation memory for testing."""
    return [
        {"role": "user", "content": "Hello, can you help me?"},
        {"role": "assistant", "content": "Of course! I'm here to help."},
        {"role": "user", "content": "What's the weather like?"}
    ]


@pytest.fixture
def invalid_memory():
    """Invalid conversation memory for testing error handling."""
    return [
        {"role": "user"},  # Missing content
        {"role": "invalid_role", "content": "test"},  # Invalid role
        {"content": "missing role"},  # Missing role
        "not a dict"  # Invalid format
    ]


@pytest.fixture
def large_dataset():
    """Large dataset for performance testing."""
    return {
        f"Prompt{i}": {
            "versions": {
                f"v{j}": {
                    "is_live": j == 1,
                    "config": {
                        "system_instruction": f"This is prompt {i} version {j} with variables " + " ".join([f"{{var{k}}}" for k in range(5)]),
                        "model": "gpt-3.5-turbo"
                    },
                    "schema": {
                        "required": [f"var{k}" for k in range(5)],
                        "types": {f"var{k}": "string" for k in range(5)}
                    }
                }
                for j in range(1, 4)  # 3 versions each
            }
        }
        for i in range(100)  # 100 prompts
    }


@pytest.fixture
def complex_template_variables():
    """Complex template variables for testing edge cases."""
    return {
        "simple_string": "Hello World",
        "empty_string": "",
        "unicode_string": "Hello 世界 🌍",
        "multiline_string": "Line 1\nLine 2\nLine 3",
        "number": 42,
        "float_number": 3.14159,
        "boolean_true": True,
        "boolean_false": False,
        "none_value": None,
        "list_strings": ["apple", "banana", "cherry"],
        "list_numbers": [1, 2, 3, 4, 5],
        "empty_list": [],
        "nested_dict": {
            "level1": {
                "level2": {
                    "value": "deep_value"
                }
            }
        },
        "mixed_list": ["string", 123, True, {"key": "value"}],
        "special_chars": "Special: !@#$%^&*()_+-=[]{}|;:,.<>?",
        "html_content": "<div>HTML content</div>",
        "json_string": '{"key": "value", "number": 123}'
    }


class MockPromptLoader:
    """Mock prompt loader for consistent testing."""
    
    def __init__(self, prompts_dir=None):
        self.prompts_dir = Path(prompts_dir) if prompts_dir else TEST_PROMPTS_DIR
        self._loaded = False
        self.prompts_data = {}
    
    def load_prompts(self):
        """Mock loading prompts from folder structure."""
        self._loaded = True
        
        # Use the shared helper function
        self.prompts_data = _load_prompts_from_directory(self.prompts_dir)
        
        return self.prompts_data
    
    def is_loaded(self):
        """Check if prompts are loaded."""
        return self._loaded
    
    def get_prompt_data(self, prompt_name):
        """Get specific prompt data."""
        if not self._loaded:
            raise ValueError("Prompts not loaded")
        
        if prompt_name not in self.prompts_data:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        
        return self.prompts_data[prompt_name]


@pytest.fixture
def mock_prompt_loader(test_prompts_dir):
    """Fixture providing mock prompt loader."""
    return MockPromptLoader(test_prompts_dir)


@pytest.fixture
def mock_prompt_loader_with_edge_cases():
    """Mock prompt loader with edge case data."""
    # For edge cases, we'll use the hardcoded data since these are
    # special test cases that don't exist as real prompt folders
    loader = MockPromptLoader()
    loader.prompts_data = EDGE_CASE_DATA
    loader._loaded = True
    return loader


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset global state before each test to ensure isolation."""
    # Clear any cached data or global state
    yield
    # Cleanup after test if needed


@pytest.fixture
def performance_test_config():
    """Configuration for performance testing."""
    return {
        "max_execution_time": 1.0,  # seconds
        "memory_limit_mb": 100,
        "iterations": 1000
    }


# Helper functions for tests
def create_test_prompt_file(data: Dict[str, Any], file_path: str) -> None:
    """Helper to create test prompt files."""
    with open(file_path, 'w') as f:
        yaml.dump(data, f)


def assert_valid_model_config(config: Dict[str, Any]) -> None:
    """Helper to assert valid model configuration."""
    assert isinstance(config, dict)
    assert "messages" in config
    assert "model" in config
    assert isinstance(config["messages"], list)
    assert len(config["messages"]) > 0
    assert config["messages"][0]["role"] == "system"
    assert "content" in config["messages"][0]


def assert_valid_memory_format(memory: List[Dict[str, str]]) -> None:
    """Helper to assert valid memory format."""
    assert isinstance(memory, list)
    for message in memory:
        assert isinstance(message, dict)
        assert "role" in message
        assert "content" in message
        assert message["role"] in ["user", "assistant", "system"]
        assert isinstance(message["content"], str)


# Parametrized test data
TEMPLATE_RENDERING_CASES = [
    ("Simple variable", "Hello {{name}}", {"name": "World"}, "Hello World"),
    ("Multiple variables", "{{greeting}} {{name}}!", {"greeting": "Hi", "name": "Alice"}, "Hi Alice!"),
    ("No variables", "Static text", {}, "Static text"),
    ("Empty template", "", {}, ""),
    ("Conditional", "{% if show %}Visible{% endif %}", {"show": True}, "Visible"),
    ("Loop", "{% for item in items %}{{item}} {% endfor %}", {"items": ["a", "b"]}, "a b "),
    ("Filter", "{{ name | upper }}", {"name": "john"}, "JOHN"),
    ("Nested", "{{user.name}}", {"user": {"name": "Bob"}}, "Bob"),
]

ERROR_CASES = [
    ("Missing variable", "Hello {{missing}}", {}, "UndefinedError"),
    ("Invalid syntax", "Hello {{unclosed", {}, "TemplateSyntaxError"),
    ("Type error", "{{number.upper}}", {"number": 42}, "UndefinedError"),
]


@pytest.fixture(params=TEMPLATE_RENDERING_CASES)
def template_case(request):
    """Parametrized fixture for template rendering test cases."""
    return request.param


@pytest.fixture(params=ERROR_CASES)
def error_case(request):
    """Parametrized fixture for error test cases."""
    return request.param


# Custom assertions for better test readability
class TestAssertions:
    """Custom assertions for Promptix testing."""
    
    @staticmethod
    def assert_prompt_structure(prompt_data: Dict[str, Any]):
        """Assert valid prompt data structure."""
        assert "versions" in prompt_data
        assert isinstance(prompt_data["versions"], dict)
        
        for version_name, version_data in prompt_data["versions"].items():
            assert "config" in version_data
            assert "is_live" in version_data
            assert isinstance(version_data["is_live"], bool)
            
            config = version_data["config"]
            assert "system_instruction" in config or "model" in config
    
    @staticmethod
    def assert_coverage_improvement(old_coverage: float, new_coverage: float, min_improvement: float = 5.0):
        """Assert that test coverage has improved by a minimum amount."""
        improvement = new_coverage - old_coverage
        assert improvement >= min_improvement, f"Coverage only improved by {improvement}%, expected at least {min_improvement}%"


@pytest.fixture
def test_assertions():
    """Fixture providing custom test assertions."""
    return TestAssertions
