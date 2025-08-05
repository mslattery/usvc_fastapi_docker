from fastapi.testclient import TestClient
import pytest
from httpx import ASGITransport, AsyncClient
from bs4 import BeautifulSoup

from .main import app

# --- Test Data ---
# Format: (expected_id, expected_href, expected_text)
LOGIN_LINKS_TO_TEST = [
    ("mocklogin", "/auth/login?provider=mock", "Login with Mock Service"),
    ("googlelogin", "/auth/login?provider=google", "Login with Google"),
    ("oktalogin", "/auth/login?provider=okta", "Login with Okta (Not Implemented)"),
]


@pytest.fixture(scope="module")
def client():
    """
    A fixture to provide a TestClient instance for the tests.
    Using 'with' ensures that startup and shutdown events are handled.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def soup(client: TestClient):
    """
    A fixture to fetch and parse the page content once, making tests faster.
    This is efficient if multiple tests need to check the same page.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    return BeautifulSoup(response.text, "html.parser")


def test_html_content(soup: BeautifulSoup):
    # 1. Validate the main heading
    h1_tag = soup.find("h1")
    assert h1_tag is not None, "<h1> tag not found"
    assert (
        h1_tag.text.strip() == "Authentication Demo"
    ), "Main heading text does not match"

    # 2. Validate the paragraph's content
    p_tag = soup.find("p")
    assert p_tag is not None, "<p> tag not found"
    assert "Choose a provider to log in:" in p_tag.text


@pytest.mark.parametrize(
    "expected_id, expected_href, expected_text", LOGIN_LINKS_TO_TEST
)
def test_login_links(soup: BeautifulSoup, expected_id, expected_href, expected_text):
    """
    This single test function validates all login links from the LOGIN_LINKS_TO_TEST list.
    Pytest runs this function once for each tuple in the list.
    """
    # Use a CSS selector to find the link by its unique ID.
    # The '#' symbol indicates an ID.
    link_tag = soup.select_one(f"a#{expected_id}")

    # 1. Assert that the link was found on the page
    assert link_tag is not None, f"Link with id '{expected_id}' was not found."

    # 2. Assert that the 'href' attribute is correct
    actual_href = link_tag.get("href")
    assert (
        actual_href == expected_href
    ), f"For link '{expected_id}', expected href '{expected_href}', but got '{actual_href}'."

    # 3. Assert that the link's visible text is correct
    actual_text = link_tag.get_text(strip=True)
    assert (
        actual_text == expected_text
    ), f"For link '{expected_id}', expected text '{expected_text}', but got '{actual_text}'."
