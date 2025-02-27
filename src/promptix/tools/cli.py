"""
CLI wrapper for Promptix.
Ensures that the `openai` CLI command is routed through the `promptix` package.
"""

import sys
import os
import subprocess
import socket
import argparse
from openai.cli import main as openai_main
from ..core.config import Config

def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return None

def launch_studio(port=8501):
    """Launch the Promptix Studio server using Streamlit."""
    app_path = os.path.join(os.path.dirname(__file__), "studio", "app.py")
    
    if not os.path.exists(app_path):
        print("\nError: Promptix Studio app not found.\n", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Find an available port if the requested one is in use
        if is_port_in_use(port):
            new_port = find_available_port(port)
            if new_port is None:
                print(f"\nError: Could not find an available port after trying {port} through {port+9}\n", 
                      file=sys.stderr)
                sys.exit(1)
            print(f"\nPort {port} is in use. Trying port {new_port}...")
            port = new_port

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
            # Create parser for studio command
            parser = argparse.ArgumentParser(
                prog="promptix studio",
                description="Launch Promptix Studio web interface",
                usage="promptix studio [-p PORT] [--port PORT]"
            )
            parser.add_argument(
                "-p", "--port",
                type=int,
                default=8501,
                help="Port to run the studio on (default: 8501)"
            )
            
            # Remove 'studio' from sys.argv to parse remaining args
            sys.argv.pop(1)
            args = parser.parse_args(sys.argv[1:])
            
            launch_studio(args.port)
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