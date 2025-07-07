#!/usr/bin/env python3
"""
CLI Status Commands

Handles status, version, and configuration display functionality.
"""

from pathlib import Path


def show_status() -> None:
    """Show system status."""
    print("🤖 AgentX System Status")
    print("=" * 30)

    try:
        # Check if observability monitor is available
        from ..observability.monitor import get_monitor
        monitor = get_monitor()
        dashboard_data = monitor.get_dashboard_data()

        print(f"📊 Observability: {'🟢 Available' if monitor else '🔴 Unavailable'}")
        print(f"   Mode: {'Integrated' if dashboard_data['is_integrated'] else 'Independent'}")
        print(f"   Running: {'Yes' if dashboard_data['is_running'] else 'No'}")
        print(f"   Tasks: {dashboard_data['total_tasks']}")
        print(f"   Memory Items: {dashboard_data['total_memory_items']}")
        print(f"   Data Directory: {dashboard_data['data_dir']}")

    except Exception as e:
        print(f"📊 Observability: 🔴 Error - {e}")

    try:
        # Check if server is running
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        print(f"🌐 API Server: {'🟢 Running' if response.status_code == 200 else '🔴 Error'}")
        print(f"   URL: http://localhost:8000")
        print(f"   Start with: agentx start")
    except:
        print("🌐 API Server: 🔴 Not running")
        print("   Start with: agentx start")

    try:
        # Check if web dashboard is running
        import requests
        response = requests.get("http://localhost:8501", timeout=2)
        print(f"📱 Web Dashboard: {'🟢 Running' if response.status_code == 200 else '🔴 Error'}")
        print(f"   URL: http://localhost:8501")
        print(f"   Tech: FastAPI + HTMX + TailwindCSS + Preline UI v3.10")
        print(f"   Theme: Professional SaaS dashboard styling")
    except:
        print("📱 Web Dashboard: 🔴 Not running")
        print("   Run 'agentx monitor --web' to start the modern dashboard")

    # Check examples
    examples_dir = Path("examples")
    if examples_dir.exists():
        examples = [d.name for d in examples_dir.iterdir() if d.is_dir()]
        print(f"📚 Examples: {len(examples)} available")
        for example in examples[:3]:  # Show first 3
            print(f"   • {example}")
        if len(examples) > 3:
            print(f"   ... and {len(examples) - 3} more")
    else:
        print("📚 Examples: 🔴 Not found")


def show_version() -> None:
    """Show version information."""
    print("🤖 AgentX Version Information")
    print("=" * 35)

    try:
        # Try to get version from package
        import importlib.metadata
        version = importlib.metadata.version("agentx")
        print(f"Version: {version}")
    except:
        print("Version: Development")

    print("Components:")

    # Check core components
    try:
        from .. import core
        print("  ✅ Core Framework")
    except:
        print("  ❌ Core Framework")

    try:
        from .. import observability
        print("  ✅ Observability System")
    except:
        print("  ❌ Observability System")

    try:
        from .. import server
        print("  ✅ API Server")
    except:
        print("  ❌ API Server")

    # Check key dependencies
    print("\nKey Dependencies:")
    dependencies = [
        ("fastapi", "FastAPI"),
        ("streamlit", "Streamlit"),
        ("openai", "OpenAI"),
        ("mem0ai", "Mem0"),
        ("pandas", "Pandas"),
        ("plotly", "Plotly")
    ]

    for module, name in dependencies:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name}")


def show_config() -> None:
    """Show current configuration."""
    print("🤖 AgentX Configuration")
    print("=" * 28)

    # Check environment variables
    import os
    env_vars = [
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
        "TAVILY_API_KEY",
        "SERP_API_KEY"
    ]

    print("Environment Variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask the key for security
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"  ✅ {var}: {masked}")
        else:
            print(f"  ❌ {var}: Not set")

    # Check data directory
    print("\nData Storage:")
    data_dir = Path("agentx_data")
    if data_dir.exists():
        files = list(data_dir.glob("*.json"))
        print(f"  📁 Data Directory: {data_dir} ({len(files)} files)")
        for file in files:
            size = file.stat().st_size
            print(f"     • {file.name}: {size} bytes")
    else:
        print(f"  📁 Data Directory: {data_dir} (not created yet)")


def init_config() -> None:
    """Initialize default configuration."""
    print("🤖 Initializing AgentX Configuration")
    print("=" * 40)

    # Create data directory
    data_dir = Path("agentx_data")
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Created data directory: {data_dir}")

    # Create example .env file
    env_file = Path(".env.example")
    if not env_file.exists():
        env_content = """# AgentX Environment Variables
# Copy this file to .env and fill in your API keys

# OpenAI API Key (for GPT models)
OPENAI_API_KEY=your_openai_api_key_here

# DeepSeek API Key (alternative to OpenAI)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Tavily API Key (for web search)
TAVILY_API_KEY=your_tavily_api_key_here

# SERP API Key (alternative web search)
SERP_API_KEY=your_serp_api_key_here
"""
        env_file.write_text(env_content)
        print(f"✅ Created example environment file: {env_file}")

    print("\n📋 Next steps:")
    print("1. Copy .env.example to .env")
    print("2. Fill in your API keys in the .env file")
    print("3. Run 'agentx status' to check configuration")
