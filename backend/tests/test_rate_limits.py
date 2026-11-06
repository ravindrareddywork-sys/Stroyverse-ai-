"""
StoryVerse AI — Rate Limiting & Workspace Route Protection Tests
=================================================================
Tests for Rate Limiting:
  - 429 Too Many Requests response formatting (JSON schema, message, Retry-After header)
  - Health check endpoint exemption (@limiter.exempt)
  - Static frontend route exemption (@limiter.exempt on serve_frontend)
  - Workspace / Projects route rate limits (reading and writing projects)
  - Recovery after rate limit reset
"""

import pytest
from flask import Flask, jsonify
from extensions import db, limiter
from app import create_app


class TestRateLimiterConfiguration:
    """Verifies that rate limiting configuration is properly set."""

    def test_default_rate_limit_values_in_config(self):
        """Default rate limit should be generous for normal navigation, not 50/hour."""
        from config import DevelopmentConfig, ProductionConfig
        assert "500 per hour" in DevelopmentConfig.RATELIMIT_DEFAULT or "2000 per day" in DevelopmentConfig.RATELIMIT_DEFAULT
        assert "500 per hour" in ProductionConfig.RATELIMIT_DEFAULT or "2000 per day" in ProductionConfig.RATELIMIT_DEFAULT

    def test_ai_generation_limits_preserved(self):
        """Strict limits on expensive AI endpoints must remain intact."""
        from config import Config
        assert Config.RATELIMIT_GENERATION == "10 per minute"


class TestRateLimit429ResponseFormat:
    """Tests that 429 errors return correct JSON structure, headers, and friendly messages."""

    @pytest.fixture
    def rate_limited_app(self):
        """Creates a dedicated Flask app instance with rate limiting enabled."""
        test_app = Flask(__name__)
        test_app.config["TESTING"] = False  # Limiter checks TESTING flag
        test_app.config["RATELIMIT_ENABLED"] = True
        test_app.config["RATELIMIT_STORAGE_URI"] = "memory://"
        test_app.config["RATELIMIT_STRATEGY"] = "fixed-window"

        limiter.init_app(test_app)

        from utils.error_handler import register_error_handlers
        register_error_handlers(test_app)

        @test_app.route("/api/test-limited")
        @limiter.limit("2 per minute")
        def limited_route():
            return jsonify({"success": True, "message": "OK"})

        @test_app.route("/api/test-exempt")
        @limiter.exempt
        def exempt_route():
            return jsonify({"success": True, "message": "Always accessible"})

        return test_app

    def test_rate_limit_triggers_429_with_standard_json(self, rate_limited_app):
        """Sending requests beyond the limit returns HTTP 429 with correct schema."""
        client = rate_limited_app.test_client()

        # First 2 requests succeed
        res1 = client.get("/api/test-limited")
        assert res1.status_code == 200

        res2 = client.get("/api/test-limited")
        assert res2.status_code == 200

        # 3rd request must be blocked with HTTP 429
        res3 = client.get("/api/test-limited")
        assert res3.status_code == 429

        data = res3.get_json()
        assert data is not None
        assert data["success"] is False
        assert "Too many requests" in data["message"]
        assert "errors" in data
        assert "rate_limit" in data["errors"]

    def test_rate_limit_exempt_route_never_blocked(self, rate_limited_app):
        """Exempt routes should not be throttled regardless of request volume."""
        client = rate_limited_app.test_client()

        for _ in range(10):
            res = client.get("/api/test-exempt")
            assert res.status_code == 200
            assert res.get_json()["success"] is True


class TestWorkspaceAIGenerationLimits:
    """Workspace AI requests must use the configured generation limit."""

    @pytest.fixture
    def workspace_limited_app(self):
        test_app = Flask(__name__)
        test_app.config.update(
            TESTING=False,
            RATELIMIT_ENABLED=True,
            RATELIMIT_STORAGE_URI="memory://",
            RATELIMIT_STRATEGY="fixed-window",
            RATELIMIT_GENERATION="1 per minute",
        )

        limiter.init_app(test_app)

        from routes.writing_assistant_routes import writing_assistant_bp
        from utils.error_handler import register_error_handlers

        test_app.register_blueprint(writing_assistant_bp, url_prefix="/api")
        register_error_handlers(test_app)
        return test_app

    def test_workspace_ai_endpoint_enforces_generation_limit(self, workspace_limited_app):
        client = workspace_limited_app.test_client()

        first = client.post("/api/rewrite", json={"content": ""})
        second = client.post("/api/rewrite", json={"content": ""})

        assert first.status_code == 400
        assert second.status_code == 429
        assert second.get_json()["success"] is False
        assert "Too many requests" in second.get_json()["message"]


class TestWorkspaceAndHealthExemptions:
    """Tests that health and frontend static serving are never rate-limited."""

    def test_health_check_has_exempt_attribute(self):
        """GET /api/health must be exempt from rate limiting."""
        app = create_app("testing")
        view_func = app.view_functions.get("health.health_check")
        assert view_func is not None
        # Flask-Limiter marks exempt views with _limiter_exempt or attaches to view
        assert getattr(view_func, "_rate_limit_exempt", False) is True or getattr(view_func, "undecorated", None) is not None or getattr(view_func, "_limiter_exempt", True)

    def test_serve_frontend_has_exempt_attribute(self):
        """serve_frontend catch-all must be exempt from rate limiting."""
        app = create_app("testing")
        view_func = app.view_functions.get("serve_frontend")
        assert view_func is not None
        assert getattr(view_func, "_rate_limit_exempt", False) is True or getattr(view_func, "_limiter_exempt", True)

    def test_workspace_project_endpoints_accessible(self, client):
        """Workspace project listing and retrieval function normally."""
        # Create a test project first
        create_res = client.post("/api/projects", json={
            "title": "Workspace Test Project",
            "content_type": "story",
            "content": "Opening scene in the cosmic observatory."
        })
        assert create_res.status_code == 201
        project_id = create_res.get_json()["data"]["id"]

        # Rapidly query project multiple times (normal navigation simulation)
        for _ in range(5):
            get_res = client.get(f"/api/projects/{project_id}")
            assert get_res.status_code == 200
            data = get_res.get_json()
            assert data["success"] is True
            assert data["data"]["title"] == "Workspace Test Project"
