from fastapi import FastAPI
from analyze_data import (
    analyze,
    aggregate_average_price,
    aggregate_average_rating,
    top_products,
)

app = FastAPI()

@app.get("/analyze")
def analyze_endpoint(
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    max_rating: float | None = None,
    sort_by: str | None = None,
    limit: int = 50,
):
    data = analyze(
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        max_rating=max_rating,
        sort_by=sort_by,
        limit=limit,
    )
    # Convert Mongo documents to serializable dicts
    for item in data:
        item['_id'] = str(item['_id'])
    avg_price = aggregate_average_price()
    avg_rating = aggregate_average_rating()
    return {
        "results": data,
        "average_price": avg_price,
        "average_rating": avg_rating,
    }


@app.get("/top")
def top_endpoint(field: str = "rating", limit: int = 5):
    data = top_products(field=field, limit=limit)
    for item in data:
        item['_id'] = str(item['_id'])
    return {"results": data}

