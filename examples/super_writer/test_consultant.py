#!/usr/bin/env python3
"""
Test script for the consultant agent only.
Tests if the consultant creates requirements.md file.
"""

import asyncio
import sys
import os
from pathlib import Path

# Framework will handle clean logging automatically
# Uncomment below if you need extra verbose framework details
# os.environ['AGENTX_VERBOSE'] = '1'

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agentx import start_task

async def main():
    """Test the consultant agent only."""
    
    # Test topic
    topic = "The Future of Artificial Intelligence in Healthcare"
    
    print(f"🧪 Testing Consultant Agent with topic: '{topic}'")
    print("=" * 60)
    
    # Create a minimal team config with just the consultant (using correct format)
    test_config = {
        "name": "consultant_test",
        "description": "Test consultant agent only",
        "agents": [
            {
                "name": "consultant",
                "description": "Requirements gathering and project planning specialist",
                "prompt_template": "prompts/consultant.md",
                "llm_config": {
                    "model": "deepseek/deepseek-chat",
                    "temperature": 0.7,
                    "max_tokens": 4096
                }
            }
        ],
        "execution": {
            "mode": "autonomous",
            "max_rounds": 5,
            "timeout_seconds": 300,
            "initial_agent": "consultant"
        }
    }
    
    # Save test config
    import yaml
    config_path = "config/consultant.yaml"
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
        print("🤖 Running consultant to completion...")
        await executor._execute()
        
        print(f"\n🔍 Task completed. Status: Complete={executor.task.is_complete}, Rounds={executor.task.round_count}")
        
        # Check if requirements document was created (should be in artifacts folder)
        artifacts_dir = Path(executor.task.workspace_dir) / "artifacts"
        requirements_files = []
        if artifacts_dir.exists():
            # Look for requirements documents in artifacts
            requirements_files = list(artifacts_dir.glob("*requirements*"))
        
        if requirements_files:
            requirements_file = requirements_files[0]  # Take the first match
            print(f"✅ SUCCESS: Requirements document was created in artifacts!")
            print(f"📄 File: {requirements_file.name}")
            print(f"📄 File size: {requirements_file.stat().st_size} bytes")
            print("\n📝 Content preview:")
            print("-" * 40)
            with open(requirements_file, 'r') as f:
                content = f.read()
                print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print("❌ FAILED: Requirements document was not created in artifacts folder")
            # Also check workspace root for backward compatibility
            root_requirements = Path(executor.task.workspace_dir) / "requirements.md"
            if root_requirements.exists():
                print("⚠️  NOTE: Found requirements.md in workspace root (should be in artifacts/)")
            else:
                print("   No requirements document found anywhere in workspace")
            
        # List all files in workspace
        print(f"\n📂 Files in workspace ({executor.task.workspace_dir}):")
        workspace_path = Path(executor.task.workspace_dir)
        if workspace_path.exists():
            for file_path in workspace_path.rglob("*"):
                if file_path.is_file():
                    print(f"  📄 {file_path.relative_to(workspace_path)}")
        
        # Show conversation history
        print(f"\n💬 Conversation history ({len(executor.task.history)} steps):")
        for i, step in enumerate(executor.task.history):
            print(f"  Step {i+1}: {step.agent_name}")
            for part in step.parts:
                if hasattr(part, 'text'):
                    print(f"    Text: {part.text[:100]}...")
                elif hasattr(part, 'tool_name'):
                    print(f"    Tool: {part.tool_name}")
        
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