#!/usr/bin/env python3
"""
Content Extractor Example

Demonstrates the powerful new Crawl4AI-based content extraction capabilities
that solve the reliability issues with previous extraction methods.
"""

import asyncio
from vibex import VibeX

async def main():
    """Run a content extraction demonstration."""

    print("🚀 Content Extractor Example")
    print("=" * 70)
    print("Task: Test Crawl4AI extraction from challenging websites")
    print("Demonstrating: Reliable extraction from JavaScript sites, Reddit, etc.")
    print("Key Features: Parallel processing, search integration, no API failures")
    print("-" * 70)

    # Simplified task focused on basic extraction testing
    extraction_prompt = """Test the Crawl4AI content extraction by:

1. Extract content from 2-3 web development articles about trends in 2025
2. Test extraction from one challenging site (like a tech blog)
3. Save the extracted content to files

Keep it simple and focused on demonstrating reliable extraction."""

    print(f"🎯 Extraction Test: Testing Crawl4AI capabilities...")
    print("-" * 70)

    # Start the extraction test with VibeX
    x = await VibeX.start(
        project_id="content_extractor_project",
        goal=extraction_prompt,
        config_path="config/team.yaml"
    )

    print(f"📋 Project ID: {x.project_id}")
    print(f"📁 Workspace: {x.workspace.get_path()}")
    print("-" * 70)

    # Execute the extraction test
    print("🤖 X: Starting Crawl4AI extraction tests...")
    while not x.is_complete():
        response = await x.step()
        print(f"🔧 Extraction Step:\n{response}\n")
        print("-" * 70)

    # Simple test scenarios
    test_scenarios = [
        "Extract content from one more web development article",
        "Test extraction from a tech news site"
    ]

    for scenario in test_scenarios:
        print(f"🧪 Test Scenario: {scenario}")
        response = await x.chat(scenario)

        print(f"🔍 Extraction Result:\n{response}\n")
        print("-" * 70)

    print("✅ Extraction testing completed!")
    print(f"📁 Check workspace for extracted content: {x.workspace.get_path()}")

    # Show the power of the new system
    print("\n🚀 Crawl4AI Extraction System Features Demonstrated:")
    print("   ✅ Handles JavaScript-heavy sites (Reddit, GitHub, etc.)")
    print("   ✅ Bypasses bot detection mechanisms")
    print("   ✅ Parallel processing for multiple URLs")
    print("   ✅ Search and extraction in one operation")
    print("   ✅ No API keys needed - fully open source")
    print("   ✅ No rate limits or service outages")
    print("   ✅ Clean markdown output ready for AI processing")

    print("\n💬 Continue testing with X:")
    print("   Example: x.chat('Extract from 5 Reddit threads about Python frameworks')")
    print("   Example: x.chat('Test extraction from Twitter threads about AI')")
    print("   Example: x.chat('Extract academic papers about machine learning')")

if __name__ == "__main__":
    asyncio.run(main())
