import os
from pymongo import MongoClient
from bs4 import BeautifulSoup
import re
from collections import defaultdict
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

    category, subcategory = classify_category(soup, title.get_text() if title else "")
    specs = {}
    if subcategory == "laptop":
        specs = extract_laptop_specs(soup)

    return {
        "title": title.get_text(strip=True) if title else None,
        "price": _to_float(price.get_text()) if price else None,
        "image_url": image["src"] if image and image.has_attr("src") else None,
        "rating": _to_float(rating.get_text()) if rating else None,
        "description": description.get_text(strip=True) if description else None,
        "features": features,
        "asin": asin_field["value"] if asin_field and asin_field.has_attr("value") else None,
        "category": category,
        "subcategory": subcategory,
        "specs": specs,
    }


def classify_category(soup: BeautifulSoup, title: str) -> tuple[str | None, str | None]:
    text = " ".join([title.lower(), soup.get_text(" ").lower()])
    if any(word in text for word in ["laptop", "notebook"]):
        return "electronics", "laptop"
    if any(word in text for word in ["smartphone", "mobile phone", "cell phone"]):
        return "electronics", "mobile"
    if any(word in text for word in ["television", "tv", "oled", "lcd"]):
        return "electronics", "television"
    if "electronics" in text:
        return "electronics", None
    return None, None


def extract_laptop_specs(soup: BeautifulSoup) -> dict:
    specs = defaultdict(str)
    table = soup.find(id="productDetails_techSpec_section_1") or soup.find("table", id="technicalSpecifications")
    if not table:
        table = soup.find("table", {"class": "tech-specs"})
    if not table:
        return specs
    for row in table.find_all("tr"):
        header = row.find("th")
        value_td = row.find("td")
        if not header or not value_td:
            continue
        key = header.get_text(strip=True).lower()
        value = value_td.get_text(strip=True)
        if "processor" in key or "cpu" in key:
            specs["cpu"] = value
        elif "model" == key or "model" in key:
            specs["model"] = value
        elif "gpu" in key or "graphics" in key:
            specs["gpu"] = value
        elif "ram" in key or "memory" in key:
            specs["ram"] = value
        elif "storage" in key or "hard drive" in key or "ssd" in key:
            specs["storage"] = value
        elif "screen" in key or "display" in key:
            specs["display"] = value
    return dict(specs)


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
