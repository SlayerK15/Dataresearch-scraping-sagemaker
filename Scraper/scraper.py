import asyncio
import random
import os
import subprocess
import uuid
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from pymongo import MongoClient
from dotenv import load_dotenv

import logger

load_dotenv()

SCRAPER_API_KEY = "APIKEY"  # Replace with a valid key

client = MongoClient(os.getenv("MONGO_URI"))
db = client.scraper_db
collection = db.raw_html

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

def load_proxies():
    path = os.path.join(os.path.dirname(__file__), "proxies.txt")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [p.strip() for p in f if p.strip()]

PROXIES = load_proxies()

timeout = ClientTimeout(total=60)

async def fetch(session: ClientSession, url: str, proxy: str | None = None) -> BeautifulSoup:
    scraperapi_url = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={url}"
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        async with session.get(scraperapi_url, headers=headers, proxy=proxy) as resp:
            resp.raise_for_status()
            text = await resp.text()
            return BeautifulSoup(text, "html.parser")
    except Exception as e:
        logger.logging.error(f"Request failed: {e}")
        raise

def get_total_pages(soup: BeautifulSoup) -> int:
    try:
        pagination = soup.select('span.s-pagination-item')
        if pagination:
            return int(pagination[-1].text.strip())
    except Exception as e:
        logger.logging.error(f"Pagination extraction error: {e}")
        return 1
    return 1

# Corrected URL extraction
def extract_product_urls(soup):
    links = soup.select("a.a-link-normal.s-no-outline")
    urls = []
    for link in links:
        href = link.get('href')
        if href:
            full_url = urljoin("https://www.amazon.in", href)
            urls.append(full_url)
    return urls

async def scrape_product(session: ClientSession, url: str, proxy: str | None = None):
    soup = await fetch(session, url, proxy)
    collection.insert_one({
        "url": url,
        "html": str(soup),
        "timestamp": asyncio.get_event_loop().time()
    })
    logger.logging.info(f"Scraped and saved: {url}")

async def scrape_page(session: ClientSession, page_url: str, proxy: str | None = None):
    soup = await fetch(session, page_url, proxy)
    product_urls = extract_product_urls(soup)
    tasks = [scrape_product(session, purl, proxy) for purl in product_urls]
    await asyncio.gather(*tasks)
    await asyncio.sleep(random.uniform(1, 2))

SCRAPER_IMAGE = os.getenv("SCRAPER_WORKER_IMAGE", "scraper")

def launch_scraper_container(page_url: str):
    mongo_uri = os.getenv("MONGO_URI")
    name = f"scraper-{uuid.uuid4().hex[:6]}"
    cmd = [
        "docker",
        "run",
        "-d",
        "--rm",
        "--name",
        name,
        "-e",
        f"MONGO_URI={mongo_uri}",
        "-e",
        f"PAGE_URL={page_url}",
        SCRAPER_IMAGE,
        "python",
        "page_worker.py",
    ]
    try:
        subprocess.run(cmd, check=True)
        logger.logging.info(f"Launched container {name} for {page_url}")
    except Exception as e:
        logger.logging.error(f"Container launch failed for {page_url}: {e}")

async def scrape_category(url: str):
    async with ClientSession(timeout=timeout) as session:
        proxy = random.choice(PROXIES) if PROXIES else None
        first_page_soup = await fetch(session, url, proxy)
        total_pages = get_total_pages(first_page_soup)
        logger.logging.info(f"Total pages found: {total_pages}")

    base_url = url + "&page={}"
    for page in range(1, total_pages + 1):
        page_url = base_url.format(page)
        logger.logging.info(f"Launching container for page {page}")
        launch_scraper_container(page_url)

async def scrape_multiple(urls: list[str]):
    for url in urls:
        await scrape_category(url)
