from fastapi import FastAPI, Body
from scraper import scrape_category
import logger
from typing import List

app = FastAPI()

@app.get("/scrape")
def scrape(url: str):
    logger.logging.info(f"Scraping initiated for URL: {url}")
    try:
        scrape_category(url)
        return {"status": "success", "url": url}
    except Exception as e:
        logger.logging.error(f"Error during scrape: {str(e)}")
        return {"status": "failed", "error": str(e)}


@app.post("/scrape-batch")
def scrape_batch(urls: List[str] = Body(...)):
    logger.logging.info(f"Batch scraping initiated for {len(urls)} URLs")
    results = []
    for url in urls:
        try:
            scrape_category(url)
            results.append({"url": url, "status": "success"})
        except Exception as e:
            logger.logging.error(f"Batch scrape error for {url}: {e}")
            results.append({"url": url, "status": "failed", "error": str(e)})
    return {"results": results}
