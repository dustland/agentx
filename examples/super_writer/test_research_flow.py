#!/usr/bin/env python3
"""
Test script for consultant + researcher flow only.
Tests if intermediate research files are created.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agentx import start_task

async def main():
    """Test the consultant + researcher flow only."""
    
    # Test topic
    topic = "The Future of Artificial Intelligence in Healthcare"
    
    print(f"🧪 Testing Consultant + Researcher Flow with topic: '{topic}'")
    print("=" * 60)
    
    # Create a config with just consultant and researcher
    test_config = {
        "name": "research_test",
        "description": "Test consultant and researcher agents only",
        "agents": [
            {
                "name": "consultant",
                "description": "Requirements gathering and project planning specialist",
                "prompt_template": "prompts/consultant.md",
                "llm_config": {
                    "model": "deepseek/deepseek-chat",
                    "temperature": 0.3,
                    "max_tokens": 4096
                }
            },
            {
                "name": "researcher",
                "description": "Research specialist for comprehensive information gathering",
                "prompt_template": "prompts/researcher.md",
                "llm_config": {
                    "model": "deepseek/deepseek-chat",
                    "temperature": 0.2,
                    "max_tokens": 4096
                }
            }
        ],
        "handoffs": [
            {
                "from_agent": "consultant",
                "to_agent": "researcher",
                "condition": "requirements are clear and research is needed"
            }
        ],
        "orchestrator": {
            "max_rounds": 20,
            "timeout": 1800,
            "brain_config": {
                "model": "deepseek/deepseek-chat",
                "temperature": 0.0,
                "max_tokens": 100,
                "timeout": 15
            }
        },
        "execution": {
            "mode": "autonomous",
            "max_rounds": 20,
            "timeout_seconds": 1800,
            "initial_agent": "consultant"
        }
    }
    
    # Save test config
    import yaml
    config_path = "config/research_test.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(test_config, f, default_flow_style=False)
    
    try:
        # Start the task
        executor = start_task(
            prompt=topic,
            config_path=config_path
        )
        
        print(f"\n📋 Task ID: {executor.task.task_id}")
        print(f"📁 Workspace: {executor.task.workspace_dir}")
        print(f"🔗 Full path: {os.path.abspath(executor.task.workspace_dir)}")
        print("-" * 60)
        
        # Run to completion
        print("🤖 Running consultant + researcher to completion...")
        await executor._execute()
        
        print(f"\n🔍 Task completed. Status: Complete={executor.task.is_complete}, Rounds={executor.task.round_count}")
        
        # Check what files were created
        workspace_path = Path(executor.task.workspace_dir)
        artifacts_dir = workspace_path / "artifacts"
        
        print(f"\n📂 Files created in artifacts:")
        if artifacts_dir.exists():
            for file_path in artifacts_dir.rglob("*.md"):
                print(f"  📄 {file_path.name} ({file_path.stat().st_size} bytes)")
                # Show first few lines of content
                with open(file_path, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')[:3]
                    preview = '\n'.join(lines)
                    print(f"      Preview: {preview[:100]}...")
        
        # Check temp directory too
        temp_dir = workspace_path / "temp"
        if temp_dir.exists() and any(temp_dir.iterdir()):
            print(f"\n📂 Files in temp:")
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    print(f"  📄 {file_path.name}")
        
        # Show conversation history
        print(f"\n💬 Agent sequence ({len(executor.task.history)} steps):")
        for i, step in enumerate(executor.task.history):
            print(f"  Step {i+1}: {step.agent_name}")
            # Show tool calls if any
            for part in step.parts:
                if hasattr(part, 'tool_name'):
                    print(f"    🔧 Tool: {part.tool_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup test config
        if os.path.exists(config_path):
            os.remove(config_path)

if __name__ == "__main__":
    asyncio.run(main()) 