"""
StoryVerse AI — Response Utility
===================================
Provides standard helper functions for creating consistent
JSON API responses across all routes.

Simple explanation:
  Instead of building the same JSON structure {success, message, data}
  in every route, we write it once here and reuse it everywhere.
  This ensures ALL API responses look the same — which is important
  for the frontend JavaScript to handle them reliably.
"""

from flask import jsonify


def success_response(message, data=None, status_code=200):
    """
    Creates a standard success JSON response.

    Args:
        message (str): Human-readable success message.
        data (dict|list|None): The actual response payload.
        status_code (int): HTTP status code (default: 200).

    Returns:
        tuple: (Flask Response object, HTTP status code)

    Example output:
        {
            "success": true,
            "message": "Story generated successfully",
            "data": { "title": "...", "content": "..." }
        }
    """
    response = {
        "success": True,
        "message": message,
    }
    if data is not None:
        response["data"] = data

    return jsonify(response), status_code


def error_response(message, errors=None, status_code=400):
    """
    Creates a standard error JSON response.

    Args:
        message (str): Human-readable error message.
        errors (dict|None): Field-specific validation errors.
        status_code (int): HTTP status code (default: 400).

    Returns:
        tuple: (Flask Response object, HTTP status code)

    Example output:
        {
            "success": false,
            "message": "Validation failed",
            "errors": {
                "topic": "Topic cannot be empty"
            }
        }
    """
    response = {
        "success": False,
        "message": message,
    }
    if errors is not None:
        response["errors"] = errors

    return jsonify(response), status_code


def created_response(message, data=None):
    """
    Shortcut for 201 Created responses (used when saving a new resource).

    Args:
        message (str): Success message.
        data (dict|None): The created resource data.

    Returns:
        tuple: (Flask Response object, 201)
    """
    return success_response(message, data, status_code=201)


def not_found_response(message="Resource not found"):
    """
    Shortcut for 404 Not Found responses.

    Args:
        message (str): Error message describing what wasn't found.

    Returns:
        tuple: (Flask Response object, 404)
    """
    return error_response(message, status_code=404)


def server_error_response(message="An internal server error occurred"):
    """
    Shortcut for 500 Internal Server Error responses.
    Never include stack traces or internal details in this message.

    Args:
        message (str): Safe, user-friendly error message.

    Returns:
        tuple: (Flask Response object, 500)
    """
    return error_response(message, status_code=500)


def ai_error_response(message="AI service is temporarily unavailable"):
    """
    Shortcut for 502 Bad Gateway responses (AI provider failures).

    Args:
        message (str): Safe error message about AI failure.

    Returns:
        tuple: (Flask Response object, 502)
    """
    return error_response(message, status_code=502)


def rate_limit_response(message="Too many requests. Please wait a moment and try again."):
    """
    Shortcut for 429 Too Many Requests responses.

    Args:
        message (str): Rate limit message.

    Returns:
        tuple: (Flask Response object, 429)
    """
    return error_response(message, status_code=429)
