"""
Simple runner functions for AgentX examples
"""

import sys
import subprocess
from pathlib import Path
import os
from typing import Optional

def run_example(example_name: str = "superwriter") -> int:
    """Run an example."""
    examples_dir = Path("examples")
    example_path = examples_dir / example_name

    if not example_path.exists():
        print(f"❌ Example '{example_name}' not found in {examples_dir}")
        available = [d.name for d in examples_dir.iterdir() if d.is_dir()]
        if available:
            print(f"📋 Available examples: {', '.join(available)}")
        return 1

    # Look for demo.py first, then other runnable files
    demo_file = example_path / "demo.py"
    if demo_file.exists():
        print(f"🚀 Running {example_name} example...")
        result = subprocess.run([sys.executable, "demo.py"], cwd=str(example_path))
        return result.returncode

    main_file = example_path / "main.py"
    if main_file.exists():
        print(f"🚀 Running {example_name} example...")
        result = subprocess.run([sys.executable, "main.py"], cwd=str(example_path))
        return result.returncode

    print(f"❌ No demo.py or main.py found in {example_path}")
    return 1

def start():
    """Start the AgentX API server with integrated observability."""
    print("🤖 Starting AgentX API Server (Integrated Mode)")
    print("=" * 50)
    print("📊 Observability features enabled:")
    print("  • Real-time event capture")
    print("  • Task conversation tracking")
    print("  • Memory monitoring")
    print("  • Web dashboard at http://localhost:8000/monitor")
    print()

    try:
        # Import and initialize observability monitor first
        from agentx.observability.monitor import get_monitor
        monitor = get_monitor()
        monitor.start()
        print("✅ Observability monitor initialized")

        # Start the API server
        from agentx.server.api import app
        import uvicorn

        # Add observability routes to the server
        @app.get("/monitor")
        async def monitor_dashboard():
            """Redirect to the observability dashboard."""
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/monitor/dashboard")

        @app.get("/monitor/status")
        async def monitor_status():
            """Get monitor status."""
            return monitor.get_dashboard_data()

        @app.get("/monitor/tasks/{task_id}/conversation")
        async def get_task_conversation(task_id: str):
            """Get conversation history for a task."""
            return monitor.get_task_conversation(task_id)

        @app.get("/monitor/events")
        async def get_events(event_type: str = None, limit: int = 100):
            """Get events."""
            return monitor.get_events(event_type, limit)

        @app.get("/monitor/memory")
        async def get_memory_overview():
            """Get memory overview."""
            return {
                "categories": monitor.get_memory_categories(),
                "total_items": len(monitor.memory_viewer.memory_cache)
            }

        @app.get("/monitor/memory/{category}")
        async def get_memory_by_category(category: str):
            """Get memory by category."""
            return monitor.get_memory_by_category(category)

        print("🌐 Server starting at http://localhost:8000")
        print("📊 Monitor dashboard at http://localhost:8000/monitor")

        uvicorn.run(app, host="0.0.0.0", port=8000)
        return 0

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1



def monitor(project_path: Optional[str] = None):
    """Run observability monitor in independent mode (post-mortem analysis)."""
    print("🤖 Starting AgentX Observability Monitor (Independent Mode)")
    print("=" * 60)
    print("📊 Independent mode features:")
    print("  • Memory inspection from persisted data")
    print("  • Task conversation history")
    print("  • Data export capabilities")
    print("  • No real-time events (requires integrated mode)")
    print()

    try:
        from agentx.observability.monitor import get_monitor

        # Create monitor in independent mode with smart project directory detection
        monitor = get_monitor(project_path)
        monitor.start()

        if monitor.is_integrated:
            print("⚠️  Warning: Detected integrated mode. Consider using 'agentx start' instead.")

        print("✅ Monitor started successfully")
        print()
        print("📊 Observability Monitor CLI")
        print("Commands:")
        print("  status    - Show monitor status")
        print("  tasks     - Show recent tasks")
        print("  memory    - Show memory categories")
        print("  search    - Search memory")
        print("  export    - Export all data to JSON")
        print("  refresh   - Refresh data from API (if server running)")
        print("  web       - Start web interface")
        print("  quit      - Stop monitor and exit")
        print()

        # Simple CLI loop
        while True:
            try:
                cmd = input("monitor> ").strip().lower()

                if cmd == "quit" or cmd == "exit":
                    break
                elif cmd == "status":
                    data = monitor.get_dashboard_data()
                    print(f"Mode: {'Integrated' if data['is_integrated'] else 'Independent'}")
                    print(f"Running: {data['is_running']}")
                    print(f"Tasks: {data['total_tasks']}")
                    print(f"Memory items: {data['total_memory_items']}")
                    print(f"Memory categories: {data['memory_categories']}")
                    print(f"Data directory: {data['data_dir']}")
                    if data['is_integrated']:
                        print(f"Events: {data['total_events']}")
                elif cmd == "tasks":
                    tasks = monitor.get_recent_tasks(10)
                    if tasks:
                        print(f"Recent tasks ({len(tasks)}):")
                        for task_id in tasks:
                            history = monitor.get_task_conversation(task_id)
                            print(f"  • {task_id}: {len(history)} messages")
                    else:
                        print("No tasks found")
                elif cmd == "memory":
                    categories = monitor.get_memory_categories()
                    if categories:
                        print(f"Memory categories ({len(categories)}):")
                        for cat in categories:
                            items = monitor.get_memory_by_category(cat)
                            print(f"  • {cat}: {len(items)} items")
                    else:
                        print("No memory data found")
                elif cmd.startswith("search "):
                    query = cmd[7:].strip()
                    if query:
                        results = monitor.search_memory(query)
                        if results:
                            print(f"Search results for '{query}' ({len(results)} items):")
                            for key in list(results.keys())[:5]:  # Show first 5
                                print(f"  • {key}")
                            if len(results) > 5:
                                print(f"  ... and {len(results) - 5} more")
                        else:
                            print(f"No results found for '{query}'")
                    else:
                        print("Usage: search <query>")
                elif cmd == "refresh":
                    print("Refreshing data...")
                    import asyncio
                    try:
                        asyncio.run(monitor.refresh_data())
                        print("✅ Data refreshed")
                    except Exception as e:
                        print(f"❌ Refresh failed: {e}")
                elif cmd == "export":
                    import json
                    from datetime import datetime

                    # Export all data
                    data = {
                        "dashboard": monitor.get_dashboard_data(),
                        "tasks": {task_id: monitor.get_task_conversation(task_id)
                                 for task_id in monitor.get_recent_tasks(50)},
                        "memory_categories": {cat: monitor.get_memory_by_category(cat)
                                            for cat in monitor.get_memory_categories()},
                        "exported_at": datetime.now().isoformat()
                    }

                    filename = f"agentx_observability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w') as f:
                        json.dump(data, f, indent=2, default=str)
                    print(f"✅ Data exported to {filename}")
                elif cmd == "web":
                    print("🌐 Starting web interface...")
                    print("This will open the Streamlit dashboard in your browser.")
                    print("Press Ctrl+C to stop the web interface and return to CLI.")
                    try:
                        import subprocess
                        import sys
                        from pathlib import Path

                        # Get the path to the web interface
                        web_file = Path(__file__).parent / "observability" / "web.py"

                        # Set up environment with correct PYTHONPATH
                        env = os.environ.copy()
                        src_path = str(Path(__file__).parent.parent)  # Points to src directory
                        if "PYTHONPATH" in env:
                            env["PYTHONPATH"] = f"{src_path}:{env['PYTHONPATH']}"
                        else:
                            env["PYTHONPATH"] = src_path

                        # Run streamlit with proper environment
                        result = subprocess.run([
                            sys.executable, "-m", "streamlit", "run", str(web_file),
                            "--server.port", "8501",
                            "--server.headless", "false",
                            "--server.runOnSave", "true"
                        ], env=env)

                        print("🌐 Web interface stopped")

                    except KeyboardInterrupt:
                        print("\n🌐 Web interface stopped")
                    except Exception as e:
                        print(f"❌ Error starting web interface: {e}")
                elif cmd == "help":
                    print("Commands: status, tasks, memory, search <query>, export, refresh, web, quit")
                elif cmd:
                    print(f"Unknown command: {cmd}. Type 'help' for available commands.")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        monitor.stop()
        print("🛑 Monitor stopped")
        return 0

    except Exception as e:
        print(f"❌ Error starting monitor: {e}")
        return 1

def web(project_path: Optional[str] = None, host: str = "0.0.0.0", port: int = 8501):
    """Start the modern web-based observability dashboard."""
    print("🌐 Starting AgentX Observability Web Dashboard")
    print("=" * 50)

    try:
        from agentx.observability.web_app import run_web_app

        print("🚀 Starting modern web dashboard...")
        print(f"📊 Dashboard will open at http://localhost:{port}")
        print("🎨 Features: FastAPI + HTMX + TailwindCSS + Preline UI")
        print("🔄 Press Ctrl+C to stop")
        print()

        # Run the modern web app
        run_web_app(host=host, port=port, project_path=project_path)
        return 0

    except KeyboardInterrupt:
        print("\n🛑 Web dashboard stopped")
        return 0
    except Exception as e:
        print(f"❌ Error starting web dashboard: {e}")
        print("💡 Tip: Make sure you have FastAPI and Jinja2 installed:")
        print("   uv add fastapi jinja2 python-multipart")
        return 1


def docs(regenerate: bool = True):
    """Generate AgentX API documentation."""
    print("📖 AgentX API Documentation Generator")
    print("=" * 40)

    # Check if the API docs generation script exists
    scripts_dir = Path("scripts")
    generate_script = scripts_dir / "generate_api_docs.py"

    if not generate_script.exists():
        print(f"❌ API docs generator not found: {generate_script}")
        return 1

    try:
        if regenerate:
            print("🔄 Regenerating API documentation...")
            result = subprocess.run([sys.executable, str(generate_script)])

            if result.returncode == 0:
                print("✅ API documentation generated successfully")
                print("📂 Documentation available at: docs/content/api/")
                print()
                print("💡 Next steps:")
                print("  • To build the docs site: cd docs && pnpm build")
                print("  • To serve locally: cd docs && pnpm dev")
                return 0
            else:
                print("❌ API documentation generation failed")
                return 1
        else:
            print("📖 API documentation is up to date")
            print("📂 Location: docs/content/api/")
            return 0

    except Exception as e:
        print(f"❌ Error generating API docs: {e}")
        return 1


def build_docs(command: str = "build"):
    """Build and serve AgentX documentation site."""
    print("🌐 AgentX Documentation Site Builder")
    print("=" * 40)

    # Check if docs directory exists
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print(f"❌ Documentation directory not found: {docs_dir}")
        return 1

    # Check if pnpm is available
    try:
        subprocess.run(["pnpm", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pnpm is required but not found")
        print("💡 Install pnpm: https://pnpm.io/installation")
        return 1

    try:
        print(f"🔧 Working directory: {docs_dir}")

        # Install dependencies if node_modules doesn't exist
        node_modules = docs_dir / "node_modules"
        if not node_modules.exists():
            print("📦 Installing dependencies...")
            result = subprocess.run(["pnpm", "install"], cwd=docs_dir)
            if result.returncode != 0:
                print("❌ Failed to install dependencies")
                return 1
            print("✅ Dependencies installed")

        if command == "build":
            print("🔨 Building documentation site...")
            result = subprocess.run(["pnpm", "build"], cwd=docs_dir)
            if result.returncode == 0:
                print("✅ Documentation site built successfully")
                print(f"📂 Output available in: {docs_dir / 'out'}")
                return 0
            else:
                print("❌ Build failed")
                return 1

        elif command == "dev" or command == "serve":
            print("🚀 Starting development server...")
            print("📖 Documentation will open at http://localhost:3000")
            print("🔄 Press Ctrl+C to stop")
            try:
                result = subprocess.run(["pnpm", "dev"], cwd=docs_dir)
                return result.returncode
            except KeyboardInterrupt:
                print("\n🛑 Development server stopped")
                return 0

        else:
            print(f"❌ Unknown command: {command}")
            print("💡 Available commands: build, dev, serve")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def setup_hooks():
    """Set up pre-commit hooks for the project."""
    print("🪝 AgentX Pre-commit Hooks Setup")
    print("=" * 35)

    # Check if .pre-commit-config.yaml exists
    config_file = Path(".pre-commit-config.yaml")
    if not config_file.exists():
        print(f"❌ Pre-commit configuration not found: {config_file}")
        print("💡 Make sure .pre-commit-config.yaml exists in the project root")
        return 1

    try:
        print("📦 Installing dev dependencies...")
        # Ensure dev dependencies are installed
        result = subprocess.run(["uv", "sync", "--dev"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to install dev dependencies")
            print(f"Error: {result.stderr}")
            return 1

        print("🔧 Installing pre-commit hooks...")
        # Run pre-commit install using uv run to ensure proper environment
        result = subprocess.run(["uv", "run", "pre-commit", "install"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to install pre-commit hooks")
            print(f"Error: {result.stderr}")
            return 1

        print("✅ Pre-commit hooks installed successfully")
        print()
        print("🎯 What happens now:")
        print("  • API docs will be auto-generated when src/agentx/*.py files change")
        print("  • Code formatting and linting will run before each commit")
        print("  • Large files and merge conflicts will be detected")
        print()
        print("💡 To test the hooks:")
        print("  • Make a change to a Python file in src/agentx/")
        print("  • Run: git add . && git commit -m 'test'")
        print("  • Watch the API docs get generated automatically!")
        print()
        print("🚀 To run hooks manually: pre-commit run --all-files")

        return 0

    except Exception as e:
        print(f"❌ Error setting up hooks: {e}")
        return 1


def dev():
    """Run AgentX in development mode with hot reloading."""
    print("🔥 Starting AgentX Development Mode")
    print("=" * 40)
    print("🔧 Features enabled:")
    print("  • Hot reloading")
    print("  • Debug logging")
    print("  • File watching")
    print()

    try:
        from agentx.server.api import app
        import uvicorn

        print("🌐 Development server starting at http://localhost:8000")
        print("🔄 Changes will trigger automatic reload")
        print("📊 Monitor dashboard at http://localhost:8000/monitor")
        print("🔄 Press Ctrl+C to stop")

        uvicorn.run(
            "agentx.server.api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["src/agentx"],
            log_level="debug"
        )
        return 0

    except KeyboardInterrupt:
        print("\n🛑 Development server stopped")
        return 0
    except Exception as e:
        print(f"❌ Error starting development server: {e}")
        return 1


def test():
    """Run AgentX test suite."""
    print("🧪 Running AgentX Test Suite")
    print("=" * 30)

    try:
        import pytest

        # Run pytest with common options
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ])

        if result.returncode == 0:
            print("✅ All tests passed")
        else:
            print("❌ Some tests failed")

        return result.returncode

    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1
