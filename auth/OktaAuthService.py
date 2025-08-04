# =================================================================
# File: auth/OktaAuthService.py (Placeholder)
# =================================================================
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from auth.authService import AuthService
from models.user import User

class OktaAuthService(AuthService):
    """Placeholder implementation for Okta SSO."""
    def authenticate(self, token: str) -> User:
        raise NotImplementedError("Okta authentication not implemented.")

    async def auth_login_redirect(self) -> Response:
        return JSONResponse(
            status_code=501,
            content={"detail": "Okta login not implemented."}
        )

    async def auth_callback(self, request: Request) -> Response:
        return JSONResponse(
            status_code=501,
            content={"detail": "Okta callback not implemented."}
        )
    
    async def auth_logout(self) -> Response:
        return JSONResponse(
            status_code=501,
            content={"detail": "Okta logout not implemented."}
        )
