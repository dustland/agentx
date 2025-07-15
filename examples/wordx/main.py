#!/usr/bin/env python3
"""
WordX Example - Complete Document Processing Workflow
===================================================

This example demonstrates how to use the WordX system for professional
document processing with multi-agent teams.

Features:
- Professional document review and editing
- Multi-agent collaboration workflow
- Real-time processing with Web UI
- Office.js integration for Microsoft Word
- Comprehensive compliance checking

Usage:
    python main.py [options]

Options:
    --backend-only    Run only the backend service
    --demo           Run with demo document
    --help           Show this help message
"""

import asyncio
import argparse
import logging
from pathlib import Path
from typing import Optional

from agentx import start_task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_config_path() -> Path:
    """Get the path to the team configuration file"""
    return Path(__file__).parent / "backend" / "config" / "team.yaml"

def get_demo_document() -> str:
    """Get a demo document for testing"""
    return """
    # Business Proposal: Enhanced Customer Support Initiative

    ## Executive Summary

    This proposal outlines our plan to improve customer support through AI-powered solutions and enhanced team training.
    The initiative will focus on reducing response times, improving customer satisfaction, and implementing proactive support measures.

    ## Background

    Our current customer support system faces several challenges including long response times, inconsistent service quality,
    and limited availability during peak hours. Customer satisfaction scores have declined 15% over the past quarter.

    ## Proposed Solution

    We recommend implementing a comprehensive support enhancement program including:

    1. AI-powered chatbot for initial customer inquiries
    2. Enhanced training program for support staff
    3. Extended support hours coverage
    4. Proactive customer outreach system

    ## Implementation Timeline

    Phase 1 (Months 1-2): AI chatbot deployment and staff training
    Phase 2 (Months 3-4): Extended hours implementation
    Phase 3 (Months 5-6): Proactive outreach system launch

    ## Budget Requirements

    Total estimated cost: $150,000 over 6 months
    Expected ROI: 25% improvement in customer satisfaction
    Break-even point: 8 months

    ## Next Steps

    We request approval to proceed with Phase 1 implementation beginning next month.
    """

async def process_document_with_agents(document_content: str, task_description: str) -> None:
    """Process a document using the WordX agent team"""
    try:
        print("🚀 Starting WordX Document Processing")
        print("="*50)
        print(f"📄 Document Length: {len(document_content)} characters")
        print(f"📋 Task: {task_description}")
        print("="*50)

        # Create the initial prompt
        initial_prompt = f"""
        Document Processing Task:

        Task Description: {task_description}

        Document Content:
        {document_content}

        Please review this document using the complete WordX workflow:
        1. Document Reviewer: Analyze structure and clarity
        2. Content Editor: Improve writing quality and engagement
        3. Formatter: Optimize layout and presentation
        4. Compliance Auditor: Ensure standards and compliance

        Provide comprehensive improvements and recommendations.
        """

        # Start the AgentX task
        config_path = get_config_path()

        print("🤖 Initializing agent team...")
        x = await start_task(initial_prompt, str(config_path))

        print("✅ Agent team initialized successfully")
        print("🔄 Processing document with multi-agent workflow...")

        # Process with streaming updates
        step_count = 0
        while not x.is_complete:
            step_count += 1
            print(f"\n📊 Step {step_count}: Agent team working...")

            response = await x.step()

            # Show progress
            print(f"💬 Agent Response: {response[:200]}...")

            # Prevent infinite loops
            if step_count > 20:
                print("⚠️  Maximum steps reached. Stopping process.")
                break

        print("\n✅ Document processing completed!")
        print("="*50)

        # Show final results
        if hasattr(x, 'get_final_result'):
            final_result = x.get_final_result()
            print("📋 Final Processing Results:")
            print(final_result)
        else:
            print("📋 Processing completed successfully.")

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        print(f"❌ Error: {str(e)}")

async def interactive_demo():
    """Run interactive demo with user input"""
    print("🎯 WordX Interactive Demo")
    print("="*50)

    # Get task description from user
    task_description = input("📝 What would you like to do with the document? (Press Enter for default): ").strip()

    if not task_description:
        task_description = "Review this document for clarity, structure, and professional presentation. Provide comprehensive improvements."

    # Get document content
    use_demo = input("📄 Use demo document? (y/n, default: y): ").strip().lower()

    if use_demo != 'n':
        document_content = get_demo_document()
        print("✅ Using demo business proposal document")
    else:
        print("📝 Enter your document content (paste and press Ctrl+D on Linux/Mac or Ctrl+Z on Windows):")
        document_content = ""
        try:
            while True:
                line = input()
                document_content += line + "\n"
        except EOFError:
            pass

    if not document_content.strip():
        print("❌ No document content provided. Using demo document.")
        document_content = get_demo_document()

    # Process the document
    await process_document_with_agents(document_content, task_description)

def start_backend_server():
    """Start the WordX backend server"""
    print("🚀 Starting WordX Backend Server")
    print("="*50)
    print("🌐 Backend will be available at: http://localhost:7779")
    print("📚 API documentation: http://localhost:7779/docs")
    print("🔧 Use with Office.js add-in for complete WordX experience")
    print("="*50)

    try:
        # Import and run the backend
        from backend.main import app
        import uvicorn

        uvicorn.run(
            app,
            host="0.0.0.0",
            port=7779,
            log_level="info"
        )
    except ImportError:
        print("❌ Backend dependencies not installed.")
        print("💡 Install with: pip install -r backend/requirements.txt")
    except Exception as e:
        print(f"❌ Error starting backend: {str(e)}")

def show_setup_instructions():
    """Show setup instructions for WordX"""
    print("📋 WordX Setup Instructions")
    print("="*50)
    print("1. Backend Setup:")
    print("   cd backend")
    print("   pip install -r requirements.txt")
    print("   python main.py")
    print()
    print("2. Office.js Add-in Setup:")
    print("   cd addon")
    print("   npm install")
    print("   npm start")
    print()
    print("3. Word Add-in Installation:")
    print("   - Open Microsoft Word")
    print("   - Go to Insert > My Add-ins > Upload My Add-in")
    print("   - Select the manifest.xml file")
    print("   - Click 'WordX' in the ribbon")
    print()
    print("4. Environment Setup:")
    print("   - cd backend && cp environment.template .env")
    print("   - Edit backend/.env with your API keys")
    print()
    print("🎯 For complete professional document processing!")
    print("="*50)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="WordX - AI-powered document processing with multi-agent teams"
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Run only the backend service"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with demo document"
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Show setup instructions"
    )

    args = parser.parse_args()

    if args.setup:
        show_setup_instructions()
        return

    if args.backend_only:
        start_backend_server()
        return

    if args.demo:
        # Run with demo document
        demo_content = get_demo_document()
        task_description = "Review this business proposal for clarity, structure, and professional presentation. Provide comprehensive improvements."
        await process_document_with_agents(demo_content, task_description)
        return

    # Run interactive demo
    await interactive_demo()

if __name__ == "__main__":
    print("🎯 WordX - AI-Powered Document Processing")
    print("   Built with AgentX Multi-Agent Framework")
    print("   Professional document review, editing, and compliance")
    print()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 WordX demo terminated by user")
    except Exception as e:
        logger.error(f"Error running WordX demo: {str(e)}")
        print(f"❌ Error: {str(e)}")
        print("💡 Try: python main.py --setup for setup instructions")
