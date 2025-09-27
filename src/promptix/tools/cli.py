"""
Improved CLI for Promptix using Click and Rich.
Modern, user-friendly command-line interface with beautiful output.
"""

import sys
import os
import subprocess
import socket
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich import print as rich_print

from openai.cli import main as openai_main
from ..core.config import Config
from ..core.workspace_manager import WorkspaceManager

# Create rich consoles for beautiful output
console = Console()
error_console = Console(stderr=True)

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port: int, max_attempts: int = 10) -> Optional[int]:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return None

@click.group()
@click.version_option()
def cli():
    """
    🚀 Promptix CLI - AI Prompt Engineering Made Easy
    
    A modern CLI for managing AI prompts, agents, and launching Promptix Studio.
    """
    pass

@cli.command()
@click.option(
    '--port', '-p', 
    default=8501, 
    type=int,
    help='Port to run the studio on'
)
def studio(port: int):
    """🎨 Launch Promptix Studio web interface"""
    app_path = os.path.join(os.path.dirname(__file__), "studio", "app.py")
    
    if not os.path.exists(app_path):
        error_console.print("[bold red]❌ Error:[/bold red] Promptix Studio app not found.")
        sys.exit(1)
    
    try:
        # Find an available port if the requested one is in use
        if is_port_in_use(port):
            console.print(f"[yellow]⚠️  Port {port} is in use. Finding available port...[/yellow]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Searching for available port...", total=None)
                new_port = find_available_port(port)
            
            if new_port is None:
                error_console.print(
                    f"[bold red]❌ Error:[/bold red] Could not find an available port after trying {port} through {port+9}"
                )
                sys.exit(1)
            
            console.print(f"[green]✅ Found available port: {new_port}[/green]")
            port = new_port

        # Create a nice panel with launch information
        launch_panel = Panel(
            f"[bold green]🚀 Launching Promptix Studio[/bold green]\n\n"
            f"[blue]Port:[/blue] {port}\n"
            f"[blue]URL:[/blue] http://localhost:{port}\n"
            f"[dim]Press Ctrl+C to stop the server[/dim]",
            title="Promptix Studio",
            border_style="green"
        )
        console.print(launch_panel)
        
        subprocess.run(
            ["streamlit", "run", app_path, "--server.port", str(port)],
            check=True
        )
    except FileNotFoundError:
        error_console.print(
            "[bold red]❌ Error:[/bold red] Streamlit is not installed.\n"
            "[yellow]💡 Fix:[/yellow] pip install streamlit"
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        error_console.print(f"[bold red]❌ Error launching Promptix Studio:[/bold red] {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[green]👋 Thanks for using Promptix Studio! See you next time![/green]")
        sys.exit(0)

@cli.group()
def agent():
    """🤖 Manage Promptix agents"""
    pass

@agent.command()
@click.argument('name')
def create(name: str):
    """Create a new agent
    
    NAME: Name for the new agent (e.g., 'code-reviewer')
    """
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"Creating agent '{name}'...", total=100)
            
            manager = WorkspaceManager()
            progress.update(task, advance=50)
            
            manager.create_agent(name)
            progress.update(task, advance=50)
        
        # Success message with nice formatting
        success_panel = Panel(
            f"[bold green]✅ Agent '{name}' created successfully![/bold green]\n\n"
            f"[blue]Next steps:[/blue]\n"
            f"• Configure your agent in prompts/{name}/\n"
            f"• Edit prompts/{name}/config.yaml\n"
            f"• Start building prompts in prompts/{name}/current.md",
            title="Success",
            border_style="green"
        )
        console.print(success_panel)
        
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@agent.command()
def list():
    """📋 List all agents in the current workspace"""
    try:
        manager = WorkspaceManager()
        agents = manager.list_agents()
        
        if not agents:
            console.print("[yellow]📭 No agents found in this workspace[/yellow]")
            console.print("[dim]💡 Create your first agent with: promptix agent create <name>[/dim]")
            return
        
        table = Table(title="Promptix Agents", show_header=True, header_style="bold blue")
        table.add_column("Agent Name", style="cyan")
        table.add_column("Directory", style="dim")
        
        for agent_name in agents:
            agent_path = f"prompts/{agent_name}/"
            table.add_row(agent_name, agent_path)
        
        console.print(table)
        console.print(f"\n[green]Found {len(agents)} agent(s)[/green]")
        
    except Exception as e:
        error_console.print(f"[bold red]❌ Error listing agents:[/bold red] {e}")
        sys.exit(1)

@cli.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.pass_context
def openai(ctx):
    """🔗 Pass-through to OpenAI CLI commands
    
    All arguments after 'openai' are passed directly to the OpenAI CLI.
    """
    try:
        # Validate configuration for OpenAI commands
        Config.validate()
        
        console.print("[dim]Passing command to OpenAI CLI...[/dim]")
        
        # Reconstruct the original command for OpenAI
        original_args = ['openai'] + ctx.args
        sys.argv = original_args
        
        sys.exit(openai_main())
    except Exception as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {str(e)}")
        sys.exit(1)

def main():
    """
    Main CLI entry point for Promptix.
    Enhanced with Click and Rich for better UX.
    """
    try:
        # Handle the case where user runs OpenAI commands directly
        if len(sys.argv) > 1 and sys.argv[1] not in ['studio', 'agent', 'openai', '--help', '--version']:
            # This looks like an OpenAI command, redirect
            Config.validate()
            sys.exit(openai_main())
        
        cli()
        
    except KeyboardInterrupt:
        console.print("\n[green]👋 Thanks for using Promptix! See you next time![/green]")
        sys.exit(0)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
