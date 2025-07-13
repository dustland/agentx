#!/usr/bin/env python3
"""
AutoWriter - Deep Research Writing System

A Google-inspired multi-agent system for generating comprehensive research reports.
Uses systematic decomposition and specialized agent orchestration.
"""

import asyncio
from pathlib import Path
from agentx import start_task

async def main():
    """
    This is the main entry point for the auto_writer example.
    It uses the new XAgent interface for conversational task management.
    """
    # Get the absolute path to the configuration file
    script_dir = Path(__file__).parent
    config_path = script_dir / "config" / "team.yaml"

    # The user's goal for the task
    prompt = """Generate a comprehensive and visually stunning report on the key trends shaping web development in 2025.

    The report must be an interactive HTML page that MATCHES OR EXCEEDS the quality demonstrated in samples/design_trends_report.html, featuring:
    - Modern design with Tailwind CSS and sophisticated color schemes using CSS custom properties
    - Interactive data visualizations using ECharts library
    - Professional typography with multiple Google Fonts (sans-serif + serif)
    - Advanced visual effects including glassmorphism, smooth animations, and micro-interactions
    - Responsive design with mobile-first approach
    - Card-based layouts with proper spacing and shadows

    Content must cover: new frontend frameworks (React, Vue, Svelte, SolidJS), meta-frameworks (Next.js, Astro, Qwik), backend technologies, AI integration in development, and modern UX/UI design paradigms.

    The final output must be professional, polished, and suitable for a C-suite audience, with quality rivaling top design agencies like those of Stripe, Vercel, or Linear.

    CRITICAL INSTRUCTION FOR WEB DESIGNER: HTML files must maintain proper document structure. Build the complete HTML content in memory first, then use write_file to save it. For very large HTML files, consider using JavaScript to load dynamic content or splitting into multiple pages. Never use append_file for HTML as it will corrupt the document structure."""

    print("🚀 AutoWriter - Starting comprehensive report generation...")
    print(f"📋 Task: {prompt[:100]}...")
    print("-" * 80)

    # Start the task with XAgent - creates a conversational interface
    x = await start_task(prompt, str(config_path))
    
    # Configure parallel execution for faster processing
    x.set_parallel_execution(enabled=True, max_concurrent=4)
    
    print(f"📋 Task ID: {x.task_id}")
    print(f"📁 Workspace: {x.workspace.get_workspace_path()}")
    print(f"⚡ Parallel execution: {x.get_parallel_settings()}")
    print("-" * 80)

    # Execute the task autonomously with parallel execution
    print("🤖 X: Starting the comprehensive report generation...")
    step_count = 0
    while not x.is_complete and step_count < 15:  # Safety limit
        response = await x.step()
        step_count += 1
        
        # Show parallel execution info
        parallel_count = response.count("✅")
        if parallel_count > 1:
            print(f"🔥 Step {step_count}: Executed {parallel_count} tasks in parallel")
        else:
            print(f"🔄 Step {step_count}: Sequential execution")
            
        print(f"🤖 X: {response[:200]}...")
        print("-" * 40)

    print("\n✅ TASK COMPLETE")
    print(f"📁 Workspace: {x.workspace.get_workspace_path()}")
    print(f"📋 Task ID: {x.task_id}")

    # Check for artifacts in the workspace
    workspace_path = x.workspace.get_workspace_path()
    artifacts_path = workspace_path / "artifacts"

    if artifacts_path.exists():
        artifact_files = list(artifacts_path.glob("*"))
        if artifact_files:
            print(f"📄 Generated artifacts:")
            for artifact in artifact_files:
                print(f"   - {artifact.name}")
        else:
            print("📄 No artifacts found in artifacts directory")
    else:
        print("📄 No artifacts directory found")

    print(f"\n🔗 Full workspace path: {workspace_path}")
    print("📁 Check the workspace directory for the generated report and artifacts.")

    # Demonstrate conversational interaction
    print("\n💬 You can also chat with X to modify the report:")
    print("   Example: x.chat('Make the report more visual with charts')")
    print("   Example: x.chat('Add a section about security trends')")
    print("   Example: x.chat('Generate an executive summary')")

if __name__ == "__main__":
    asyncio.run(main())
