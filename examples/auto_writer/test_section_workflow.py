#!/usr/bin/env python3
"""
Test Section-Based Writing Workflow

Tests the new workflow where:
1. Writer creates individual sections with proper naming
2. Writer merges sections into draft
3. Reviewer polishes draft into final document
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from agentx import start_task
import json

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

async def main():
    print("📝 Testing Section-Based Writing Workflow")
    print("=" * 60)
    
    # Prompt that should trigger section-based writing
    prompt = """Create a technical comparison report: PostgreSQL vs MySQL for enterprise applications.
    
    The report should have these distinct sections:
    1. Executive Summary
    2. Performance Comparison
    3. Feature Analysis
    4. Enterprise Use Cases
    5. Recommendations
    
    Each section should be comprehensive with real data and examples."""
    
    print("🚀 Starting section-based auto_writer...")
    x = await start_task(prompt, "config/team.yaml")
    
    workspace_path = Path(x.workspace.get_workspace_path())
    artifacts_path = workspace_path / "artifacts"
    print(f"📁 Workspace: {workspace_path}")
    
    # Monitor the workflow
    step_count = 0
    max_steps = 10
    section_files_created = False
    draft_created = False
    polished_created = False
    
    while not x.is_complete and step_count < max_steps:
        print(f"\n🔄 Step {step_count + 1}/{max_steps}")
        response = await x.step()
        step_count += 1
        
        # Monitor agent activity
        current_agent = "Unknown"
        if "researcher" in response.lower():
            current_agent = "Researcher"
        elif "writer" in response.lower():
            current_agent = "Writer"
        elif "reviewer" in response.lower():
            current_agent = "Reviewer"
        
        print(f"👤 Active Agent: {current_agent}")
        print(f"Response preview: {response[:150]}...")
        
        # Check for section files
        if artifacts_path.exists():
            section_files = list(artifacts_path.glob("section_*.md"))
            if section_files and not section_files_created:
                section_files_created = True
                print(f"\n✅ SECTION FILES CREATED:")
                for f in sorted(section_files):
                    print(f"   📄 {f.name} ({f.stat().st_size:,} bytes)")
            
            # Check for draft
            draft_files = list(artifacts_path.glob("*draft*.md"))
            if draft_files and not draft_created:
                draft_created = True
                print(f"\n✅ DRAFT CREATED:")
                for f in draft_files:
                    print(f"   📄 {f.name} ({f.stat().st_size:,} bytes)")
            
            # Check for polished version
            polished_files = list(artifacts_path.glob("*polished*.md")) + list(artifacts_path.glob("*final*.md"))
            if polished_files and not polished_created:
                polished_created = True
                print(f"\n✅ POLISHED VERSION CREATED:")
                for f in polished_files:
                    print(f"   📄 {f.name} ({f.stat().st_size:,} bytes)")
    
    # Final validation
    print(f"\n\n📊 WORKFLOW VALIDATION:")
    print(f"Total steps: {step_count}")
    
    # Validate section files
    if artifacts_path.exists():
        section_files = sorted(list(artifacts_path.glob("section_*.md")))
        
        if section_files:
            print(f"\n✅ Section Files ({len(section_files)} found):")
            expected_sections = ["summary", "performance", "feature", "use_cases", "recommendations"]
            
            for i, f in enumerate(section_files):
                # Check naming convention
                expected_pattern = f"section_{i+1:02d}_"
                if expected_pattern in f.name:
                    print(f"   ✅ {f.name} - Correct naming pattern")
                else:
                    print(f"   ❌ {f.name} - Wrong pattern (expected {expected_pattern})")
                
                # Check content
                content = f.read_text()
                if len(content) > 1000:
                    print(f"      ✅ Good content size: {len(content):,} chars")
                else:
                    print(f"      ⚠️  Small content: {len(content):,} chars")
        else:
            print("\n❌ No section files created!")
    
    # Validate merge
    draft_files = list(artifacts_path.glob("*draft*.md"))
    if draft_files:
        draft = draft_files[0]
        content = draft.read_text()
        print(f"\n✅ Draft Document:")
        print(f"   📄 {draft.name} ({len(content):,} chars)")
        
        # Check if all sections were merged
        section_count = content.count("# ")  # Count major headings
        print(f"   📊 Sections found: {section_count}")
    else:
        print("\n❌ No draft document created!")
    
    # Validate polish
    final_files = list(artifacts_path.glob("*polished*.md")) + list(artifacts_path.glob("*final*.md"))
    if final_files:
        final = final_files[0]
        content = final.read_text()
        print(f"\n✅ Final Document:")
        print(f"   📄 {final.name} ({len(content):,} chars)")
        
        # Compare with draft
        if draft_files:
            draft_content = draft_files[0].read_text()
            if len(content) != len(draft_content):
                print(f"   ✅ Document was polished (size changed)")
            else:
                print(f"   ⚠️  Document may not have been polished")
    else:
        print("\n❌ No polished document created!")
    
    # Summary
    print("\n📋 WORKFLOW SUMMARY:")
    print(f"{'✅' if section_files_created else '❌'} Section files created with proper naming")
    print(f"{'✅' if draft_created else '❌'} Draft document created from sections")
    print(f"{'✅' if polished_created else '❌'} Final polished document created")
    
    if section_files_created and draft_created and polished_created:
        print("\n🎉 SUCCESS: Complete section-based workflow executed!")
    else:
        print("\n⚠️  INCOMPLETE: Some workflow steps were missed")

if __name__ == "__main__":
    asyncio.run(main())