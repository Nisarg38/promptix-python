"""
Layer composition engine for multi-dimensional prompt customization.

This component handles composing prompts by merging blocks from multiple layers,
enabling runtime-selected overrides based on variables like OEM, store type, locale, etc.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from jinja2 import BaseLoader, Environment, TemplateError

from ..exceptions import (
    ConfigurationError,
    LayerNotFoundError,
    LayerRequiredError,
    TemplateRenderError,
)


@dataclass
class LayerConfig:
    """Configuration for a single layer axis."""

    name: str
    variable: str
    path: str
    required: bool = False
    default: Optional[str] = None


@dataclass
class BlockDefinition:
    """A parsed block from a template."""

    name: str
    content: str
    mode: str = "replace"  # replace, append, prepend


@dataclass
class CompositionDebugInfo:
    """Debug information about the composition process."""

    base_template: str
    layers_applied: List[Dict[str, Any]] = field(default_factory=list)
    layers_skipped: List[str] = field(default_factory=list)
    blocks_overridden: Dict[str, List[str]] = field(default_factory=dict)


class LayerComposer:
    """
    Composes prompts by merging blocks from multiple layers.

    The composition algorithm:
    1. Load base template and extract all block definitions
    2. For each layer in merge_order:
       a. Check if layer variable is provided
       b. Load layer template if it exists
       c. Extract block overrides from layer
       d. Merge into accumulated blocks based on mode
    3. Reconstruct final template with merged blocks
    4. Render with Jinja2 variable substitution

    Example:
        composer = LayerComposer(Path("prompts"))
        result = composer.compose(
            prompt_name="ServiceAgent",
            variables={"store_type": "automotive", "oem": "honda"},
        )
    """

    def __init__(
        self,
        prompts_dir: Path,
        logger: Optional[Any] = None
    ) -> None:
        """
        Initialize the LayerComposer.

        Args:
            prompts_dir: Path to the prompts directory.
            logger: Optional logger instance for dependency injection.
        """
        self.prompts_dir = Path(prompts_dir)
        self._logger = logger

        # Regex pattern for block extraction
        # Matches: {% block name %} or {% block name mode="append" %}
        self._block_pattern = re.compile(
            r'{%\s*block\s+(\w+)(?:\s+mode=["\'](\w+)["\'])?\s*%}'
            r'(.*?)'
            r'{%\s*endblock\s*%}',
            re.DOTALL
        )

        # Pattern for super() calls
        self._super_pattern = re.compile(r'{{\s*super\(\)\s*}}')

        # Caches for performance
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        self._block_cache: Dict[str, Dict[str, BlockDefinition]] = {}

    def compose(
        self,
        prompt_name: str,
        variables: Dict[str, Any],
        base_version: Optional[str] = None,
        layer_versions: Optional[Dict[str, str]] = None,
        skip_layers: Optional[List[str]] = None,
        _debug: bool = False
    ) -> Any:
        """
        Compose a prompt with layer overrides.

        Args:
            prompt_name: Name of the prompt template.
            variables: Variables for template rendering and layer selection.
            base_version: Version of base template (None = current).
            layer_versions: Version overrides for specific layers.
            skip_layers: Layer names to skip.
            _debug: If True, returns tuple of (prompt, debug_info).

        Returns:
            Fully composed and rendered prompt string.
            If _debug is True, returns tuple of (prompt, CompositionDebugInfo).

        Raises:
            LayerRequiredError: If a required layer variable is not provided.
            TemplateRenderError: If template rendering fails.
            ConfigurationError: If configuration is invalid.
        """
        layer_versions = layer_versions or {}
        skip_layers = skip_layers or []

        # Initialize debug info
        debug_info = CompositionDebugInfo(
            base_template=f"{prompt_name}/{'versions/' + base_version + '.md' if base_version else 'current.md'}"
        )

        # Load prompt config
        prompt_dir = self.prompts_dir / prompt_name
        config = self._load_config(prompt_dir)
        composition_config = config.get("composition", {})

        # If no composition config, fall back to base template only
        if not composition_config:
            base_content = self._load_template(prompt_dir, base_version)
            result = self._render(base_content, variables, prompt_name)
            if _debug:
                return result, debug_info
            return result

        # Load base template
        base_content = self._load_template(prompt_dir, base_version)

        # Extract blocks from base
        blocks = self._extract_blocks(base_content)
        base_structure = base_content

        # Get layer configs
        layer_configs = self._parse_layer_configs(composition_config)
        merge_order = composition_config.get("merge_order", [])

        # Apply layers in order
        for layer_name in merge_order:
            if layer_name in skip_layers:
                debug_info.layers_skipped.append(layer_name)
                continue

            layer_config = next(
                (lc for lc in layer_configs if lc.name == layer_name),
                None
            )
            if not layer_config:
                continue

            # Get layer value from variables or default
            layer_value = variables.get(
                layer_config.variable,
                layer_config.default
            )

            if not layer_value:
                if layer_config.required:
                    raise LayerRequiredError(
                        layer_name=layer_name,
                        variable_name=layer_config.variable,
                        prompt_name=prompt_name
                    )
                debug_info.layers_skipped.append(layer_name)
                continue

            # Load layer template
            layer_version = layer_versions.get(layer_name)
            layer_content = self._load_layer(
                prompt_dir,
                layer_config.path,
                str(layer_value),
                layer_version
            )

            if layer_content:
                # Extract and merge layer blocks
                layer_blocks = self._extract_blocks(layer_content)
                blocks, modified_blocks = self._merge_blocks(
                    blocks,
                    layer_blocks,
                    layer_name
                )

                # Track applied layer
                debug_info.layers_applied.append({
                    "name": layer_name,
                    "value": layer_value,
                    "version": layer_version or "current"
                })

                # Track which blocks were modified
                for block_name in modified_blocks:
                    if block_name not in debug_info.blocks_overridden:
                        debug_info.blocks_overridden[block_name] = []
                    debug_info.blocks_overridden[block_name].append(layer_name)
            else:
                debug_info.layers_skipped.append(layer_name)

        # Reconstruct template with merged blocks
        final_template = self._reconstruct_template(base_structure, blocks)

        # Render with Jinja2
        result = self._render(final_template, variables, prompt_name)

        if _debug:
            return result, debug_info
        return result

    def list_layers(self, prompt_name: str) -> Dict[str, List[str]]:
        """
        List available layers and their values for a prompt.

        Args:
            prompt_name: Name of the prompt template.

        Returns:
            Dict mapping layer names to lists of available values.
        """
        prompt_dir = self.prompts_dir / prompt_name
        config = self._load_config(prompt_dir)
        composition_config = config.get("composition", {})

        if not composition_config:
            return {}

        layer_configs = self._parse_layer_configs(composition_config)
        result: Dict[str, List[str]] = {}

        for layer_config in layer_configs:
            layer_path = prompt_dir / layer_config.path
            if layer_path.exists() and layer_path.is_dir():
                values = [
                    d.name for d in layer_path.iterdir()
                    if d.is_dir() and (d / "current.md").exists()
                ]
                result[layer_config.name] = sorted(values)
            else:
                result[layer_config.name] = []

        return result

    def _extract_blocks(self, content: str) -> Dict[str, BlockDefinition]:
        """
        Extract all block definitions from template content.

        Args:
            content: Template content to parse.

        Returns:
            Dict mapping block names to BlockDefinition objects.
        """
        blocks: Dict[str, BlockDefinition] = {}
        for match in self._block_pattern.finditer(content):
            name = match.group(1)
            mode = match.group(2) or "replace"
            block_content = match.group(3).strip()
            blocks[name] = BlockDefinition(
                name=name,
                content=block_content,
                mode=mode
            )
        return blocks

    def _merge_blocks(
        self,
        base_blocks: Dict[str, BlockDefinition],
        layer_blocks: Dict[str, BlockDefinition],
        layer_name: str
    ) -> Tuple[Dict[str, BlockDefinition], List[str]]:
        """
        Merge layer blocks into base blocks.

        Args:
            base_blocks: Current accumulated blocks.
            layer_blocks: Blocks from the layer to merge.
            layer_name: Name of the layer (for logging).

        Returns:
            Tuple of (merged blocks dict, list of modified block names).
        """
        result = dict(base_blocks)
        modified: List[str] = []

        for name, layer_block in layer_blocks.items():
            if name not in result:
                # New block from layer - warn but allow (for flexibility)
                if self._logger:
                    self._logger.warning(
                        f"Layer '{layer_name}' defines block '{name}' "
                        f"not in base template - ignoring"
                    )
                continue

            base_block = result[name]
            modified.append(name)

            if layer_block.mode == "replace":
                # Check for super() calls
                if self._super_pattern.search(layer_block.content):
                    # Replace all super() calls with parent content
                    merged_content = self._super_pattern.sub(
                        lambda _: base_block.content,
                        layer_block.content
                    )
                    result[name] = BlockDefinition(
                        name=name,
                        content=merged_content,
                        mode="replace"
                    )
                else:
                    # Complete replacement
                    result[name] = BlockDefinition(
                        name=name,
                        content=layer_block.content,
                        mode="replace"
                    )

            elif layer_block.mode == "append":
                result[name] = BlockDefinition(
                    name=name,
                    content=f"{base_block.content}\n{layer_block.content}",
                    mode="replace"
                )

            elif layer_block.mode == "prepend":
                result[name] = BlockDefinition(
                    name=name,
                    content=f"{layer_block.content}\n{base_block.content}",
                    mode="replace"
                )

        return result, modified

    def _reconstruct_template(
        self,
        structure: str,
        blocks: Dict[str, BlockDefinition]
    ) -> str:
        """
        Replace block placeholders with merged content.

        Args:
            structure: Original template structure.
            blocks: Merged block definitions.

        Returns:
            Template with blocks replaced by their content.
        """
        result = structure
        for name, block in blocks.items():
            # Replace block definition with content
            pattern = re.compile(
                r'{%\s*block\s+' + re.escape(name) +
                r'(?:\s+mode=["\'](\w+)["\'])?\s*%}'
                r'.*?'
                r'{%\s*endblock\s*%}',
                re.DOTALL
            )
            result = pattern.sub(block.content, result)
        return result

    def _load_template(
        self,
        prompt_dir: Path,
        version: Optional[str]
    ) -> str:
        """
        Load base template content.

        Args:
            prompt_dir: Path to the prompt directory.
            version: Optional version to load.

        Returns:
            Template content as string.

        Raises:
            ConfigurationError: If template file not found.
        """
        if version:
            path = prompt_dir / "versions" / f"{version}.md"
        else:
            path = prompt_dir / "current.md"

        if not path.exists():
            raise ConfigurationError(
                config_issue=f"Template not found: {path}",
                config_path=str(path)
            )

        return path.read_text(encoding="utf-8")

    def _load_layer(
        self,
        prompt_dir: Path,
        layer_path: str,
        layer_value: str,
        version: Optional[str]
    ) -> Optional[str]:
        """
        Load a layer template if it exists.

        Args:
            prompt_dir: Path to the prompt directory.
            layer_path: Relative path to layer directory.
            layer_value: Value identifying which layer variant to load.
            version: Optional version to load.

        Returns:
            Layer template content, or None if not found.
        """
        layer_dir = prompt_dir / layer_path / layer_value

        if version:
            path = layer_dir / "versions" / f"{version}.md"
        else:
            path = layer_dir / "current.md"

        if not path.exists():
            return None

        return path.read_text(encoding="utf-8")

    def _load_config(self, prompt_dir: Path) -> Dict[str, Any]:
        """
        Load prompt configuration with caching.

        Args:
            prompt_dir: Path to the prompt directory.

        Returns:
            Configuration dict.
        """
        cache_key = str(prompt_dir)
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]

        config_path = prompt_dir / "config.yaml"
        if not config_path.exists():
            self._config_cache[cache_key] = {}
            return {}

        try:
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                self._config_cache[cache_key] = config
                return config
        except yaml.YAMLError as e:
            raise ConfigurationError(
                config_issue=f"Invalid YAML in config: {e}",
                config_path=str(config_path)
            )

    def _parse_layer_configs(
        self,
        composition_config: Dict[str, Any]
    ) -> List[LayerConfig]:
        """
        Parse layer configurations from composition config.

        Args:
            composition_config: The 'composition' section of config.yaml.

        Returns:
            List of LayerConfig objects.
        """
        layers: List[LayerConfig] = []
        for layer_dict in composition_config.get("layers", []):
            layers.append(LayerConfig(
                name=layer_dict["name"],
                variable=layer_dict["variable"],
                path=layer_dict["path"],
                required=layer_dict.get("required", False),
                default=layer_dict.get("default")
            ))
        return layers

    def _render(
        self,
        template: str,
        variables: Dict[str, Any],
        prompt_name: str
    ) -> str:
        """
        Render final template with Jinja2.

        Args:
            template: Template string to render.
            variables: Variables for substitution.
            prompt_name: Name of prompt for error reporting.

        Returns:
            Rendered template string.

        Raises:
            TemplateRenderError: If rendering fails.
        """
        env = Environment(
            loader=BaseLoader(),
            trim_blocks=True,
            lstrip_blocks=True
        )

        try:
            template_obj = env.from_string(template)
            result = template_obj.render(**variables)
            # Convert escaped newlines to actual line breaks
            return result.replace("\\n", "\n")
        except TemplateError as e:
            raise TemplateRenderError(
                prompt_name=prompt_name,
                template_error=str(e),
                variables=variables
            )

    def clear_cache(self) -> None:
        """Clear all internal caches."""
        self._config_cache.clear()
        self._block_cache.clear()
