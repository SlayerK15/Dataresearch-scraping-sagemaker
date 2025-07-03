from fastapi import FastAPI
from analyze_data import analyze

app = FastAPI()

@app.get("/analyze")
def analyze_endpoint(min_price: float | None = None, max_price: float | None = None):
    data = analyze(min_price=min_price, max_price=max_price)
    # Convert Mongo documents to serializable dicts
    for item in data:
        item['_id'] = str(item['_id'])
    return {"results": data}

