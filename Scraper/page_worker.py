import asyncio
import os
import random

from aiohttp import ClientSession

from scraper import scrape_page, timeout, PROXIES
import logger

async def main():
    page_url = os.getenv("PAGE_URL")
    if not page_url:
        logger.logging.error("PAGE_URL not set")
        return
    proxy = random.choice(PROXIES) if PROXIES else None
    async with ClientSession(timeout=timeout) as session:
        try:
            await scrape_page(session, page_url, proxy)
        except Exception as e:
            logger.logging.error(f"Error scraping {page_url}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
