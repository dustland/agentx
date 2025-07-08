# Web Scraping

*Module: [`agentx.builtin_tools.web`](https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py)*

Web Tools - Opinionated web automation and content extraction.

Built-in integrations:
- Firecrawl: Web content extraction
- requests + BeautifulSoup: Content extraction
- browser-use: AI-first browser automation (better than Playwright for agents)

## WebContent <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L21" class="source-link" title="View source code">source</a>

Extracted web content.

## BrowserAction <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L33" class="source-link" title="View source code">source</a>

Browser automation action result.

## WebTool <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L42" class="source-link" title="View source code">source</a>

Web content extraction and browser automation tool.

Combines Firecrawl for content extraction and browser-use for automation.

### __init__ <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L49" class="source-link" title="View source code">source</a>

```python
def __init__(self, jina_api_key: Optional[str] = None)
```
### extract_content <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L87" class="source-link" title="View source code">source</a>

```python
async def extract_content(self, urls: Union[str, List[str]], prompt: str = 'Extract the main content from this webpage') -> ToolResult
```

Extract clean content from one or more URLs using Jina Reader.

Jina Reader is specifically designed for AI content extraction and handles
anti-bot protection, JavaScript rendering, and modern web challenges.

**Args:**
    urls: A single URL or list of URLs to extract content from
    prompt: Description of what content to focus on (optional)

**Returns:**
    ToolResult with extracted content

### extract_content_with_visuals <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L208" class="source-link" title="View source code">source</a>

```python
async def extract_content_with_visuals(self, url: str, prompt: str, capture_screenshot: bool = True, enable_web_search: bool = False) -> ToolResult
```

Enhanced content extraction that captures both textual and visual data from web pages.
This method is specifically designed to extract data from charts, graphs, infographics,
and other visual elements that traditional text extraction might miss.

**Args:**
    url: Single URL to extract content from (required)
    prompt: Detailed prompt describing what to extract, including visual elements (required)
    capture_screenshot: Whether to capture full-page screenshot for visual analysis, defaults to True
    enable_web_search: Whether to expand search beyond the URL, defaults to False

**Returns:**
    ToolResult with comprehensive extracted content including visual data

### crawl_website <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L320" class="source-link" title="View source code">source</a>

```python
async def crawl_website(self, url: str, limit: int = 10, exclude_paths: Optional[List[str]] = None) -> ToolResult
```

Crawl multiple pages from a website.

**Args:**
    url: The base URL to start crawling from (required)
    limit: Maximum number of pages to crawl, defaults to 10
    exclude_paths: URL paths to exclude from crawling (optional)

**Returns:**
    ToolResult with list of WebContent objects

### automate_browser <a href="https://github.com/dustland/agentx/blob/main/src/agentx/builtin_tools/web.py#L386" class="source-link" title="View source code">source</a>

```python
async def automate_browser(self, instruction: str, url: Optional[str] = None) -> ToolResult
```

Perform browser automation using natural language instructions.

**Args:**
    instruction: Natural language instruction for browser action (required)
    url: Optional URL to navigate to first

**Returns:**
    ToolResult with BrowserAction containing action result
