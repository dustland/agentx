#!/usr/bin/env python3
import sys
import traceback

try:
    print("Starting server debug...")
    from vibex.server.api import app
    from vibex.core.project import start_project
    
    # Test the start_project function directly
    print("Testing start_project function...")
    import asyncio
    
    async def test():
        try:
            project = await start_project(
                goal="",
                config_path="examples/simple_chat/config/team.yaml"
            )
            print(f"Project created successfully: {project.project_id}")
            return project
        except Exception as e:
            print(f"Error creating project: {e}")
            traceback.print_exc()
            return None
    
    # Run the test
    asyncio.run(test())
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()