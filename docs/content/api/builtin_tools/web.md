# Web Scraping

*Module: [`agentx.builtin_tools.web`](https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py)*

Web Tools - Opinionated content extraction using the best available methods.

Uses Crawl4AI as the primary and only method for reliability and consistency.
No complex fallback chains - if Crawl4AI fails, the extraction fails clearly.

## WebContent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L22" class="source-link" title="View source code">source</a>

Extracted web content.

## WebTool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L33" class="source-link" title="View source code">source</a>

Opinionated web content extraction tool using Crawl4AI.

Simple, reliable, and consistent - no complex fallback chains.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L40" class="source-link" title="View source code">source</a>

```python
def __init__(self, workspace_storage = None)
```
### extract_content <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L48" class="source-link" title="View source code">source</a>

```python
async def extract_content(self, urls: Union[str, List[str]], prompt: str = 'Extract main content') -> ToolResult
```

Extract content from URLs using Crawl4AI (open source, handles JS, reliable).

**Args:**
    urls: Single URL or list of URLs to extract from
    prompt: Optional focus prompt (currently unused)

**Returns:**
    ToolResult with extracted content summaries and file paths
