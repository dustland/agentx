# Migration Guide: Switching from Crawl4AI to Firecrawl

This guide helps you migrate from the Crawl4AI-based web extraction to the new Firecrawl implementation.

## Why Switch to Firecrawl?

1. **Simpler API**: Firecrawl provides a cleaner, more intuitive API
2. **Better reliability**: Built-in retry logic and error handling
3. **No browser context issues**: Firecrawl manages browser instances internally
4. **Optimized for LLMs**: Returns clean markdown by default

## Key Changes

### API Changes

The `extract_urls` method signature has changed:

**Old (Crawl4AI):**
```python
await web_tool.extract_urls(
    urls,
    extraction_type="markdown",  # or "structured", "css", "regex"
    schema=None,
    css_selector=None,
    regex_patterns=None,
    enable_virtual_scroll=False,
    enable_pdf=False,
    js_code=None,
    wait_for=None
)
```

**New (Firecrawl):**
```python
await web_tool.extract_urls(
    urls,
    formats=["markdown", "html"],
    only_main_content=True,
    include_tags=None,
    exclude_tags=None,
    wait_for_selector=None,
    timeout=30000
)
```

### Parameter Mapping

| Crawl4AI Parameter | Firecrawl Equivalent | Notes |
|-------------------|---------------------|--------|
| `extraction_type` | `formats` | Now accepts list of formats |
| `css_selector` | `include_tags` | Use HTML tags instead of CSS selectors |
| `enable_virtual_scroll` | N/A | Firecrawl handles scrolling automatically |
| `js_code` | N/A | Not directly supported |
| `wait_for` | `wait_for_selector` | Same functionality |
| N/A | `only_main_content` | New feature to exclude navigation, ads |
| N/A | `exclude_tags` | New feature to exclude specific tags |

### Environment Setup

You need to set up a Firecrawl API key:

```bash
# Add to your .env file
FIRECRAWL_API_KEY=your-api-key-here
```

Get your API key from: https://www.firecrawl.dev/app/sign-in

### Code Examples

**Basic extraction:**
```python
# Old way
result = await web_tool.extract_urls(url, extraction_type="markdown")

# New way
result = await web_tool.extract_urls(url, formats=["markdown"])
```

**Targeted extraction:**
```python
# Old way
result = await web_tool.extract_urls(
    url,
    extraction_type="css",
    css_selector=".article-content"
)

# New way
result = await web_tool.extract_urls(
    url,
    include_tags=["article", "main"],
    only_main_content=True
)
```

**Waiting for dynamic content:**
```python
# Old way
result = await web_tool.extract_urls(
    url,
    wait_for=".content-loaded"
)

# New way
result = await web_tool.extract_urls(
    url,
    wait_for_selector=".content-loaded"
)
```

## Backward Compatibility

The old `web_crawl4ai.py` file has been preserved as a backup. If you need to temporarily revert:

```python
# Temporarily use the old implementation
from vibex.builtin_tools.web_crawl4ai import WebTool
```

However, we recommend migrating to Firecrawl as soon as possible for better reliability and performance.

## Troubleshooting

1. **401 Unauthorized errors**: Make sure your `FIRECRAWL_API_KEY` is set correctly
2. **Timeout errors**: Increase the `timeout` parameter (default is 30000ms)
3. **Missing content**: Try setting `only_main_content=False` to get full page content
4. **Different output format**: Firecrawl returns cleaner markdown by default, which may differ from Crawl4AI's output