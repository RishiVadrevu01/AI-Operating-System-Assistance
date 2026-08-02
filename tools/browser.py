import webbrowser
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def open_url(url: str) -> Dict[str, Any]:
    """Open a specified URL in the default web browser."""
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        return {"status": "success", "message": f"Opened URL: {url}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to open URL '{url}': {str(e)}"}

def search_youtube(query: str) -> Dict[str, Any]:
    """Search YouTube for a specific query."""
    try:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return {"status": "success", "message": f"Opened YouTube search for '{query}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed YouTube search: {str(e)}"}

def search_google(query: str) -> Dict[str, Any]:
    """Search Google for a given query."""
    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return {"status": "success", "message": f"Opened Google search for '{query}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed Google search: {str(e)}"}

async def navigate_with_playwright(url: str, headless: bool = False) -> Dict[str, Any]:
    """Automate page navigation using Playwright for advanced tasks."""
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            page = await browser.new_page()
            await page.goto(url)
            title = await page.title()
            await browser.close()
            return {"status": "success", "page_title": title, "url": url}
    except Exception as e:
        return {"status": "error", "message": f"Playwright navigation failed: {str(e)}"}
