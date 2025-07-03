import os
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection strings from environment
MONGO_RAW_URI = os.getenv("MONGO_RAW_URI", "mongodb://localhost:27017")
MONGO_PROCESSED_URI = os.getenv("MONGO_PROCESSED_URI", "mongodb://localhost:27017")

raw_client = MongoClient(MONGO_RAW_URI)
processed_client = MongoClient(MONGO_PROCESSED_URI)

raw_collection = raw_client.scraper_db.raw_html
processed_collection = processed_client.processed_db.cleaned_data

def _to_float(text: str | None) -> float | None:
    if not text:
        return None
    numbers = re.findall(r"[\d,.]+", text)
    if not numbers:
        return None
    return float(numbers[0].replace(",", ""))


def extract_data(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("span", id="productTitle")
    price = soup.select_one("span.a-price span.a-offscreen") or soup.find("span", id="priceblock_ourprice")
    image = soup.find("img", id="landingImage")
    rating = soup.find("span", class_="a-icon-alt")
    description = soup.select_one("#productDescription")
    features = [li.get_text(strip=True) for li in soup.select("#feature-bullets li")]
    asin_field = soup.find("input", id="ASIN")

    return {
        "title": title.get_text(strip=True) if title else None,
        "price": _to_float(price.get_text()) if price else None,
        "image_url": image["src"] if image and image.has_attr("src") else None,
        "rating": _to_float(rating.get_text()) if rating else None,
        "description": description.get_text(strip=True) if description else None,
        "features": features,
        "asin": asin_field["value"] if asin_field and asin_field.has_attr("value") else None,
    }


def process_documents(limit=100):
    docs = raw_collection.find().limit(limit)
    for doc in docs:
        data = extract_data(doc.get("html", ""))
        data.update({"source_url": doc.get("url"), "timestamp": doc.get("timestamp")})
        processed_collection.update_one(
            {"source_url": data["source_url"]},
            {"$set": data},
            upsert=True
        )
        print(f"Processed {doc.get('url')}")

if __name__ == "__main__":
    process_documents()
