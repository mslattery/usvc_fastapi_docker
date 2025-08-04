# =================================================================
# File: auth/authService.py
# =================================================================
from fastapi import Request, Response

# We import the User model from its new location
from models.user import User


class AuthService:
    """Abstract Base Class for Authentication Services."""

    def authenticate(self, token: str) -> User:
        """
        Authenticates a user based on a token.
        This method must be implemented by concrete auth services.
        """
        raise NotImplementedError

    async def auth_login_redirect(self) -> Response:
        """
        Returns a RedirectResponse to the provider's login page.
        """
        raise NotImplementedError

    async def auth_callback(self, request: Request) -> Response:
        """
        Processes the authentication callback from the provider.
        """
        raise NotImplementedError

    async def auth_logout(self) -> Response:
        """
        Handles user logout.
        """
        raise NotImplementedError
