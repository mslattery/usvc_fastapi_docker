# models/test_user.py

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

# --- Imports for Colocated Tests ---

# Use a relative import because test_user.py is a sibling to user.py
from .user import User

# Imports for the endpoint tests
from app.main import app
from auth.dependencies import get_current_active_user


# --- Part 1: Unit Tests for the User Model ---


def test_user_model_creation_success():
    """Tests successful creation of the User model with valid data."""
    user_data = {
        "id": "google-123",
        "provider": "google",
        "email": "valid.email@example.com",
        "display_name": "Test User",
    }
    user = User(**user_data)

    assert user.id == user_data["id"]
    assert user.email == user_data["email"]
    # Check that the default value was applied correctly
    assert user.disabled is False


def test_user_model_invalid_email():
    """Tests that Pydantic raises a ValidationError for a bad email."""
    invalid_data = {
        "id": "google-456",
        "provider": "google",
        "email": "not-a-valid-email",  # This is invalid
        "display_name": "Another User",
    }
    # Use pytest.raises as a context manager to assert that an error is thrown
    with pytest.raises(ValidationError) as excinfo:
        User(**invalid_data)

    # Optionally, check the error message for more detail
    assert "value is not a valid email address" in str(excinfo.value)


def test_user_model_missing_required_field():
    """Tests that Pydantic raises a ValidationError if a required field is missing."""
    incomplete_data = {
        "provider": "google",
        "email": "test@example.com",
    }
    with pytest.raises(ValidationError) as excinfo:
        User(**incomplete_data)

    errors = excinfo.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("id",)  # The location of the error is the 'id' field
    assert errors[0]["type"] == "missing"


# --- Part 2: Integration Tests for the /users/me Endpoint ---


@pytest.fixture
def client():
    """Provides a fresh, isolated TestClient for each test function."""
    app.dependency_overrides = {}
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}


def test_read_current_user_success(client: TestClient):
    """
    Tests the success case for GET /users/me with a valid, authenticated user.
    """
    fake_user_data = {
        "id": "google-123456789",
        "provider": "google",
        "email": "test.user@example.com",
        "display_name": "Test User",
        "disabled": False,
        # Add the missing field to your source data for completeness
        "picture": None,
    }
    fake_user = User(**fake_user_data)

    def override_get_current_active_user():
        return fake_user

    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    response = client.get("/users/me")

    assert response.status_code == 200

    # Assert against the dynamically generated dict from the Pydantic model
    # This automatically includes all fields, even those with default values.
    assert response.json() == fake_user.model_dump()


def test_read_current_user_unauthorized(client: TestClient):
    """
    Tests the failure case for GET /users/me when no authentication is provided.
    """
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated. No valid cookie or authorization headers found."
    }
