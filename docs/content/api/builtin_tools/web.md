# Web Scraping

*Module: [`agentx.builtin_tools.web`](https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py)*

Web Tools - Advanced URL content extraction using crawl4ai 0.7.0.

Supports multiple extraction strategies:
- Markdown: Clean markdown extraction (default)
- Structured: Schema-based structured data extraction
- CSS: Targeted extraction using CSS selectors

Features:
- Virtual scroll for infinite scroll pages
- Custom JavaScript execution
- Flexible extraction strategies
- Workspace integration for saving extracted content

## WebContent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L49" class="source-link" title="View source code">source</a>

Content extracted from a web page.

## WebTool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L59" class="source-link" title="View source code">source</a>

Advanced web content extraction tool using crawl4ai 0.7.0.

Provides intelligent content extraction with multiple strategies:
- CSS selector-based targeted extraction
- Virtual scroll for dynamic content
- Custom JavaScript execution

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L69" class="source-link" title="View source code">source</a>

```python
def __init__(self, workspace_storage: Optional[Any] = None) -> None
```
### extract_urls <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L77" class="source-link" title="View source code">source</a>

```python
async def extract_urls(self, urls: Union[str, List[str]], extraction_type: str = 'markdown', schema: Optional[Dict[str, Any]] = None, css_selector: Optional[str] = None, regex_patterns: Optional[List[str]] = None, enable_virtual_scroll: bool = False, enable_pdf: bool = False, js_code: Optional[str] = None, wait_for: Optional[str] = None) -> ToolResult
```

Extract content from URLs using Crawl4AI with advanced features.
