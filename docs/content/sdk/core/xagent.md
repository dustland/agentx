---
title: XAgent
description: VibeX XAgent - The project's conversational representative
---

_Module: [`vibex.xagent`](https://github.com/dustland/vibex/blob/main/src/vibex/xagent.py)_

The `XAgent` is the main entry point for interacting with the VibeX framework. It acts as a conversational representative for your projects, managing the agent team, and executing tasks based on your goals.

## Usage

```python
import asyncio
from vibex import XAgent

async def main():
    # Start a new project
    x = await XAgent.start(
        goal="Create a report on the latest AI trends.",
        config_path="path/to/your/team.yaml"
    )

    # Autonomously execute the project plan
    while not x.is_complete():
        response = await x.step()
        print(response)

    # Chat for refinements
    response = await x.chat("Add a section on ethical considerations.")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## XAgentResponse <a href="https://github.com/dustland/vibex/blob/main/src/vibex/xagent.py#L50" class="source-link" title="View source code">source</a>

The `XAgentResponse` object is returned from chat interactions and contains the agent's response, along with metadata about the execution.

### **init** <a href="https://github.com/dustland/vibex/blob/main/src/vibex/xagent.py#L53" class="source-link" title="View source code">source</a>

Initializes the `XAgentResponse`.

## XAgent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/xagent.py#L70" class="source-link" title="View source code">source</a>

The main class for managing and interacting with VibeX projects.

### start <a href="https://github.com/dustland/vibex/blob/main/src/vibex/xagent.py#L100" class="source-link" title="View source code">source</a>

A class method to start a new project. This is the recommended way to create an `XAgent` instance.

### chat <a href="https://github.com/dustland/vibex/blob/main/src/vibex/xagent.py#L261" class="source-link" title="View source code">source</a>

Send a conversational message to the `XAgent` to ask questions, provide feedback, or adjust the plan.

### step <a href="https://github.com/dustland/vibex/blob/main/src/vibex/xagent.py#L915" class="source-link" title="View source code">source</a>

Execute the next autonomous step in the project plan.

### is_complete <a href="https://github.com/dustland/vibex/blob/main/src/vibex/xagent.py#L896" class="source-link" title="View source code">source</a>

Check if the project is complete.

### register_tool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/xagent.py#L908" class="source-link" title="View source code">source</a>

Register a custom tool with the `XAgent`'s tool manager.
