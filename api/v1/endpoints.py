from fastapi import APIRouter, Depends
from typing import Annotated
from auth import get_current_user # Import the shared dependency

router = APIRouter()

@router.get("/items/{item_id}", description="Get an item by its ID")
async def read_item_v1(
    item_id: int,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    return {
        "version": "v1",
        "item_id": item_id,
        "owner_email": current_user.get("email")
    }