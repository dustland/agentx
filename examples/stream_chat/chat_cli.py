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

from vibex import VibeX

# A simple async function to handle the chat logic
async def chat(message: str, project_id: str = None, goal: str = None):
    """
    Starts a VibeX session and sends a message.
    If project_id is provided, it resumes that project.
    """
    config_path = "config/team.yaml"
    
    # The VibeX.start method handles setup and teardown
    x = await VibeX.start(
        project_id=project_id,
        goal=goal,
        config_path=config_path,
    )
        
    # Stream the response from the agent team
    async for chunk in x.stream_chat(message):
        # Print each chunk as it arrives
        print(chunk, end="", flush=True)
            
    print() # Newline after the stream is complete
    return x.project_id


async def main():
    if len(sys.argv) < 2:
        print("Usage: chat_cli.py <message> [project_id]", file=sys.stderr)
        sys.exit(1)
        
    message = sys.argv[1]
    project_id = sys.argv[2] if len(sys.argv) > 2 else None
    goal = message if not project_id else None

    # Run the chat function
    new_project_id = await chat(message, project_id, goal)
    
    if not project_id:
        print(f"\nNew project started with ID: {new_project_id}", file=sys.stderr)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting chat.", file=sys.stderr)