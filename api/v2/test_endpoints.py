# tests/v2/test_endpoint.py

import pytest
from fastapi.testclient import TestClient

# You'll need a main 'app' instance that includes your router.
# Let's assume you have a file 'main.py' that creates the app.
from app.main import app


@pytest.fixture(scope="module")
def client():
    """
    Create a TestClient instance that can be used in all tests in this module.
    """
    with TestClient(app) as c:
        yield c


def test_health_check(client: TestClient):
    """
    Tests the /api/v2/health endpoint.
    """
    # 1. Make a request to the health endpoint
    # The prefix '/api/v2' is added when you include the router in your main app
    response = client.get("/api/v2/health")

    # 2. Assert the HTTP status code is 200 (OK)
    assert (
        response.status_code == 200
    ), f"Expected status code 200, but got {response.status_code}"

    # 3. Assert the response body is the expected JSON
    expected_response = {"status": "ok"}
    assert (
        response.json() == expected_response
    ), f"Expected {expected_response}, but got {response.json()}"

    # 4. (Optional but good practice) Assert the content-type header
    assert response.headers["content-type"] == "application/json"
