# =================================================================
# File: testAuth.py (Main Application)
# =================================================================
import logging
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Header, Request, Response as FastAPIResponse
from fastapi.responses import HTMLResponse

# Import all services and the base class/model
from auth.dependencies import get_auth_service_from_query, get_auth_service_from_header, get_current_active_user
from auth.authService import AuthService
from models.user import User

# Import the versioned routers
from api.v1 import endpoints as v1_endpoints
from api.v2 import endpoints as v2_endpoints

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s - %(filename)s - line:%(lineno)d - func:%(funcName)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Starting FastAPI application...")

# --- FastAPI App Initialization ---
app = FastAPI(
    title="usvc_fastapi_docker API",
    description="",
    version="1.0.0",
    contact={"name": "Slats", "email": "test@sncsoftware.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

# --- Include the API Router ---
app.include_router(v1_endpoints.router, prefix="/api/v1", tags=["v1"])
app.include_router(v2_endpoints.router, prefix="/api/v2", tags=["v2"])

# --- Authentication Flow Endpoints ---
# --- Authentication Flow Endpoints ---
@app.get("/auth/login", tags=["Authentication"])
async def login(
    auth_service: Annotated[AuthService, Depends(get_auth_service_from_query)]
) -> FastAPIResponse:
    logger.info("Login...")
    return await auth_service.auth_login_redirect()

@app.get("/auth/callback", tags=["Authentication"])
async def callback(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service_from_query)],
) -> FastAPIResponse:
    return await auth_service.auth_callback(request)

@app.get("/auth/logout", tags=["Authentication"])
async def logout(
    auth_service: Annotated[AuthService, Depends(get_auth_service_from_query)]
) -> FastAPIResponse:
    return await auth_service.auth_logout()

@app.get("/users/me", response_model=User, tags=["User"])
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Get the current authenticated user's details.
    This endpoint is protected and requires 'X-Auth-Provider' and 'Authorization' headers.
    """
    return current_user
        
# --- Root Endpoint ---
@app.get("/", tags=["General"])
def read_root():
    """Root endpoint with links to start the authentication process."""
    content = """
    <body>
        <h1>Authentication Demo</h1>
        <p>Choose a provider to log in:</p>
        <ul>
            <li><a href="/auth/login?provider=mock">Login with Mock Service</a></li>
            <li><a href="/auth/login?provider=google">Login with Google</a></li>
            <li><a href="/auth/login?provider=okta">Login with Okta (Not Implemented)</a></li>
        </ul>
    </body>
    """
    return HTMLResponse(content=content)