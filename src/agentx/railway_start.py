#!/usr/bin/env python3
"""
Railway deployment starter for AgentX
Runs both API server and Studio in production
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def start_services():
    """Start both API and Studio services."""
    processes = []
    
    # Get ports from environment
    api_port = os.environ.get('PORT', '8000')
    studio_port = os.environ.get('STUDIO_PORT', '3000')
    
    # Start API server
    print(f"Starting AgentX API on port {api_port}...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "agentx", "start", "--port", api_port, "--host", "0.0.0.0"],
        env={**os.environ, "PYTHONUNBUFFERED": "1"}
    )
    processes.append(api_process)
    
    # Give API time to start
    time.sleep(3)
    
    # Start Studio
    studio_path = Path(__file__).parent.parent.parent / "studio"
    if studio_path.exists():
        print(f"Starting AgentX Studio on port {studio_port}...")
        studio_env = {
            **os.environ,
            "PORT": studio_port,
            "AGENTX_API_URL": f"http://localhost:{api_port}",
            "NODE_ENV": "production"
        }
        studio_process = subprocess.Popen(
            ["pnpm", "run", "start"],
            cwd=studio_path,
            env=studio_env
        )
        processes.append(studio_process)
    else:
        print("Studio directory not found, running API only")
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\nShutting down services...")
        for proc in processes:
            proc.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Wait for processes
    print(f"\n✅ AgentX services running:")
    print(f"   API:    http://0.0.0.0:{api_port}")
    if len(processes) > 1:
        print(f"   Studio: http://0.0.0.0:{studio_port}")
    print("\nPress Ctrl+C to stop")
    
    # Keep running
    while True:
        for proc in processes:
            if proc.poll() is not None:
                print(f"Process {proc.pid} exited with code {proc.returncode}")
                signal_handler(None, None)
        time.sleep(1)

if __name__ == "__main__":
    start_services()