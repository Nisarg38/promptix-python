"""
Promptix - Prompt Version Control System

A library for managing and using prompts locally with Promptix Studio integration.
Provides a simple interface to manage prompts through a web UI and use them in your code.

Core Features:
- Prompt version control and management
- System message templating
- Variable substitution
- Configuration management
- Provider-specific enhancements

Usage:
1. Manage prompts: Run 'promptix studio' in terminal
2. Use prompts:
   from promptix import Promptix
   prompt = Promptix.get_prompt("template_name", variable="value")
"""

from .core.base import Promptix
from .tools.cli import main as cli_main

__version__ = "0.1.0"
__all__ = ["Promptix", "cli_main"]
