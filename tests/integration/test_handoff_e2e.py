"""
End-to-end test for handoff functionality.
"""

import pytest
import asyncio
from pathlib import Path
import yaml

from agentx import start_task


@pytest.mark.asyncio
async def test_handoff_execution(tmp_path):
    """Test that handoffs work end-to-end in a real scenario."""

    # Create a simple team config with handoffs
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    team_config = {
        "name": "Test Handoff Team",
        "agents": [
            {
                "name": "starter",
                "description": "Starts the work",
                "system_message": "You start tasks. When done, say 'work is ready for finisher'.",
                "tools": ["file_write"]
            },
            {
                "name": "finisher",
                "description": "Finishes the work",
                "system_message": "You finish tasks that the starter began.",
                "tools": ["file_read", "file_write"]
            }
        ],
        "handoffs": [
            {
                "from_agent": "starter",
                "to_agent": "finisher",
                "condition": "work is ready for finisher",
                "priority": 1
            }
        ],
        "execution": {
            "initial_agent": "starter",
            "mode": "autonomous",
            "max_rounds": 5
        }
    }

    config_file = config_dir / "team.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(team_config, f)

    # Start a task that should trigger handoff
    x = await start_task(
        prompt="Create a file called test.txt with 'Hello' in it, then have it finished.",
        config_path=str(config_file)
    )

    # Execute steps
    steps_executed = 0
    max_steps = 10
    handoff_occurred = False

    while not x.is_complete and steps_executed < max_steps:
        response = await x.step()
        steps_executed += 1

        # Check if handoff occurred
        if "Handing off to finisher" in response:
            handoff_occurred = True
            break

    # Verify handoff happened
    assert handoff_occurred, "Handoff did not occur as expected"

    # Verify the plan was modified
    assert x.plan is not None
    assert len(x.plan.tasks) >= 2, "Plan should have at least 2 tasks after handoff"

    # Find the handoff task
    handoff_task = None
    for task in x.plan.tasks:
        if task.id.startswith("handoff_"):
            handoff_task = task
            break

    assert handoff_task is not None, "Handoff task not found in plan"
    assert handoff_task.agent == "finisher", "Handoff task should be assigned to finisher"


@pytest.mark.asyncio
async def test_no_handoff_when_condition_not_met(tmp_path):
    """Test that handoffs don't occur when conditions aren't met."""

    # Create config with handoff condition that won't be met
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    team_config = {
        "name": "Test No Handoff Team",
        "agents": [
            {
                "name": "worker",
                "description": "Does work",
                "system_message": "You do work but never mention errors.",
                "tools": ["file_write"]
            },
            {
                "name": "fixer",
                "description": "Fixes errors",
                "system_message": "You fix errors.",
                "tools": ["file_read", "file_write"]
            }
        ],
        "handoffs": [
            {
                "from_agent": "worker",
                "to_agent": "fixer",
                "condition": "error occurred and needs fixing",
                "priority": 1
            }
        ],
        "execution": {
            "initial_agent": "worker",
            "mode": "autonomous",
            "max_rounds": 3
        }
    }

    config_file = config_dir / "team.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(team_config, f)

    # Start a task that should NOT trigger handoff
    x = await start_task(
        prompt="Create a file called success.txt with 'All good' in it.",
        config_path=str(config_file)
    )

    # Execute steps
    steps_executed = 0
    max_steps = 5
    handoff_occurred = False

    while not x.is_complete and steps_executed < max_steps:
        response = await x.step()
        steps_executed += 1

        if "Handing off" in response:
            handoff_occurred = True

    # Verify no handoff happened
    assert not handoff_occurred, "Handoff should not have occurred"

    # Verify plan wasn't modified with handoff tasks
    if x.plan:
        for task in x.plan.tasks:
            assert not task.id.startswith("handoff_"), "No handoff tasks should be in plan"
