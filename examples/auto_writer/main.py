#!/usr/bin/env python3
"""
AutoWriter - Deep Research Writing System

A Google-inspired multi-agent system for generating comprehensive research reports.
Uses systematic decomposition and specialized agent orchestration.
"""

import asyncio
from pathlib import Path
from datetime import datetime
import time
from vibex import VibeX

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
    
    # Record start time
    start_time = time.time()
    start_datetime = datetime.now()

    # Start the project with VibeX
    x = await VibeX.start(
        project_id="auto_writer_project",
        goal=prompt,
        config_path=str(config_path),
    )
    
    # Configure parallel execution for faster processing
    x.set_parallel_execution(enabled=True, max_concurrent=4)
    
    print(f"📋 Project ID: {x.project_id}")
    print(f"📁 Project Space: {x.workspace.get_path()}")
    print(f"⚡ Parallel execution: {x.get_parallel_settings()}")
    print("-" * 80)

    # Execute the project autonomously with parallel execution
    print("🤖 X: Starting the comprehensive report generation...")
    step_count = 0
    while not x.is_complete() and step_count < 15:  # Safety limit
        response = await x.step()
        step_count += 1
        
        # Show parallel execution info
        parallel_count = 0
        if isinstance(response, list):
            parallel_count = len(response)

        if parallel_count > 1:
            print(f"🔥 Step {step_count}: Executed {parallel_count} tasks in parallel")
        else:
            print(f"🔄 Step {step_count}: Sequential execution")
            
        print(f"🤖 X: {str(response)[:200]}...")
        print("-" * 40)

    # Record end time
    end_time = time.time()
    end_datetime = datetime.now()
    total_duration = end_time - start_time

    # Check for artifacts in the workspace
    workspace_path = x.workspace.get_path()
    artifacts_path = workspace_path / "artifacts"
    artifact_files = list(artifacts_path.glob("*")) if artifacts_path.exists() else []
    artifact_count = len(artifact_files)

    # Print comprehensive execution summary
    print("\n" + "=" * 80)
    print("✅ PROJECT COMPLETE - EXECUTION SUMMARY")
    print("=" * 80)
    print(f"📋 Project ID: {x.project_id}")
    print(f"📁 Workspace: {workspace_path}")
    print("-" * 80)
    print(f"📅 Start Time: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 End Time: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
    print("-" * 80)
    print(f"📊 Steps Executed: {step_count}")
    print(f"⚡ Avg Time/Step: {total_duration/step_count:.1f}s" if step_count > 0 else "")
    print(f"🚀 Performance: {step_count / (total_duration/60):.1f} steps/minute" if total_duration > 0 else "")
    print("-" * 80)
    print(f"📄 Artifacts Generated: {artifact_count} files")
    if artifact_files:
        for artifact in artifact_files[:5]:  # Show first 5 artifacts
            print(f"   • {artifact.name}")
        if artifact_count > 5:
            print(f"   • ... and {artifact_count - 5} more files")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
