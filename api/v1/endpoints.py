# =================================================================
# api/v1/endpoint.py
# =================================================================
from fastapi import APIRouter, Depends
from typing import Annotated

# Import the new dependency and the User model
from auth.dependencies import get_current_active_user
from models.user import User

router = APIRouter()

# Healthcheck endpoint
@router.get("/health", description="Healthcheck endpoint")
async def healthcheck():
    return {"status": "ok"} 

@router.get("/items/{item_id}", description="Get an item by its ID", response_model=dict)
async def read_item_v1(
    item_id: int,
    # This is the key change: Depend on the new function to get the user
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    This endpoint is now protected. To access it, you must provide:
    - 'X-Auth-Provider': 'google' or 'okta'
    - 'Authorization': 'google-someuserid'
    """
    return {
        "version": "v1",
        "item_details": {
            "id": item_id,
            "description": "This is a V2 item."
        },
        "owner_email": current_user.email,
        "owner_provider": current_user.provider,
        "owner_display_name": current_user.display_name,
    }
