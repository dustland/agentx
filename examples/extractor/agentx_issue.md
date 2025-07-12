# Browser crashes with Crawl4AI on macOS - Workaround implemented

## Description

When using Crawl4AI for web content extraction in AgentX on macOS, the browser context crashes with errors like:

```
playwright._impl._errors.Error: BrowserContext.close: Target page, context or browser has been closed
```

This is accompanied by crashpad warnings:

```
[pid=2490][err] [0712/130645.209238:WARNING:third_party/crashpad/crashpad/handler/mac/crash_report_exception_handler.cc:235] UniversalExceptionRaise: (os/kern) failure (5)
```

## Root Cause

This is related to a browser lifecycle management bug in Crawl4AI that has been fixed in PR https://github.com/unclecode/crawl4ai/pull/1211 but not yet released.

## Workaround Implemented

We've implemented a workaround in commit f865adb that:

1. Uses system Chrome instead of bundled Chromium (`chrome_channel="chrome"`)
2. Creates a new crawler instance for each URL to avoid context reuse
3. Uses `browser_mode="context"` instead of the default
4. Disables persistent context

The workaround is in `src/agentx/builtin_tools/web.py` in the `_extract_with_crawl4ai_fixed` method.

## Environment

- Platform: macOS (Darwin 25.0.0)
- Python: 3.13
- crawl4ai: 0.6.3
- AgentX version: Latest

## Action Items

- [ ] Track Crawl4AI release that includes PR #1211
- [ ] Remove workaround once new version is released
- [ ] Update minimum Crawl4AI version requirement

## Related

- Crawl4AI PR: https://github.com/unclecode/crawl4ai/pull/1211
- Workaround implementation: f865adb

## Testing

The workaround has been tested successfully:
- ✅ No more browser crashes
- ✅ Extracts content from example.com, httpbin.org
- ✅ Handles Reddit URLs without crashing (content still blocked by bot protection)

```python
# Test script available in examples/extractor/test_crawl4ai_fixed.py
uv run python examples/extractor/test_crawl4ai_fixed.py
```
