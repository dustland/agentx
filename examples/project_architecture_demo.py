"""
Demo of the new Project-based architecture in VibeX v2.0

This example shows how Projects contain Tasks, and each Task is executed by a single agent.
"""

import asyncio
from vibex import VibeX
from vibex.core.plan import Plan
from vibex.core.task import Task


async def main():
    """
    Example: Building a documentation website as a Project with multiple Tasks.
    """
    
    # 1. Start a new project (not a task!)
    print("🚀 Starting a new documentation project...")
    project = await VibeX.start(
        project_id="doc_website_project",
        goal="Build a comprehensive documentation website for our API",
        config_path="examples/web_team/config/team.yaml"
    )
    
    # The project's X agent is our interface
    x_agent = project.x_agent
    
    # 2. X agent creates a plan with multiple tasks
    print("\n📋 X agent is creating a plan...")
    
    # In practice, this would be done by the X agent through LLM
    # Here we show the structure for clarity
    plan = Plan(
        goal="Build a comprehensive documentation website for our API",
        tasks=[
            Task(
                id="research",
                name="Research Documentation Needs",
                goal="Analyze the API and determine what documentation is needed",
                agent="researcher",  # Single agent assignment
            ),
            Task(
                id="structure",
                name="Design Site Structure",
                goal="Create the information architecture and site map",
                agent="designer",  # Single agent assignment
                dependencies=["research"]
            ),
            Task(
                id="backend",
                name="Setup Documentation Framework",
                goal="Initialize MkDocs or similar framework with the designed structure",
                agent="developer",  # Single agent assignment
                dependencies=["structure"]
            ),
            Task(
                id="content",
                name="Write API Documentation",
                goal="Create comprehensive documentation for all API endpoints",
                agent="writer",  # Single agent assignment
                dependencies=["backend"]
            ),
            Task(
                id="examples",
                name="Create Code Examples",
                goal="Write practical code examples for each API endpoint",
                agent="developer",  # Same agent can handle multiple tasks
                dependencies=["content"]
            ),
            Task(
                id="review",
                name="Review and Polish",
                goal="Review all documentation for accuracy and clarity",
                agent="reviewer",  # Single agent assignment
                dependencies=["content", "examples"]
            )
        ]
    )
    
    await project.set_plan(plan)
    
    # 3. Check project status
    summary = project.get_summary()
    print(f"\n📊 Project Summary:")
    print(f"   - Goal: {summary['goal']}")
    print(f"   - Total Tasks: {summary['tasks']['total']}")
    print(f"   - Team Size: {summary['team_size']} agents")
    
    # 4. Execute tasks (X agent handles this automatically)
    print("\n🔄 Executing project plan...")
    
    # Get tasks that can run in parallel
    parallel_tasks = await project.get_parallel_tasks(max_tasks=2)
    print(f"\n⚡ Can execute {len(parallel_tasks)} tasks in parallel:")
    for task in parallel_tasks:
                    print(f"   - {task.action} (assigned to: {task.assigned_to})")
    
    # 5. Conversational interaction with the project
    print("\n💬 Chatting with the project's X agent...")
    
    # User can adjust the plan or ask questions
    response = await x_agent.chat("Make sure the documentation includes interactive examples")
    print(f"X Agent: {response}")
    
    # User can request specific changes
    response = await x_agent.chat("Add a task for creating video tutorials")
    print(f"X Agent: {response}")
    
    # 6. Monitor progress
    print("\n📈 Checking project progress...")
    progress = project.plan.get_progress_summary()
    print(f"   - Progress: {progress['percentage']}%")
    print(f"   - Status breakdown: {progress['status_counts']}")
    
    # 7. Task-level details
    print("\n🔍 Task Details:")
    for task in project.plan.tasks:
        print(f"\n   Task: {task.action}")
        print(f"   - ID: {task.id}")
        print(f"   - Status: {task.status}")
        print(f"   - Agent: {task.assigned_to or 'Not assigned'}")
        print(f"   - Dependencies: {task.dependencies or 'None'}")
    
    # 8. Project completion
    if project.is_complete():
        print("\n✅ Project completed successfully!")
    else:
        print("\n⏳ Project is still in progress...")


async def example_parallel_execution():
    """
    Example showing how multiple tasks can be executed in parallel by different agents.
    """
    print("\n🎯 Example: Parallel Task Execution")
    print("=" * 50)
    
    # Create a project with tasks that can run in parallel
    project = await VibeX.start(
        project_id="competitor_analysis_project",
        goal="Analyze competitor websites",
        config_path="examples/analysis_team/config/team.yaml"
    )
    
    # Plan with parallel tasks
    plan = Plan(
        goal="Analyze competitor websites",
        tasks=[
            # These three tasks have no dependencies, so they can run in parallel
            Task(
                id="analyze_competitor_1",
                name="Analyze TechCorp Website",
                goal="Deep analysis of TechCorp's features and UX",
                agent="analyst_1"
            ),
            Task(
                id="analyze_competitor_2", 
                name="Analyze DataFlow Website",
                goal="Deep analysis of DataFlow's features and UX",
                agent="analyst_2"
            ),
            Task(
                id="analyze_competitor_3",
                name="Analyze CloudBase Website", 
                goal="Deep analysis of CloudBase's features and UX",
                agent="analyst_3"
            ),
            # This task depends on all analyses
            Task(
                id="synthesize",
                name="Create Comparison Report",
                goal="Synthesize findings into a comprehensive comparison",
                agent="synthesizer",
                dependencies=["analyze_competitor_1", "analyze_competitor_2", "analyze_competitor_3"]
            )
        ]
    )
    
    await project.set_plan(plan)
    
    # Get all tasks that can run in parallel
    parallel_tasks = await project.get_parallel_tasks()
    print(f"\n⚡ {len(parallel_tasks)} tasks can run in parallel:")
    for task in parallel_tasks:
        print(f"   - {task.action} → {task.assigned_to}")
    
    # In real execution, these would run concurrently
    print("\n🚀 All three analysis tasks would execute simultaneously by different agents")


if __name__ == "__main__":
    print("VibeX v2.0 - Project Architecture Demo")
    print("=====================================\n")
    
    # Run the main demo
    asyncio.run(main())
    
    # Run the parallel execution example
    asyncio.run(example_parallel_execution())