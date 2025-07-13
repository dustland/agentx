#!/usr/bin/env python3
"""
Quick Auto Writer - Tests the complete flow with minimal content
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from agentx import start_task

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

async def main():
    print("⚡ Quick Auto Writer Test")
    print("=" * 60)

    # Debug: Check if API key is loaded
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        print(f"✅ DEEPSEEK_API_KEY loaded: {deepseek_key[:10]}...")
    else:
        print("❌ DEEPSEEK_API_KEY not found")

    # Much simpler, focused task to avoid timeouts
    prompt = """Create a focused report comparing Flask vs FastAPI for Python web development in 2025.

Requirements:
- Research both frameworks briefly
- Create a professional markdown document
- Convert to HTML with modern styling

Keep it concise but high-quality."""

    print("🚀 Starting quick auto_writer...")
    x = await start_task(prompt, "config/team.yaml")

    workspace_path = Path(x.workspace.get_workspace_path())
    print(f"📁 Workspace: {workspace_path}")

    # Run through the complete workflow
    step_count = 0
    max_steps = 8  # Limit to prevent infinite loops

    while not x.is_complete and step_count < max_steps:
        print(f"\n🔄 Step {step_count + 1}/{max_steps}")
        response = await x.step()
        step_count += 1

        # Show abbreviated response
        print(f"Response: {response[:150]}...")

        # Check current files
        artifacts = list((workspace_path / "artifacts").glob("*.md")) + list((workspace_path / "artifacts").glob("*.html"))
        if artifacts:
            print(f"📁 Current files: {len(artifacts)}")
            for f in artifacts[-2:]:  # Show last 2 files
                size = f.stat().st_size
                status = "✅" if size > 1000 else "⚠️"
                print(f"   {status} {f.name} ({size:,} bytes)")

    # Final analysis
    print(f"\n📊 Final Results:")
    print(f"Completed: {x.is_complete}")
    print(f"Steps taken: {step_count}")

    artifacts = list((workspace_path / "artifacts").glob("*"))
    total_files = len(artifacts)
    md_files = len(list((workspace_path / "artifacts").glob("*.md")))
    html_files = len(list((workspace_path / "artifacts").glob("*.html")))

    print(f"Total files: {total_files}")
    print(f"Markdown files: {md_files}")
    print(f"HTML files: {html_files}")

    # Check for final HTML
    html_files_list = list((workspace_path / "artifacts").glob("*.html"))
    if html_files_list:
        html_file = html_files_list[0]
        size = html_file.stat().st_size
        print(f"\n🎉 HTML REPORT CREATED!")
        print(f"File: {html_file.name}")
        print(f"Size: {size:,} bytes")

        if size > 10000:
            print("✅ Good size - likely comprehensive")
        elif size > 3000:
            print("⚠️ Medium size - may need improvement")
        else:
            print("❌ Small size - likely incomplete")

        # Show HTML preview
        try:
            content = html_file.read_text()
            print(f"\nHTML preview (first 300 chars):")
            print("-" * 40)
            print(content[:300] + "...")
            print("-" * 40)
        except:
            print("Could not read HTML file")
    else:
        print("\n❌ No HTML report found")

        # Check what we do have
        print("\nFiles created:")
        for f in artifacts:
            if f.is_file():
                size = f.stat().st_size
                print(f"  - {f.name} ({size:,} bytes)")

if __name__ == "__main__":
    asyncio.run(main())
