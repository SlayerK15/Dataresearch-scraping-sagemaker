import os
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection strings from environment
MONGO_RAW_URI = os.getenv("MONGO_RAW_URI", "mongodb://localhost:27017")
MONGO_PROCESSED_URI = os.getenv("MONGO_PROCESSED_URI", "mongodb://localhost:27017")

raw_client = MongoClient(MONGO_RAW_URI)
processed_client = MongoClient(MONGO_PROCESSED_URI)

raw_collection = raw_client.scraper_db.raw_html
processed_collection = processed_client.processed_db.cleaned_data

def extract_data(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("span", id="productTitle")
    price = soup.find("span", class_="a-price")
    return {
        "title": title.get_text(strip=True) if title else None,
        "price": price.get_text(strip=True) if price else None,
    }


def process_documents(limit=100):
    docs = raw_collection.find().limit(limit)
    for doc in docs:
        data = extract_data(doc.get("html", ""))
        data.update({"source_url": doc.get("url"), "timestamp": doc.get("timestamp")})
        processed_collection.insert_one(data)
        print(f"Processed {doc.get('url')}")

if __name__ == "__main__":
    process_documents()
