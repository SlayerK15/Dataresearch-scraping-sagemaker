import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import time
import random
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logger
from urllib.parse import urljoin

load_dotenv()

SCRAPER_API_KEY = "APIKEY"  # Replace with a valid key

client = MongoClient(os.getenv("MONGO_URI"))
db = client.scraper_db
collection = db.raw_html

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_soup(url):
    scraperapi_url = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={url}"

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=5, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(scraperapi_url, headers=headers, timeout=60)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        logger.logging.error(f"ScraperAPI Request failed after retries: {e}")
        raise e

def get_total_pages(soup):
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

def scrape_product(url):
    soup = get_soup(url)
    collection.insert_one({
        "url": url,
        "html": str(soup),
        "timestamp": time.time()
    })
    logger.logging.info(f"Scraped and saved: {url}")

def scrape_category(url):
    first_page_soup = get_soup(url)
    total_pages = get_total_pages(first_page_soup)
    logger.logging.info(f"Total pages found: {total_pages}")

    base_url = url + "&page={}"

    for page in range(1, total_pages + 1):
        logger.logging.info(f"Scraping page: {page}")
        try:
            soup = get_soup(base_url.format(page))
            product_urls = extract_product_urls(soup)

            for product_url in product_urls:
                try:
                    scrape_product(product_url)
                except Exception as e:
                    logger.logging.error(f"Failed scraping product {product_url}: {e}")
                time.sleep(random.uniform(1, 3))  # Rate limiting

        except Exception as e:
            logger.logging.error(f"Failed scraping page {page}: {e}")
