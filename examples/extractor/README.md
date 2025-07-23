# Content Extractor Example

This example demonstrates **powerful web content extraction** using VibeX's new Crawl4AI-powered tools.

## Purpose

Showcases the enhanced content extraction capabilities:

- 🚀 **Crawl4AI Integration**: Handles JavaScript, dynamic content, bypasses bot detection
- 🔍 **Parallel Processing**: Extract from multiple URLs simultaneously
- 🧠 **Smart Research**: Combines search with content extraction
- 📊 **Reliable Results**: No more API failures or rate limits

## The Problem (Solved!)

Previous web extraction was unreliable:

- ❌ **Jina Reader**: Frequent outages and API failures
- ❌ **Simple parsers**: Couldn't handle JavaScript sites
- ❌ **Bot detection**: Blocked on Reddit, Twitter, etc.
- ❌ **Rate limits**: API quotas and throttling

## The Solution

New Crawl4AI-powered extraction:

```python
# Reliable extraction from complex sites
extract_content(urls)  # Uses Crawl4AI - handles JS, bypasses detection

# Search and extract in one step
search_and_extract(["quantum computing drug discovery", "molecular simulation"])

# Parallel processing for efficiency
web_search(["topic1", "topic2", "topic3"])  # All in parallel
```

Result: **Reliable extraction from any website** including Reddit, Twitter, research papers, and dynamic content sites.

## What This Example Demonstrates

1. **Crawl4AI Power**: Extracting from JavaScript-heavy sites that fail with other tools
2. **Parallel Efficiency**: Processing multiple URLs and queries simultaneously
3. **Search Integration**: Combined search and extraction workflow
4. **Reliable Operation**: No API failures, no bot detection issues

## Usage

```bash
cd examples/extractor
python main.py
```

**Prerequisites**:

```bash
# Install Crawl4AI (if not already done)
uv add crawl4ai
```

## Expected Output

The researcher will demonstrate:

- **Reliable Extraction**: Successfully extracting from complex sites
- **Parallel Processing**: Multiple queries and URLs processed simultaneously
- **Search Integration**: Using `search_and_extract` for comprehensive research
- **Quality Content**: Rich, detailed information with proper formatting

Check the taskspace folder for the extracted content files.

## Key Features Tested

### 1. **Complex Site Handling**

- Reddit discussions and technical content
- Twitter/X posts and threads
- Research papers and academic sites
- News articles with dynamic loading

### 2. **Parallel Processing**

- Multiple search queries executed simultaneously
- Batch URL extraction for efficiency
- Reduced total processing time

### 3. **Integrated Workflow**

- `search_and_extract()` - search + extraction in one step
- Automatic content saving to taskspace files
- Clean markdown output ready for analysis

## The Demonstration

**Task**: Extract content from challenging websites to show Crawl4AI's power

**What the Agent Will Do**:

1. Use `search_and_extract` to find and extract content in one operation
2. Process multiple complex URLs that would fail with other tools
3. Extract from JavaScript-heavy sites (Reddit, Twitter, etc.)
4. Save comprehensive content with proper formatting

**Expected Results**:

- ✅ **Successful extraction** from sites that block other tools
- ✅ **Rich content** with proper formatting and structure
- ✅ **Fast processing** through parallel operations
- ✅ **Saved files** ready for further analysis

All powered by Crawl4AI - no API keys needed, no rate limits, no failures!

## Tech Demo Highlights

This example specifically tests:

- **Reddit extraction**: Technical discussions and comments
- **Research paper extraction**: Academic content with complex formatting
- **News site extraction**: Articles with dynamic loading
- **Parallel processing**: Multiple URLs processed simultaneously
- **Search integration**: Finding and extracting content in one step

Perfect for demonstrating how VibeX has solved the web content extraction challenges!
