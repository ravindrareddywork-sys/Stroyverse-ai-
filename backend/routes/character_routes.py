"""
StoryVerse AI — Character Routes
===================================
Flask Blueprint providing REST API endpoints for:
  - POST /api/generate-character            : Generates a full 19-dimension character profile bible
  - POST /api/generate-character-variations : Generates multiple diverse character concepts
"""

import logging
from flask import Blueprint, request

from services.character_service import character_service
from services.ai_service import AIService
from services.ai_provider import AIError
from utils.validators import validate_character_input, validate_character_variations_input
from utils.response import success_response, error_response

logger = logging.getLogger(__name__)

character_bp = Blueprint("character", __name__)


@character_bp.route("/generate-character", methods=["POST"])
def generate_character():
    """
    POST /api/generate-character
    Accepts character parameters (concept, role, archetype, genre, age, etc.),
    validates input, calls AI provider, and returns a structured 19-point profile bible.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_character_input(data)
        if errors:
            return error_response(
                "Validation failed. Please check your inputs.",
                errors=errors,
                status_code=400
            )

        result = character_service.generate_character(data)
        return success_response(
            "Character profile generated successfully.",
            data=result,
            status_code=200
        )

    except Exception as err:
        if not isinstance(err, AIError):
            logger.exception("Unexpected single-character profile generation failure")
        return AIService.handle_api_error(err)


@character_bp.route("/generate-character-variations", methods=["POST"])
def generate_character_variations():
    """
    POST /api/generate-character-variations
    Accepts story premise and parameters, validates input, calls AI provider,
    and returns multiple distinct character concepts.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_character_variations_input(data)
        if errors:
            return error_response(
                "Validation failed. Please check your inputs.",
                errors=errors,
                status_code=400
            )

        result = character_service.generate_character_variations(data)
        return success_response(
            "Character variations generated successfully.",
            data=result,
            status_code=200
        )

    except Exception as err:
        return AIService.handle_api_error(err)
