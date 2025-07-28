# Web Scraping

*Module: [`vibex.builtin_tools.web`](https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/web.py)*

Web Tools - Advanced URL content extraction using Firecrawl.

Supports multiple extraction strategies:
- Markdown: Clean markdown extraction (default)
- HTML: Raw HTML extraction
- Links: Extract all links from the page
- Screenshot: Capture page screenshot

Features:
- Simple API with built-in error handling
- Automatic retry on failures
- Clean markdown output optimized for LLMs
- Taskspace integration for saving extracted content

## WebContent <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/web.py#L39" class="source-link" title="View source code">source</a>

Content extracted from a web page.

## WebTool <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/web.py#L49" class="source-link" title="View source code">source</a>

Advanced web content extraction tool using Firecrawl.

Provides intelligent content extraction with multiple strategies:
- Clean markdown extraction optimized for LLMs
- HTML extraction for full content
- Link extraction for crawling
- Screenshot capture

### __init__ <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/web.py#L60" class="source-link" title="View source code">source</a>

```python
def __init__(self, project_storage: Optional[Any] = None) -> None
```

### extract_urls <a href="https://github.com/dustland/vibex/blob/main/src/vibex/builtin_tools/web.py#L82" class="source-link" title="View source code">source</a>

```python
async def extract_urls(
    self,
    urls: Union[str, List[str]],
    formats: List[str] = ["markdown", "html"],
    only_main_content: bool = True,
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    wait_for_selector: Optional[str] = None,
    timeout: int = 30000
) -> ToolResult
```

Extract content from URLs using Firecrawl with advanced features.

**Parameters:**
- `urls`: Single URL or list of URLs to extract content from
- `formats`: List of formats to extract (default: ["markdown", "html"])
- `only_main_content`: Extract only main content, excluding navigation, ads, etc. (default: True)
- `include_tags`: List of HTML tags to include in extraction
- `exclude_tags`: List of HTML tags to exclude from extraction
- `wait_for_selector`: CSS selector to wait for before extraction
- `timeout`: Timeout in milliseconds (default: 30000)

**Returns:**
- `ToolResult` with extracted content and metadata

## Usage Examples

### Basic URL Extraction

```python
from vibex.builtin_tools.web import WebTool

web_tool = WebTool()

# Extract content from a single URL
result = await web_tool.extract_urls("https://example.com")

# Extract from multiple URLs
urls = ["https://example1.com", "https://example2.com"]
result = await web_tool.extract_urls(urls)
```

### Advanced Extraction Options

```python
# Extract with specific options
result = await web_tool.extract_urls(
    "https://example.com",
    formats=["markdown"],  # Only markdown format
    only_main_content=True,  # Skip navigation, ads, etc.
    include_tags=["article", "main"],  # Focus on these tags
    exclude_tags=["nav", "footer"],  # Exclude these tags
    wait_for_selector=".content-loaded",  # Wait for dynamic content
    timeout=60000  # 60 second timeout
)
```

## Environment Setup

To use Firecrawl, you need to set the `FIRECRAWL_API_KEY` environment variable:

```bash
export FIRECRAWL_API_KEY=your-api-key-here
```

Or in your `.env` file:

```
FIRECRAWL_API_KEY=your-api-key-here
```

Get your API key from [Firecrawl Dashboard](https://www.firecrawl.dev/app/sign-in).