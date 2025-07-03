import requests
from bs4 import BeautifulSoup
import time
import random
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logger

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client.scraper_db
collection = db.raw_html

def get_proxies():
    with open("proxies.txt", "r") as file:
        proxies = file.read().splitlines()
    return proxies

def get_random_proxy():
    proxies = get_proxies()
    return {"http": random.choice(proxies), "https": random.choice(proxies)}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_soup(url):
    proxy = get_random_proxy()
    response = requests.get(url, headers=headers, proxies=proxy)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def get_total_pages(soup):
    try:
        pagination = soup.select('span.s-pagination-item')  # Adjust based on website
        if pagination:
            return int(pagination[-1].text.strip())
    except:
        return 1
    return 1

def extract_product_urls(soup):
    links = soup.select("a.a-link-normal.s-no-outline")
    urls = ["https://amazon.in" + link['href'] for link in links if link.get('href')]
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
        soup = get_soup(base_url.format(page))
        product_urls = extract_product_urls(soup)
        
        for product_url in product_urls:
            scrape_product(product_url)
            time.sleep(random.uniform(1, 4))  # Rate limiting
