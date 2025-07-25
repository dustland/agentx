#!/usr/bin/env python3
import asyncio
from pathlib import Path
from vibex import VibeX

async def main():
    config_path = Path(__file__).parent / "config" / "team.yaml"

    print("Chat started! Type 'quit' or 'q' to exit.")

    # Initialize VibeX for chat
    print("Initializing VibeX...")
    x = await VibeX.start(
        project_id="simple_chat_project",
        config_path=str(config_path),
    )

    # Start the conversation loop
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'q']:
                break

            # Chat with VibeX
            print("X: ", end="", flush=True)
            response = await x.chat(user_input)
            print(response)

        except (KeyboardInterrupt, EOFError):
            break

    print("\nChat ended.")


if __name__ == "__main__":
    asyncio.run(main())