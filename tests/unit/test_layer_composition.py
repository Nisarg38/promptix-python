"""
Unit tests for LayerComposer component.

Tests cover block extraction, merging, layer loading, and full composition.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

from promptix.core.components.layer_composer import (
    LayerComposer,
    LayerConfig,
    BlockDefinition,
    CompositionDebugInfo,
)
from promptix.core.exceptions import (
    LayerRequiredError,
    ConfigurationError,
    TemplateRenderError,
)


@pytest.fixture
def layers_fixture_path():
    """Get the path to the layers test fixtures."""
    return Path(__file__).parent.parent / "fixtures" / "test_prompts_layers"


@pytest.fixture
def layer_composer(layers_fixture_path):
    """Create a LayerComposer instance with test fixtures."""
    return LayerComposer(prompts_dir=layers_fixture_path)


@pytest.fixture
def temp_prompts_dir():
    """Create a temporary prompts directory for isolated tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestBlockExtraction:
    """Test block extraction from templates."""

    def test_extract_simple_block(self, layer_composer):
        """Extract a basic block."""
        content = """{% block greeting %}Hello, World!{% endblock %}"""
        blocks = layer_composer._extract_blocks(content)

        assert "greeting" in blocks
        assert blocks["greeting"].name == "greeting"
        assert blocks["greeting"].content == "Hello, World!"
        assert blocks["greeting"].mode == "replace"

    def test_extract_block_with_mode(self, layer_composer):
        """Extract block with mode='append'."""
        content = """{% block capabilities mode="append" %}Extra capability{% endblock %}"""
        blocks = layer_composer._extract_blocks(content)

        assert "capabilities" in blocks
        assert blocks["capabilities"].mode == "append"
        assert blocks["capabilities"].content == "Extra capability"

    def test_extract_block_with_single_quotes(self, layer_composer):
        """Extract block with mode using single quotes."""
        content = """{% block capabilities mode='prepend' %}First capability{% endblock %}"""
        blocks = layer_composer._extract_blocks(content)

        assert "capabilities" in blocks
        assert blocks["capabilities"].mode == "prepend"

    def test_extract_multiple_blocks(self, layer_composer):
        """Extract several blocks from one template."""
        content = """
        {% block header %}Header content{% endblock %}
        Some text in between
        {% block body %}Body content{% endblock %}
        {% block footer %}Footer content{% endblock %}
        """
        blocks = layer_composer._extract_blocks(content)

        assert len(blocks) == 3
        assert "header" in blocks
        assert "body" in blocks
        assert "footer" in blocks
        assert blocks["header"].content == "Header content"
        assert blocks["body"].content == "Body content"
        assert blocks["footer"].content == "Footer content"

    def test_extract_block_with_nested_jinja(self, layer_composer):
        """Block containing {% if %} statements."""
        content = """{% block capabilities %}
{% if premium %}
- Premium Support
{% endif %}
- Standard Support
{% endblock %}"""
        blocks = layer_composer._extract_blocks(content)

        assert "capabilities" in blocks
        assert "{% if premium %}" in blocks["capabilities"].content
        assert "- Premium Support" in blocks["capabilities"].content

    def test_extract_empty_block(self, layer_composer):
        """Empty block definition."""
        content = """{% block escalation %}{% endblock %}"""
        blocks = layer_composer._extract_blocks(content)

        assert "escalation" in blocks
        assert blocks["escalation"].content == ""

    def test_extract_block_with_whitespace(self, layer_composer):
        """Block with only whitespace."""
        content = """{% block escalation %}

        {% endblock %}"""
        blocks = layer_composer._extract_blocks(content)

        assert "escalation" in blocks
        # Content should be stripped
        assert blocks["escalation"].content == ""

    def test_no_blocks(self, layer_composer):
        """Template with no blocks returns empty dict."""
        content = """This is just a simple template with {{ variable }}."""
        blocks = layer_composer._extract_blocks(content)

        assert blocks == {}


class TestBlockMerging:
    """Test block merge operations."""

    def test_merge_replace_mode(self, layer_composer):
        """Default replace completely overrides parent."""
        base_blocks = {
            "greeting": BlockDefinition(
                name="greeting",
                content="Hello from base",
                mode="replace"
            )
        }
        layer_blocks = {
            "greeting": BlockDefinition(
                name="greeting",
                content="Hello from layer",
                mode="replace"
            )
        }

        result, modified = layer_composer._merge_blocks(
            base_blocks, layer_blocks, "test_layer"
        )

        assert result["greeting"].content == "Hello from layer"
        assert "greeting" in modified

    def test_merge_append_mode(self, layer_composer):
        """Append adds after parent content."""
        base_blocks = {
            "capabilities": BlockDefinition(
                name="capabilities",
                content="- Base Capability",
                mode="replace"
            )
        }
        layer_blocks = {
            "capabilities": BlockDefinition(
                name="capabilities",
                content="- Layer Capability",
                mode="append"
            )
        }

        result, modified = layer_composer._merge_blocks(
            base_blocks, layer_blocks, "test_layer"
        )

        assert "- Base Capability" in result["capabilities"].content
        assert "- Layer Capability" in result["capabilities"].content
        # Base should come first
        assert result["capabilities"].content.index("Base") < result["capabilities"].content.index("Layer")

    def test_merge_prepend_mode(self, layer_composer):
        """Prepend adds before parent content."""
        base_blocks = {
            "capabilities": BlockDefinition(
                name="capabilities",
                content="- Base Capability",
                mode="replace"
            )
        }
        layer_blocks = {
            "capabilities": BlockDefinition(
                name="capabilities",
                content="- Layer Capability",
                mode="prepend"
            )
        }

        result, modified = layer_composer._merge_blocks(
            base_blocks, layer_blocks, "test_layer"
        )

        assert "- Base Capability" in result["capabilities"].content
        assert "- Layer Capability" in result["capabilities"].content
        # Layer should come first
        assert result["capabilities"].content.index("Layer") < result["capabilities"].content.index("Base")

    def test_merge_with_super(self, layer_composer):
        """super() is replaced with parent content."""
        base_blocks = {
            "capabilities": BlockDefinition(
                name="capabilities",
                content="- Base Capability",
                mode="replace"
            )
        }
        layer_blocks = {
            "capabilities": BlockDefinition(
                name="capabilities",
                content="{{ super() }}\n- Layer Capability",
                mode="replace"
            )
        }

        result, modified = layer_composer._merge_blocks(
            base_blocks, layer_blocks, "test_layer"
        )

        assert "- Base Capability" in result["capabilities"].content
        assert "- Layer Capability" in result["capabilities"].content
        assert "{{ super() }}" not in result["capabilities"].content

    def test_merge_multiple_super_calls(self, layer_composer):
        """Multiple super() calls all get replaced."""
        base_blocks = {
            "content": BlockDefinition(
                name="content",
                content="BASE",
                mode="replace"
            )
        }
        layer_blocks = {
            "content": BlockDefinition(
                name="content",
                content="Before {{ super() }} Middle {{ super() }} After",
                mode="replace"
            )
        }

        result, modified = layer_composer._merge_blocks(
            base_blocks, layer_blocks, "test_layer"
        )

        assert result["content"].content == "Before BASE Middle BASE After"

    def test_merge_unknown_block_ignored(self, layer_composer):
        """Layer block not in base is ignored."""
        mock_logger = Mock()
        layer_composer._logger = mock_logger

        base_blocks = {
            "existing": BlockDefinition(
                name="existing",
                content="Existing content",
                mode="replace"
            )
        }
        layer_blocks = {
            "new_block": BlockDefinition(
                name="new_block",
                content="New content",
                mode="replace"
            )
        }

        result, modified = layer_composer._merge_blocks(
            base_blocks, layer_blocks, "test_layer"
        )

        assert "new_block" not in result
        assert "existing" in result
        mock_logger.warning.assert_called_once()

    def test_merge_preserves_unmodified_blocks(self, layer_composer):
        """Blocks not in layer keep base content."""
        base_blocks = {
            "header": BlockDefinition(
                name="header",
                content="Header content",
                mode="replace"
            ),
            "footer": BlockDefinition(
                name="footer",
                content="Footer content",
                mode="replace"
            )
        }
        layer_blocks = {
            "header": BlockDefinition(
                name="header",
                content="New header",
                mode="replace"
            )
        }

        result, modified = layer_composer._merge_blocks(
            base_blocks, layer_blocks, "test_layer"
        )

        assert result["header"].content == "New header"
        assert result["footer"].content == "Footer content"
        assert "header" in modified
        assert "footer" not in modified


class TestLayerLoading:
    """Test layer file resolution and loading."""

    def test_load_current_version(self, layer_composer, layers_fixture_path):
        """Load current.md when no version specified."""
        content = layer_composer._load_layer(
            prompt_dir=layers_fixture_path / "CustomerSupport",
            layer_path="layers/tier",
            layer_value="premium",
            version=None
        )

        assert content is not None
        assert "Premium" in content

    def test_load_specific_version(self, layer_composer, layers_fixture_path):
        """Load versions/v1.md when version='v1'."""
        content = layer_composer._load_layer(
            prompt_dir=layers_fixture_path / "CustomerSupport",
            layer_path="layers/tier",
            layer_value="premium",
            version="v1"
        )

        assert content is not None
        assert "(v1)" in content or "v1" in content.lower()

    def test_missing_layer_optional(self, layer_composer, layers_fixture_path):
        """Missing optional layer returns None."""
        content = layer_composer._load_layer(
            prompt_dir=layers_fixture_path / "CustomerSupport",
            layer_path="layers/region",
            layer_value="nonexistent_region",
            version=None
        )

        assert content is None

    def test_load_config(self, layer_composer, layers_fixture_path):
        """Test config loading from prompt directory."""
        config = layer_composer._load_config(
            layers_fixture_path / "CustomerSupport"
        )

        assert "composition" in config
        assert "layers" in config["composition"]
        assert "merge_order" in config["composition"]


class TestComposition:
    """Test full composition pipeline."""

    def test_compose_no_layers_config(self, temp_prompts_dir):
        """Base template only when no layers configured."""
        # Create minimal prompt without composition config
        prompt_dir = temp_prompts_dir / "SimplePrompt"
        prompt_dir.mkdir(parents=True)

        config_content = """
metadata:
  name: SimplePrompt
config:
  model: gpt-4
"""
        (prompt_dir / "config.yaml").write_text(config_content)
        (prompt_dir / "current.md").write_text("Hello, {{ name }}!")

        composer = LayerComposer(prompts_dir=temp_prompts_dir)
        result = composer.compose(
            prompt_name="SimplePrompt",
            variables={"name": "World"}
        )

        assert result == "Hello, World!"

    def test_compose_single_layer(self, layer_composer):
        """Single layer overrides base blocks."""
        result = layer_composer.compose(
            prompt_name="CustomerSupport",
            variables={
                "company_name": "TechCorp",
                "product_line": "software"
            }
        )

        assert "TechCorp" in result
        assert "software" in result.lower()

    def test_compose_multiple_layers_order(self, layer_composer):
        """Later layers override earlier layers."""
        result = layer_composer.compose(
            prompt_name="CustomerSupport",
            variables={
                "company_name": "TechCorp",
                "product_line": "software",
                "tier": "premium"
            }
        )

        # Should have premium-specific content from tier layer
        assert "Premium" in result

    def test_compose_with_skip_layers(self, layer_composer):
        """Skipped layers not applied."""
        result_with_region = layer_composer.compose(
            prompt_name="CustomerSupport",
            variables={
                "company_name": "TechCorp",
                "region": "eu"
            }
        )

        result_without_region = layer_composer.compose(
            prompt_name="CustomerSupport",
            variables={
                "company_name": "TechCorp",
                "region": "eu"
            },
            skip_layers=["region"]
        )

        # EU content should only be in result_with_region
        assert "Vous etes" in result_with_region
        assert "Vous etes" not in result_without_region

    def test_compose_with_layer_versions(self, layer_composer):
        """Specific versions loaded for layers."""
        result = layer_composer.compose(
            prompt_name="CustomerSupport",
            variables={
                "company_name": "TechCorp",
                "tier": "premium"
            },
            layer_versions={"tier": "v1"}
        )

        # v1 version should be used
        assert "(v1)" in result or "v1" in result.lower()

    def test_compose_variables_in_blocks(self, layer_composer):
        """Jinja2 variables work in merged blocks."""
        result = layer_composer.compose(
            prompt_name="CustomerSupport",
            variables={
                "company_name": "My Custom Company"
            }
        )

        assert "My Custom Company" in result

    def test_compose_debug_mode(self, layer_composer):
        """Debug mode returns composition info."""
        result, debug_info = layer_composer.compose(
            prompt_name="CustomerSupport",
            variables={
                "company_name": "TechCorp",
                "product_line": "software",
                "tier": "premium"
            },
            _debug=True
        )

        assert isinstance(debug_info, CompositionDebugInfo)
        # At least 2 layers applied: product_line and tier
        assert len(debug_info.layers_applied) >= 2
        assert any(l["name"] == "product_line" for l in debug_info.layers_applied)
        assert any(l["name"] == "tier" for l in debug_info.layers_applied)


class TestLayerIntrospection:
    """Test layer discovery functionality."""

    def test_list_layers(self, layer_composer):
        """List available layers for a prompt."""
        layers = layer_composer.list_layers("CustomerSupport")

        assert "product_line" in layers
        assert "region" in layers
        assert "tier" in layers

        assert "software" in layers["product_line"]
        assert "hardware" in layers["product_line"]
        assert "us" in layers["region"]
        assert "eu" in layers["region"]
        assert "basic" in layers["tier"]
        assert "premium" in layers["tier"]

    def test_list_layers_no_composition(self, temp_prompts_dir):
        """Return empty dict for prompts without composition config."""
        prompt_dir = temp_prompts_dir / "NoLayers"
        prompt_dir.mkdir(parents=True)
        (prompt_dir / "config.yaml").write_text("metadata:\n  name: NoLayers")
        (prompt_dir / "current.md").write_text("Simple prompt")

        composer = LayerComposer(prompts_dir=temp_prompts_dir)
        layers = composer.list_layers("NoLayers")

        assert layers == {}


class TestErrorHandling:
    """Test error scenarios."""

    def test_required_layer_missing(self, temp_prompts_dir):
        """Required layer variable not provided raises error."""
        prompt_dir = temp_prompts_dir / "RequiredLayer"
        prompt_dir.mkdir(parents=True)
        layers_dir = prompt_dir / "layers" / "region" / "us"
        layers_dir.mkdir(parents=True)

        config_content = """
metadata:
  name: RequiredLayer
composition:
  layers:
    - name: region
      variable: region
      path: layers/region
      required: true
  merge_order:
    - region
"""
        (prompt_dir / "config.yaml").write_text(config_content)
        (prompt_dir / "current.md").write_text("{% block content %}Base{% endblock %}")
        (layers_dir / "current.md").write_text("{% block content %}US{% endblock %}")

        composer = LayerComposer(prompts_dir=temp_prompts_dir)

        with pytest.raises(LayerRequiredError) as exc_info:
            composer.compose(
                prompt_name="RequiredLayer",
                variables={}  # Missing required 'region' variable
            )

        assert "region" in str(exc_info.value)

    def test_invalid_config_yaml(self, temp_prompts_dir):
        """Invalid YAML in config raises ConfigurationError."""
        prompt_dir = temp_prompts_dir / "InvalidConfig"
        prompt_dir.mkdir(parents=True)

        (prompt_dir / "config.yaml").write_text("invalid: yaml: [unclosed")
        (prompt_dir / "current.md").write_text("Test")

        composer = LayerComposer(prompts_dir=temp_prompts_dir)

        with pytest.raises(ConfigurationError):
            composer.compose(
                prompt_name="InvalidConfig",
                variables={}
            )

    def test_template_not_found(self, temp_prompts_dir):
        """Missing base template raises ConfigurationError."""
        prompt_dir = temp_prompts_dir / "NoTemplate"
        prompt_dir.mkdir(parents=True)
        (prompt_dir / "config.yaml").write_text("metadata:\n  name: NoTemplate")
        # No current.md created

        composer = LayerComposer(prompts_dir=temp_prompts_dir)

        with pytest.raises(ConfigurationError):
            composer.compose(
                prompt_name="NoTemplate",
                variables={}
            )

    def test_template_render_error(self, temp_prompts_dir):
        """Invalid Jinja2 syntax raises TemplateRenderError."""
        prompt_dir = temp_prompts_dir / "BadTemplate"
        prompt_dir.mkdir(parents=True)
        (prompt_dir / "config.yaml").write_text("metadata:\n  name: BadTemplate")
        (prompt_dir / "current.md").write_text("{{ undefined_filter | nonexistent }}")

        composer = LayerComposer(prompts_dir=temp_prompts_dir)

        with pytest.raises(TemplateRenderError):
            composer.compose(
                prompt_name="BadTemplate",
                variables={}
            )


class TestCaching:
    """Test caching functionality."""

    def test_config_caching(self, layer_composer, layers_fixture_path):
        """Config is cached after first load."""
        # Load config twice
        config1 = layer_composer._load_config(layers_fixture_path / "CustomerSupport")
        config2 = layer_composer._load_config(layers_fixture_path / "CustomerSupport")

        # Should be the same object due to caching
        assert config1 is config2

    def test_clear_cache(self, layer_composer, layers_fixture_path):
        """Cache can be cleared."""
        # Load config to populate cache
        layer_composer._load_config(layers_fixture_path / "CustomerSupport")
        assert len(layer_composer._config_cache) > 0

        layer_composer.clear_cache()

        assert len(layer_composer._config_cache) == 0
        assert len(layer_composer._block_cache) == 0
