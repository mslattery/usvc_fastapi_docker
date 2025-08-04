# =================================================================
# auth/MockAuthService.py
# =================================================================
import jwt
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.config import Config
from starlette.datastructures import Secret

from auth.authService import AuthService
from models.user import User

# Reuse the same secret key for consistency
config = Config(".env")
SECRET_KEY = config("SECRET_KEY", cast=Secret, default="A_RANDOM_SECRET_KEY")

class MockAuthService(AuthService):
    """A mock authentication service for local testing."""

    def authenticate(self, token: str) -> User:
        """Authenticates a user from a simple mock token."""
        if not token or not token.startswith("mock-"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Mock token")
        user_id = token.split("-")[1]
        return User(id=user_id, email=f"{user_id}@mock.com", provider="mock", display_name=f"Mock User {user_id}")

    async def auth_login_redirect(self) -> Response:
        """Redirects to the mock callback endpoint to simulate a login."""
        # In a real flow, the provider would redirect here after user login.
        # We are simulating this by redirecting directly.
        return RedirectResponse(url="/auth/callback?provider=mock&code=mock_success_code")

    async def auth_callback(self, request: Request) -> Response:
        """
        Simulates processing the callback from the provider.
        Creates a session token and sets it in a cookie.
        """
        # In a real flow, we'd exchange the 'code' for a user token. Here we just invent a user.
        mock_user = {
            "provider": "mock",
            "id": "mockuser123",
            "email": "test@mock.com",
            "display_name": "Local Test User",
            "picture": "https://example.com/mockuser"
        }
        session_token = jwt.encode(mock_user, str(SECRET_KEY), algorithm="HS256")

        response = HTMLResponse(
            content=f"""<p>Authenticated as {mock_user['display_name']}. 
            <a href='/api/v1/items/123'>Test API v1</a>            
            | <a href='/api/v2/items/123'>Test API v2</a>            
            | <a href='/auth/logout?provider=mock'>Logout</a></p>"""
        )
        response.set_cookie(key="access_token", value=f"Bearer {session_token}", httponly=True)
        return response

    async def auth_logout(self) -> Response:
        """Logs the user out by clearing the session cookie."""
        response = HTMLResponse(content="<p>You are logged out. <a href='/'>Home</a></p>")
        response.delete_cookie("access_token")
        return response
