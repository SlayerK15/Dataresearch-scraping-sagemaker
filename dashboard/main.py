from fastapi import FastAPI, Body
import httpx
from collections import Counter

SCRAPER_URL = "http://scraper:8000/scrape"
ANALYSIS_SERVICE = "http://sagemaker2:8500"

app = FastAPI()


@app.post("/submit-urls")
async def submit_urls(urls: list[str] = Body(...)):
    async with httpx.AsyncClient() as client:
        for url in urls:
            await client.get(SCRAPER_URL, params={"url": url})
    return {"status": "submitted", "count": len(urls)}


@app.get("/results")
async def get_results(
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    max_rating: float | None = None,
    sort_by: str | None = None,
    limit: int = 50,
):
    params = {
        "min_price": min_price,
        "max_price": max_price,
        "min_rating": min_rating,
        "max_rating": max_rating,
        "sort_by": sort_by,
        "limit": limit,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ANALYSIS_SERVICE}/analyze", params=params)
        return resp.json()


@app.get("/recommendations")
async def recommendations(field: str = "rating", limit: int = 5):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ANALYSIS_SERVICE}/top", params={"field": field, "limit": limit})
        return resp.json()


@app.get("/keywords")
async def keywords(limit: int = 10):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ANALYSIS_SERVICE}/analyze", params={"limit": 100})
    data = resp.json().get("results", [])
    titles = " ".join(item.get("title", "") for item in data)
    words = [w.lower() for w in titles.split() if len(w) > 4]
    common = Counter(words).most_common(limit)
    return {"keywords": common}
