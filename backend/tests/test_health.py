"""
Tests for the health check endpoint.

HOW THIS TEST WORKS:
- We use FastAPI's TestClient (built on httpx) which simulates HTTP requests
  without actually starting a server. This means the test runs instantly
  and doesn't need a real server running.

- Each test function calls an endpoint and checks ("asserts") that the
  response matches what we expect.

WHY THIS FILE EXISTS:
- Automated tests catch bugs before they reach users
- If removed, the only way to verify the endpoint works is to manually
  start the server and open a browser — every single time you make a change
"""

from fastapi.testclient import TestClient

from app.main import app

# Create a test client — this acts like a browser making requests,
# but it runs entirely in Python without needing a real server
client = TestClient(app)


def test_health_check_returns_200():
    """The health endpoint should return HTTP 200 (success)."""
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_check_returns_healthy_status():
    """The response should contain status: healthy."""
    response = client.get("/api/health")
    data = response.json()
    assert data["status"] == "healthy"


def test_health_check_returns_app_name():
    """The response should include the application name."""
    response = client.get("/api/health")
    data = response.json()
    assert data["app_name"] == "FitMind AI"


def test_health_check_returns_timestamp():
    """The response should include a timestamp."""
    response = client.get("/api/health")
    data = response.json()
    assert "timestamp" in data
