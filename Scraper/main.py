from fastapi import FastAPI
from scraper import scrape_category
import logger

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
