import os
from pymongo import MongoClient, DESCENDING, ASCENDING
from dotenv import load_dotenv

load_dotenv()

MONGO_PROCESSED_URI = os.getenv("MONGO_PROCESSED_URI", "mongodb://localhost:27017")
processed_client = MongoClient(MONGO_PROCESSED_URI)
processed_collection = processed_client.processed_db.cleaned_data


def analyze(min_price=None, max_price=None, min_rating=None, max_rating=None, sort_by=None, limit=50):
    query = {}
    if min_price is not None:
        query.setdefault('price', {})['$gte'] = min_price
    if max_price is not None:
        query.setdefault('price', {})['$lte'] = max_price
    if min_rating is not None:
        query.setdefault('rating', {})['$gte'] = min_rating
    if max_rating is not None:
        query.setdefault('rating', {})['$lte'] = max_rating

    cursor = processed_collection.find(query)
    if sort_by:
        direction = DESCENDING if sort_by.startswith('-') else ASCENDING
        field = sort_by.lstrip('+-')
        cursor = cursor.sort(field, direction)
    if limit:
        cursor = cursor.limit(limit)
    return list(cursor)


def aggregate_average_price():
    pipeline = [
        {"$match": {"price": {"$ne": None}}},
        {"$group": {"_id": None, "avg_price": {"$avg": "$price"}}},
    ]
    agg = list(processed_collection.aggregate(pipeline))
    return agg[0]["avg_price"] if agg else None


def aggregate_average_rating():
    pipeline = [
        {"$match": {"rating": {"$ne": None}}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}},
    ]
    agg = list(processed_collection.aggregate(pipeline))
    return agg[0]["avg_rating"] if agg else None


def top_products(field: str = "rating", limit: int = 5):
    direction = DESCENDING
    cursor = processed_collection.find({field: {"$ne": None}}).sort(field, direction).limit(limit)
    return list(cursor)


if __name__ == "__main__":
    data = analyze()
    for item in data:
        print(item)
