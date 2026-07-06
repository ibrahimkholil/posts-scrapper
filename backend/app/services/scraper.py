from playwright.async_api import async_playwright
from readability import Document
import httpx


async def scrape_url(url: str) -> dict:
    """
    Scrape content from a URL using Playwright for JavaScript rendering.
    Returns extracted title and HTML content.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Get the full HTML
            html = await page.content()
            
            # Use readability to extract main content
            doc = Document(html)
            title = doc.title()
            content_html = doc.summary()
            
            # Get all images for later processing
            images = await page.query_selector_all('img')
            image_urls = []
            for img in images:
                src = await img.get_attribute('src')
                if src and src.startswith('http'):
                    image_urls.append(src)
            
            return {
                "title": title,
                "content": content_html,
                "images": image_urls,
                "url": url
            }
        finally:
            await browser.close()
