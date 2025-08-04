import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi_sso.sso.google import GoogleSSO
from fastapi.security import OAuth2PasswordBearer
from okta_jwt.jwt import validate_token as validate_locally

from jose import jwt

# Import the versioned routers
from api.v1 import endpoints as v1_endpoints
from api.v2 import endpoints as v2_endpoints

from starlette.config import Config
from starlette.datastructures import Secret

# Config will be read from environment variables and/or ".env" files.
config = Config(".env")
DEBUG = config('DEBUG', cast=bool, default=False)
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", cast=str)
GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET", cast=Secret)
SECRET_KEY = config("SECRET_KEY", cast=Secret)

# Load credentials from environment variables
# GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
# SECRET_KEY = os.environ.get("SECRET_KEY")

# App definition
app = FastAPI(
    title="usvc_fastapi_docker API",
    description="",
    version="1.0.0",
    contact={"name": "Slats", "email": "test@sncsoftware.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

def retrieve_token(authorization, issuer, scope='items'):
    headers = {
        'accept': 'application/json',
        'authorization': authorization,
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'scope': scope,
    }
    url = issuer + '/v1/token'

    response = httpx.post(url, headers=headers, data=data)

    if response.status_code == httpx.codes.OK:
        return response.json()
    else:
        raise HTTPException(status_code=400, detail=response.text)



# Initialize Google SSO
google_sso = GoogleSSO(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=str(GOOGLE_CLIENT_SECRET),
    # redirect_uri="https://eiq13rppi9.execute-api.us-east-1.amazonaws.com/auth/callback",
    redirect_uri="http://localhost:8989/auth/callback",
    allow_insecure_http=True,  # Use False in production with HTTPS
)


# --- SSO and Auth Routes ---
@app.get("/auth/login", tags=["auth"])
async def auth_login():
    """Redirects the user to Google for authentication."""
    # Use the SSO object as a context manager for security
    async with google_sso:
        return await google_sso.get_login_redirect()


@app.get("/auth/callback", tags=["auth"])
async def auth_callback(request: Request):
    """Processes the authentication response from Google."""
    # Use the SSO object as a context manager for security
    async with google_sso:
        user = await google_sso.verify_and_process(request)

    if not user:
        return HTMLResponse(
            content="<p>Authentication failed. Please try again.</p>", status_code=401
        )

    session_token = jwt.encode(user.model_dump(), str(SECRET_KEY), algorithm="HS256")

    response = HTMLResponse(
        content="<p>Successfully authenticated! You can now use the API. <a href='/api/v1/items/1'>Try V1</a> | <a href='/api/v2/items/1'>Try V2</a> | <a href='/auth/logout'>Logout</a></p>"
    )
    response.set_cookie(
        key="access_token", value=f"Bearer {session_token}", httponly=True
    )
    return response


@app.get("/auth/logout", tags=["auth"])
async def auth_logout(response: Response):
    response = HTMLResponse(
        content="<p>You have been logged out. <a href='/'>Home</a></p>"
    )
    response.delete_cookie("access_token")
    return response


# --- Mount API Version Routers ---

app.include_router(v1_endpoints.router, prefix="/api/v1", tags=["v1"])
app.include_router(v2_endpoints.router, prefix="/api/v2", tags=["v2"])


@app.get("/", tags=["Root"])
def read_root():
    return HTMLResponse(
        '<h1>SSO Protected API</h1><a href="/auth/login">Login with Google</a>'
    )
