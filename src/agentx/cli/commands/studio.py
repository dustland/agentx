"""Studio CLI commands for AgentX."""

import os
import sys
import subprocess
import webbrowser
import time
import signal
from pathlib import Path
from typing import Optional

import click
import psutil

from ...utils.logger import get_logger

logger = get_logger(__name__)


def find_free_port(start_port: int, max_attempts: int = 10) -> int:
    """Find a free port starting from start_port."""
    import socket
    
    for i in range(max_attempts):
        port = start_port + i
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find free port after {max_attempts} attempts")


def is_process_running(port: int) -> bool:
    """Check if a process is running on the given port."""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return True
    return False


def ensure_api_running(api_port: int) -> Optional[subprocess.Popen]:
    """Ensure the API server is running."""
    if is_process_running(api_port):
        logger.info(f"API server already running on port {api_port}")
        return None
    
    logger.info(f"Starting API server on port {api_port}...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "agentx", "start", "--port", str(api_port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for API to be ready
    for _ in range(30):  # 30 second timeout
        if is_process_running(api_port):
            logger.info("API server started successfully")
            return api_process
        time.sleep(1)
    
    api_process.terminate()
    raise RuntimeError("Failed to start API server")


def get_studio_path() -> Path:
    """Get the path to the studio directory."""
    # Try relative to the package
    package_dir = Path(__file__).parent.parent.parent.parent
    studio_path = package_dir / "studio"
    
    if studio_path.exists():
        return studio_path
    
    # Try relative to current directory
    studio_path = Path.cwd() / "studio"
    if studio_path.exists():
        return studio_path
    
    raise RuntimeError("Could not find studio directory. Make sure you're in the AgentX project root.")


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--port', '-p', default=3333, help='Port for the studio UI')
@click.option('--api-port', default=8000, help='Port for the API server')
@click.option('--no-api', is_flag=True, help='Don\'t start the API server')
@click.option('--open', '-o', is_flag=True, help='Open studio in browser')
def studio(ctx, port: int, api_port: int, no_api: bool, open: bool):
    """AgentX Studio - Unified interface for task execution and observability.
    
    If no subcommand is given, starts the studio (equivalent to 'start' command).
    """
    if ctx.invoked_subcommand is None:
        # If no subcommand, run start
        ctx.invoke(start, port=port, api_port=api_port, no_api=no_api, open=open, production=False)


@studio.command()
@click.option('--port', '-p', default=3333, help='Port for the studio UI')
@click.option('--api-port', default=8000, help='Port for the API server')
@click.option('--no-api', is_flag=True, help='Don\'t start the API server')
@click.option('--open', '-o', is_flag=True, help='Open studio in browser')
@click.option('--production', is_flag=True, help='Run in production mode')
def start(port: int, api_port: int, no_api: bool, open: bool, production: bool):
    """Start AgentX Studio UI."""
    studio_path = get_studio_path()
    
    # Check if pnpm is available (studio uses pnpm)
    try:
        subprocess.run(['pnpm', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("pnpm is not installed. Please install pnpm first.")
        logger.info("Run: npm install -g pnpm")
        sys.exit(1)
    
    # Check if npm dependencies are installed
    node_modules = studio_path / "node_modules"
    if not node_modules.exists():
        logger.error("Studio dependencies not installed. Run 'agentx studio setup' first.")
        sys.exit(1)
    
    # Prepare environment
    env = os.environ.copy()
    env['NEXT_PUBLIC_AGENTX_API_URL'] = f'http://localhost:{api_port}'
    
    # Start studio with integrated backend handling
    try:
        logger.info(f"Starting AgentX Studio on http://localhost:{port}")
        
        if production:
            # Build and run production
            logger.info("Building studio for production...")
            subprocess.run(['pnpm', 'run', 'build'], cwd=studio_path, check=True, env=env)
            
            # Use dev:full for integrated backend in production too
            studio_process = subprocess.Popen(
                ['pnpm', 'run', 'start'],
                cwd=studio_path,
                env=env
            )
        else:
            # Run development server with integrated backend
            if no_api:
                cmd = ['pnpm', 'run', 'dev']
            else:
                cmd = ['pnpm', 'run', 'dev:full']
                
            studio_process = subprocess.Popen(
                cmd,
                cwd=studio_path,
                env=env
            )
        
        # Open browser if requested
        if open:
            time.sleep(3)  # Wait for server to start
            webbrowser.open(f'http://localhost:{port}')
        
        logger.info("Studio is running. Press Ctrl+C to stop.")
        
        # Wait for studio process
        studio_process.wait()
        
    except KeyboardInterrupt:
        logger.info("Shutting down studio...")
    finally:
        # Cleanup
        if 'studio_process' in locals():
            studio_process.terminate()
            # Give time for graceful shutdown
            time.sleep(2)
            if studio_process.poll() is None:
                studio_process.kill()


@studio.command()
def setup():
    """Install studio dependencies."""
    studio_path = get_studio_path()
    
    logger.info("Setting up AgentX Studio...")
    
    # Check if pnpm is available
    try:
        subprocess.run(['pnpm', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("pnpm not found. Installing pnpm...")
        try:
            subprocess.run(['npm', 'install', '-g', 'pnpm'], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("npm is not installed. Please install Node.js and npm first.")
            logger.info("Visit https://nodejs.org/ to download and install Node.js")
            sys.exit(1)
    
    # Run the studio setup script
    try:
        logger.info("Running studio setup...")
        subprocess.run(['pnpm', 'run', 'setup'], cwd=studio_path, check=True)
        
        # Also create .env.local from example if it doesn't exist
        env_example = studio_path / '.env.example'
        env_local = studio_path / '.env.local'
        if env_example.exists() and not env_local.exists():
            import shutil
            shutil.copy(env_example, env_local)
            logger.info("Created .env.local from .env.example")
        
        logger.info("Studio setup completed successfully!")
        logger.info("You can now run 'agentx studio' to launch the UI")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to setup studio: {e}")
        sys.exit(1)


@studio.command()
@click.option('--port', '-p', default=3333, help='Port for the studio UI')
@click.option('--api-port', default=8000, help='Port for the API server')
def dev(port: int, api_port: int):
    """Start both API and Studio in development mode."""
    # Just invoke the start command with the same parameters
    # Since start already handles everything with dev:full
    ctx = click.get_current_context()
    ctx.invoke(start, port=port, api_port=api_port, no_api=False, open=False, production=False)


# Make studio command group available
__all__ = ['studio']