# Crawl4AI Browser Lifecycle Bug Workaround

## Issue Summary

When using Crawl4AI on macOS, browser contexts crash with errors like:
- `BrowserContext.close: Target page, context or browser has been closed`
- `BrowserContext.new_page: Target page, context or browser has been closed`

This appears to be related to the browser lifecycle management bug fixed in PR #1211 but not yet released.

## Symptoms

```
[pid=2490][err] [0712/130645.209238:WARNING:third_party/crashpad/crashpad/handler/mac/crash_report_exception_handler.cc:235] UniversalExceptionRaise: (os/kern) failure (5)
```

Followed by Playwright errors:
```
playwright._impl._errors.Error: BrowserContext.new_page: Target page, context or browser has been closed
```

## Workaround

Based on PR #1211, the workaround is to use `browser_mode="dedicated"` instead of the default:

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# Use dedicated browser mode to avoid lifecycle bug
browser_config = BrowserConfig(
    browser_type="chromium",
    headless=True,
    browser_mode="dedicated",  # Critical: avoids the lifecycle bug
    use_persistent_context=False,  # Don't use persistent context
    extra_args=[
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--no-first-run',
        '--no-default-browser-check'
    ]
)

# Run configuration with minimal options
run_config = CrawlerRunConfig(
    word_count_threshold=10,
    page_timeout=30000,
    exclude_external_links=True,
    exclude_social_media_links=True,
    wait_until="domcontentloaded"
)

# Use the crawler
async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url=url, config=run_config)
```

## Key Points

1. **Don't use `browser_mode="builtin"`** - This causes the lifecycle bug
2. **Use `browser_mode="dedicated"`** - Creates a new browser instance for each crawler
3. **Avoid persistent context** - Set `use_persistent_context=False`
4. **Don't pass boolean to `markdown_generator`** - Let it use default

## Testing

This workaround has been tested successfully on:
- macOS (Darwin 25.0.0)
- Python 3.13
- crawl4ai 0.6.3
- Successfully extracts from example.com, httpbin.org, and Reddit (though Reddit still blocks content)

## Environment

```
Platform: darwin
OS Version: Darwin 25.0.0
Python: 3.13
crawl4ai: 0.6.3
```

## Related Issues

- PR #1211: https://github.com/unclecode/crawl4ai/pull/1211
- Browser crashes on macOS with default configuration
- Affects AgentX integration: https://github.com/dustland/agentx

## Action Items

1. Apply this workaround until the fix in PR #1211 is released
2. Update to use default configuration once new version is released
3. Track this issue in AgentX for future cleanup
