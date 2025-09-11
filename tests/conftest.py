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


# Sample test data for prompts
SAMPLE_PROMPTS_DATA = {
    "SimpleChat": {
        "versions": {
            "v1": {
                "is_live": True,
                "config": {
                    "system_instruction": "You are {{assistant_name}}, a helpful assistant for {{user_name}}.",
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7
                },
                "schema": {
                    "required": ["user_name", "assistant_name"],
                    "types": {
                        "user_name": "string",
                        "assistant_name": "string"
                    }
                }
            },
            "v2": {
                "is_live": False,
                "config": {
                    "system_instruction": "You are {{assistant_name}} with personality {{personality_type}}. Help {{user_name}}.",
                    "model": "claude-3-sonnet-20240229",
                    "temperature": 0.5
                },
                "schema": {
                    "required": ["user_name", "assistant_name", "personality_type"],
                    "types": {
                        "user_name": "string",
                        "assistant_name": "string",
                        "personality_type": ["friendly", "professional", "creative"]
                    }
                }
            }
        }
    },
    "CodeReviewer": {
        "versions": {
            "v1": {
                "is_live": True,
                "config": {
                    "system_instruction": "Review this {{programming_language}} code for {{review_focus}}:\n\n{{code_snippet}}",
                    "model": "gpt-4",
                    "temperature": 0.2
                },
                "schema": {
                    "required": ["code_snippet", "programming_language", "review_focus"],
                    "types": {
                        "code_snippet": "string",
                        "programming_language": "string",
                        "review_focus": "string"
                    }
                }
            },
            "v2": {
                "is_live": False,
                "config": {
                    "system_instruction": "Review this {{programming_language}} code for {{review_focus}} with severity {{severity}}:\n\n{{code_snippet}}",
                    "model": "claude-3-opus-20240229",
                    "temperature": 0.1
                },
                "schema": {
                    "required": ["code_snippet", "programming_language", "review_focus", "severity"],
                    "types": {
                        "code_snippet": "string",
                        "programming_language": "string",
                        "review_focus": "string",
                        "severity": ["low", "medium", "high", "critical"]
                    }
                }
            }
        }
    },
    "TemplateDemo": {
        "versions": {
            "v1": {
                "is_live": True,
                "config": {
                    "system_instruction": "Create {{content_type}} about {{theme}} for {{difficulty}} level{% if elements %} covering: {{ elements | join(', ') }}{% endif %}.",
                    "model": "gpt-3.5-turbo"
                },
                "schema": {
                    "required": ["content_type", "theme", "difficulty"],
                    "types": {
                        "content_type": ["tutorial", "article", "guide"],
                        "theme": "string",
                        "difficulty": ["beginner", "intermediate", "advanced"],
                        "elements": "array"
                    }
                }
            }
        }
    },
    "ComplexCodeReviewer": {
        "versions": {
            "v1": {
                "is_live": True,
                "config": {
                    "system_instruction": "Review {{programming_language}} code for {{review_focus}} (severity: {{severity}}):\n\n{{code_snippet}}\n\nActive tools: {{active_tools}}",
                    "model": "gpt-4",
                    "tools": ["complexity_analyzer", "security_scanner", "style_checker"]
                },
                "schema": {
                    "required": ["code_snippet", "programming_language", "review_focus", "severity"],
                    "types": {
                        "code_snippet": "string",
                        "programming_language": "string",
                        "review_focus": "string",
                        "severity": ["low", "medium", "high", "critical"],
                        "active_tools": "string"
                    }
                }
            }
        }
    }
}

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
def sample_prompts_data():
    """Fixture providing sample prompt data for testing."""
    import copy
    return copy.deepcopy(SAMPLE_PROMPTS_DATA)

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
def temp_prompts_file(sample_prompts_data):
    """Create a temporary YAML file with sample prompt data."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_prompts_data, f)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    try:
        os.unlink(temp_file_path)
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
def mock_config():
    """Mock configuration object for testing."""
    mock = MagicMock()
    mock.get_prompt_file_path.return_value = "/test/path/prompts.yaml"
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
    
    def __init__(self, prompts_data=None):
        self.prompts_data = prompts_data or SAMPLE_PROMPTS_DATA
        self._loaded = False
    
    def load_prompts(self):
        """Mock loading prompts."""
        self._loaded = True
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
def mock_prompt_loader():
    """Fixture providing mock prompt loader."""
    return MockPromptLoader()


@pytest.fixture
def mock_prompt_loader_with_edge_cases():
    """Mock prompt loader with edge case data."""
    return MockPromptLoader(EDGE_CASE_DATA)


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
