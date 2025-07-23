#!/usr/bin/env python3
"""
WordX Setup Script
=================

This script helps you set up and configure the WordX add-in for Microsoft Word.
It handles backend setup, Office.js configuration, and environment setup.

Usage:
    python wordx_setup.py [options]

Options:
    --install-deps    Install all dependencies
    --check-env       Check environment and requirements
    --start-dev       Start development servers
    --help           Show this help message
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from typing import List, Tuple, Optional

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a header with formatting"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def run_command(cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error(f"Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} found")
    return True

def check_node_version():
    """Check if Node.js version is compatible"""
    success, output = run_command(['node', '--version'], check=False)
    if not success:
        print_error("Node.js not found. Please install Node.js 16+")
        return False

    version = output.strip().replace('v', '')
    major = int(version.split('.')[0])

    if major < 16:
        print_error(f"Node.js 16+ required, found {major}")
        return False

    print_success(f"Node.js {version} found")
    return True

def check_uv():
    """Check if uv is available"""
    success, output = run_command(['uv', '--version'], check=False)
    if not success:
        print_error("uv not found. Please install uv (https://github.com/astral-sh/uv)")
        print_info("Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False
    print_success(f"uv {output.strip()} found")
    return True

def check_npm():
    """Check if pnpm or npm is available"""
    # First try pnpm
    success, output = run_command(['pnpm', '--version'], check=False)
    if success:
        print_success(f"pnpm {output.strip()} found")
        return True

    # Fall back to npm
    success, output = run_command(['npm', '--version'], check=False)
    if success:
        print_success(f"npm {output.strip()} found (consider using pnpm for better performance)")
        return True

    print_error("Neither pnpm nor npm found. Please install pnpm or npm")
    print_info("Install pnpm with: npm install -g pnpm")
    return False

def check_vibex_installation():
    """Check if VibeX is installed"""
    try:
        import vibex
        print_success("VibeX framework found")
        return True
    except ImportError:
        print_warning("VibeX not found. Will install with dependencies.")
        return False

def check_environment_variables():
    """Check for required environment variables"""
    api_keys = {
        'DEEPSEEK_API_KEY': 'DeepSeek',
        'OPENAI_API_KEY': 'OpenAI',
        'ANTHROPIC_API_KEY': 'Claude (Anthropic)',
        'GOOGLE_API_KEY': 'Google Gemini'
    }

    found_keys = []
    missing_keys = []

    for var, name in api_keys.items():
        if os.getenv(var):
            found_keys.append(name)
        else:
            missing_keys.append(name)

    if not found_keys:
        print_error("No AI model API keys found!")
        print_info("You need at least one of the following API keys:")
        for var, name in api_keys.items():
            print_info(f"  - {var} for {name}")
        return False

    print_success(f"API keys configured for: {', '.join(found_keys)}")
    if missing_keys:
        print_info(f"Optional API keys not set: {', '.join(missing_keys)}")
    return True

def install_backend_dependencies():
    """Install backend Python dependencies"""
    print_info("Installing backend dependencies with uv...")

    wordx_dir = Path(__file__).parent

    # Create virtual environment if it doesn't exist
    print_info("Creating virtual environment...")
    success, output = run_command(['uv', 'venv'], cwd=wordx_dir)
    if not success:
        print_error(f"Failed to create virtual environment: {output}")
        return False

    # Install dependencies using pyproject.toml
    print_info("Installing dependencies from pyproject.toml...")
    success, output = run_command(['uv', 'pip', 'install', '-e', '.'], cwd=wordx_dir)

    if success:
        print_success("Backend dependencies installed")

        # Install dev dependencies
        print_info("Installing development dependencies...")
        success_dev, output_dev = run_command(['uv', 'pip', 'install', '-e', '.[dev]'], cwd=wordx_dir)
        if success_dev:
            print_success("Development dependencies installed")
        else:
            print_warning(f"Failed to install dev dependencies: {output_dev}")

        return True
    else:
        print_error(f"Failed to install backend dependencies: {output}")
        return False

def install_addon_dependencies():
    """Install Office.js add-in dependencies"""
    print_info("Installing Office.js add-in dependencies...")

    addon_dir = Path(__file__).parent / "addon"

    # Try pnpm first
    success, output = run_command(['pnpm', 'install'], cwd=addon_dir, check=False)

    if not success:
        # Fall back to npm
        print_info("pnpm not found, falling back to npm...")
        success, output = run_command(['npm', 'install'], cwd=addon_dir)

    if success:
        print_success("Add-in dependencies installed")
        print_info("Microsoft Office Add-in debugging tools are now available")
        return True
    else:
        print_error(f"Failed to install add-in dependencies: {output}")
        return False

def create_env_file():
    """Create .env file template"""
    env_file = Path(__file__).parent / "backend" / ".env"
    template_file = Path(__file__).parent / "backend" / "environment.template"

    if env_file.exists():
        print_info(".env file already exists")
        return True

    if template_file.exists():
        try:
            import shutil
            shutil.copy(template_file, env_file)
            print_success("Created .env file from template")
            print_info(f"Please edit {env_file} with your API keys")
            return True
        except Exception as e:
            print_error(f"Failed to copy environment template: {e}")
            return False
    else:
        print_error("Environment template file not found")
        return False

def update_addon_config():
    """Update addon config.js with backend URL from environment"""
    import os
    from dotenv import load_dotenv

    # Load environment variables
    env_file = Path(__file__).parent / "backend" / ".env"
    if env_file.exists():
        load_dotenv(env_file)

    # Get backend port from environment
    backend_host = os.getenv("WORDX_BACKEND_HOST", "localhost")
    backend_port = os.getenv("WORDX_BACKEND_PORT", "7779")
    backend_url = f"http://{backend_host}:{backend_port}"

    # Update config.js
    config_file = Path(__file__).parent / "addon" / "config.js"

    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                content = f.read()

            # Replace the backend URL
            import re
            new_content = re.sub(
                r"BACKEND_URL:\s*'[^']+'",
                f"BACKEND_URL: '{backend_url}'",
                content
            )

            with open(config_file, 'w') as f:
                f.write(new_content)

            print_success(f"Updated addon config with backend URL: {backend_url}")
            return True
        except Exception as e:
            print_error(f"Failed to update addon config: {e}")
            return False
    else:
        print_warning("Addon config.js not found")
        return False

def validate_manifest():
    """Validate the Office.js manifest"""
    print_info("Validating Office.js manifest...")

    addon_dir = Path(__file__).parent / "addon"

    # Try to validate using office-addin-manifest
    success, output = run_command(['npm', 'run', 'validate'], cwd=addon_dir, check=False)

    if success:
        print_success("Manifest validation passed")
        return True
    else:
        print_warning("Manifest validation had issues:")
        print_info(output)
        print_info("This might be normal for local development")
        return True  # Don't fail setup for validation warnings

def start_development_servers():
    """Start both backend and add-in development servers"""
    print_info("Starting development servers...")

    # Update addon config with backend URL
    update_addon_config()

    # Start backend in background
    print_info("Starting backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, "backend/main.py"],
        cwd=Path(__file__).parent
    )

    # Wait a moment for backend to start
    import time
    time.sleep(3)

    # Start add-in development server
    print_info("Starting Office Add-in development server...")
    print_info("This will:")
    print_info("  - Start the HTTPS development server")
    print_info("  - Open Word for Mac")
    print_info("  - Automatically sideload the add-in")
    print_info("")
    print_info("Press Ctrl+C to stop both servers")

    addon_dir = Path(__file__).parent / "addon"

    try:
        # Use the standard Microsoft Office Add-in debugging tool
        # This handles HTTPS certificates, server startup, and sideloading automatically
        result = run_command(['pnpm', '--version'], check=False)
        if result[0]:
            subprocess.run(['pnpm', 'start:desktop'], cwd=addon_dir)
        else:
            subprocess.run(['npm', 'run', 'start:desktop'], cwd=addon_dir)
    except KeyboardInterrupt:
        print_info("Shutting down servers...")
        backend_process.terminate()
        backend_process.wait()
        print_info("Servers stopped.")

def check_environment():
    """Check the entire development environment"""
    print_header("Environment Check")

    checks = [
        ("Python version", check_python_version),
        ("Node.js version", check_node_version),
        ("uv availability", check_uv),
        ("pnpm/npm availability", check_npm),
        ("VibeX installation", check_vibex_installation),
        ("Environment variables", check_environment_variables),
    ]

    all_passed = True
    for name, check_func in checks:
        print_info(f"Checking {name}...")
        if not check_func():
            all_passed = False

    if all_passed:
        print_success("All environment checks passed!")
    else:
        print_warning("Some checks failed. Please address the issues above.")

    return all_passed

def install_dependencies():
    """Install all required dependencies"""
    print_header("Installing Dependencies")

    # Check prerequisites
    if not check_python_version() or not check_node_version():
        print_error("Prerequisites not met. Please install Python 3.9+ and Node.js 16+")
        return False

    # Install backend dependencies
    if not install_backend_dependencies():
        return False

    # Install add-in dependencies
    if not install_addon_dependencies():
        return False

    # Create .env file
    create_env_file()

    # Update addon config
    update_addon_config()

    # Validate manifest
    validate_manifest()

    print_success("All dependencies installed successfully!")
    return True

def show_usage_instructions():
    """Show usage instructions after setup"""
    print_header("WordX Setup Complete!")

    print("🎯 Next Steps:")
    print("1. Edit the backend/.env file with your API keys")
    print("2. Activate the virtual environment:")
    print("   source .venv/bin/activate  # On Unix/macOS")
    print("   .venv\\Scripts\\activate     # On Windows")
    print("3. Start the development servers:")
    print("   python wordx_setup.py --start-dev")
    print("4. In Microsoft Word:")
    print("   - Go to Insert > My Add-ins > Upload My Add-in")
    print("   - Select the manifest.xml file from the addon directory")
    print("   - Click 'WordX' in the ribbon")
    print()
    print("📚 Documentation:")
    print("   - README.md - Complete setup and usage guide")
    print("   - Backend API: http://localhost:7779/docs")
    print("   - Add-in UI: https://localhost:7778")
    print()
    print("🎉 Happy document processing with WordX!")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="WordX Setup Script")
    parser.add_argument("--install-deps", action="store_true", help="Install all dependencies")
    parser.add_argument("--check-env", action="store_true", help="Check environment and requirements")
    parser.add_argument("--start-dev", action="store_true", help="Start development servers")

    args = parser.parse_args()

    if args.check_env:
        check_environment()
    elif args.install_deps:
        if install_dependencies():
            show_usage_instructions()
    elif args.start_dev:
        start_development_servers()
    else:
        # Interactive setup
        print_header("WordX Setup")
        print("Welcome to WordX setup!")
        print("This script will help you configure WordX for Microsoft Word.")
        print()

        # Check environment
        if not check_environment():
            print_error("Environment check failed. Please address the issues above.")
            return

        # Ask to install dependencies
        install = input("Install dependencies? (y/n): ").lower().strip()
        if install == 'y':
            if install_dependencies():
                show_usage_instructions()
        else:
            print_info("Skipping dependency installation.")
            print_info("Run 'python wordx_setup.py --install-deps' to install dependencies later.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Setup interrupted by user{Colors.ENDC}")
    except Exception as e:
        print_error(f"Setup failed: {e}")
        sys.exit(1)
