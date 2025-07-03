from fastapi import FastAPI, Body
import requests

SCRAPER_URL = "http://localhost:8000/scrape"
ANALYSIS_SERVICE = "http://localhost:8500/analyze"

app = FastAPI()

@app.post("/submit-urls")
def submit_urls(urls: list[str] = Body(...)):
    for url in urls:
        requests.get(SCRAPER_URL, params={"url": url})
    return {"status": "submitted", "count": len(urls)}

@app.get("/results")
def get_results(min_price: float | None = None, max_price: float | None = None):
    resp = requests.get(ANALYSIS_SERVICE, params={"min_price": min_price, "max_price": max_price})
    return resp.json()
