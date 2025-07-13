#!/usr/bin/env python3
"""
Explore GitHub repositories for auto_writer research
"""

import asyncio
from pathlib import Path
from agentx import start_task
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent.parent / ".env")

async def explore_repo(repo_url: str, research_focus: str):
    """
    Research a GitHub repository for technical insights
    """
    prompt = f"""Analyze the GitHub repository: {repo_url}

Focus on: {research_focus}

Extract and analyze:
1. README and documentation
2. Code structure and architecture
3. Performance benchmarks if available
4. Issues and discussions about performance/features
5. Release notes and changelog
6. Example code and best practices

Create a comprehensive technical analysis document.
"""

    x = await start_task(prompt, "config/team.yaml")
    workspace = Path(x.workspace.get_workspace_path())

    # Let it run a few steps
    for i in range(5):
        if x.is_complete:
            break
        print(f"\nStep {i+1}: {await x.step()}"[:100] + "...")

    print(f"\nWorkspace: {workspace}")
    return workspace

# Example usage
if __name__ == "__main__":
    # Analyze Flask and FastAPI repos
    asyncio.run(explore_repo(
        "https://github.com/pallets/flask",
        "Technical architecture, performance optimizations, WSGI implementation"
    ))
