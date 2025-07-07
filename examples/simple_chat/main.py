#!/usr/bin/env python3
import asyncio
from pathlib import Path
from agentx.core.task import TaskExecutor

async def main():
    config_path = Path(__file__).parent / "config" / "team.yaml"
    
    # Create a TaskExecutor instance for conversational interaction
    executor = TaskExecutor(str(config_path))
    
    print("Chat started! Type 'quit' or 'q' to exit.")
    
    # Get the first user input
    user_input = input("You: ").strip()
    if user_input.lower() in ['quit', 'q']:
        return
    
    # Start the conversation
    await executor.start(user_input)
    
    # Get the first response
    print("Assistant: ", end="", flush=True)
    response = await executor.step()
    print(response)
    
    # Continue the conversation
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'q']:
            break
        
        # Add user message and get response
        executor.add_user_message(user_input)
        print("Assistant: ", end="", flush=True)
        response = await executor.step()
        print(response)

if __name__ == "__main__":
    asyncio.run(main()) 