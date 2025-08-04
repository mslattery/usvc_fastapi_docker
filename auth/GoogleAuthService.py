import jwt
from fastapi import HTTPException, Request, status, Response
from fastapi.responses import HTMLResponse
from fastapi_sso.sso.google import GoogleSSO
from starlette.config import Config
from starlette.datastructures import Secret

from auth.authService import AuthService
from models.user import User

config = Config(".env")
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", cast=str, default="YOUR_GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config(
    "GOOGLE_CLIENT_SECRET", cast=Secret, default="YOUR_GOOGLE_CLIENT_SECRET"
)
SECRET_KEY = config("SECRET_KEY", cast=Secret, default="A_RANDOM_SECRET_KEY")

google_sso = GoogleSSO(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=str(GOOGLE_CLIENT_SECRET),
    redirect_uri="http://localhost:8000/auth/callback?provider=google",
    allow_insecure_http=True,
    scope=["openid", "email", "profile"],
)


class GoogleAuthService(AuthService):
    """Implementation of AuthService for Google SSO."""

    def authenticate(self, token: str) -> User:
        """
        In a real app, this would decode the JWT from the cookie.
        For this example, we'll use the mock token from the header.
        """
        if not token or not token.startswith("google-"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token"
            )
        user_id = token.split("-")[1]
        return User(
            id=user_id,
            email=f"{user_id}@google.com",
            provider="google",
            display_name="Mock User",
        )

    async def auth_login_redirect(self) -> Response:
        async with google_sso:
            return await google_sso.get_login_redirect()

    async def auth_callback(self, request: Request) -> Response:
        async with google_sso:
            user = await google_sso.verify_and_process(request)
        if not user:
            return HTMLResponse(
                content="<p>Authentication failed.</p>", status_code=401
            )

        # Create a complete session data payload from the user object
        session_data = {
            "provider": user.provider,
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "picture": user.picture,
        }
        session_token = jwt.encode(session_data, str(SECRET_KEY), algorithm="HS256")

        response = HTMLResponse(
            content=f"<p>Authenticated as {user.display_name}. <a href='/api/v1/items/1'>Test API</a> | <a href='/auth/logout?provider=google'>Logout</a></p>"
        )
        response.set_cookie(
            key="access_token", value=f"Bearer {session_token}", httponly=True
        )
        return response

    async def auth_logout(self) -> Response:
        response = HTMLResponse(
            content="<p>You are logged out. <a href='/'>Home</a></p>"
        )
        response.delete_cookie("access_token")
        return response
