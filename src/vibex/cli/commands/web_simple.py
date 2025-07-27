"""Simplified Web CLI for pip-installed VibeX."""

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

# Web package files embedded as base64
WEB_PACKAGE = {
    "package.json": """
{
  "name": "vibex-web-embedded",
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
    # We'll include minimal files needed for a basic web
}


def get_embedded_web_path() -> Path:
    """Get or create the embedded web directory."""
    # Use a consistent location in user's home directory
    web_dir = Path.home() / ".vibex" / "web"
    
    # Check if already extracted
    if (web_dir / "package.json").exists():
        return web_dir
    
    # Extract embedded web
    logger.info("Extracting embedded web files...")
    web_dir.mkdir(parents=True, exist_ok=True)
    
    # Write package files
    for filename, content in WEB_PACKAGE.items():
        (web_dir / filename).write_text(content.strip())
    
    # Create minimal Next.js structure
    create_minimal_web(web_dir)
    
    return web_dir


def create_minimal_web(web_dir: Path):
    """Create a minimal web structure."""
    # Create directories
    (web_dir / "pages").mkdir(exist_ok=True)
    (web_dir / "styles").mkdir(exist_ok=True)
    (web_dir / "public").mkdir(exist_ok=True)
    
    # Create minimal pages/index.tsx
    (web_dir / "pages" / "index.tsx").write_text("""
import { useEffect, useState } from 'react'

export default function Home() {
  const [apiUrl, setApiUrl] = useState('')
  const [tasks, setTasks] = useState([])
  
  useEffect(() => {
    setApiUrl(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7770')
  }, [])

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>VibeX</h1>
      <p>Connected to API: {apiUrl}</p>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>Quick Start</h2>
        <p>This is a minimal web interface. For the full experience:</p>
        <ol>
          <li>Clone the VibeX repository</li>
          <li>Run <code>vibex web setup</code> in the project directory</li>
          <li>Run <code>vibex web start</code></li>
        </ol>
      </div>
      
      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
        <h3>API Status</h3>
        <p>Make sure VibeX API is running on port 7770</p>
        <pre>vibex start</pre>
      </div>
    </div>
  )
}
""")
    
    # Create next.config.js
    (web_dir / "next.config.js").write_text("""
module.exports = {
  reactStrictMode: true,
  env: {
            NEXT_PUBLIC_API_URL: process.env.AGENTX_API_URL || 'http://localhost:7770',
  },
}
""")
    
    # Create minimal styles/globals.css
    (web_dir / "styles" / "globals.css").write_text("""
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
    (web_dir / "pages" / "_app.tsx").write_text("""
import '../styles/globals.css'
import type { AppProps } from 'next/app'

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />
}
""")


def download_full_web(target_dir: Path) -> bool:
    """Download the full web from GitHub."""
    try:
        logger.info("Downloading full VibeX from GitHub...")
        
        # Use git to clone just the web directory
        subprocess.run([
            'git', 'clone', '--depth', '1', '--filter=blob:none', '--sparse',
            'https://github.com/yourusername/vibex.git',
            str(target_dir / '.tmp')
        ], check=True, capture_output=True)
        
        subprocess.run([
            'git', '-C', str(target_dir / '.tmp'), 'sparse-checkout', 'set', 'web'
        ], check=True, capture_output=True)
        
        # Move web files
        shutil.move(str(target_dir / '.tmp' / 'web'), str(target_dir))
        shutil.rmtree(str(target_dir / '.tmp'))
        
        logger.info("Full web downloaded successfully!")
        return True
        
    except Exception as e:
        logger.warning(f"Could not download full web: {e}")
        logger.info("Using embedded minimal web instead")
        return False


def ensure_web_available() -> tuple[Path, bool]:
    """Ensure web is available, either full or embedded."""
    # First, check if we're in a project with web/
    local_web = Path.cwd() / "web"
    if local_web.exists() and (local_web / "package.json").exists():
        logger.info("Using local web from project directory")
        return local_web, True
    
    # Check if full web is already downloaded
    full_web = Path.home() / ".vibex" / "web-full"
    if full_web.exists() and (full_web / "package.json").exists():
        return full_web, True
    
    # Try to download full web
    if download_full_web(Path.home() / ".vibex"):
        return Path.home() / ".vibex" / "web-full", True
    
    # Fall back to embedded minimal web
    return get_embedded_web_path(), False


def run_web_command(
    action: str = "start",
    port: int = 7777,
    api_port: int = 7770,
    no_api: bool = False,
    open_browser: bool = True,
    production: bool = False
):
    """Run web with automatic detection and fallback."""
    web_path, is_full = ensure_web_available()
    
    if action == "setup":
        logger.info(f"Installing dependencies in {web_path}...")
        subprocess.run(['npm', 'install'], cwd=web_path, check=True)
        logger.info("Setup completed!")
        return
    
    # Check if dependencies are installed
    if not (web_path / "node_modules").exists():
        logger.info("Installing web dependencies...")
        subprocess.run(['npm', 'install'], cwd=web_path, check=True)
    
    # Prepare environment
    env = os.environ.copy()
    env['AGENTX_API_URL'] = f'http://localhost:{api_port}'
    env['NODE_ENV'] = 'production' if production else 'development'
    
    # Start API if needed
    api_process = None
    if not no_api:
        logger.info(f"Starting API server on port {api_port}...")
        api_process = subprocess.Popen(
            [sys.executable, "-m", "vibex", "start", "--port", str(api_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(3)  # Give API time to start
    
    try:
        # Start web
        logger.info(f"Starting VibeX on http://localhost:{port}")
        
        if not is_full:
            logger.info("Note: Running minimal embedded web. For full features, clone the VibeX repository.")
        
        if production:
            subprocess.run(['npm', 'run', 'build'], cwd=web_path, check=True)
            web_cmd = ['npm', 'run', 'start', '--', '-p', str(port)]
        else:
            web_cmd = ['npm', 'run', 'dev', '--', '-p', str(port)]
        
        web_process = subprocess.Popen(web_cmd, cwd=web_path, env=env)
        
        # Open browser
        if open_browser:
            time.sleep(2)
            webbrowser.open(f'http://localhost:{port}')
        
        logger.info(f"\n✨ VibeX is running at http://localhost:{port}")
        logger.info("Press Ctrl+C to stop.\n")
        
        web_process.wait()
        
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
    finally:
        if web_process:
            web_process.terminate()
        if api_process:
            api_process.terminate()