"""
CLI wrapper for Promptix.
Ensures that the `openai` CLI command is routed through the `promptix` package.
"""

import sys
import os
import subprocess
from openai.cli import main as openai_main
from ..core.config import Config

def launch_studio(port=8501):
    """Launch the Promptix Studio server using Streamlit."""
    app_path = os.path.join(os.path.dirname(__file__), "studio", "app.py")
    
    if not os.path.exists(app_path):
        print("\nError: Promptix Studio app not found.\n", file=sys.stderr)
        sys.exit(1)
    
    try:
        print(f"\nLaunching Promptix Studio on port {port}...\n")
        subprocess.run(
            ["streamlit", "run", app_path, "--server.port", str(port)],
            check=True
        )
    except FileNotFoundError:
        print("\nError: Streamlit is not installed. Please install it using: pip install streamlit\n", 
              file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\nError launching Promptix Studio: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using Promptix Studio! See you next time!\n")
        sys.exit(0)

def main():
    """
    Main CLI entry point for Promptix.
    Handles both Promptix-specific commands and OpenAI CLI passthrough.
    """
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "studio":
            # Handle studio command
            port = 8501
            if len(sys.argv) > 2 and sys.argv[2].startswith("--port="):
                try:
                    port = int(sys.argv[2].split("=")[1])
                except ValueError:
                    print("\nInvalid port number. Using default port 8501.\n", file=sys.stderr)
            launch_studio(port)
        else:
            # Validate configuration for OpenAI commands
            Config.validate()
            # Redirect to the OpenAI CLI
            sys.exit(openai_main())
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for using Promptix! See you next time!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1) 