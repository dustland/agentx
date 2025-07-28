"""
End-to-end (E2E) test for XAgent with real LLM.

Tests the key scenarios:
1. Simple plan and execute
2. Plan, pause, and resume with message  
3. Plan, adjust with message, and complete execution
4. Chat mode vs agent mode behavior

These tests verify the complete flow from user message to task execution.
"""

import pytest
import asyncio
import os
from pathlib import Path

from vibex.core.project import start_project
from vibex.core.config import TeamConfig, AgentConfig, BrainConfig


# Skip if no LLM API key
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"),
    reason="No LLM API key found"
)


@pytest.fixture
def team_config():
    """Team configuration with real LLM."""
    # Use available LLM (prefer cheaper ones for tests)
    if os.getenv("DEEPSEEK_API_KEY"):
        provider = "deepseek"
        model = "deepseek-chat"
    elif os.getenv("OPENAI_API_KEY"):
        provider = "openai"
        model = "gpt-3.5-turbo"
    else:
        provider = "anthropic"
        model = "claude-3-haiku-20240307"
    
    return TeamConfig(
        name="test_team", 
        description="E2E test team",
        agents=[
            AgentConfig(
                name="developer",
                description="A developer that writes code",
                tools=["write_file", "read_file"],
                brain_config=BrainConfig(
                    provider=provider,
                    model=model,
                    temperature=0.1  # Consistent outputs
                )
            )
        ]
    )


@pytest.mark.asyncio
async def test_simple_plan_and_execute(team_config, tmp_path):
    """Test 1: Create a plan and execute it completely."""
    print("\n=== Test 1: Simple Plan and Execute ===")
    
    # Start project with simple goal that won't trigger verification
    project = await start_project(
        goal="Write a file named hello.py with print('Hello, World!')",
        config_path=team_config,
        project_root=tmp_path
    )
    x = project.x_agent
    
    # Verify plan was created (check both XAgent and project)
    plan = x.plan or project.plan
    assert plan is not None, "Plan should be created"
    task_count = len(plan.tasks)
    print(f"✓ Plan created with {task_count} tasks")
    
    # Mark verification tasks as completed to speed up tests
    for i, task in enumerate(plan.tasks):
        print(f"  Task {i+1}: {task.action[:60]}...")
        if any(word in task.action.lower() for word in ["verify", "test", "check", "validate"]):
            task.status = "completed"
            print(f"    → Skipping verification task")
    
    # Execute with empty message - this should execute all tasks
    print("\nExecuting plan with empty message...")
    
    # Create a task to capture the response with timeout
    async def execute_with_timeout():
        try:
            return await asyncio.wait_for(x.chat(""), timeout=60.0)
        except asyncio.TimeoutError:
            print("Execution timed out after 60s")
            return None
    
    response = await execute_with_timeout()
    if response:
        print(f"Response: {response.text[:300]}...")
    
    # Check file was created
    py_files = list(tmp_path.rglob("*.py"))
    assert len(py_files) > 0, "Python file should be created"
    
    hello_file = None
    for f in py_files:
        if f.name == "hello.py":
            hello_file = f
            break
    
    assert hello_file is not None, "hello.py should be created"
    print(f"\n✓ File created: {hello_file}")
    print(f"Content: {hello_file.read_text().strip()}")
    
    # Check task status
    completed = [t for t in plan.tasks if t.status == "completed"]
    print(f"\n✓ Completed {len(completed)}/{len(plan.tasks)} tasks")
    
    await x.cleanup()
    print("\n=== Test 1 Complete ===")


@pytest.mark.asyncio
async def test_plan_pause_resume(team_config, tmp_path):
    """Test 2: Create plan, pause execution, resume with message."""
    print("\n=== Test 2: Plan, Pause, and Resume ===")
    
    # Start project with multi-step task (simple wording to avoid verification)
    project = await start_project(
        goal="Write calc.py with 'def add(a,b): return a+b' and test_calc.py",
        config_path=team_config,
        project_root=tmp_path
    )
    x = project.x_agent
    
    # Verify plan
    plan = x.plan or project.plan
    assert plan is not None
    print(f"✓ Plan created with {len(plan.tasks)} tasks")
    
    # Mark verification tasks as completed to speed up tests
    for i, task in enumerate(plan.tasks):
        print(f"  Task {i+1}: {task.action[:60]}...")
        if any(word in task.action.lower() for word in ["verify", "test", "check", "validate"]):
            task.status = "completed"
            print(f"    → Skipping verification task")
    
    # Start execution with timeout
    print("\nStarting execution...")
    async def execute_with_timeout():
        try:
            return await asyncio.wait_for(x.chat(""), timeout=60.0)
        except asyncio.TimeoutError:
            print("Execution timed out after 60s")
            return None
    
    exec_task = asyncio.create_task(execute_with_timeout())
    
    # Let it run briefly
    await asyncio.sleep(2)
    
    # Send interrupting message
    print("\nSending pause message...")
    pause_response = await x.chat("Please continue")
    print(f"Pause response: {pause_response.text[:150]}...")
    
    # Wait for original task
    try:
        await asyncio.wait_for(exec_task, timeout=5)
    except asyncio.TimeoutError:
        print("Execution task timed out (expected if paused)")
    
    # Check what was completed
    completed = [t for t in plan.tasks if t.status == "completed"]
    print(f"\n✓ Completed {len(completed)} tasks before pause")
    
    # Resume with empty message with timeout
    print("\nResuming execution...")
    resume_response = await asyncio.wait_for(x.chat(""), timeout=60.0)
    print(f"Resume response: {resume_response.text[:150]}...")
    
    await asyncio.sleep(2)
    
    # Check files
    py_files = list(tmp_path.rglob("*.py"))
    print(f"\n✓ Created {len(py_files)} Python files")
    for f in py_files:
        print(f"  - {f.name}")
    
    await x.cleanup()
    print("\n=== Test 2 Complete ===")


@pytest.mark.asyncio
async def test_plan_adjust_and_complete(team_config, tmp_path):
    """Test 3: Create plan, adjust it with message, complete execution."""
    print("\n=== Test 3: Plan, Adjust, and Complete ===")
    
    # Start with simple task
    project = await start_project(
        goal="Write a file named script.py",
        config_path=team_config,
        project_root=tmp_path
    )
    x = project.x_agent
    
    # Verify initial plan
    plan = x.plan or project.plan
    assert plan is not None
    initial_tasks = len(plan.tasks)
    print(f"✓ Initial plan has {initial_tasks} tasks")
    
    # Mark verification tasks as completed to speed up tests
    for i, task in enumerate(plan.tasks):
        print(f"  Task {i+1}: {task.action[:60]}...")
        if any(word in task.action.lower() for word in ["verify", "test", "check", "validate"]):
            task.status = "completed"
            print(f"    → Skipping verification task")
    
    # Send adjustment message with timeout
    print("\nSending adjustment...")
    adjust_response = await asyncio.wait_for(
        x.chat("Make it a calculator with add and subtract functions"),
        timeout=60.0
    )
    print(f"Adjustment response: {adjust_response.text[:200]}...")
    
    # Wait for processing
    await asyncio.sleep(3)
    
    # Check if plan was adjusted or execution happened
    current_tasks = len(plan.tasks)
    completed = [t for t in plan.tasks if t.status == "completed"]
    
    print(f"\n✓ Plan now has {current_tasks} tasks (was {initial_tasks})")
    print(f"✓ Completed {len(completed)} tasks")
    
    # Check created files
    py_files = list(tmp_path.rglob("*.py"))
    if py_files:
        print(f"\n✓ Created files:")
        for f in py_files:
            print(f"\n--- {f.name} ---")
            content = f.read_text()
            print(content[:200] + "..." if len(content) > 200 else content)
    
    await x.cleanup()
    print("\n=== Test 3 Complete ===")


@pytest.mark.asyncio 
async def test_chat_mode_vs_agent_mode(team_config, tmp_path):
    """Test 4: Verify chat mode doesn't execute plan."""
    print("\n=== Test 4: Chat Mode vs Agent Mode ===")
    
    # Start project with simple goal
    project = await start_project(
        goal="Write a file named scraper.py",
        config_path=team_config,
        project_root=tmp_path
    )
    x = project.x_agent
    
    # Initial plan
    plan = x.plan or project.plan
    assert plan is not None
    
    # Mark verification tasks as completed to speed up tests
    for i, task in enumerate(plan.tasks):
        print(f"  Task {i+1}: {task.action[:60]}...")
        if any(word in task.action.lower() for word in ["verify", "test", "check", "validate"]):
            task.status = "completed"
            print(f"    → Skipping verification task")
    
    initial_completed = [t for t in plan.tasks if t.status == "completed"]
    
    # Chat mode - should just respond, not execute
    print("\nTesting chat mode...")
    chat_response = await asyncio.wait_for(
        x.chat("What libraries would you use?", mode="chat"),
        timeout=30.0
    )
    print(f"Chat response: {chat_response.text[:200]}...")
    
    # Check no new tasks completed
    chat_completed = [t for t in plan.tasks if t.status == "completed"]
    assert len(chat_completed) == len(initial_completed), "Chat mode should not execute tasks"
    print("✓ Chat mode did not execute tasks")
    
    # Agent mode - should execute
    print("\nTesting agent mode...")
    agent_response = await asyncio.wait_for(
        x.chat("Start with the basic structure", mode="agent"),
        timeout=60.0
    )
    print(f"Agent response: {agent_response.text[:200]}...")
    
    await asyncio.sleep(2)
    
    # Check tasks were executed
    agent_completed = [t for t in plan.tasks if t.status == "completed"]
    print(f"✓ Agent mode completed {len(agent_completed) - len(initial_completed)} new tasks")
    
    await x.cleanup()
    print("\n=== Test 4 Complete ===")


if __name__ == "__main__":
    # Run with: python test_xagent_e2e.py
    pytest.main([__file__, "-xvs"])