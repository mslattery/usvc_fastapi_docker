# tests/v1/test_endpoint.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from auth.dependencies import get_current_active_user
from models.user import User


@pytest.fixture(scope="module")
def client():
    """
    Create a TestClient instance that can be used in all tests in this module.
    """
    with TestClient(app) as c:
        yield c


# 1. Create a fake user object that mimics your real User model
# This is the user our mock dependency will return.
fake_user = User(
    id="google-fakeuser123",
    provider="google",
    email="fake.user@example.com",
    display_name="Fake User",
    disabled=False,
)


# 2. Create the override function
# This function will be swapped in to replace the real 'get_current_active_user'
async def override_get_current_active_user():
    """A mock dependency that returns a predefined user."""
    return fake_user


# --- The Tests ---


def test_read_item_as_authenticated_user(client: TestClient):
    """
    Tests the success case for GET /items/{item_id} with a valid user.
    """
    # 3. Apply the dependency override for this test
    # This tells FastAPI: "For any calls made with 'client', when you see
    # 'get_current_active_user', use 'override_get_current_active_user' instead."
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    # Make the request. We still include headers as a best practice,
    # even though our override function doesn't use them.
    item_id_to_test = 42
    response = client.get(
        f"/api/v1/items/{item_id_to_test}",
        headers={
            "X-Auth-Provider": "google",
            "Authorization": "google-fakeuser123",
        },
    )

    # Assert the response is successful
    assert response.status_code == 200

    # Assert the response payload is correct and includes the fake user's data
    expected_data = {
        "version": "v1",
        "item_details": {"id": item_id_to_test, "description": "This is a V2 item."},
        "owner_email": fake_user.email,
        "owner_provider": fake_user.provider,
        "owner_display_name": fake_user.display_name,
    }
    assert response.json() == expected_data

    # 4. Clean up the override after the test
    app.dependency_overrides = {}


def test_read_item_unauthorized(client: TestClient):
    """
    Tests the failure case for GET /items/{item_id} without authentication.
    """
    # Ensure no overrides are active for this test
    app.dependency_overrides = {}

    # Make the request WITHOUT headers
    response = client.get("/api/v1/items/42")

    # The real 'get_current_active_user' should execute and fail,
    # returning a 401 Unauthorized error.
    assert response.status_code == 401

    # You can also check the error detail if your dependency provides one
    assert (
        response.json()["detail"]
        == "Not authenticated. No valid cookie or authorization headers found."
    )
