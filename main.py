# main.py
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(title="My Quick API")

@app.get("/")
def read_root():
    return {"message": "Hello from a Dockerized FastAPI!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

# Mangum is an adapter for running ASGI applications in a Lambda environment.
handler = Mangum(app)