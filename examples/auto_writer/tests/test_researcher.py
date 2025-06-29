import asyncio
import os
import sys
import shutil

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')))

from agentx import execute_task

# The config file for this specific test
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'configs', 'researcher_config.yaml'))
WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), '..', 'workspace')


async def test_researcher():
    """Tests the Researcher agent's ability to create and update a plan, generate artifacts, and write a final brief."""
    test_prompt = "Generate a research brief on the topic: 'The impact of AI on the US job market'."
    
    print("🧪 Testing Researcher...")
    print("=" * 50)
    
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)

    task = await execute_task(
        prompt=test_prompt,
        config_path=CONFIG_PATH,
        stream=False,
    )
    
    task_id = task.id
    task_workspace = os.path.join(WORKSPACE_DIR, task_id)
    artifacts_dir = os.path.join(task_workspace, "artifacts")

    print(f" Agent 'Researcher' completed. Task ID: {task_id}")
    print(f" Verifying outputs in: {task_workspace}")

    # 1. Check for the final research brief
    final_brief_path = os.path.join(task_workspace, "research_brief.md")
    assert os.path.exists(final_brief_path), f"Final research_brief.md not found in {task_workspace}"
    print("  ✅ Found final file: research_brief.md")

    # 2. Check that the artifacts directory was created
    assert os.path.exists(artifacts_dir), f"Artifacts directory not created: {artifacts_dir}"
    print(f"  ✅ Found artifacts directory: {artifacts_dir}")

    # 3. Check for the research plan
    plan_path = os.path.join(artifacts_dir, "research_plan.md")
    assert os.path.exists(plan_path), f"research_plan.md not found in {artifacts_dir}"
    print("  ✅ Found plan file: artifacts/research_plan.md")

    # 4. Check that the plan is marked as complete
    with open(plan_path, 'r') as f:
        plan_content = f.read()
        assert '[-]' not in plan_content, "Found incomplete tasks '[ ]' in the final research plan."
        assert '[x]' in plan_content, "Did not find any completed tasks '[x]' in the final research plan."
    print("  ✅ Research plan is marked as complete.")

    # 5. Check for at least one search result and one extracted content file
    artifacts_content = os.listdir(artifacts_dir)
    has_search_result = any(f.startswith("search_results_") for f in artifacts_content)
    has_extracted_content = any(f.startswith("extracted_content_") for f in artifacts_content)

    assert has_search_result, "No search result files found in artifacts directory."
    print("  ✅ Found at least one search_results file.")
    
    assert has_extracted_content, "No extracted content files found in artifacts directory."
    print("  ✅ Found at least one extracted_content file.")

    print(f"✅ Test for Researcher passed!")
    print("=" * 50)
    
    # Clean up workspace after test
    shutil.rmtree(WORKSPACE_DIR)


if __name__ == "__main__":
    # Change CWD to the parent directory of the script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(test_researcher()) 