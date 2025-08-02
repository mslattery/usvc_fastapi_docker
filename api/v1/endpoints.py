from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi_limiter.depends import RateLimiter

# Authentication Library
from auth import get_current_user
from api.v1.healthcheck import perform_healthcheck

# Rate Limiting
from fastapi_simple_rate_limiter import rate_limiter

router = APIRouter()

# Healthcheck endpoint
@router.get(
    "/health",
    description="Healthcheck endpoint",
)
@rate_limiter(limit=3, seconds=5)
async def healthcheck():
    return await perform_healthcheck()

# Get Items by ID
@router.get("/items/{item_id}", description="Get an item by its ID")
async def read_item_v1(
    item_id: int, current_user: Annotated[dict, Depends(get_current_user)]
):
    return {
        "version": "v1",
        "item_id": item_id,
        "owner_email": current_user.get("email"),
    }
