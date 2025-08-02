from fastapi import APIRouter, Depends
from typing import Annotated
from auth import get_current_user # Import the shared dependency

router = APIRouter()

# Healthcheck endpoint
@router.get("/hc", description="Healthcheck endpoint")
@router.get("/health", description="Healthcheck endpoint")
async def healthcheck():
    return {"status": "ok"} 

@router.get("/items/{item_id}", description="Get an item by its ID")
async def read_item_v2(
    item_id: int,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    return {
        "version": "v2",
        "item_details": {
            "id": item_id,
            "description": "This is a V2 item."
        },
        "retrieved_by": current_user
    }