#!/usr/bin/env python3
import asyncio
from pathlib import Path
from vibex.core.xagent import XAgent
from vibex.config.team_loader import load_team_config

async def main():
    config_path = Path(__file__).parent / "config" / "team.yaml"

    print("Chat started! Type 'quit' or 'q' to exit.")

    # Initialize XAgent for chat (no initial prompt for pure chat mode)
    print("Initializing X...")
    team_config = load_team_config(str(config_path))
    x = XAgent(team_config=team_config)

    # Start the conversation loop
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'q']:
            break

        # Chat with X
        print("X: ", end="", flush=True)
        response = await x.chat(user_input)
        print(response.text)

        # Show additional info if available
        if response.preserved_steps:
            print(f"  (Preserved {len(response.preserved_steps)} completed steps)")
        if response.regenerated_steps:
            print(f"  (Regenerated {len(response.regenerated_steps)} steps)")

if __name__ == "__main__":
    asyncio.run(main())