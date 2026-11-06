"""
StoryVerse AI — Health Check Routes
=====================================
Provides a single GET /api/health endpoint that lets the frontend
(and monitoring tools) verify that the backend is running and the
database is reachable.

Simple explanation:
  Think of this like a "ping" for the server.
  When the frontend loads, it calls this endpoint first.
  If it gets back {"success": true}, it knows the backend is alive.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint
from extensions import db, limiter
from utils.response import success_response, server_error_response

logger = logging.getLogger(__name__)

# Create a Blueprint called "health"
# All routes in this file are grouped under this blueprint.
health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
@limiter.exempt
def health_check():
    """
    GET /api/health

    Returns the operational status of the backend server and database.

    Response (200):
        {
            "success": true,
            "message": "StoryVerse AI backend is running",
            "data": {
                "status": "healthy",
                "version": "2.0.0",
                "timestamp": "2024-01-01T00:00:00Z",
                "database": "connected",
                "services": { "ai": "configured" | "not_configured" }
            }
        }

    Response (500):
        {
            "success": false,
            "message": "Backend is running but database is unavailable"
        }
    """
    try:
        # Probe the database with a lightweight query
        db.session.execute(db.text("SELECT 1"))
        db_status = "connected"
    except Exception as db_err:
        logger.error(f"Database health check failed: {db_err}")
        return server_error_response(
            "Backend is running but database is unavailable"
        )

    # Import here to avoid circular imports at module level
    import os

    ai_status = "configured" if os.environ.get("GEMINI_API_KEY") else "not_configured"

    data = {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "services": {
            "ai": ai_status,
        },
    }

    return success_response("StoryVerse AI backend is running", data)
