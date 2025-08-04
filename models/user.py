# =================================================================
# File: models/user.py
# =================================================================
from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(..., description="The user's unique ID from the provider.")
    email: str = Field(..., description="The user's email address.")
    provider: str = Field(..., description="The authentication provider (e.g., 'google').")
    display_name: str | None = Field(None, description="The user's display name.")
    picture: str | None = Field(None, description="URL to the user's profile picture.")