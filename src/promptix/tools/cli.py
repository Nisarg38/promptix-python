"""
Improved CLI for Promptix using Click and Rich.
Modern, user-friendly command-line interface with beautiful output.
"""

import sys
import os
import subprocess
import socket
import shutil
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
from .version_manager import VersionManager
from .hook_manager import HookManager

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
    # Resolve and validate streamlit executable
    streamlit_path = shutil.which("streamlit")
    if not streamlit_path:
        error_console.print(
            "[bold red]❌ Error:[/bold red] Streamlit is not installed.\n"
            "[yellow]💡 Fix:[/yellow] pip install streamlit"
        )
        sys.exit(1)
    
    # Convert to absolute path and validate app path
    app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "studio", "app.py"))
    
    if not os.path.exists(app_path):
        error_console.print("[bold red]❌ Error:[/bold red] Promptix Studio app not found.")
        sys.exit(1)
    
    if not os.path.isfile(app_path):
        error_console.print("[bold red]❌ Error:[/bold red] Promptix Studio app path is not a file.")
        sys.exit(1)
    
    try:
        # Validate and normalize port
        if not isinstance(port, int) or port < 1 or port > 65535:
            error_console.print("[bold red]❌ Error:[/bold red] Port must be between 1 and 65535")
            sys.exit(1)
        
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
            [streamlit_path, "run", app_path, "--server.port", str(port)],
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

@cli.group()
def version():
    """🔄 Manage prompt versions"""
    pass

@version.command()
def list():
    """📋 List all agents and their current versions"""
    try:
        vm = VersionManager()
        vm.list_agents()
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@version.command()
@click.argument('agent')
def versions(agent: str):
    """📋 List all versions for a specific agent
    
    AGENT: Name of the agent to list versions for
    """
    try:
        vm = VersionManager()
        vm.list_versions(agent)
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@version.command()
@click.argument('agent')
@click.argument('version_name')
def get(agent: str, version_name: str):
    """📖 Get content of a specific version
    
    AGENT: Name of the agent
    VERSION_NAME: Version to retrieve (e.g., v001)
    """
    try:
        vm = VersionManager()
        vm.get_version(agent, version_name)
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@version.command()
@click.argument('agent')
@click.argument('version_name')
def switch(agent: str, version_name: str):
    """🔄 Switch agent to a specific version
    
    AGENT: Name of the agent
    VERSION_NAME: Version to switch to (e.g., v001)
    """
    try:
        console.print(f"[yellow]🔄 Switching {agent} to {version_name}...[/yellow]")
        
        vm = VersionManager()
        vm.switch_version(agent, version_name)
        
        success_panel = Panel(
            f"[bold green]✅ Successfully switched {agent} to {version_name}[/bold green]\n\n"
            f"[blue]Next steps:[/blue]\n"
            f"• Review current.md to see the deployed version\n"
            f"• Commit changes: git add . && git commit -m 'Switch to {version_name}'\n"
            f"• The pre-commit hook will create a new version if needed",
            title="Version Switch Complete",
            border_style="green"
        )
        console.print(success_panel)
        
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@version.command()
@click.argument('agent')
@click.option('--name', help='Version name (auto-generated if not provided)')
@click.option('--notes', default='Manually created', help='Version notes')
def create(agent: str, name: str, notes: str):
    """➕ Create a new version from current.md
    
    AGENT: Name of the agent
    """
    try:
        console.print(f"[yellow]➕ Creating new version for {agent}...[/yellow]")
        
        vm = VersionManager()
        vm.create_version(agent, name, notes)
        
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@cli.group()
def hooks():
    """🔧 Manage git pre-commit hooks"""
    pass

@hooks.command()
@click.option('--force', is_flag=True, help='Overwrite existing hook')
def install(force: bool):
    """🔧 Install the Promptix pre-commit hook"""
    try:
        console.print("[yellow]🔧 Installing Promptix pre-commit hook...[/yellow]")
        
        hm = HookManager()
        had_existing_hook = hm.has_existing_hook()
        hm.install_hook(force)

        if force or not had_existing_hook:
            install_panel = Panel(
                f"[bold green]✅ Promptix pre-commit hook installed![/bold green]\n\n"
                f"[blue]What happens now:[/blue]\n"
                f"• Every time you edit current.md and commit, a new version is created\n"
                f"• When you change current_version in config.yaml, that version is deployed\n"
                f"• Use 'SKIP_PROMPTIX_HOOK=1 git commit' to bypass when needed\n\n"
                f"[blue]Try it:[/blue]\n"
                f"• Edit any prompts/*/current.md file\n"
                f"• Run: git add . && git commit -m 'Test versioning'\n"
                f"• Check the new version in prompts/*/versions/",
                title="Hook Installation Complete",
                border_style="green"
            )
            console.print(install_panel)
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@hooks.command()
def uninstall():
    """🗑️ Uninstall the Promptix pre-commit hook"""
    try:
        console.print("[yellow]🗑️ Uninstalling Promptix pre-commit hook...[/yellow]")
        
        hm = HookManager()
        hm.uninstall_hook()
        
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@hooks.command()
def enable():
    """✅ Enable a disabled hook"""
    try:
        hm = HookManager()
        hm.enable_hook()
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@hooks.command()
def disable():
    """⏸️ Disable the hook temporarily"""
    try:
        hm = HookManager()
        hm.disable_hook()
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@hooks.command()
def status():
    """📊 Show hook installation status"""
    try:
        hm = HookManager()
        hm.status()
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
        sys.exit(1)

@hooks.command()
def test():
    """🧪 Test the hook without committing"""
    try:
        hm = HookManager()
        hm.test_hook()
    except ValueError as e:
        error_console.print(f"[bold red]❌ Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        error_console.print(f"[bold red]❌ Unexpected error:[/bold red] {e}")
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
        # Check if first arg is a flag (starts with '-') or a recognized top-level command
        if len(sys.argv) > 1:
            first_arg = sys.argv[1]
            # List of recognized top-level commands
            top_level_commands = ['studio', 'agent', 'openai', 'version', 'hooks']
            
            # Don't redirect if it's a flag or a recognized command
            if not first_arg.startswith('-') and first_arg not in top_level_commands:
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
