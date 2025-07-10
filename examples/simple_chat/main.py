#!/usr/bin/env python3
import asyncio
from pathlib import Path
from agentx import start_task

async def main():
    config_path = Path(__file__).parent / "config" / "team.yaml"

    print("Chat started! Type 'quit' or 'q' to exit.")

    # Get the first user input
    user_input = input("You: ").strip()
    if user_input.lower() in ['quit', 'q']:
        return

    # Start the conversation with XAgent
    print("Initializing X...")
    x = await start_task(user_input, str(config_path))

    # Get the first response
    print("X: ", end="", flush=True)
    response = await x.chat(user_input)
    print(response.text)

    # Continue the conversation
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
