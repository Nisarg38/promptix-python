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
   
   # Or use the builder pattern:
   config = Promptix.builder("template_name").with_variable("value").build()
"""

from .core.base import Promptix

__version__ = "0.2.0"
__all__ = ["Promptix"]
