#!/usr/bin/env python3
"""
Direct test of the improved summarization tool
"""

import asyncio
import os
from pathlib import Path
import sys

# Add the agentx source to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from agentx.builtin_tools.document import DocumentTool
from agentx.storage.workspace import WorkspaceStorage

async def test_summarize():
    print("🧪 Testing Document Summarization Tool")
    print("=" * 50)

    # Create test workspace
    workspace_path = Path("./test_workspace")
    workspace_path.mkdir(exist_ok=True)

    # Create workspace storage
    workspace = WorkspaceStorage(str(workspace_path))

    # Create test files with sample content
    test_files = {
        "flask_article.md": """
# Flask Framework Overview

Flask is a lightweight web framework for Python. It's designed to be simple and flexible.

## Key Features
- Minimalist design
- Easy to learn
- Extensive documentation
- Large community support

## Performance
Flask can handle moderate traffic loads effectively. For high-performance needs, consider using production WSGI servers.

## Use Cases
- Small to medium web applications
- REST APIs
- Prototyping
- Educational projects
        """,
        "fastapi_article.md": """
# FastAPI Framework Analysis

FastAPI is a modern, fast web framework for building APIs with Python.

## Key Features
- Automatic API documentation
- Type hints integration
- High performance
- Modern Python features

## Performance
FastAPI is one of the fastest Python frameworks, comparable to NodeJS and Go.

## Use Cases
- High-performance APIs
- Machine learning model serving
- Microservices
- Data science applications
        """
    }

    # Save test files to workspace
    for filename, content in test_files.items():
        await workspace.store_artifact(
            name=filename,
            content=content,
            content_type="text/markdown",
            metadata={"test": True}
        )
        print(f"✅ Created test file: {filename}")

    # Create document tool
    document_tool = DocumentTool(workspace_storage=workspace)

    # Test AI summarization
    print("\n🤖 Testing AI-powered summarization...")

    try:
        result = await document_tool.summarize_documents(
            input_files=list(test_files.keys()),
            output_filename="research_summary.md",
            summary_prompt="Create a comprehensive comparison of Flask vs FastAPI frameworks, highlighting their strengths, performance characteristics, and ideal use cases."
        )

        if result.success:
            print("✅ AI Summarization successful!")
            print(f"Result: {result.result}")
            print(f"Metadata: {result.metadata}")

            # Read and display the summary
            summary_content = await workspace.get_artifact("research_summary.md")
            print("\n📄 Generated Summary (first 500 chars):")
            print("-" * 40)
            print(summary_content[:500] + "...")
            print("-" * 40)

        else:
            print(f"❌ AI Summarization failed: {result.error}")

    except Exception as e:
        print(f"❌ Exception during summarization: {e}")

    # Cleanup
    import shutil
    shutil.rmtree(workspace_path, ignore_errors=True)
    print("\n🧹 Cleanup completed")

if __name__ == "__main__":
    asyncio.run(test_summarize())
