# Browser lifecycle bug causing crashes on macOS - Workaround available

## Description

When using Crawl4AI on macOS with the default configuration, browser contexts crash with Playwright errors:

```
playwright._impl._errors.Error: BrowserContext.close: Target page, context or browser has been closed
=========================== logs ===========================
<launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --enable-features=NetworkService,NetworkServiceInProcess --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --disable-blink-features=AutomationControlled --user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 --user-data-dir=/var/folders/lf/z1692qs52zq96hqw2d97r29c0000gn/T/playwright_chromiumdev_profile-7ZUAUZ --remote-debugging-pipe --no-sandbox --no-startup-window
============================================================

Code context:
 523           parsed_st = _extract_stack_trace_information_from_stack(st, is_internal)
 524           self._api_zone.set(parsed_st)
 525           try:
 526               return await cb()
 527           except Exception as error:
 528 →             raise rewrite_error(error, f"{parsed_st['apiName']}: {error}") from None
```

This is accompanied by macOS crashpad warnings indicating browser process issues.

## Environment

- Platform: macOS (Darwin 25.0.0)
- Python: 3.13
- crawl4ai: 0.6.3
- Playwright: Latest

## Root Cause

Based on PR #1211, this appears to be related to browser lifecycle management, particularly when using the default browser mode configuration.

## Workaround

Until PR #1211 is released, here's a working workaround:

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

# Working configuration that avoids the bug
browser_config = BrowserConfig(
    browser_type="chromium",
    headless=True,
    # Use system Chrome instead of bundled Chromium
    chrome_channel="chrome",
    # Use context mode to avoid lifecycle issues
    browser_mode="context",
    # Don't use persistent context
    use_persistent_context=False,
    # Minimal args for stability
    extra_args=['--no-sandbox', '--disable-dev-shm-usage']
)

# Important: Create a new crawler instance for each URL
# to avoid context reuse issues
for url in urls:
    async with AsyncWebCrawler(config=browser_config) as crawler:
        run_config = CrawlerRunConfig(
            word_count_threshold=10,
            page_timeout=30000,
            exclude_external_links=True,
            exclude_social_media_links=True,
            wait_until="domcontentloaded"
        )

        result = await crawler.arun(url=url, config=run_config)
```

## Key Points for the Workaround

1. **Use system Chrome**: Set `chrome_channel="chrome"` to use the system Chrome instead of bundled Chromium
2. **Use context mode**: Set `browser_mode="context"` instead of the default
3. **No persistent context**: Set `use_persistent_context=False`
4. **New crawler per URL**: Create a fresh crawler instance for each URL to avoid context reuse

## Testing

This workaround has been tested successfully on macOS with:
- ✅ No browser crashes
- ✅ Successful extraction from example.com, httpbin.org, reddit.com
- ✅ Stable operation across multiple URLs

## Request

Could PR #1211 be prioritized for release? This bug significantly impacts macOS users. The workaround works but requires non-obvious configuration changes that users need to discover through trial and error.

## Related Projects Affected

- AgentX: https://github.com/Dustland/agentx (implemented workaround in f865adb)

Thank you for the great work on Crawl4AI! Looking forward to the fix being released.
