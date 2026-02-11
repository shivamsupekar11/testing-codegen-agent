"""Browser management with page caching."""

import os
import re
import time
import hashlib
import asyncio

from playwright.async_api import async_playwright, Page

_CACHE_DIR = ".dom_cache"
_browser = None
_playwright = None
_page_cache = {}


async def _get_browser():
    """Get or create a headless Chromium browser."""
    global _browser, _playwright
    if _browser is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
    return _browser


async def get_page(url: str) -> Page:
    """Get a Playwright page for the URL, using disk caching.

    This function manages a singleton browser instance and implements disk-based
    caching for HTML content. It prevents redundant network requests for the same
    URL within a 1-hour window.

    Args:
        url: The full URL to load.

    Returns:
        A Playwright Page object with the loaded content.
    """
    if url in _page_cache:
        return _page_cache[url]["page"]
    
    browser = await _get_browser()
    context = await browser.new_context()
    page = await context.new_page()
    
    # Check disk cache
    cache_path = os.path.join(_CACHE_DIR, f"{hashlib.md5(url.encode()).hexdigest()}.html")
    cached_html = None
    
    if os.path.exists(cache_path) and time.time() - os.path.getmtime(cache_path) < 3600:
        with open(cache_path, "r", encoding="utf-8") as f:
            cached_html = f.read()
    
    if cached_html:
        # Inject base tag, strip scripts to freeze DOM
        if "<base" not in cached_html[:1000].lower():
            cached_html = cached_html.replace("<head>", f'<head><base href="{url}">', 1)
        cached_html = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", "", cached_html, flags=re.I)
        await page.set_content(cached_html, wait_until="domcontentloaded")
    else:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(2000)
            await _scroll_to_load(page)
            os.makedirs(_CACHE_DIR, exist_ok=True)
            content = await page.content()
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            # If navigation fails, we still return the page, though it might be empty or error state
            # but usually we'd want to raise or handle it. For now, let's just log print
            print(f"Error loading {url}: {e}")
            pass

    
    _page_cache[url] = {"page": page, "context": context}
    return page


async def _scroll_to_load(page: Page):
    """Scroll page to trigger lazy-loaded content."""
    try:
        height = await page.evaluate("document.body.scrollHeight")
        viewport = await page.evaluate("window.innerHeight")
        pos = 0
        while pos < height:
            pos += viewport
            await page.evaluate(f"window.scrollTo(0, {pos})")
            await page.wait_for_timeout(300)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height > height:
                height = new_height
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_load_state("networkidle", timeout=5000)
    except:
        await page.wait_for_timeout(1000)
