"""
StoryVerse AI — Screenplay / Script Routes
============================================
Flask Blueprint providing REST API endpoints for:
  - POST /api/generate-script : Generates a complete multi-scene screenplay
  - POST /api/generate-scene  : Generates a single focused dramatic scene
"""

import logging
from flask import Blueprint, request

from services.script_service import script_service
from services.ai_service import AIService
from utils.validators import validate_script_input, validate_scene_input
from utils.response import success_response, error_response

logger = logging.getLogger(__name__)

script_bp = Blueprint("script", __name__)


@script_bp.route("/generate-script", methods=["POST"])
def generate_script():
    """
    POST /api/generate-script
    Accepts screenplay parameters, validates input, calls AI provider,
    and returns parsed scenes + industry-standard formatted screenplay text.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_script_input(data)
        if errors:
            return error_response(
                "Validation failed. Please check your inputs.",
                errors=errors,
                status_code=400
            )

        result = script_service.generate_script(data)
        return success_response(
            "Screenplay generated successfully.",
            data=result,
            status_code=200
        )

    except Exception as err:
        return AIService.handle_api_error(err)


@script_bp.route("/generate-scene", methods=["POST"])
def generate_scene():
    """
    POST /api/generate-scene
    Accepts scene parameters, validates input, calls AI provider,
    and returns a formatted individual scene.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_scene_input(data)
        if errors:
            return error_response(
                "Validation failed. Please check your inputs.",
                errors=errors,
                status_code=400
            )

        result = script_service.generate_scene(data)
        return success_response(
            "Scene generated successfully.",
            data=result,
            status_code=200
        )

    except Exception as err:
        return AIService.handle_api_error(err)
