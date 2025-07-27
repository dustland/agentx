#!/usr/bin/env python3
"""
Universal VibeX CLI

Provides a unified command-line interface for all VibeX operations.
"""

import sys
import os
from pathlib import Path
from ..run import start, monitor, web, run_example
from .parser import create_parser
from .status import show_status, show_version, show_config, init_config
from .bootstrap import bootstrap_project


def main():
    """Main CLI entry point."""
    parser = create_parser()

    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Handle case where command is None (for test compatibility)
    if not hasattr(args, 'command') or args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "init":
            return bootstrap_project(
                project_name=args.project_name,
                template=args.template,
                model=args.model,
                interactive=not args.no_interactive
            )

        elif args.command == "start":
            # TODO: Use args.port and args.host when updating start function
            return start()

        elif args.command == "monitor":
            if args.web:
                return web(
                    project_path=getattr(args, 'project_path', None),
                    host=args.host,
                    port=args.port
                )
            else:
                return monitor(project_path=getattr(args, 'project_path', None))

        elif args.command == "status":
            show_status()
            return 0

        elif args.command == "example":
            return run_example(args.name)

        elif args.command == "version":
            show_version()
            return 0

        elif args.command == "config":
            if args.config_action == "show":
                show_config()
            elif args.config_action == "init":
                init_config()
            else:
                print("Available config actions: show, init")
                return 1
            return 0

        elif args.command == "debug":
            import asyncio
            from .debug import debug_task
            asyncio.run(debug_task(args.team_config, args.project_id))
            return 0

        elif args.command == "web":
            # Handle web commands
            web_action = getattr(args, 'web_action', None)
            
            # Check if we're in a project directory with full web interface
            local_web = Path.cwd() / "web"
            if local_web.exists():
                # Use full web implementation
                try:
                    from .commands.web import web
                    # Convert argparse args to click format
                    import sys
                    sys.argv = ['vibex', 'web']
                    if web_action:
                        sys.argv.append(web_action)
                    if hasattr(args, 'port'):
                        sys.argv.extend(['--port', str(args.port)])
                    if hasattr(args, 'api_port'):
                        sys.argv.extend(['--api-port', str(args.api_port)])
                    if hasattr(args, 'no_api') and args.no_api:
                        sys.argv.append('--no-api')
                    if hasattr(args, 'open') and args.open:
                        sys.argv.append('--open')
                    if hasattr(args, 'production') and args.production:
                        sys.argv.append('--production')
                    return web()
                except ImportError:
                    pass
            
            # Use simplified web interface for pip-installed version
            from .commands.web_simple import run_web_command
            
            if not web_action:
                # Default to start if no subcommand given
                return run_web_command(
                    action="start",
                    open_browser=True
                )
            
            if web_action == "start":
                return run_web_command(
                    action="start",
                    port=args.port,
                    api_port=args.api_port,
                    no_api=args.no_api,
                    open_browser=args.open,
                    production=args.production
                )
            elif web_action == "setup":
                return run_web_command(action="setup")
            elif web_action == "dev":
                return run_web_command(
                    action="start",
                    port=args.port,
                    api_port=args.api_port,
                    production=False
                )
            else:
                print(f"Unknown web action: {web_action}")
                return 1

        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
