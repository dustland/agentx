#!/usr/bin/env python3
"""
CLI Argument Parser

Defines the command-line interface structure and argument parsing for VibeX.
"""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="vibex",
        description="🤖 VibeX - Multi-Agent Framework with Observability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vibex init                      # Create new project with interactive wizard
  vibex init --template writing   # Create writing project template
  vibex start                     # Start API server with observability
  vibex monitor                   # Start observability monitor (CLI)
  vibex monitor --web             # Start web dashboard
  vibex web                       # Launch VibeX Web UI
  vibex web dev                   # Start API and Web interface in dev mode
  vibex status                    # Show system status
  vibex example superwriter       # Run specific example

For more information, visit: https://github.com/dustland/vibex
        """
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND"
    )

    # Bootstrap/Init command
    _add_init_parser(subparsers)

    # Start command (API server)
    _add_start_parser(subparsers)

    # Monitor command (merged with web)
    _add_monitor_parser(subparsers)

    # Status command
    _add_status_parser(subparsers)

    # Example command
    _add_example_parser(subparsers)

    # Version command
    _add_version_parser(subparsers)

    # Config command
    _add_config_parser(subparsers)

    # Debug command
    _add_debug_parser(subparsers)

    # Web command
    _add_web_parser(subparsers)

    return parser


def _add_init_parser(subparsers) -> None:
    """Add the init/bootstrap command parser."""
    init_parser = subparsers.add_parser(
        "init",
        help="Create new VibeX project with interactive wizard",
        description="Bootstrap a new VibeX project with essential builtin roles"
    )
    init_parser.add_argument(
        "project_name",
        nargs="?",
        help="Name of the project to create (optional, will prompt if not provided)"
    )
    init_parser.add_argument(
        "--template",
        choices=["writing", "coding", "ops", "custom"],
        help="Project template to use (writing/coding/ops/custom)"
    )
    init_parser.add_argument(
        "--model",
        default="deepseek",
        choices=["deepseek", "openai", "claude", "gemini"],
        help="Default LLM provider (default: deepseek)"
    )
    init_parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Skip interactive prompts and use defaults"
    )


def _add_start_parser(subparsers) -> None:
    """Add the start command parser."""
    start_parser = subparsers.add_parser(
        "start",
        help="Start API server with integrated observability",
        description="Start the VibeX API server with full observability features"
    )
    start_parser.add_argument(
        "--port",
        type=int,
        default=7770,
        help="Port to run the server on (default: 7770)"
    )
    start_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )


def _add_monitor_parser(subparsers) -> None:
    """Add the monitor command parser."""
    monitor_parser = subparsers.add_parser(
        "monitor",
        help="Start observability monitor (CLI or web interface)",
        description="Start the observability monitor for analysis and debugging"
    )
    monitor_parser.add_argument(
        "--web",
        action="store_true",
        help="Start web interface instead of CLI (default: CLI)"
    )
    monitor_parser.add_argument(
        "--port",
        type=int,
        default=7772,
        help="Port for web interface (default: 7772, only used with --web)"
    )
    monitor_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for web interface (default: 0.0.0.0, only used with --web)"
    )
    monitor_parser.add_argument(
        "--data-dir",
        help="Path to vibex data directory (default: auto-detect)"
    )


def _add_status_parser(subparsers) -> None:
    """Add the status command parser."""
    subparsers.add_parser(
        "status",
        help="Show system status and health",
        description="Display current status of VibeX components"
    )


def _add_example_parser(subparsers) -> None:
    """Add the example command parser."""
    example_parser = subparsers.add_parser(
        "example",
        help="Run a specific example",
        description="Run a specific VibeX example by name"
    )
    example_parser.add_argument(
        "name",
        help="Name of the example to run (e.g., superwriter)"
    )


def _add_version_parser(subparsers) -> None:
    """Add the version command parser."""
    subparsers.add_parser(
        "version",
        help="Show version information",
        description="Display VibeX version and component information"
    )


def _add_config_parser(subparsers) -> None:
    """Add the config command parser."""
    config_parser = subparsers.add_parser(
        "config",
        help="Configuration management",
        description="Manage VibeX configuration"
    )
    config_subparsers = config_parser.add_subparsers(
        dest="config_action",
        help="Configuration actions"
    )
    config_subparsers.add_parser("show", help="Show current configuration")
    config_subparsers.add_parser("init", help="Initialize default configuration")


def _add_debug_parser(subparsers) -> None:
    """Add the debug command parser."""
    debug_parser = subparsers.add_parser(
        "debug",
        help="Start debugging session for a task",
        description="Start interactive debugging session with breakpoints and state inspection"
    )
    debug_parser.add_argument(
        "team_config",
        help="Path to team configuration file"
    )
    debug_parser.add_argument(
        "project_id",
        help="Task ID to debug"
    )


def _add_web_parser(subparsers) -> None:
    """Add the web command parser."""
    web_parser = subparsers.add_parser(
        "web",
        help="VibeX Web - Web UI for project execution and observability",
        description="Launch and manage the VibeX Web interface"
    )
    
    web_subparsers = web_parser.add_subparsers(
        dest="web_action",
        help="Web interface actions"
    )
    
    # Start subcommand
    start_parser = web_subparsers.add_parser(
        "start",
        help="Start VibeX Web UI"
    )
    start_parser.add_argument(
        "--port", "-p",
        type=int,
        default=7777,
        help="Port for the web UI (default: 7777)"
    )
    start_parser.add_argument(
        "--api-port",
        type=int,
        default=7770,
        help="Port for the API server (default: 7770)"
    )
    start_parser.add_argument(
        "--no-api",
        action="store_true",
        help="Don't start the API server"
    )
    start_parser.add_argument(
        "--open", "-o",
        action="store_true",
        help="Open web interface in browser"
    )
    start_parser.add_argument(
        "--production",
        action="store_true",
        help="Run in production mode"
    )
    
    # Setup subcommand
    web_subparsers.add_parser(
        "setup",
        help="Install web interface dependencies"
    )
    
    # Dev subcommand
    dev_parser = web_subparsers.add_parser(
        "dev",
        help="Start both API and Web interface in development mode"
    )
    dev_parser.add_argument(
        "--port", "-p",
        type=int,
        default=7777,
        help="Port for the web UI (default: 7777)"
    )
    dev_parser.add_argument(
        "--api-port",
        type=int,
        default=7770,
        help="Port for the API server (default: 7770)"
    )
