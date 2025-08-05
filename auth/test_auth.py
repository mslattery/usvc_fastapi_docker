# auth/test_auth.py

import pytest
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse, RedirectResponse
from unittest.mock import AsyncMock

from .dependencies import get_auth_service_from_query
from app.main import app


@pytest.fixture
def client():
    """
    A fixture to provide a fresh TestClient for EACH test function.
    This ensures dependency overrides from one test don't affect another.
    """
    # We must clear overrides at the beginning of each test
    app.dependency_overrides = {}
    with TestClient(app) as c:
        yield c
    # And clear them again after, just to be safe
    app.dependency_overrides = {}


# --- Mock Auth Service ---
class MockAuthService:
    def __init__(self, provider: str, success: bool = True):
        self.provider = provider
        self.auth_login_redirect = AsyncMock(
            return_value=RedirectResponse(url=f"https://fake-auth.com/{provider}/login")
        )
        if success:
            successful_response = RedirectResponse(url="/dashboard")
            successful_response.set_cookie(
                key="session_token", value="fake-session-id-12345"
            )
            self.auth_callback = AsyncMock(return_value=successful_response)
        else:
            failed_response = JSONResponse(
                status_code=403,
                content={"detail": "Authentication failed: Invalid state or code"},
            )
            self.auth_callback = AsyncMock(return_value=failed_response)
        # Mock for the /auth/logout endpoint
        logout_response = RedirectResponse(url="/")
        # Simulate clearing the cookie by setting its max-age to 0
        logout_response.delete_cookie(key="session_token")
        self.auth_logout = AsyncMock(return_value=logout_response)


# --- test_login_redirects_for_each_provider (This test was already correct) ---
@pytest.mark.parametrize("provider_name", ["google", "okta", "mock_service"])
def test_login_redirects_for_each_provider(client: TestClient, provider_name: str):
    # This test doesn't check mock calls, so its original structure is fine.
    def override_get_auth_service():
        return MockAuthService(provider=provider_name)

    app.dependency_overrides[get_auth_service_from_query] = override_get_auth_service
    response = client.get(
        f"/auth/login?provider={provider_name}", follow_redirects=False
    )
    assert response.status_code == 307
    assert (
        response.headers.get("location")
        == f"https://fake-auth.com/{provider_name}/login"
    )
    app.dependency_overrides = {}


# --- CORRECTED CALLBACK TESTS ---


def test_auth_callback_success(client: TestClient):
    """
    Tests the success case for the callback.
    """
    provider = "google"

    # STEP 1: Create the mock instance that will be shared.
    mock_service_instance = MockAuthService(provider=provider, success=True)

    # STEP 2: The override function returns the SHARED instance.
    def override_get_auth_service():
        return mock_service_instance

    # Apply the override
    app.dependency_overrides[get_auth_service_from_query] = override_get_auth_service

    # Make the request
    response = client.get(
        f"/auth/callback?provider={provider}&code=some-auth-code&state=some-state-value",
        follow_redirects=False,
    )

    # STEP 3: Assert against the SHARED instance. This will now work.
    mock_service_instance.auth_callback.assert_called_once()

    # The rest of your assertions
    assert response.status_code == 307
    assert response.headers.get("location") == "/dashboard"
    assert "session_token" in response.cookies
    assert response.cookies["session_token"] == "fake-session-id-12345"

    # Clean up
    app.dependency_overrides = {}


def test_auth_callback_failure(client: TestClient):
    """
    Tests the failure case for the callback.
    """
    provider = "google"

    # Apply the same correct pattern here for consistency and correctness
    mock_service_instance = MockAuthService(provider=provider, success=False)

    def override_get_auth_service():
        return mock_service_instance

    app.dependency_overrides[get_auth_service_from_query] = override_get_auth_service

    response = client.get(
        f"/auth/callback?provider={provider}&error=access_denied",
        follow_redirects=False,
    )

    mock_service_instance.auth_callback.assert_called_once()
    assert response.status_code == 403
    assert response.json() == {"detail": "Authentication failed: Invalid state or code"}
    assert "session_token" not in response.cookies

    app.dependency_overrides = {}


def test_logout(client: TestClient):
    """
    Tests that the logout endpoint clears the session cookie
    and redirects the user to the homepage.
    """
    provider = "google"

    # 1. Create a mock RedirectResponse that we will tell our mock to return
    # This response simulates clearing a cookie and redirecting.
    expected_logout_response = RedirectResponse(url="/")
    expected_logout_response.delete_cookie("session_token")

    # 2. Create a mock service instance
    mock_service_instance = MockAuthService(provider=provider)
    # CRITICAL: Tell its auth_logout mock method what to return
    mock_service_instance.auth_logout.return_value = expected_logout_response

    # 3. Set up the dependency override to return our specific instance
    def override_get_auth_service():
        return mock_service_instance

    app.dependency_overrides[get_auth_service_from_query] = override_get_auth_service

    # 4. Set a cookie on the client to simulate a logged-in user
    client.cookies.set("session_token", "fake-session-id-12345")

    # 5. Make the request
    response = client.get(
        f"/auth/logout?provider={provider}",
        follow_redirects=False,
    )

    # --- DEBUGGING STEP ---
    # If the test fails on the status_code assert, the print statement below
    # will run, showing you what the body of the 200 OK response was.
    if response.status_code != 307:
        print("Response was not a redirect. Body:", response.text)

    # 6. Assertions
    # Check that the status code is for a redirect
    assert response.status_code == 307

    # Check that the redirect location is correct
    assert response.headers.get("location") == "/"

    # Check that the service method was called
    mock_service_instance.auth_logout.assert_called_once()

    # Check that the cookie was cleared
    set_cookie_header = response.headers.get("set-cookie")
    assert set_cookie_header.startswith("session_token=")
    assert "Max-Age=0" in set_cookie_header
