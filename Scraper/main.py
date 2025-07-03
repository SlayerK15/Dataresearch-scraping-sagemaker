from fastapi import FastAPI, Body
import asyncio
from scraper import scrape_category, scrape_multiple
import logger
from typing import List

app = FastAPI()

@app.get("/scrape")
async def scrape(url: str):
    logger.logging.info(f"Scraping initiated for URL: {url}")
    try:
        await scrape_category(url)
        return {"status": "success", "url": url}
    except Exception as e:
        logger.logging.error(f"Error during scrape: {str(e)}")
        return {"status": "failed", "error": str(e)}


@app.post("/scrape-batch")
async def scrape_batch(urls: List[str] = Body(...)):
    logger.logging.info(f"Batch scraping initiated for {len(urls)} URLs")
    try:
        await scrape_multiple(urls)
        return {"status": "submitted", "count": len(urls)}
    except Exception as e:
        logger.logging.error(f"Batch scrape error: {e}")
        return {"status": "failed", "error": str(e)}
