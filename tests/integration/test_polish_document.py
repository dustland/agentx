#!/usr/bin/env python3
"""
Integration test for polish_document tool with realistic auto_writer content.
Tests timeout handling, chunking, and the deepseek-reasoner model.
"""

import asyncio
import tempfile
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agentx.builtin_tools.document import DocumentTool
from agentx.storage.taskspace import TaskspaceStorage


async def test_polish_with_sections():
    """Test polishing a document with multiple sections like auto_writer output."""
    # Create test workspace
    temp_dir = tempfile.mkdtemp()
    workspace = TaskspaceStorage(workspace_path=temp_dir)
    doc_tool = DocumentTool(workspace_storage=workspace)
    
    # Create a test document with multiple sections (like auto_writer output)
    test_content = """# Web Development Trends 2025 Report

## Executive Summary

This report provides a comprehensive analysis of the key trends shaping web development in 2025. Based on extensive research across multiple sources, we've identified several critical developments that are transforming how modern applications are built and deployed.

The landscape of web development continues to evolve rapidly, with artificial intelligence, edge computing, and new frameworks leading the charge. Organizations must adapt to these changes to remain competitive in an increasingly digital marketplace.

## Frontend Frameworks Evolution

### React and Next.js Dominance

React continues to dominate the frontend landscape with Next.js emerging as the preferred meta-framework. The latest versions introduce revolutionary features including:

- Server Components for improved performance
- Streaming SSR capabilities
- Enhanced developer experience with improved tooling
- Built-in optimization features

The community has embraced these changes, with adoption rates showing significant growth across enterprise applications.

### Vue.js Renaissance

Vue.js has experienced a remarkable resurgence with Vue 3's composition API gaining widespread adoption. Key developments include:

- Improved TypeScript support
- Enhanced performance metrics
- Growing ecosystem of tools and libraries
- Strong community support

### Emerging Contenders

New frameworks like Qwik and Solid are challenging established players with innovative approaches to reactivity and performance optimization. These frameworks promise near-zero JavaScript overhead and exceptional time-to-interactive metrics.

## Backend Technologies Transformation

### Serverless Architecture Maturity

Serverless computing has reached a new level of maturity in 2025. Organizations are increasingly adopting serverless-first strategies, driven by:

- Reduced operational overhead
- Automatic scaling capabilities
- Cost optimization benefits
- Improved developer productivity

Major cloud providers have enhanced their serverless offerings with better cold start performance and expanded runtime support.

### Edge Computing Revolution

Edge computing is transforming how applications are deployed and scaled. Key benefits include:

- Ultra-low latency for global users
- Reduced bandwidth costs
- Enhanced security through distributed architecture
- Improved resilience and fault tolerance

### Database Evolution

Modern database technologies are evolving to meet new demands:

- Vector databases for AI applications
- Distributed SQL solutions
- Real-time synchronization capabilities
- Enhanced security features

## AI Integration in Development

### Code Generation and Assistance

AI-powered development tools have become mainstream, with capabilities including:

- Intelligent code completion
- Automated bug detection
- Code review assistance
- Documentation generation

These tools are fundamentally changing developer workflows and productivity metrics.

### Testing and Quality Assurance

AI is revolutionizing testing practices through:

- Automated test generation
- Intelligent test case prioritization
- Predictive bug detection
- Performance optimization recommendations

### Deployment and Operations

AI-driven operations tools provide:

- Automated deployment strategies
- Predictive scaling
- Anomaly detection
- Self-healing systems

## Performance and Optimization

### Core Web Vitals Focus

Performance optimization remains critical with emphasis on:

- Largest Contentful Paint (LCP)
- First Input Delay (FID)
- Cumulative Layout Shift (CLS)
- Interaction to Next Paint (INP)

### Modern Build Tools

New generation build tools offer:

- Lightning-fast compilation
- Intelligent code splitting
- Advanced tree shaking
- Module federation capabilities

## Security Considerations

### Zero Trust Architecture

Security practices are evolving toward zero trust models:

- Continuous verification
- Least privilege access
- Encrypted communications
- Regular security audits

### Supply Chain Security

Focus on securing the software supply chain through:

- Dependency scanning
- Vulnerability monitoring
- Secure development practices
- Regular updates and patches

## Future Outlook

The web development landscape in 2025 presents both opportunities and challenges. Organizations that embrace these trends while maintaining focus on user experience and security will be best positioned for success.

Key recommendations include:

1. Invest in AI-powered development tools
2. Adopt edge computing strategies
3. Prioritize performance optimization
4. Implement robust security practices
5. Foster continuous learning culture

## Conclusion

Web development in 2025 is characterized by rapid innovation, with AI integration, edge computing, and performance optimization leading the transformation. Success requires balancing adoption of new technologies with proven practices and maintaining focus on delivering value to users.

Organizations must remain agile and adaptive, continuously evaluating new tools and approaches while ensuring stability and security of their applications.
"""
    
    # Save test document
    await workspace.store_artifact('draft_report.md', test_content, 'text/markdown')
    
    print(f'📄 Test document created: {len(test_content)} characters')
    print(f'📊 Sections: {test_content.count("##")} major sections')
    
    # Test polishing with the reasoner model
    print('\n🔧 Starting polish with deepseek-reasoner...')
    start_time = asyncio.get_event_loop().time()
    
    result = await doc_tool.polish_document(
        'draft_report.md',
        polish_instructions="Ensure smooth transitions between sections and consistent professional tone throughout."
    )
    
    elapsed_time = asyncio.get_event_loop().time() - start_time
    
    print(f'\n⏱️  Polish completed in {elapsed_time:.1f} seconds')
    print(f'📊 Result: {"✅ SUCCESS" if result.success else "❌ FAILED"}')
    
    if result.success:
        print(f'📝 Output file: {result.metadata.get("output_file")}')
        
        # Check if chunking was used
        if elapsed_time > 60:
            print('🔄 Large document processed (may have used chunking)')
    else:
        print(f'❌ Error: {result.error}')
        if 'timeout' in str(result.error).lower():
            print('⏱️  Timeout issue detected!')
    
    print('\n✅ Polish test completed')


async def test_polish_timeout_handling():
    """Test that large documents don't timeout with the increased limit."""
    temp_dir = tempfile.mkdtemp()
    workspace = TaskspaceStorage(workspace_path=temp_dir)
    doc_tool = DocumentTool(workspace_storage=workspace)
    
    # Create a very large document that would timeout with 30s limit
    large_content = "# Large Test Document\n\n"
    
    # Add many sections to make it large
    for i in range(20):
        large_content += f"\n## Section {i+1}\n\n"
        large_content += "This is a test section with substantial content. " * 100
        large_content += "\n\nMore detailed information follows:\n\n"
        large_content += "- Important point about web development\n" * 10
        large_content += "\n"
    
    await workspace.store_artifact('large_draft.md', large_content, 'text/markdown')
    
    print(f'\n📄 Large document test: {len(large_content)} characters')
    print('🔧 Testing timeout handling...')
    
    result = await doc_tool.polish_document('large_draft.md')
    
    if result.success:
        print('✅ Large document polished successfully (timeout fixed!)')
    else:
        print(f'❌ Failed: {result.error}')
        if 'timeout' in str(result.error).lower():
            print('⚠️  Still hitting timeout - may need further optimization')


if __name__ == "__main__":
    print("🧪 Testing polish_document with realistic auto_writer content...")
    print("This simulates polishing a large research report.\n")
    
    async def run_all_tests():
        await test_polish_with_sections()
        await test_polish_timeout_handling()
    
    asyncio.run(run_all_tests())