import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_PROCESSED_URI = os.getenv("MONGO_PROCESSED_URI", "mongodb://localhost:27017")
processed_client = MongoClient(MONGO_PROCESSED_URI)
processed_collection = processed_client.processed_db.cleaned_data


def analyze(min_price=None, max_price=None):
    query = {}
    if min_price:
        query.setdefault('price', {})['$gte'] = min_price
    if max_price:
        query.setdefault('price', {})['$lte'] = max_price

    results = processed_collection.find(query)
    return list(results)


if __name__ == "__main__":
    data = analyze()
    for item in data:
        print(item)
