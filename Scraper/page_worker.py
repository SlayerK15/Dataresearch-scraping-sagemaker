import asyncio
import os
import random

from aiohttp import ClientSession

from scraper import scrape_page, timeout, PROXIES
import logger

async def main():
    urls_env = os.getenv("PAGE_URLS")
    if not urls_env:
        logger.logging.error("PAGE_URLS not set")
        return
    page_urls = [u for u in urls_env.split(',') if u]
    proxy = random.choice(PROXIES) if PROXIES else None
    async with ClientSession(timeout=timeout) as session:
        for page_url in page_urls:
            try:
                await scrape_page(session, page_url, proxy)
            except Exception as e:
                logger.logging.error(f"Error scraping {page_url}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
