"""
StoryVerse AI — Story Routes
==============================
Flask Blueprint providing REST API endpoints for:
  - POST /api/generate-story : Generates a full structured story
  - POST /api/regenerate     : Rewrites/regenerates an existing story
  - POST /api/expand         : Expands story with sensory and emotional depth
  - POST /api/shorten        : Condenses story text preserving core plot beats
  - POST /api/continue       : Seamlessly extends story from where it ended
"""

import logging
from flask import Blueprint, request

from services.story_service import story_service
from services.ai_service import AIService
from utils.validators import validate_story_input, validate_story_operation_input
from utils.response import success_response, error_response

logger = logging.getLogger(__name__)

story_bp = Blueprint("story", __name__)


@story_bp.route("/generate-story", methods=["POST"])
def generate_story():
    """
    POST /api/generate-story
    Accepts story parameters, validates input, calls Gemini/Mock AI,
    and returns 10 structured sections + complete text.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_story_input(data)
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        result = story_service.generate_story(data)
        return success_response("Story generated successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)


@story_bp.route("/regenerate", methods=["POST"])
def regenerate_story():
    """
    POST /api/regenerate
    Regenerates or retells an existing story with updated instructions.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_story_operation_input(data, "regenerate")
        if errors:
            return error_response("Validation failed.", errors=errors, status_code=400)

        result = story_service.regenerate_story(data)
        return success_response("Story regenerated successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)


@story_bp.route("/expand", methods=["POST"])
def expand_story():
    """
    POST /api/expand
    Expands an existing story section with vivid sensory descriptions.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_story_operation_input(data, "expand")
        if errors:
            return error_response("Validation failed.", errors=errors, status_code=400)

        result = story_service.expand_story(data)
        return success_response("Story expanded successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)


@story_bp.route("/shorten", methods=["POST"])
def shorten_story():
    """
    POST /api/shorten
    Condenses an existing story while preserving critical plot points.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_story_operation_input(data, "shorten")
        if errors:
            return error_response("Validation failed.", errors=errors, status_code=400)

        result = story_service.shorten_story(data)
        return success_response("Story condensed successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)


@story_bp.route("/continue", methods=["POST"])
def continue_story():
    """
    POST /api/continue
    Extends a story seamlessly from where it left off.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_story_operation_input(data, "continue")
        if errors:
            return error_response("Validation failed.", errors=errors, status_code=400)

        result = story_service.continue_story(data)
        return success_response("Story continued successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)
