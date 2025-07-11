"""
AgentX Debugging CLI

Provides step-through debugging capabilities for AgentX tasks including
breakpoints, state inspection, and context modification.
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ..core.xagent import XAgent
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DebugSession:
    """Interactive debugging session for AgentX tasks."""

    def __init__(self, xagent: XAgent):
        self.xagent = xagent
        self.task_id = xagent.task_id
        self.running = True

    async def start(self):
        """Start the interactive debugging session."""
        print(f"🐛 AgentX Debug Session - Task: {self.task_id}")
        print("=" * 60)

        # Show initial state
        await self._show_status()

        print("\n💡 Debug Commands:")
        print("  status     - Show current task status")
        print("  inspect    - Inspect detailed task state")
        print("  history    - Show conversation history")
        print("  step       - Execute one step")
        print("  chat       - Send a chat message")
        print("  plan       - Show current plan")
        print("  workspace  - List workspace files")
        print("  quit       - Exit debug session")
        print()

        # Interactive loop
        while self.running:
            try:
                command = input("debug> ").strip().lower()
                await self._handle_command(command)
            except KeyboardInterrupt:
                print("\n🛑 Debug session interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def _handle_command(self, command: str):
        """Handle debug commands."""
        parts = command.split()
        if not parts:
            return

        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "quit" or cmd == "exit":
            self.running = False
            print("👋 Exiting debug session")

        elif cmd == "status":
            await self._show_status()

        elif cmd == "inspect":
            await self._inspect_state()

        elif cmd == "history":
            await self._show_history(int(args[0]) if args else 10)

        elif cmd == "step":
            await self._step_execution()

        elif cmd == "chat":
            if not args:
                print("Usage: chat <message>")
                return
            message = " ".join(args)
            await self._chat_message(message)

        elif cmd == "plan":
            await self._show_plan()

        elif cmd == "workspace":
            await self._list_workspace()

        elif cmd == "help":
            await self._show_help()

        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")

    async def _show_status(self):
        """Show current task status."""
        try:
            print(f"📊 Task Status: {self.task_id}")
            print(f"  Complete: {self.xagent.is_complete}")
            print(f"  History Length: {len(self.xagent.history.messages)}")
            print(f"  Current Plan: {'Yes' if self.xagent.current_plan else 'No'}")

            if self.xagent.current_plan:
                completed = sum(1 for task in self.xagent.current_plan.tasks if task.status == "completed")
                total = len(self.xagent.current_plan.tasks)
                print(f"  Plan Progress: {completed}/{total} tasks completed")

            workspace_path = self.xagent.workspace.get_workspace_path()
            artifacts = list(workspace_path.glob("**/*"))
            print(f"  Workspace Files: {len([f for f in artifacts if f.is_file()])}")
        except Exception as e:
            print(f"❌ Error getting status: {e}")

    async def _inspect_state(self):
        """Show detailed task state inspection."""
        try:
            state = {
                "task_id": self.task_id,
                "is_complete": self.xagent.is_complete,
                "specialist_agents": list(self.xagent.specialist_agents.keys()),
                "workspace_path": str(self.xagent.workspace.get_workspace_path()),
                "plan_initialized": self.xagent._plan_initialized,
                "conversation_history_length": len(self.xagent.conversation_history),
                "message_history_length": len(self.xagent.history.messages),
            }

            if self.xagent.current_plan:
                state["plan"] = {
                    "goal": self.xagent.current_plan.goal,
                    "tasks": [
                        {
                            "id": task.id,
                            "name": task.name,
                            "status": task.status,
                            "agent": task.agent
                        }
                        for task in self.xagent.current_plan.tasks
                    ]
                }

            print("🔍 Detailed Task Inspection:")
            print(json.dumps(state, indent=2, default=str))
        except Exception as e:
            print(f"❌ Error inspecting state: {e}")

    async def _show_history(self, limit: int = 10):
        """Show conversation history."""
        try:
            messages = self.xagent.history.messages

            if not messages:
                print("📜 No conversation history yet")
                return

            history = messages[-limit:] if limit > 0 else messages

            print(f"📜 Conversation History (last {len(history)} messages):")
            for i, msg in enumerate(history, 1):
                timestamp = msg.timestamp.strftime("%H:%M:%S") if hasattr(msg, 'timestamp') and msg.timestamp else "N/A"
                role = msg.role if hasattr(msg, 'role') else "unknown"
                print(f"  {i}. [{timestamp}] {role}:")

                content = msg.content if hasattr(msg, 'content') else str(msg)
                if len(content) > 100:
                    content = content[:100] + "..."
                print(f"     {content}")
                print()
        except Exception as e:
            print(f"❌ Error showing history: {e}")

    async def _chat_message(self, message: str):
        """Send a chat message to XAgent."""
        try:
            print(f"💬 Sending: {message}")
            response = await self.xagent.chat(message)
            print(f"🤖 X: {response.text}")

            if response.artifacts:
                print(f"📎 Artifacts: {len(response.artifacts)} created/modified")
        except Exception as e:
            print(f"❌ Error chatting: {e}")

    async def _show_plan(self):
        """Show the current execution plan."""
        try:
            if not self.xagent.current_plan:
                print("📋 No plan created yet")
                return

            plan = self.xagent.current_plan
            print(f"📋 Execution Plan: {plan.goal}")
            print("Tasks:")

            for i, task in enumerate(plan.tasks, 1):
                status_icon = "✅" if task.status == "completed" else "⏳" if task.status == "in_progress" else "⭕"
                print(f"  {i}. {status_icon} {task.name}")
                print(f"     Agent: {task.agent}")
                print(f"     Goal: {task.goal}")
                if task.dependencies:
                    print(f"     Dependencies: {', '.join(task.dependencies)}")
                print()
        except Exception as e:
            print(f"❌ Error showing plan: {e}")

    async def _list_workspace(self):
        """List files in the workspace."""
        try:
            workspace_path = self.xagent.workspace.get_workspace_path()
            print(f"📁 Workspace: {workspace_path}")

            # List all files recursively
            files = list(workspace_path.rglob("*"))
            files = [f for f in files if f.is_file()]

            if not files:
                print("  (empty)")
            else:
                for file in sorted(files):
                    relative_path = file.relative_to(workspace_path)
                    size = file.stat().st_size
                    print(f"  📄 {relative_path} ({size} bytes)")
        except Exception as e:
            print(f"❌ Error listing workspace: {e}")

    async def _step_execution(self):
        """Execute one step."""
        try:
            if self.xagent.is_complete:
                print("✅ Task is already complete")
                return

            print("⏭️ Executing one step...")
            response = await self.xagent.step()
            print(f"📝 Step result: {response}")

            # Show updated status
            await self._show_status()
        except Exception as e:
            print(f"❌ Error stepping: {e}")



    async def _show_help(self):
        """Show help information."""
        print("🐛 AgentX Debug Commands:")
        print("  status         - Show current task status")
        print("  inspect        - Show detailed task state")
        print("  history [N]    - Show last N conversation messages (default: 10)")
        print("  step           - Execute one step of the plan")
        print("  chat MESSAGE   - Send a chat message to X")
        print("  plan           - Show current execution plan")
        print("  workspace      - List files in workspace")
        print("  quit           - Exit debug session")


async def debug_task(team_config_path: str, task_id: Optional[str] = None, workspace_dir: Optional[str] = None):
    """Start a debugging session for a task."""
    try:
        # Check if we're loading an existing task
        if workspace_dir:
            workspace_path = Path(workspace_dir)
            if not workspace_path.exists():
                print(f"❌ Workspace not found: {workspace_dir}")
                return

            # Create XAgent with existing workspace
            xagent = XAgent(
                team_config=team_config_path,
                task_id=task_id,
                workspace_dir=workspace_path
            )
            print(f"📂 Loaded task from workspace: {workspace_path}")
        else:
            # Create new XAgent
            xagent = XAgent(
                team_config=team_config_path,
                task_id=task_id
            )
            print(f"🆕 Created new task: {xagent.task_id}")

        # Start debug session
        debug_session = DebugSession(xagent)
        await debug_session.start()

    except Exception as e:
        print(f"❌ Error starting debug session: {e}")
        logger.exception("Debug session error")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m agentx.cli.debug <team_config_path> [task_id] [workspace_dir]")
        sys.exit(1)

    team_config_path = sys.argv[1]
    task_id = sys.argv[2] if len(sys.argv) > 2 else None
    workspace_dir = sys.argv[3] if len(sys.argv) > 3 else None

    asyncio.run(debug_task(team_config_path, task_id, workspace_dir))
