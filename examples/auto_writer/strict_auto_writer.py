#!/usr/bin/env python3
"""
Strict Auto Writer - Each step must succeed before continuing
NO FALLBACKS, NO FAKE OUTPUTS
"""

import asyncio
import sys
from pathlib import Path
from agentx import start_task
from agentx.storage.factory import StorageFactory
from agentx.builtin_tools.search import SearchTool
from agentx.builtin_tools.web import WebTool

async def main():
    """Run strict auto writer with validation at each step."""

    print("🚀 STRICT Auto Writer - No Fallbacks, Real Results Only")
    print("=" * 70)

    # Step 1: Initialize workspace
    print("\n📁 STEP 1: Initialize Workspace")
    workspace_path = Path("./strict_workspace")
    try:
        workspace = StorageFactory.create_workspace_storage(str(workspace_path))
        artifacts_path = workspace_path / "artifacts"
        artifacts_path.mkdir(exist_ok=True)
        print("✅ Workspace initialized")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        sys.exit(1)

    # Step 2: Initialize tools with workspace
    print("\n🔧 STEP 2: Initialize Tools")
    try:
        search_tool = SearchTool(workspace_storage=workspace)
        web_tool = WebTool(workspace_storage=workspace)
        print(f"✅ Tools initialized with workspace: {workspace}")
        print(f"   Search tool workspace: {getattr(search_tool, 'workspace', 'None')}")
        print(f"   Web tool workspace: {getattr(web_tool, 'workspace', 'None')}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        sys.exit(1)

    # Step 3: Search and extract content
    print("\n🔍 STEP 3: Search and Extract Content")
    try:
        # Use search_and_extract which handles everything
        result = await search_tool.search_and_extract(
            queries=[
                "web development trends 2025 medium dev.to",
                "React Vue Svelte comparison 2025",
                "AI integration web development 2025"
            ],
            max_results=10,  # More results to find good URLs
            max_extract=5    # Extract from top 5
        )

        if not result.success:
            raise Exception(f"Search failed: {result.error}")

        # Check what's in the result metadata
        print(f"\nExtraction metadata: {result.metadata}")

        # Also check artifacts directory immediately
        print(f"\nChecking artifacts directory...")
        if artifacts_path.exists():
            files = list(artifacts_path.glob("*.md"))
            print(f"Found {len(files)} MD files in artifacts:")
            for f in files[:5]:
                print(f"  - {f.name} ({f.stat().st_size} bytes)")

        # Verify files were actually saved
        saved_files = []

        # Files are already saved! Just get them from the artifacts directory
        for f in artifacts_path.glob("*.md"):
            if not f.name.startswith('.'):
                size = f.stat().st_size
                saved_files.append((f.name, size))
                print(f"✅ Found: {f.name} ({size} bytes)")

        if not saved_files:
            raise Exception("No files were saved!")

        # Count how many are substantial
        substantial_files = [f for f in saved_files if f[1] > 5000]
        if len(substantial_files) < 5:
            raise Exception(f"Not enough substantial files: only {len(substantial_files)} files > 5KB")

        print(f"✅ Extracted and saved {len(saved_files)} files ({len(substantial_files)} substantial)")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        sys.exit(1)

    # Step 4: Verify content quality
    print("\n📝 STEP 4: Verify Content Quality")
    try:
        # Calculate total content size
        total_size = sum(f[1] for f in saved_files)
        print(f"✅ Total content extracted: {total_size:,} bytes")

        if total_size < 50000:  # 50KB minimum
            raise Exception(f"Insufficient content: only {total_size} bytes")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        sys.exit(1)

    # Step 5: Use AgentX to create the report
    print("\n🤖 STEP 5: Generate Report with AgentX")
    prompt = f"""Create a comprehensive HTML report on web development trends in 2025.

IMPORTANT:
- Read the extracted content files to gather information
- The report must be comprehensive and detailed
- Include specific statistics and quotes from the research
- Create a visually stunning HTML with modern CSS
- Save as web_dev_trends_2025_report.html

Available research files (use read_file with these exact filenames):
{chr(10).join([f"- {f[0]}" for f in saved_files])}

DO NOT create fake content. Use only the actual research provided."""

    try:
        x = await start_task(prompt, "config/team.yaml")

        # Let it run
        while not x.is_complete:
            response = await x.step()
            print(f".")

        # Verify HTML was created
        html_file = artifacts_path / "web_dev_trends_2025_report.html"
        if not html_file.exists():
            # Try without artifacts path
            workspace_files = list(workspace_path.glob("*.html"))
            if workspace_files:
                html_file = workspace_files[0]
                html_size = html_file.stat().st_size
            else:
                raise Exception("No HTML report was created!")
        else:
            html_size = html_file.stat().st_size

        if html_size < 10000:  # 10KB minimum for HTML
            raise Exception(f"HTML too small: only {html_size} bytes")

        print(f"\n✅ HTML report created: {html_size} bytes")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        sys.exit(1)

    print("\n✅ SUCCESS! All steps completed.")
    print(f"📁 Results in: {workspace_path}")

if __name__ == "__main__":
    asyncio.run(main())
