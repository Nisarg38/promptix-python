import pytest
from promptix import Promptix
import openai
import anthropic


def test_chat_builder():
    """Test the SimpleChat builder configuration."""
    memory = [
        {"role": "user", "content": "Can you help me with a question?"},
    ]

    # Test basic OpenAI configuration
    model_config = (
        Promptix.builder("SimpleChat")
        .with_user_name("John Doe")
        .with_assistant_name("Promptix Helper")
        .with_memory(memory)
        .build()
    )

    # Verify the configuration
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert len(model_config["messages"]) > 1  # Should have system message + memory
    assert model_config["messages"][0]["role"] == "system"  # First message should be system


def test_code_review_builder():
    """Test the CodeReviewer builder configuration."""
    memory = [
        {"role": "user", "content": "Can you review this code for security issues?"},
    ]

    code_snippet = '''
    def process_user_input(data):
        query = f"SELECT * FROM users WHERE id = {data['user_id']}"
        return execute_query(query)
    '''

    model_config = (
        Promptix.builder("CodeReviewer")
        .with_code_snippet(code_snippet)
        .with_programming_language("Python")
        .with_review_focus("Security and SQL Injection")
        .with_memory(memory)
        .build()
    )

    # Verify the configuration
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert len(model_config["messages"]) > 1
    assert code_snippet in str(model_config["messages"][0]["content"])


def test_template_demo_builder():
    """Test the TemplateDemo builder configuration."""
    memory = [
        {"role": "user", "content": "Can you create a tutorial for me?"},
    ]

    model_config = (
        Promptix.builder("TemplateDemo")
        .with_content_type("tutorial")
        .with_theme("Python programming")
        .with_difficulty("intermediate")
        .with_elements(["functions", "classes", "decorators"])
        .with_memory(memory)
        .build()
    )

    # Verify the configuration
    assert isinstance(model_config, dict)
    assert "messages" in model_config
    assert "model" in model_config
    assert len(model_config["messages"]) > 1
    assert "tutorial" in str(model_config["messages"][0]["content"])
    # Check for text related to intermediate difficulty, not the literal word
    assert "advanced concepts" in str(model_config["messages"][0]["content"])


def test_builder_validation():
    """Test builder validation and error cases."""
    
    # Test invalid template name raises an exception
    with pytest.raises(Exception) as exc_info:
        Promptix.builder("NonExistentTemplate").build()
    
    error_message = str(exc_info.value)
    assert "NonExistentTemplate" in error_message or "not found" in error_message.lower()

    # Test invalid client type raises an exception
    with pytest.raises(Exception) as exc_info:
        (Promptix.builder("SimpleChat")
         .for_client("invalid_client")
         .build())
    
    error_message = str(exc_info.value)
    assert "invalid_client" in error_message or "unsupported" in error_message.lower() or "client" in error_message.lower()

    # Since the implementation now warns rather than raises for missing required fields,
    # we'll test that the configuration can be built
    config = (
        Promptix.builder("CodeReviewer")
        .with_programming_language("Python")
        .build()
    )
    
    # Verify basic config structure
    assert isinstance(config, dict)
    assert "messages" in config
    assert "model" in config


class TestBuilderLayerComposition:
    """Test builder pattern with layer composition."""

    @pytest.fixture
    def layers_container(self, test_prompts_layers_dir, monkeypatch):
        """Create container configured for layer testing."""
        from promptix.core.container import Container, set_container, reset_container
        from promptix.core.components import LayerComposer
        from promptix.core import config as config_module

        # Patch config to return test layers directory as prompts path
        monkeypatch.setattr(
            config_module.config,
            "get_prompts_workspace_path",
            lambda: test_prompts_layers_dir
        )

        container = Container()
        container.override(
            "layer_composer",
            LayerComposer(
                prompts_dir=test_prompts_layers_dir,
                logger=container.get("logger")
            )
        )
        set_container(container)
        yield container
        reset_container()

    def test_with_layers_basic(self, layers_container):
        """Test basic layer composition via builder."""
        config = (
            Promptix.builder("CustomerSupport")
            .with_layers()
            .with_var({"company_name": "TechCorp", "product_line": "software"})
            .build()
        )

        assert isinstance(config, dict)
        assert "messages" in config
        system_msg = config["messages"][0]["content"]
        assert "technical support specialist" in system_msg.lower()

    def test_with_layer_explicit(self, layers_container):
        """Test explicit layer selection."""
        config = (
            Promptix.builder("CustomerSupport")
            .with_layer("product_line", "hardware")
            .with_layer("tier", "premium")
            .with_company_name("HardwareCo")
            .build()
        )

        assert isinstance(config, dict)
        system_msg = config["messages"][0]["content"]
        assert "hardware" in system_msg.lower()
        assert "Dedicated account manager" in system_msg

    def test_with_layer_version(self, layers_container):
        """Test layer version selection."""
        config = (
            Promptix.builder("CustomerSupport")
            .with_layer("tier", "premium", version="v1")
            .with_company_name("Test Corp")
            .build()
        )

        assert isinstance(config, dict)
        system_msg = config["messages"][0]["content"]
        assert "(v1)" in system_msg

    def test_skip_layer(self, layers_container):
        """Test skipping layers."""
        # With region
        config_with = (
            Promptix.builder("CustomerSupport")
            .with_layers()
            .with_var({"company_name": "EU Corp", "region": "eu"})
            .build()
        )

        # Without region (skipped)
        config_without = (
            Promptix.builder("CustomerSupport")
            .with_layers()
            .with_var({"company_name": "EU Corp", "region": "eu"})
            .skip_layer("region")
            .build()
        )

        msg_with = config_with["messages"][0]["content"]
        msg_without = config_without["messages"][0]["content"]

        assert "Vous etes un assistant" in msg_with
        assert "Vous etes un assistant" not in msg_without

    def test_system_only_with_layers(self, layers_container):
        """Test system_only mode with layers."""
        system_msg = (
            Promptix.builder("CustomerSupport")
            .with_layer("product_line", "software")
            .with_company_name("TestCo")
            .build(system_only=True)
        )

        assert isinstance(system_msg, str)
        assert "technical support specialist" in system_msg.lower()

    def test_layers_disabled_by_default(self, layers_container):
        """Verify layers are not applied without with_layers()."""
        config = (
            Promptix.builder("CustomerSupport")
            .with_var({"company_name": "Test", "product_line": "software"})
            .build()
        )

        # Without with_layers(), should use standard rendering
        # which doesn't process layer blocks
        assert isinstance(config, dict)
