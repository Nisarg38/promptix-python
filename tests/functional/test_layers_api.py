"""
Functional tests for layer composition API.

Tests the public API methods get_composed_prompt() and list_layers().
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from promptix import Promptix
from promptix.core.container import Container, set_container, reset_container
from promptix.core.components import LayerComposer
from promptix.core.exceptions import LayerRequiredError


@pytest.fixture
def layers_container(test_prompts_layers_dir):
    """Create a container configured for layer testing."""
    container = Container()
    # Override the layer_composer with one pointing to test fixtures
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


class TestGetComposedPrompt:
    """Test public API for layer composition."""

    def test_basic_composition(self, layers_container):
        """Basic usage with auto-selected layers."""
        prompt = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="Test Company"
        )

        assert isinstance(prompt, str)
        assert "Test Company" in prompt
        # Should have base content
        assert "customer support assistant" in prompt.lower()

    def test_single_layer_selection(self, layers_container):
        """Single layer is applied based on variable."""
        prompt = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="TechSoft Inc",
            product_line="software"
        )

        assert "TechSoft Inc" in prompt
        assert "technical support specialist" in prompt.lower()
        assert "software" in prompt.lower()

    def test_multiple_layers_merge(self, layers_container):
        """Multiple layers merge in order."""
        prompt = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="Premium Hardware Co",
            product_line="hardware",
            tier="premium"
        )

        assert "Premium Hardware Co" in prompt
        # Should have hardware content
        assert "hardware" in prompt.lower()
        # Should have premium tier content
        assert "Premium" in prompt
        # Premium tier benefits should be present
        assert "Dedicated account manager" in prompt

    def test_region_layer_eu(self, layers_container):
        """Region layer applies region-specific content."""
        prompt = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="European Tech",
            region="eu"
        )

        assert "European Tech" in prompt
        # EU content should be present (French greeting or GDPR)
        assert "Vous etes un assistant" in prompt or "GDPR" in prompt

    def test_all_layers_combined(self, layers_container):
        """All three layers applied together."""
        prompt = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="Global Software EU",
            product_line="software",
            region="eu",
            tier="premium"
        )

        assert "Global Software EU" in prompt
        # EU identity from region layer
        assert "Vous etes un assistant" in prompt or "GDPR" in prompt
        # Premium tier benefits should still be there
        assert "Premium" in prompt or "priority" in prompt.lower()

    def test_explicit_layer_versions(self, layers_container):
        """Explicit version selection for layers."""
        prompt = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="Test Store",
            tier="premium",
            layer_versions={"tier": "v1"}
        )

        # v1 version should be used (has "(v1)" marker)
        assert "(v1)" in prompt or "v1" in prompt.lower()

    def test_skip_layers(self, layers_container):
        """Skip specific layers."""
        # With region layer
        prompt_with_region = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="Test Store",
            region="eu"
        )

        # Without region layer (skipped)
        prompt_without_region = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="Test Store",
            region="eu",
            skip_layers=["region"]
        )

        assert "Vous etes un assistant" in prompt_with_region or "GDPR" in prompt_with_region
        # When skipped, EU-specific content should not appear
        assert "Vous etes un assistant" not in prompt_without_region

    def test_debug_mode(self, layers_container):
        """Debug mode returns composition info."""
        result = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="Debug Test",
            product_line="software",
            tier="premium",
            _debug=True
        )

        prompt, debug_info = result
        assert isinstance(prompt, str)
        assert "Debug Test" in prompt

        # Check debug info structure
        assert hasattr(debug_info, "base_template")
        assert hasattr(debug_info, "layers_applied")
        assert hasattr(debug_info, "layers_skipped")
        assert hasattr(debug_info, "blocks_overridden")

        # Should have applied at least 2 layers
        applied_names = [layer["name"] for layer in debug_info.layers_applied]
        assert "product_line" in applied_names
        assert "tier" in applied_names

    def test_base_version_selection(self, layers_container):
        """Base template version can be specified."""
        prompt = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            version="v1",
            company_name="Version Test"
        )

        assert "Version Test" in prompt
        # v1 has "(v1)" marker in identity block
        assert "(v1)" in prompt


class TestListLayers:
    """Test layer introspection functionality."""

    def test_list_layers(self, layers_container):
        """List available layers for a prompt."""
        layers = Promptix.list_layers("CustomerSupport")

        assert isinstance(layers, dict)
        assert "product_line" in layers
        assert "region" in layers
        assert "tier" in layers

        # Check layer values
        assert "software" in layers["product_line"]
        assert "hardware" in layers["product_line"]
        assert "us" in layers["region"]
        assert "eu" in layers["region"]
        assert "basic" in layers["tier"]
        assert "premium" in layers["tier"]


class TestBackwardCompatibility:
    """Ensure existing API still works."""

    def test_get_prompt_unchanged(self, test_prompts_dir):
        """get_prompt() still works without layers."""
        # Reset container to use default test prompts
        reset_container()

        prompt = Promptix.get_prompt(
            prompt_template="SimpleChat",
            user_name="Test User",
            assistant_name="Test Bot"
        )

        assert isinstance(prompt, str)
        assert "Test User" in prompt or "Test Bot" in prompt


class TestErrorHandling:
    """Test error scenarios."""

    def test_missing_prompt_template(self, layers_container):
        """Non-existent prompt raises error."""
        with pytest.raises(Exception):
            Promptix.get_composed_prompt(
                prompt_template="NonExistentPrompt",
                company_name="Test"
            )

    def test_instance_method_compose_prompt(self, layers_container):
        """Instance method compose_prompt works."""
        promptix = Promptix()
        prompt = promptix.compose_prompt(
            prompt_template="CustomerSupport",
            company_name="Instance Test",
            product_line="software"
        )

        assert "Instance Test" in prompt
        assert "software" in prompt.lower()


class TestLayerMergeModes:
    """Test different block merge modes."""

    def test_super_call_includes_parent(self, layers_container):
        """super() includes parent block content."""
        # Premium tier layer uses super() in capabilities block
        prompt = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="Premium Test",
            tier="premium"
        )

        # Should have both base capabilities AND premium-specific content
        assert "Answer product questions" in prompt or "Troubleshoot" in prompt  # From base
        assert "Dedicated account manager" in prompt  # From premium layer

    def test_replace_mode_overrides_completely(self, layers_container):
        """Replace mode completely overrides parent."""
        # EU region completely replaces identity block with French text
        prompt = Promptix.get_composed_prompt(
            prompt_template="CustomerSupport",
            company_name="EU Store",
            region="eu"
        )

        # EU identity should replace English
        assert "Vous etes un assistant" in prompt
        # Should NOT have the English identity anymore
        assert "You are a helpful customer support assistant" not in prompt
