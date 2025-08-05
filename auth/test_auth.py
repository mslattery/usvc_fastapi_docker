# auth/test_auth.py

import pytest
from fastapi.testclient import TestClient
from fastapi.responses import RedirectResponse
from unittest.mock import AsyncMock

# Use a relative import because test_auth.py is a sibling to dependencies.py
from .dependencies import get_auth_service_from_query

# To get the 'app' from a different top-level directory, we need to
# ensure pytest is run from the project root.
from app.main import app


@pytest.fixture(scope="module")
def client():
    """
    A fixture to provide a TestClient instance for the tests.
    Using 'with' ensures that startup and shutdown events are handled.
    """
    with TestClient(app) as c:
        yield c


# --- Mock Auth Service ---
class MockAuthService:
    def __init__(self, provider: str):
        self.provider = provider
        self.auth_login_redirect = AsyncMock(
            return_value=RedirectResponse(url=f"https://fake-auth.com/{provider}/login")
        )


@pytest.mark.parametrize("provider_name", ["google", "okta", "mock_service"])
def test_login_redirects_for_each_provider(client: TestClient, provider_name: str):
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
