#!/usr/bin/env python3
"""
Example demonstrating how to use variables with tools_template in Promptix.

This example shows how variables set with .with_var() can be used in tools_template 
for conditional tool selection based on variable values.
"""

import sys
import os
import json

# Add the src directory to the path so we can import promptix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.promptix import Promptix

def print_config(config):
    """Print a configuration in a readable format."""
    if isinstance(config, dict):
        print(json.dumps(config, indent=2))
    else:
        print(config)
    print()

def main():
    """Run the examples."""
    # Example 1: Using variables to conditionally select tools via tools_template
    print("Example 1: Conditional Tools with Python")
    print("(Tools template automatically selects complexity_analyzer and security_scanner for Python)")
    config1 = (
        Promptix.builder("ComplexCodeReviewer")
        .with_var({
            'programming_language': 'Python',  # This will activate Python tools
            'severity': 'high',
            'review_focus': 'security and performance'
        })
        .build()
    )
    print_config(config1)

    # Example 2: Using different variables to select different tools
    print("Example 2: Conditional Tools with Java")
    print("(Tools template automatically selects style_checker for Java)")
    config2 = (
        Promptix.builder("ComplexCodeReviewer")
        .with_var({
            'programming_language': 'Java',  # This will activate Java tools
            'severity': 'medium',
            'review_focus': 'security'
        })
        .build()
    )
    print_config(config2)

    # Example 3: Overriding tools_template with explicit tool selection
    print("Example 3: Overriding tools_template with explicit tool selection")
    print("(Explicitly adding tools that wouldn't be selected by the template)")
    config3 = (
        Promptix.builder("ComplexCodeReviewer")
        .with_var({
            'programming_language': 'JavaScript',  # No tools defined for JavaScript in template
            'severity': 'low',
            'review_focus': 'performance'
        })
        .with_tool("complexity_analyzer")  # Explicitly adding tools
        .with_tool("security_scanner")
        .with_tool_parameter("complexity_analyzer", "thresholds", {"cyclomatic": 8, "cognitive": 5})
        .build()
    )
    print_config(config3)
    
    # Example 4: Combining template-selected and explicitly-selected tools
    print("Example 4: Combining template and explicit tool selection")
    print("(Template selects style_checker for Java, and we explicitly add complexity_analyzer)")
    config4 = (
        Promptix.builder("ComplexCodeReviewer")
        .with_var({
            'programming_language': 'Java',  # Template selects style_checker for Java
            'severity': 'high',
            'review_focus': 'security and performance'
        })
        .with_tool("complexity_analyzer")  # Explicitly add another tool
        .build()
    )
    print_config(config4)

if __name__ == "__main__":
    main() 