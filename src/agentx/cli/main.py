#!/usr/bin/env python3
"""
Universal AgentX CLI

Provides a unified command-line interface for all AgentX operations.
"""

import sys
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
            asyncio.run(debug_task(args.team_config, args.task_id))
            return 0

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
