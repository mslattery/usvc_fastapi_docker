import jwt
import logging
from jwt.exceptions import PyJWTError
from fastapi import Depends, HTTPException, status, Header, Query, Request
from typing import Annotated
from starlette.config import Config
from starlette.datastructures import Secret

from auth.GoogleAuthService import GoogleAuthService
from auth.OktaAuthService import OktaAuthService
from auth.MockAuthService import MockAuthService
from auth.authService import AuthService
from models.user import User

# Get a logger instance for this module. The name will be 'some_module'
log = logging.getLogger(__name__)

config = Config(".env")
SECRET_KEY = config("SECRET_KEY", cast=Secret, default="A_RANDOM_SECRET_KEY")


def get_auth_service_from_header(
    x_auth_provider: Annotated[str | None, Header()] = None,
) -> AuthService:
    """Dependency that provides an auth service based on the 'X-Auth-Provider' header."""
    if x_auth_provider == "google":
        return GoogleAuthService()
    elif x_auth_provider == "okta":
        return OktaAuthService()
    elif x_auth_provider == "mock":
        return MockAuthService()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Auth-Provider header is missing or invalid. Use 'google', 'okta', or 'mock'.",
        )


def get_auth_service_from_query(
    provider: Annotated[str, Query(enum=["google", "okta", "mock"])],
) -> AuthService:
    log.info(f"get_auth_service_from_query called with provider: {provider}")
    """Dependency that provides an auth service based on the 'provider' query parameter."""
    if provider == "google":
        return GoogleAuthService()
    elif provider == "okta":
        return OktaAuthService()
    elif provider == "mock":
        return MockAuthService()


def get_current_active_user(
    request: Request,
    x_auth_provider: Annotated[str | None, Header()] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """
    The primary dependency for protecting endpoints.
    It authenticates a user in one of two ways, in order of priority:
    1. From the 'access_token' cookie (for browser-based sessions).
    2. From the 'X-Auth-Provider' and 'Authorization' headers (for API clients).
    """
    # 1. Try to authenticate from the cookie
    token = request.cookies.get("access_token")
    if token:
        if token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
        try:
            payload = jwt.decode(token, str(SECRET_KEY), algorithms=["HS256"])
            # The payload from the JWT is used to create the User model
            return User(**payload)
        except PyJWTError:
            # This will be caught by the final exception handler
            pass

    # 2. Fallback to authenticating from headers for API clients
    if x_auth_provider and authorization:
        try:
            auth_service = get_auth_service_from_header(x_auth_provider)
            return auth_service.authenticate(token=authorization)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during header authentication: {e}",
            )

    # 3. If neither method works, deny access.
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. No valid cookie or authorization headers found.",
        headers={"WWW-Authenticate": "Bearer"},
    )
