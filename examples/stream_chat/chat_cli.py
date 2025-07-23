#!/usr/bin/env python3
"""
Minimal CLI wrapper for VibeX chat - perfect for automation.
No logging, just input and output.
"""
import asyncio
import sys
from pathlib import Path

# Disable all logging
import logging
logging.disable(logging.CRITICAL)

# Suppress asyncio warnings
import warnings
warnings.filterwarnings("ignore")

from vibex.core.xagent import XAgent
from vibex.config.team_loader import load_team_config

async def chat(message: str, task_id: str = None):
    """Send a message and return the response."""
    config_path = Path(__file__).parent / "config" / "team.yaml"
    
    try:
        team_config = load_team_config(str(config_path))
        kwargs = {'team_config': team_config}
        if task_id:
            kwargs['task_id'] = task_id
            
        x = XAgent(**kwargs)
        response = await x.chat(message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: chat_cli.py <message> [task_id]", file=sys.stderr)
        sys.exit(1)
    
    message = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Run async function and get result
    try:
        result = asyncio.run(chat(message, task_id))
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()