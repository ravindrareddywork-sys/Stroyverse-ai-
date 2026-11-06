"""
StoryVerse AI — Health Endpoint Tests
========================================
Tests for GET /api/health

Each test function starts with "test_" so pytest discovers it automatically.
The "client" parameter is automatically provided by conftest.py.
"""

import json


class TestHealthEndpoint:
    """Groups all health-check tests together for a clean test report."""

    def test_health_returns_200(self, client):
        """The endpoint must return HTTP 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}"
        )

    def test_health_returns_json(self, client):
        """Response Content-Type must be application/json."""
        response = client.get("/api/health")
        assert response.content_type.startswith("application/json"), (
            f"Expected JSON but got {response.content_type}"
        )

    def test_health_success_field(self, client):
        """Response body must contain success: true."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert data["success"] is True

    def test_health_message_field(self, client):
        """Response must include a human-readable message."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert "message" in data
        assert len(data["message"]) > 0

    def test_health_data_structure(self, client):
        """Response data object must contain required fields."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert "data" in data
        payload = data["data"]
        assert payload["status"] == "healthy"
        assert "version" in payload
        assert "timestamp" in payload
        assert "database" in payload
        assert "services" in payload

    def test_health_database_connected(self, client):
        """Database status must be 'connected' for the test DB."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert data["data"]["database"] == "connected"

    def test_health_method_post_not_allowed(self, client):
        """POST to /api/health should return 405 Method Not Allowed."""
        response = client.post("/api/health")
        assert response.status_code == 405

    def test_unknown_route_returns_404(self, client):
        """An unknown API route must return 404 as JSON (not HTML)."""
        response = client.get("/api/nonexistent-route-xyz")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["success"] is False

    def test_404_response_is_json(self, client):
        """404 error response must be JSON, not an HTML page."""
        response = client.get("/api/nonexistent-route-xyz")
        assert response.content_type.startswith("application/json")
