# AutoWriter Tests

This directory contains focused tests for each agent in the AutoWriter multi-agent system.

## Individual Agent Tests

Each test validates one specific agent independently:

- `test_research_planner.py` - Tests research plan generation with sub-queries
- `test_search_specialist.py` - Tests web search and source identification
- `test_content_extractor.py` - Tests URL content extraction using extract_content tool
- `test_research_synthesizer.py` - Tests synthesis of extracted content
- `test_content_reasoner.py` - Tests deep analytical reasoning and insights
- `test_document_formatter.py` - Tests HTML report generation

## Test Files

- `test_consultant.py` - Tests for consultant agent functionality
- `test_content_extractor.py` - Tests for content extraction capabilities
- `test_mckinsey_extraction.py` - Tests for McKinsey-style content extraction
- `test_research_flow.py` - Tests for the complete research workflow
- `test_search_specialist.py` - Tests for search specialist agent
- `test_tools.py` - Tests for tool functionality
- `test_visual_extraction.py` - Tests for visual content extraction

## Debug Utilities

- `debug_tools.py` - Debug script to check available tools and agent configuration

## Test Configurations

- `test_single_agent.yaml` - Configuration for single agent tests
- `test_visual_extraction.yaml` - Configuration for visual extraction tests

## Running Tests

To run individual tests:

```bash
# From the auto_writer directory
python tests/test_consultant.py
python tests/test_research_flow.py
python tests/debug_tools.py
```

Note: Make sure you have the required environment variables set (e.g., `DEEPSEEK_API_KEY`) before running tests.
