#!/usr/bin/env python3
"""
Parallel Auto Writer - Demonstrates parallel execution capabilities

This version uses the new parallel execution features to speed up
the research and writing phases by running independent tasks simultaneously.
"""

import asyncio
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from agentx import start_task

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

async def main():
    print("⚡ Parallel Auto Writer")
    print("=" * 60)

    # Debug: Check if API key is loaded
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        print(f"✅ DEEPSEEK_API_KEY loaded: {deepseek_key[:10]}...")
    else:
        print("❌ DEEPSEEK_API_KEY not found")

    # More complex task that benefits from parallel execution
    prompt = """Create a comprehensive comparison report of Python web frameworks for 2025.

Requirements:
- Research Flask, FastAPI, and Django frameworks  
- Create individual sections for each framework
- Include performance, features, and use cases
- Write an introduction and conclusion
- Convert to HTML with professional styling

Focus on creating a high-quality, well-researched document."""

    print("🚀 Starting parallel auto_writer...")
    start_time = time.time()
    
    x = await start_task(prompt, "config/team.yaml")

    workspace_path = Path(x.workspace.get_workspace_path())
    print(f"📁 Workspace: {workspace_path}")

    # Run through the complete workflow with parallel execution
    step_count = 0
    max_steps = 10  # Allow more steps for comprehensive report

    while not x.is_complete and step_count < max_steps:
        print(f"\n⚡ Parallel Step {step_count + 1}/{max_steps}")
        step_start_time = time.time()
        
        # Use parallel execution for faster processing
        response = await x.step_parallel(max_concurrent=4)
        
        step_time = time.time() - step_start_time
        step_count += 1

        # Count parallel tasks executed
        parallel_count = response.count("✅")
        if parallel_count > 1:
            print(f"🔥 Executed {parallel_count} tasks in parallel ({step_time:.1f}s)")
        else:
            print(f"🔄 Executed 1 task ({step_time:.1f}s)")

        # Show abbreviated response
        print(f"📝 Response: {response[:200]}...")

        # Check current files
        artifacts_path = workspace_path / "artifacts"
        if artifacts_path.exists():
            artifacts = list(artifacts_path.glob("*.md")) + list(artifacts_path.glob("*.html"))
            if artifacts:
                print(f"📁 Current files: {len(artifacts)}")
                
                # Show research files
                research_files = [f for f in artifacts if "research" in f.name.lower()]
                if research_files:
                    print(f"   🔍 Research files: {len(research_files)}")
                
                # Show section files  
                section_files = [f for f in artifacts if "section" in f.name.lower()]
                if section_files:
                    print(f"   📄 Section files: {len(section_files)}")
                
                # Show final outputs
                html_files = [f for f in artifacts if f.suffix == ".html"]
                if html_files:
                    for html_file in html_files[-1:]:  # Show latest HTML
                        size = html_file.stat().st_size
                        print(f"   🌐 {html_file.name} ({size:,} bytes)")

        # Stop early if we have a substantial HTML file
        if artifacts_path.exists():
            html_files = list(artifacts_path.glob("*.html"))
            large_html = [f for f in html_files if f.stat().st_size > 10000]
            if large_html:
                print("✅ Large HTML file detected - workflow likely complete!")
                break

    total_time = time.time() - start_time
    
    print(f"\n🎉 Parallel execution completed!")
    print(f"⏱️  Total time: {total_time:.1f} seconds")
    print(f"📊 Steps executed: {step_count}")
    print(f"⚡ Average time per step: {total_time/step_count:.1f}s")
    
    # Final file summary
    if artifacts_path.exists():
        all_files = list(artifacts_path.glob("*"))
        total_size = sum(f.stat().st_size for f in all_files if f.is_file())
        print(f"📁 Final workspace: {len(all_files)} files, {total_size:,} bytes total")
        
        # Show key outputs
        html_files = [f for f in all_files if f.suffix == ".html"]
        if html_files:
            largest_html = max(html_files, key=lambda f: f.stat().st_size)
            print(f"🌐 Main output: {largest_html.name} ({largest_html.stat().st_size:,} bytes)")

if __name__ == "__main__":
    asyncio.run(main())