"""
Simple runner functions for VibeX examples
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
    """Start the VibeX API server with integrated observability."""
    print("🤖 Starting VibeX API Server (Integrated Mode)")
    print("=" * 50)
    print("📊 Observability features enabled:")
    print("  • Real-time event capture")
    print("  • Task conversation tracking")
    print("  • Memory monitoring")
    print("  • Web dashboard at http://localhost:7770/monitor")
    print()

    try:
        # Import and initialize observability monitor first
        from vibex.observability.monitor import get_monitor
        monitor = get_monitor()
        monitor.start()
        print("✅ Observability monitor initialized")

        # Start the API server
        from vibex.server.api import app
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

        @app.get("/monitor/projects/{project_id}/conversation")
        async def get_project_conversation(project_id: str):
            """Get conversation history for a task."""
            return monitor.get_project_conversation(project_id)

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

        print("🌐 Server starting at http://localhost:7770")
        print("📊 Monitor dashboard at http://localhost:7770/monitor")

        uvicorn.run(app, host="0.0.0.0", port=7770)
        return 0

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1



def monitor(project_path: Optional[str] = None):
    """Run observability monitor in independent mode (post-mortem analysis)."""
    print("🤖 Starting VibeX Observability Monitor (Independent Mode)")
    print("=" * 60)
    print("📊 Independent mode features:")
    print("  • Memory inspection from persisted data")
    print("  • Task conversation history")
    print("  • Data export capabilities")
    print("  • No real-time events (requires integrated mode)")
    print()

    try:
        from vibex.observability.monitor import get_monitor

        # Create monitor in independent mode with smart project directory detection
        monitor = get_monitor(project_path)
        monitor.start()

        if monitor.is_integrated:
            print("⚠️  Warning: Detected integrated mode. Consider using 'vibex start' instead.")

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
                        for project_id in tasks:
                            history = monitor.get_project_conversation(project_id)
                            print(f"  • {project_id}: {len(history)} messages")
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
                        "tasks": {project_id: monitor.get_project_conversation(project_id)
                                 for project_id in monitor.get_recent_tasks(50)},
                        "memory_categories": {cat: monitor.get_memory_by_category(cat)
                                            for cat in monitor.get_memory_categories()},
                        "exported_at": datetime.now().isoformat()
                    }

                    filename = f"vibex_observability_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
                            "--server.port", "7772",
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

def web(project_path: Optional[str] = None, host: str = "0.0.0.0", port: int = 7772):
    """Start the modern web-based observability dashboard."""
    print("🌐 Starting VibeX Observability Web Dashboard")
    print("=" * 50)

    try:
        from vibex.observability.web_app import run_web_app

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
    """Generate VibeX API documentation."""
    print("📖 VibeX API Documentation Generator")
    print("=" * 40)

    # Check if the API docs generation script exists
    scripts_dir = Path("scripts")
    generate_script = scripts_dir / "generate_sdk_docs.py"

    if not generate_script.exists():
        print(f"❌ API docs generator not found: {generate_script}")
        return 1

    try:
        if regenerate:
            print("🔄 Regenerating API documentation...")
            result = subprocess.run([sys.executable, str(generate_script)])

            if result.returncode == 0:
                print("✅ API documentation generated successfully")
                print("📂 Documentation available at: docs/content/sdk/")
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
            print("📂 Location: docs/content/sdk/")
            return 0

    except Exception as e:
        print(f"❌ Error generating API docs: {e}")
        return 1


def build_docs(command: str = "build"):
    """Build and serve VibeX documentation site."""
    print("🌐 VibeX Documentation Site Builder")
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
            print("📖 Documentation will open at http://localhost:7771")
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



def dev():
    """Run VibeX in development mode with hot reloading."""
    print("🔥 Starting VibeX Development Mode")
    print("=" * 40)
    print("🔧 Features enabled:")
    print("  • Hot reloading")
    print("  • Debug logging")
    print("  • File watching")
    print()

    try:
        from vibex.server.api import app
        import uvicorn

        print("🌐 Development server starting at http://localhost:7770")
        print("🔄 Changes will trigger automatic reload")
        print("📊 Monitor dashboard at http://localhost:7770/monitor")
        print("🔄 Press Ctrl+C to stop")

        # Note: reload=True forces single worker mode
        # For development with concurrent requests, we need to choose between:
        # 1. Hot reload (single worker) - current setting
        # 2. Multiple workers (no hot reload) - better for testing concurrent operations
        
        # To enable concurrent request handling during development, uncomment this:
        # uvicorn.run(
        #     "vibex.server.api:app",
        #     host="0.0.0.0",
        #     port=7770,
        #     workers=4,  # Multiple workers for concurrent requests
        #     log_level="debug"
        # )
        
        # Current setting: Hot reload enabled (single worker)
        uvicorn.run(
            "vibex.server.api:app",
            host="0.0.0.0",
            port=7770,
            reload=True,
            reload_dirs=["src/vibex"],
            log_level="debug",
            # Note: Can't use workers with reload=True
            # Consider running with --workers flag in production
        )
        return 0

    except KeyboardInterrupt:
        print("\n🛑 Development server stopped")
        return 0
    except Exception as e:
        print(f"❌ Error starting development server: {e}")
        return 1


def prod():
    """Run VibeX in production mode with multiple workers."""
    print("⚡ Starting VibeX Production Mode")
    print("=" * 40)
    print("🔧 Features enabled:")
    print("  • Multiple workers (4)")
    print("  • Concurrent request handling")
    print("  • Production logging")
    print()

    try:
        import uvicorn
        import os

        # Use BACKEND_PORT if set, otherwise default to 7770
        port = int(os.environ.get("BACKEND_PORT", 7770))
        
        print(f"🌐 Production server starting at http://localhost:{port}")
        print("🚀 Running with 4 workers for concurrent requests")
        print(f"📊 Monitor dashboard at http://localhost:{port}/monitor")
        print("🔄 Press Ctrl+C to stop")

        uvicorn.run(
            "vibex.server.api:app",
            host="0.0.0.0",
            port=port,
            workers=4,  # Multiple workers for concurrent requests
            log_level="info",
            access_log=True
        )
        return 0

    except KeyboardInterrupt:
        print("\n🛑 Production server stopped")
        return 0
    except Exception as e:
        print(f"❌ Error starting production server: {e}")
        return 1


def test():
    """Run VibeX test suite."""
    print("🧪 Running VibeX Test Suite")
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
