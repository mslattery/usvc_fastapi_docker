# main.py
from fastapi import FastAPI
from mangum import Mangum
from starlette.requests import Request
import cowsay


app = FastAPI(title="My Quick API")


@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
async def shutdown_event():
    pass


@app.get("/")
def read_root(request: Request):
    return {"message": cowsay.get_output_string("tux", "Ding Ding")}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


# Mangum is an adapter for running ASGI applications in a Lambda environment.
handler = Mangum(
    app,
    lifespan="auto",
    api_gateway_base_path=None,
    custom_handlers=None,
    text_mime_types=None,
)
