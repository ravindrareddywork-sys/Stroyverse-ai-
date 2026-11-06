"""
StoryVerse AI — Centralized Error Handler
==========================================
Registers error handlers on the Flask app so that ALL unhandled
errors return consistent JSON responses instead of HTML error pages.

Simple explanation:
  By default Flask returns HTML error pages (like a plain "404 Not Found"
  page). But our frontend expects JSON. This module teaches Flask to
  ALWAYS respond with JSON, even for errors, so the frontend can
  display a meaningful message to the user.
"""

import logging
from flask import jsonify

# Set up logging so errors are printed to the terminal during development
logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """
    Registers all error handlers on the Flask application.
    Call this once during app creation in app.py.

    Args:
        app: The Flask application instance.
    """

    @app.errorhandler(400)
    def bad_request(error):
        """
        400 Bad Request — The client sent a malformed or invalid request.
        Example: Invalid JSON body, missing required fields.
        """
        return jsonify({
            "success": False,
            "message": "Bad request. Please check your input and try again.",
            "errors": {}
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        """
        404 Not Found — The requested URL/resource does not exist.
        Example: Calling /api/nonexistent-endpoint
        """
        return jsonify({
            "success": False,
            "message": "The requested resource was not found.",
            "errors": {}
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """
        405 Method Not Allowed — Wrong HTTP method used.
        Example: Sending a GET request to a POST-only endpoint.
        """
        return jsonify({
            "success": False,
            "message": "HTTP method not allowed for this endpoint.",
            "errors": {}
        }), 405

    @app.errorhandler(429)
    def too_many_requests(error):
        """
        429 Too Many Requests — Rate limit exceeded.
        Returns detailed retry information when provided by Flask-Limiter.
        """
        retry_after = getattr(error, "retry_after", None)
        if retry_after is None and hasattr(error, "response") and error.response:
            retry_after = error.response.headers.get("Retry-After")

        # Parse retry_after into integer if possible
        retry_seconds = None
        if retry_after is not None:
            try:
                retry_seconds = int(retry_after)
            except (ValueError, TypeError):
                retry_seconds = None

        limit_desc = str(error.description) if hasattr(error, "description") and error.description else "Rate limit exceeded"
        
        if retry_seconds and retry_seconds > 0:
            message = f"Too many requests. Please wait {retry_seconds} second{'s' if retry_seconds != 1 else ''} and try again."
        else:
            message = "Too many requests. Please wait a moment and try again."

        response_payload = {
            "success": False,
            "message": message,
            "errors": {
                "rate_limit": limit_desc
            }
        }
        if retry_seconds is not None:
            response_payload["errors"]["retry_after"] = retry_seconds

        resp = jsonify(response_payload)
        resp.status_code = 429
        if retry_seconds is not None:
            resp.headers["Retry-After"] = str(retry_seconds)
        return resp

    @app.errorhandler(500)
    def internal_server_error(error):
        """
        500 Internal Server Error — Something unexpected went wrong on the server.
        We log the actual error internally but send a safe message to the client.
        NEVER send stack traces or internal details to the frontend.
        """
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "An internal server error occurred. Please try again later.",
            "errors": {}
        }), 500

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        """
        Catch-all handler for any unhandled Python exceptions.
        Logs the full error for debugging but returns a safe message.
        """
        logger.error(f"Unhandled exception: {type(error).__name__}: {error}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred. Please try again.",
            "errors": {}
        }), 500
