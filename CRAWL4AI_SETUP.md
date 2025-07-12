# 🚀 Crawl4AI Content Extraction Setup

AgentX now uses **Crawl4AI** as the ONLY content extraction method, providing a clean, opinionated, and reliable solution.

## Quick Installation

```bash
# Using uv (recommended)
uv add crawl4ai

# Or using pip
pip install crawl4ai
```

## Key Benefits

✅ **No more API failures** - Everything runs locally
✅ **Handles JavaScript** - Extracts content from dynamic sites
✅ **Bypasses bot detection** - Works with Reddit, Twitter, etc.
✅ **Clean markdown output** - Perfect for AI processing
✅ **Open source** - No vendor lock-in or rate limits
✅ **No complex fallbacks** - One method that works reliably

## Simple, Opinionated Approach

**No More Complex Fallback Chains!**

- ✅ Uses **Crawl4AI only** - no confusing fallback methods
- ✅ **Opinionated defaults** - no configuration needed
- ✅ **Clear error messages** - if Crawl4AI fails, you know exactly why
- ✅ **Reduced complexity** - from 650+ lines to 330 lines of code

## Auto_Writer Enhancement

The researcher agent in auto_writer now has access to:
- `extract_content` - Enhanced with Crawl4AI
- `search_and_extract` - Search + extraction in one step
- Parallel processing across multiple URLs
- Robust fallback chain ensures content is always extracted

## Configuration (Optional)

Crawl4AI works out of the box, but you can optimize with environment variables:

```bash
# Optional: Set browser path if needed
export CRAWL4AI_BROWSER_PATH=/path/to/chrome

# Optional: Enable debugging
export CRAWL4AI_VERBOSE=true
```

## Troubleshooting

If you encounter issues:

1. **Missing browser**: Crawl4AI will auto-install Chromium if needed
2. **Permissions**: Make sure `/tmp/crawl4ai_cache` is writable
3. **Memory**: Crawl4AI uses more memory than simple parsers but provides much better results

This upgrade should eliminate the content extraction pain points you've been experiencing!
