#!/usr/bin/env python3
"""
Test comprehensive writing - ensure the writer produces FULL reports
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from agentx import start_task

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

async def main():
    print("📊 Testing Comprehensive Writing")
    print("=" * 60)

    # More explicit prompt requiring comprehensive output
    prompt = """Create a COMPREHENSIVE, IN-DEPTH report comparing Flask vs FastAPI for Python web development in 2025.

REQUIREMENTS:
1. The final report must be AT LEAST 3000 words (approximately 20,000 characters)
2. Include detailed sections on:
   - Executive Summary (500+ words)
   - Technical Architecture Comparison (800+ words)
   - Performance Benchmarks and Analysis (600+ words)
   - Developer Experience Deep Dive (600+ words)
   - Ecosystem and Community Analysis (500+ words)
   - Use Case Scenarios with Code Examples (800+ words)
   - Migration Guide (500+ words)
   - Future Outlook and Predictions (500+ words)
   - Comprehensive Recommendations (500+ words)

3. Each section must include:
   - Specific examples
   - Data and statistics
   - Code snippets where relevant
   - Expert quotes from research
   - Detailed analysis, not summaries

4. The HTML output must be professionally styled with:
   - Interactive table of contents
   - Syntax highlighting for code
   - Visual charts/comparisons
   - Professional typography
   - Mobile responsive design

DO NOT create brief summaries. Create a FULL, COMPREHENSIVE report that would be worth $5000 from a consulting firm."""

    print("🚀 Starting comprehensive auto_writer...")
    x = await start_task(prompt, "config/team.yaml")

    workspace_path = Path(x.workspace.get_workspace_path())
    print(f"📁 Workspace: {workspace_path}")

    # Monitor the process
    step_count = 0
    max_steps = 12  # Allow more steps for comprehensive work

    while not x.is_complete and step_count < max_steps:
        print(f"\n🔄 Step {step_count + 1}/{max_steps}")
        response = await x.step()
        step_count += 1

        # Show response
        print(f"Response: {response[:200]}...")

        # Monitor file sizes
        artifacts = list((workspace_path / "artifacts").glob("*.md")) + list((workspace_path / "artifacts").glob("*.html"))
        if artifacts:
            print(f"\n📁 Current files:")
            for f in sorted(artifacts, key=lambda x: x.stat().st_size, reverse=True)[:5]:
                size = f.stat().st_size
                if size > 20000:
                    status = "✅ COMPREHENSIVE"
                elif size > 10000:
                    status = "🔶 GOOD SIZE"
                elif size > 5000:
                    status = "⚠️ MODERATE"
                else:
                    status = "❌ TOO SMALL"
                print(f"   {status} {f.name} ({size:,} bytes)")

    # Final analysis
    print(f"\n\n📊 FINAL QUALITY ASSESSMENT:")
    print(f"Steps taken: {step_count}")

    # Check markdown quality
    md_files = list((workspace_path / "artifacts").glob("*report*.md")) + list((workspace_path / "artifacts").glob("*comparison*.md"))
    if md_files:
        largest_md = max(md_files, key=lambda x: x.stat().st_size)
        md_size = largest_md.stat().st_size
        print(f"\n📝 Markdown Report: {largest_md.name}")
        print(f"Size: {md_size:,} bytes")
        if md_size > 20000:
            print("✅ EXCELLENT - Truly comprehensive report")
        elif md_size > 10000:
            print("🔶 GOOD - Decent depth")
        elif md_size > 5000:
            print("⚠️ MEDIOCRE - Still too brief")
        else:
            print("❌ POOR - This is just a summary!")

        # Show character count
        content = largest_md.read_text()
        word_count = len(content.split())
        print(f"Word count: {word_count:,}")
        print(f"Character count: {len(content):,}")

    # Check HTML quality
    html_files = list((workspace_path / "artifacts").glob("*.html"))
    if html_files:
        html_file = html_files[0]
        html_size = html_file.stat().st_size
        print(f"\n🌐 HTML Report: {html_file.name}")
        print(f"Size: {html_size:,} bytes")
        if html_size > 30000:
            print("✅ EXCELLENT - Professional, styled report")
        elif html_size > 15000:
            print("🔶 GOOD - Well-styled")
        elif html_size > 8000:
            print("⚠️ MEDIOCRE - Basic styling")
        else:
            print("❌ POOR - Minimal effort")

if __name__ == "__main__":
    asyncio.run(main())
