"""
CLI commands for tool management and discovery.
"""

import click
from rich.console import Console
from rich.table import Table

from ..builtin_tools import register_builtin_tools
from ..tool.registry import ToolRegistry

console = Console()


def _print_available_tools():
    """Prints a formatted table of all available tools and toolsets."""
    registry = ToolRegistry()
    tools = registry.list_tools()
    toolsets = registry.list_toolsets()

    console.print("\n[bold cyan]Available Tools[/bold cyan]")
    tool_table = Table(show_header=True, header_style="bold magenta")
    tool_table.add_column("Name", style="dim", width=30)
    tool_table.add_column("Description")

    for tool_name in sorted(tools):
        tool_func = registry.get_tool_function(tool_name)
        if tool_func:
            tool_table.add_row(tool_name, tool_func.description)
    console.print(tool_table)

    if toolsets:
        console.print("\n[bold cyan]Available Toolsets[/bold cyan]")
        toolset_table = Table(show_header=True, header_style="bold magenta")
        toolset_table.add_column("Name", style="dim", width=30)
        toolset_table.add_column("Tools")

        for ts_name in sorted(toolsets):
            ts_tools = registry._toolsets.get(ts_name, [])
            toolset_table.add_row(ts_name, ", ".join(ts_tools))
        console.print(toolset_table)


@click.group()
def tools():
    """Tool management commands."""
    pass


@tools.command(name="list")
def list_cli():
    """List all available tools with descriptions."""
    _register_builtin_tools(with_workspace=False)
    _print_available_tools()


@tools.command()
@click.argument("tool_names", nargs=-1)
def validate(tool_names):
    """Validate tool names against available tools."""
    if not tool_names:
        click.echo("Usage: agentx tools validate <tool_name1> <tool_name2> ...")
        return

    _register_builtin_tools(with_workspace=False)
    registry = ToolRegistry()

    valid_tools = []
    invalid_tools = []

    available_tools = registry.list_tools()

    for name in tool_names:
        if name in available_tools:
            valid_tools.append(name)
        else:
            invalid_tools.append(name)

    if valid_tools:
        click.echo(f"✅ Valid tools: {', '.join(valid_tools)}")

    if invalid_tools:
        click.echo(f"❌ Invalid tools: {', '.join(invalid_tools)}")
        click.echo("\nRun 'agentx tools list' to see available tools")


@tools.command()
@click.argument("agent_name")
@click.option("--description", "-d", default="", help="Agent description for better suggestions")
def suggest(agent_name, description):
    """Suggest relevant tools for an agent based on name and description."""
    click.echo("Tool suggestion is not implemented yet.")


def _register_builtin_tools(with_workspace: bool = True):
    """Register built-in tools for CLI commands."""
    registry = ToolRegistry()
    workspace_path = "./workspace" if with_workspace else None
    register_builtin_tools(registry, workspace_path=workspace_path, memory_system=None)


if __name__ == "__main__":
    tools()
