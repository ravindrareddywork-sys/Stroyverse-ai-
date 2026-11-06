"""
StoryVerse AI — Writing Assistant Routes
==========================================
Flask Blueprint providing REST API endpoints for:
  - POST /api/rewrite              : Rewrites text in various styles
  - POST /api/translate            : Translates text into English, Telugu, Tamil, or Hindi
  - POST /api/summarize            : Summarizes text in selectable lengths
  - POST /api/generate-dialogue    : Generates realistic dialogue
  - POST /api/generate-plot-twist  : Generates shocking plot twists
  - POST /api/continue-writing     : Seamlessly extends story or script text
"""

import logging
from flask import Blueprint, current_app, request

from extensions import limiter
from services.writing_assistant_service import writing_assistant_service
from services.ai_service import AIService
from utils.validators import validate_writing_assistant_input
from utils.response import success_response, error_response

logger = logging.getLogger(__name__)

writing_assistant_bp = Blueprint("writing_assistant", __name__)


@writing_assistant_bp.route("/rewrite", methods=["POST"])
@limiter.limit(lambda: current_app.config["RATELIMIT_GENERATION"])
def rewrite_text():
    """
    POST /api/rewrite
    Rewrites text with selectable style directives (clarity, grammar, professional, creative, engaging, simplify).
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_writing_assistant_input(data, operation="rewrite")
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        result = writing_assistant_service.rewrite(data)
        return success_response("Text rewritten successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)


@writing_assistant_bp.route("/translate", methods=["POST"])
@limiter.limit(lambda: current_app.config["RATELIMIT_GENERATION"])
def translate_text():
    """
    POST /api/translate
    Translates text into English, Telugu, Tamil, or Hindi preserving tone and nuances.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_writing_assistant_input(data, operation="translate")
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        result = writing_assistant_service.translate(data)
        return success_response("Text translated successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)


@writing_assistant_bp.route("/summarize", methods=["POST"])
@limiter.limit(lambda: current_app.config["RATELIMIT_GENERATION"])
def summarize_text():
    """
    POST /api/summarize
    Summarizes content in selectable lengths (short, medium, detailed).
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_writing_assistant_input(data, operation="summarize")
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        result = writing_assistant_service.summarize(data)
        return success_response("Text summarized successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)


@writing_assistant_bp.route("/generate-dialogue", methods=["POST"])
@limiter.limit(lambda: current_app.config["RATELIMIT_GENERATION"])
def generate_dialogue():
    """
    POST /api/generate-dialogue
    Generates dynamic character dialogue based on scene context, characters, and tone.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_writing_assistant_input(data, operation="generate-dialogue")
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        result = writing_assistant_service.generate_dialogue(data)
        return success_response("Dialogue generated successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)


@writing_assistant_bp.route("/generate-plot-twist", methods=["POST"])
@limiter.limit(lambda: current_app.config["RATELIMIT_GENERATION"])
def generate_plot_twist():
    """
    POST /api/generate-plot-twist
    Generates unexpected but logically sound plot twists for a story.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_writing_assistant_input(data, operation="generate-plot-twist")
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        result = writing_assistant_service.generate_plot_twist(data)
        return success_response("Plot twists generated successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)


@writing_assistant_bp.route("/continue-writing", methods=["POST"])
@limiter.limit(lambda: current_app.config["RATELIMIT_GENERATION"])
def continue_writing():
    """
    POST /api/continue-writing
    Seamlessly continues writing a narrative or script from where it ended.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_writing_assistant_input(data, operation="continue-writing")
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        result = writing_assistant_service.continue_writing(data)
        return success_response("Narrative continued successfully.", data=result, status_code=200)

    except Exception as err:
        return AIService.handle_api_error(err)
