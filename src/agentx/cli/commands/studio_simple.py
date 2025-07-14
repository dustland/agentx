"""Simplified Studio CLI for pip-installed AgentX."""

import os
import sys
import subprocess
import webbrowser
import time
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from ...utils.logger import get_logger

logger = get_logger(__name__)

# Studio package files embedded as base64
STUDIO_PACKAGE = {
    "package.json": """
{
  "name": "agentx-studio-embedded",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "lucide-react": "^0.309.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.6",
    "@types/react": "^18.2.46",
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
""",
    # We'll include minimal files needed for a basic studio
}


def get_embedded_studio_path() -> Path:
    """Get or create the embedded studio directory."""
    # Use a consistent location in user's home directory
    studio_dir = Path.home() / ".agentx" / "studio"
    
    # Check if already extracted
    if (studio_dir / "package.json").exists():
        return studio_dir
    
    # Extract embedded studio
    logger.info("Extracting embedded studio files...")
    studio_dir.mkdir(parents=True, exist_ok=True)
    
    # Write package files
    for filename, content in STUDIO_PACKAGE.items():
        (studio_dir / filename).write_text(content.strip())
    
    # Create minimal Next.js structure
    create_minimal_studio(studio_dir)
    
    return studio_dir


def create_minimal_studio(studio_dir: Path):
    """Create a minimal studio structure."""
    # Create directories
    (studio_dir / "pages").mkdir(exist_ok=True)
    (studio_dir / "styles").mkdir(exist_ok=True)
    (studio_dir / "public").mkdir(exist_ok=True)
    
    # Create minimal pages/index.tsx
    (studio_dir / "pages" / "index.tsx").write_text("""
import { useEffect, useState } from 'react'

export default function Home() {
  const [apiUrl, setApiUrl] = useState('')
  const [tasks, setTasks] = useState([])
  
  useEffect(() => {
    setApiUrl(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
  }, [])

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>AgentX Studio</h1>
      <p>Connected to API: {apiUrl}</p>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>Quick Start</h2>
        <p>This is a minimal studio interface. For the full experience:</p>
        <ol>
          <li>Clone the AgentX repository</li>
          <li>Run <code>agentx studio setup</code> in the project directory</li>
          <li>Run <code>agentx studio start</code></li>
        </ol>
      </div>
      
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
        <h3>API Status</h3>
        <p>Make sure AgentX API is running on port 8000</p>
        <pre>agentx start</pre>
      </div>
    </div>
  )
}
""")
    
    # Create next.config.js
    (studio_dir / "next.config.js").write_text("""
module.exports = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.AGENTX_API_URL || 'http://localhost:8000',
  },
}
""")
    
    # Create minimal styles/globals.css
    (studio_dir / "styles" / "globals.css").write_text("""
html, body {
  padding: 0;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen,
    Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;
}

* {
  box-sizing: border-box;
}
""")
    
    # Create pages/_app.tsx
    (studio_dir / "pages" / "_app.tsx").write_text("""
import '../styles/globals.css'
import type { AppProps } from 'next/app'

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />
}
""")


def download_full_studio(target_dir: Path) -> bool:
    """Download the full studio from GitHub."""
    try:
        logger.info("Downloading full AgentX Studio from GitHub...")
        
        # Use git to clone just the studio directory
        subprocess.run([
            'git', 'clone', '--depth', '1', '--filter=blob:none', '--sparse',
            'https://github.com/yourusername/agentx.git',
            str(target_dir / '.tmp')
        ], check=True, capture_output=True)
        
        subprocess.run([
            'git', '-C', str(target_dir / '.tmp'), 'sparse-checkout', 'set', 'studio'
        ], check=True, capture_output=True)
        
        # Move studio files
        shutil.move(str(target_dir / '.tmp' / 'studio'), str(target_dir))
        shutil.rmtree(str(target_dir / '.tmp'))
        
        logger.info("Full studio downloaded successfully!")
        return True
        
    except Exception as e:
        logger.warning(f"Could not download full studio: {e}")
        logger.info("Using embedded minimal studio instead")
        return False


def ensure_studio_available() -> tuple[Path, bool]:
    """Ensure studio is available, either full or embedded."""
    # First, check if we're in a project with studio/
    local_studio = Path.cwd() / "studio"
    if local_studio.exists() and (local_studio / "package.json").exists():
        logger.info("Using local studio from project directory")
        return local_studio, True
    
    # Check if full studio is already downloaded
    full_studio = Path.home() / ".agentx" / "studio-full"
    if full_studio.exists() and (full_studio / "package.json").exists():
        return full_studio, True
    
    # Try to download full studio
    if download_full_studio(Path.home() / ".agentx"):
        return Path.home() / ".agentx" / "studio-full", True
    
    # Fall back to embedded minimal studio
    return get_embedded_studio_path(), False


def run_studio_command(
    action: str = "start",
    port: int = 3000,
    api_port: int = 8000,
    no_api: bool = False,
    open_browser: bool = True,
    production: bool = False
):
    """Run studio with automatic detection and fallback."""
    studio_path, is_full = ensure_studio_available()
    
    if action == "setup":
        logger.info(f"Installing dependencies in {studio_path}...")
        subprocess.run(['npm', 'install'], cwd=studio_path, check=True)
        logger.info("Setup completed!")
        return
    
    # Check if dependencies are installed
    if not (studio_path / "node_modules").exists():
        logger.info("Installing studio dependencies...")
        subprocess.run(['npm', 'install'], cwd=studio_path, check=True)
    
    # Prepare environment
    env = os.environ.copy()
    env['AGENTX_API_URL'] = f'http://localhost:{api_port}'
    env['NODE_ENV'] = 'production' if production else 'development'
    
    # Start API if needed
    api_process = None
    if not no_api:
        logger.info(f"Starting API server on port {api_port}...")
        api_process = subprocess.Popen(
            [sys.executable, "-m", "agentx", "start", "--port", str(api_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Give API time to start
    
    try:
        # Start studio
        logger.info(f"Starting AgentX Studio on http://localhost:{port}")
        
        if not is_full:
            logger.info("Note: Running minimal embedded studio. For full features, clone the AgentX repository.")
        
        if production:
            subprocess.run(['npm', 'run', 'build'], cwd=studio_path, check=True)
            studio_cmd = ['npm', 'run', 'start', '--', '-p', str(port)]
        else:
            studio_cmd = ['npm', 'run', 'dev', '--', '-p', str(port)]
        
        studio_process = subprocess.Popen(studio_cmd, cwd=studio_path, env=env)
        
        # Open browser
        if open_browser:
            time.sleep(2)
            webbrowser.open(f'http://localhost:{port}')
        
        logger.info(f"\n✨ AgentX Studio is running at http://localhost:{port}")
        logger.info("Press Ctrl+C to stop.\n")
        
        studio_process.wait()
        
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    finally:
        if studio_process:
            studio_process.terminate()
        if api_process:
            api_process.terminate()