"""
StoryVerse AI — Input Validators
====================================
Validates all user input before it reaches the AI or database.
This protects against bad data, overly long inputs, and injection attacks.

Simple explanation:
  Before we let the user's input reach the AI or the database, we
  "check" it like a security guard. Is the topic too long? Is the
  genre a valid one? Did the user submit an empty form? This module
  handles all of that.
"""

import json
import re

# ============================================================
# Constants — Allowed values
# ============================================================

ALLOWED_GENRES = {
    "horror", "romance", "comedy", "thriller", "fantasy",
    "science fiction", "sci-fi", "drama", "mystery", "adventure",
    "action", "historical", "animation"
}

ALLOWED_LANGUAGES = {
    "english", "telugu", "tamil", "hindi"
}

ALLOWED_TONES = {
    "emotional", "inspirational", "funny", "suspenseful",
    "dark", "romantic", "neutral", "tense", "dramatic", "mysterious"
}

ALLOWED_LENGTHS = {
    "short", "medium", "long"
}

ALLOWED_AUDIENCES = {
    "children", "teenagers", "adults", "general audience", "general"
}

ALLOWED_CONTENT_TYPES = {
    "story", "script", "character", "other"
}

# Maximum lengths for text inputs
MAX_TOPIC_LENGTH = 2000
MAX_CONTENT_LENGTH = 100000  # 100KB for saved content
MAX_TITLE_LENGTH = 500
MAX_CHARACTERS_INPUT_LENGTH = 500
MAX_INSTRUCTIONS_LENGTH = 1000
MAX_SCENES = 20
MAX_CHARACTER_COUNT = 10


# ============================================================
# General-purpose validators
# ============================================================

def validate_required_string(value, field_name, max_length=None):
    """
    Validates that a required string field is present and not empty.

    Args:
        value: The value to validate.
        field_name (str): Name of the field (used in error messages).
        max_length (int|None): Maximum allowed length.

    Returns:
        str|None: Error message if invalid, None if valid.
    """
    if value is None or not isinstance(value, str):
        return f"{field_name} is required."
    if not value.strip():
        return f"{field_name} cannot be empty."
    if max_length and len(value.strip()) > max_length:
        return f"{field_name} must be {max_length} characters or fewer."
    return None


def validate_optional_string(value, field_name, max_length=None):
    """
    Validates an optional string field. Passes if value is None or empty,
    but validates length if a value is provided.

    Args:
        value: The value to validate.
        field_name (str): Name of the field.
        max_length (int|None): Maximum allowed length.

    Returns:
        str|None: Error message if invalid, None if valid.
    """
    if value is None or value == "":
        return None  # Optional fields are fine when empty
    if not isinstance(value, str):
        return f"{field_name} must be a string."
    if max_length and len(value.strip()) > max_length:
        return f"{field_name} must be {max_length} characters or fewer."
    return None


def validate_enum(value, field_name, allowed_values, required=True):
    """
    Validates that a value is one of the allowed options.

    Args:
        value: The value to check.
        field_name (str): Field name for error messages.
        allowed_values (set): Set of allowed string values (lowercase).
        required (bool): Whether the field is mandatory.

    Returns:
        str|None: Error message if invalid, None if valid.
    """
    if not value:
        if required:
            return f"{field_name} is required."
        return None  # Optional and not provided — OK
    if isinstance(value, str) and value.lower() in allowed_values:
        return None
    allowed_display = ", ".join(sorted(allowed_values))
    return f"{field_name} must be one of: {allowed_display}."


def validate_integer_range(value, field_name, min_val=1, max_val=100, required=True):
    """
    Validates that a numeric value is within an acceptable range.

    Args:
        value: The value to validate.
        field_name (str): Field name for error messages.
        min_val (int): Minimum allowed value.
        max_val (int): Maximum allowed value.
        required (bool): Whether the field is mandatory.

    Returns:
        str|None: Error message if invalid, None if valid.
    """
    if value is None:
        if required:
            return f"{field_name} is required."
        return None
    try:
        int_value = int(value)
        if int_value < min_val or int_value > max_val:
            return f"{field_name} must be between {min_val} and {max_val}."
        return None
    except (ValueError, TypeError):
        return f"{field_name} must be a whole number."


# ============================================================
# Domain-specific validators
# ============================================================

def validate_story_input(data):
    """
    Validates all input fields for story generation.

    Args:
        data (dict): The JSON request body from the frontend.

    Returns:
        dict: A dictionary of field → error message.
              Empty dict means all inputs are valid.
    """
    errors = {}

    # Topic is required
    err = validate_required_string(data.get("topic"), "Topic", MAX_TOPIC_LENGTH)
    if err:
        errors["topic"] = err

    # Genre is required and must be valid
    err = validate_enum(data.get("genre"), "Genre", ALLOWED_GENRES)
    if err:
        errors["genre"] = err

    # Language is optional but must be valid if provided
    if data.get("language"):
        err = validate_enum(data.get("language"), "Language", ALLOWED_LANGUAGES, required=False)
        if err:
            errors["language"] = err

    # Tone is optional but must be valid if provided
    if data.get("tone"):
        err = validate_enum(data.get("tone"), "Tone", ALLOWED_TONES, required=False)
        if err:
            errors["tone"] = err

    # Length is optional but must be valid if provided
    if data.get("length"):
        err = validate_enum(data.get("length"), "Length", ALLOWED_LENGTHS, required=False)
        if err:
            errors["length"] = err

    # Audience is optional but must be valid if provided
    if data.get("audience"):
        err = validate_enum(data.get("audience"), "Audience", ALLOWED_AUDIENCES, required=False)
        if err:
            errors["audience"] = err

    # Character count must be a reasonable number
    if data.get("character_count") is not None:
        err = validate_integer_range(
            data.get("character_count"), "Character count", 1, MAX_CHARACTER_COUNT, required=False
        )
        if err:
            errors["character_count"] = err

    # Character names (optional list or string)
    if data.get("character_names") is not None:
        c_names = data.get("character_names")
        if isinstance(c_names, list):
            if len(c_names) > MAX_CHARACTER_COUNT:
                errors["character_names"] = f"Character names list cannot exceed {MAX_CHARACTER_COUNT} names."
            else:
                for idx, name in enumerate(c_names):
                    if not isinstance(name, str) or len(name.strip()) > 100:
                        errors["character_names"] = f"Character name #{idx+1} must be a string up to 100 characters."
                        break
        elif isinstance(c_names, str):
            err = validate_optional_string(c_names, "Character names", MAX_CHARACTERS_INPUT_LENGTH)
            if err:
                errors["character_names"] = err
        else:
            errors["character_names"] = "Character names must be a list of strings or comma-separated string."

    # Optional text fields
    err = validate_optional_string(data.get("setting"), "Setting", MAX_INSTRUCTIONS_LENGTH)
    if err:
        errors["setting"] = err

    err = validate_optional_string(
        data.get("additional_instructions"), "Additional instructions", MAX_INSTRUCTIONS_LENGTH
    )
    if err:
        errors["additional_instructions"] = err

    return errors


def validate_script_input(data):
    """
    Validates all input fields for script generation.

    Args:
        data (dict): The JSON request body from the frontend.

    Returns:
        dict: Field → error message. Empty dict means valid.
    """
    errors = {}

    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    err = validate_required_string(data.get("topic"), "Topic", MAX_TOPIC_LENGTH)
    if err:
        errors["topic"] = err

    err = validate_enum(data.get("genre"), "Genre", ALLOWED_GENRES)
    if err:
        errors["genre"] = err

    if data.get("language"):
        err = validate_enum(data.get("language"), "Language", ALLOWED_LANGUAGES, required=False)
        if err:
            errors["language"] = err

    if data.get("tone"):
        err = validate_enum(data.get("tone"), "Tone", ALLOWED_TONES, required=False)
        if err:
            errors["tone"] = err

    # Number of scenes (1 - 20)
    if data.get("num_scenes") is not None:
        err = validate_integer_range(
            data.get("num_scenes"), "Number of scenes", 1, MAX_SCENES, required=False
        )
        if err:
            errors["num_scenes"] = err

    # Characters (optional string or list)
    if data.get("characters") is not None:
        chars_val = data.get("characters")
        if isinstance(chars_val, list):
            if len(chars_val) > 20:
                errors["characters"] = "Character list cannot exceed 20 characters."
            else:
                for idx, c in enumerate(chars_val):
                    if not isinstance(c, str) or len(c.strip()) > 150:
                        errors["characters"] = f"Character #{idx+1} must be a string up to 150 characters."
                        break
        elif isinstance(chars_val, str):
            err = validate_optional_string(chars_val, "Characters", MAX_CHARACTERS_INPUT_LENGTH)
            if err:
                errors["characters"] = err
        else:
            errors["characters"] = "Characters must be a string or list of strings."

    err = validate_optional_string(data.get("setting"), "Setting", MAX_INSTRUCTIONS_LENGTH)
    if err:
        errors["setting"] = err

    err = validate_optional_string(
        data.get("additional_instructions"), "Additional instructions", MAX_INSTRUCTIONS_LENGTH
    )
    if err:
        errors["additional_instructions"] = err

    return errors


def validate_scene_input(data):
    """
    Validates input fields for single scene generation.

    Args:
        data (dict): The JSON request body.

    Returns:
        dict: Field → error message. Empty dict means valid.
    """
    errors = {}

    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    # Scene goal or premise is required
    goal = data.get("scene_goal") or data.get("topic")
    err = validate_required_string(goal, "Scene goal / premise", MAX_TOPIC_LENGTH)
    if err:
        errors["scene_goal"] = err

    err = validate_optional_string(data.get("context"), "Story context", MAX_CONTENT_LENGTH)
    if err:
        errors["context"] = err

    if data.get("genre"):
        err = validate_enum(data.get("genre"), "Genre", ALLOWED_GENRES, required=False)
        if err:
            errors["genre"] = err

    if data.get("language"):
        err = validate_enum(data.get("language"), "Language", ALLOWED_LANGUAGES, required=False)
        if err:
            errors["language"] = err

    err = validate_optional_string(data.get("characters"), "Characters", MAX_CHARACTERS_INPUT_LENGTH)
    if err:
        errors["characters"] = err

    return errors


ALLOWED_CHARACTER_ROLES = {
    "protagonist", "antagonist", "supporting", "mentor", "sidekick",
    "antihero", "anti-hero", "deuteragonist", "love interest",
    "rival", "foil", "villain", "hero"
}

ALLOWED_CHARACTER_VARIATION_ROLES = ALLOWED_CHARACTER_ROLES | {
    "ensemble cast", "protagonists", "antagonists"
}


def validate_character_input(data):
    """
    Validates input for character generation. Supports both legacy description
    and rich Phase 7 parameters (role, age, gender, background, etc.).

    Args:
        data (dict): The JSON request body.

    Returns:
        dict: Field → error message. Empty dict means valid.
    """
    errors = {}

    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    # Accept 'description', 'story_context', or 'concept'
    desc = data.get("description")
    if desc is None:
        desc = data.get("story_context") or data.get("concept")

    err = validate_required_string(desc, "Character description", MAX_TOPIC_LENGTH)
    if err:
        errors["description"] = err

    err = validate_enum(data.get("genre"), "Genre", ALLOWED_GENRES, required=True)
    if err:
        errors["genre"] = err

    name_val = data.get("character_name") or data.get("name")
    if name_val:
        err = validate_optional_string(name_val, "Character name", 200)
        if err:
            errors["name"] = err

    if data.get("character_role"):
        err = validate_enum(data.get("character_role"), "Character role", ALLOWED_CHARACTER_ROLES, required=False)
        if err:
            errors["character_role"] = err

    if data.get("language"):
        err = validate_enum(data.get("language"), "Language", ALLOWED_LANGUAGES, required=False)
        if err:
            errors["language"] = err

    if data.get("tone"):
        err = validate_enum(data.get("tone"), "Tone", ALLOWED_TONES, required=False)
        if err:
            errors["tone"] = err

    # Optional string fields
    if data.get("age") is not None:
        err = validate_optional_string(str(data.get("age")), "Age", 50)
        if err:
            errors["age"] = err

    err = validate_optional_string(data.get("gender"), "Gender", 50)
    if err:
        errors["gender"] = err

    err = validate_optional_string(
        data.get("personality_type") or data.get("character_archetype"),
        "Personality / Archetype",
        150
    )
    if err:
        errors["personality_type"] = err

    err = validate_optional_string(data.get("background"), "Background", MAX_INSTRUCTIONS_LENGTH)
    if err:
        errors["background"] = err

    err = validate_optional_string(data.get("setting"), "Setting", MAX_INSTRUCTIONS_LENGTH)
    if err:
        errors["setting"] = err

    err = validate_optional_string(
        data.get("additional_instructions"), "Additional instructions", MAX_INSTRUCTIONS_LENGTH
    )
    if err:
        errors["additional_instructions"] = err

    return errors


def validate_character_variations_input(data):
    """
    Validates input for generating multiple character variations.

    Args:
        data (dict): The JSON request body.

    Returns:
        dict: Field → error message. Empty dict means valid.
    """
    errors = {}

    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    premise = (
        data.get("premise")
        or data.get("story_context")
        or data.get("description")
    )
    err = validate_required_string(premise, "Premise / Story context", MAX_TOPIC_LENGTH)
    if err:
        errors["premise"] = err

    err = validate_enum(data.get("genre"), "Genre", ALLOWED_GENRES, required=True)
    if err:
        errors["genre"] = err

    count = data.get("count")
    if count is None:
        errors["count"] = "Character count is required."
    elif isinstance(count, bool) or not isinstance(count, int):
        errors["count"] = "Character count must be an integer between 2 and 5."
    elif count < 2 or count > 5:
        errors["count"] = "Character count must be between 2 and 5."

    if data.get("character_role"):
        err = validate_enum(
            data.get("character_role"),
            "Focus role",
            ALLOWED_CHARACTER_VARIATION_ROLES,
            required=False
        )
        if err:
            errors["character_role"] = err

    if data.get("language"):
        err = validate_enum(data.get("language"), "Language", ALLOWED_LANGUAGES, required=False)
        if err:
            errors["language"] = err

    return errors


ALLOWED_SUMMARY_LENGTHS = {
    "short", "medium", "detailed", "bullet_points", "paragraph"
}

ALLOWED_REWRITE_STYLES = {
    "clarity", "grammar", "professional", "creative", "engaging", "simplify",
    "improve clarity", "improve grammar", "make it professional", "make it creative",
    "make it engaging", "simplify language"
}


def validate_writing_assistant_input(data, operation):
    """
    Validates input for writing assistant operations:
    rewrite, translate, summarize, generate-dialogue, generate-plot-twist, continue-writing.

    Args:
        data (dict): The JSON request body.
        operation (str): The operation being performed.

    Returns:
        dict: Field → error message. Empty dict means valid.
    """
    errors = {}

    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    # Normalize content / text field
    text_content = data.get("content") or data.get("text")

    if operation in ("rewrite", "translate", "summarize", "continue-writing", "continue"):
        err = validate_required_string(text_content, "Content", MAX_CONTENT_LENGTH)
        if err:
            errors["content"] = err

    if operation == "translate":
        target_lang = data.get("target_language") or data.get("language")
        if not target_lang:
            errors["target_language"] = "Target language is required for translation."
        else:
            err = validate_enum(target_lang, "Target language", ALLOWED_LANGUAGES, required=True)
            if err:
                errors["target_language"] = err

    elif operation == "summarize":
        sum_len = data.get("length") or data.get("summary_length")
        if sum_len:
            err = validate_enum(sum_len, "Summary length", ALLOWED_SUMMARY_LENGTHS, required=False)
            if err:
                errors["length"] = err

    elif operation == "generate-dialogue":
        context_field = data.get("context") or data.get("topic") or data.get("content")
        err = validate_required_string(context_field, "Scene context / topic", MAX_CONTENT_LENGTH)
        if err:
            errors["context"] = err

        if data.get("genre"):
            err = validate_enum(data.get("genre"), "Genre", ALLOWED_GENRES, required=False)
            if err:
                errors["genre"] = err

    elif operation == "generate-plot-twist":
        plot_field = data.get("premise") or data.get("plot") or data.get("context") or data.get("content")
        err = validate_required_string(plot_field, "Story premise / plot", MAX_CONTENT_LENGTH)
        if err:
            errors["premise"] = err

        if data.get("genre"):
            err = validate_enum(data.get("genre"), "Genre", ALLOWED_GENRES, required=False)
            if err:
                errors["genre"] = err

    # Shared optional parameters
    if data.get("language"):
        err = validate_enum(data.get("language"), "Language", ALLOWED_LANGUAGES, required=False)
        if err:
            errors["language"] = err

    if data.get("tone"):
        err = validate_enum(data.get("tone"), "Tone", ALLOWED_TONES, required=False)
        if err:
            errors["tone"] = err

    return errors


def validate_project_input(data, is_update=False):
    """
    Validates input for saving/updating a project.

    Args:
        data (dict): The JSON request body.
        is_update (bool): True if this is an update (title optional).

    Returns:
        dict: Field → error message. Empty dict means valid.
    """
    errors = {}

    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    # Normalize aliases
    content_type = data.get("content_type") or data.get("project_type")
    content_val = data.get("generated_content") if "generated_content" in data else data.get("content")

    if not is_update:
        err = validate_required_string(data.get("title"), "Title", MAX_TITLE_LENGTH)
        if err:
            errors["title"] = err

        err = validate_enum(content_type, "Content type", ALLOWED_CONTENT_TYPES, required=True)
        if err:
            errors["content_type"] = err
    else:
        if data.get("title") is not None:
            err = validate_required_string(data.get("title"), "Title", MAX_TITLE_LENGTH)
            if err:
                errors["title"] = err

        if content_type is not None:
            err = validate_enum(
                content_type, "Project / Content type", ALLOWED_CONTENT_TYPES, required=False
            )
            if err:
                errors["content_type"] = err

    if content_val is not None:
        err = validate_optional_string(content_val, "Content", MAX_CONTENT_LENGTH)
        if err:
            errors["content"] = err

    if data.get("genre"):
        err = validate_optional_string(data.get("genre"), "Genre", 100)
        if err:
            errors["genre"] = err

    if data.get("language"):
        err = validate_optional_string(data.get("language"), "Language", 50)
        if err:
            errors["language"] = err

    if data.get("tone"):
        err = validate_optional_string(data.get("tone"), "Tone", 50)
        if err:
            errors["tone"] = err

    desc_val = data.get("description") or data.get("topic")
    if desc_val:
        err = validate_optional_string(desc_val, "Description / Topic", MAX_TOPIC_LENGTH)
        if err:
            errors["description"] = err

    if data.get("input_summary") is not None:
        err = validate_optional_string(data.get("input_summary"), "Input summary", 500)
        if err:
            errors["input_summary"] = err

    if data.get("ai_model") is not None:
        err = validate_optional_string(data.get("ai_model"), "AI model", 100)
        if err:
            errors["ai_model"] = err

    generation_parameters = data.get("generation_parameters")
    if generation_parameters is not None:
        if not isinstance(generation_parameters, dict):
            errors["generation_parameters"] = "Generation parameters must be an object."
        elif len(json.dumps(generation_parameters, ensure_ascii=False)) > 10000:
            errors["generation_parameters"] = "Generation parameters are too large."

    if data.get("tokens_used") is not None:
        err = validate_integer_range(data.get("tokens_used"), "Tokens used", 0, 2147483647, required=False)
        if err:
            errors["tokens_used"] = err

    return errors


def validate_version_input(data):
    """
    Validates input for saving a project version snapshot.

    Args:
        data (dict): The JSON request body.

    Returns:
        dict: Field → error message. Empty dict means valid.
    """
    errors = {}

    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    content_val = data.get("content") if "content" in data else data.get("generated_content")
    err = validate_required_string(content_val, "Version content", MAX_CONTENT_LENGTH)
    if err:
        errors["content"] = err

    summary = data.get("summary") or data.get("version_note") or data.get("input_summary")
    if summary:
        err = validate_optional_string(summary, "Version summary", 500)
        if err:
            errors["summary"] = err

    return errors


def validate_story_operation_input(data, operation):
    """
    Validates input for story operations (regenerate, expand, shorten, continue).

    Args:
        data (dict): The JSON request body.
        operation (str): 'regenerate' | 'expand' | 'shorten' | 'continue'

    Returns:
        dict: Field -> error message. Empty dict means valid.
    """
    errors = {}

    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    # For continue/expand/shorten, existing content is required
    if operation in ("expand", "shorten", "continue"):
        err = validate_required_string(data.get("content"), "Story content", MAX_CONTENT_LENGTH)
        if err:
            errors["content"] = err

    # For regenerate, either content or topic/genre must be provided
    elif operation == "regenerate":
        content = data.get("content")
        topic = data.get("topic")
        if not content and not topic:
            errors["content"] = "Either existing story content or a topic is required for regeneration."
        if content:
            err = validate_optional_string(content, "Story content", MAX_CONTENT_LENGTH)
            if err:
                errors["content"] = err
        if topic:
            err = validate_optional_string(topic, "Topic", MAX_TOPIC_LENGTH)
            if err:
                errors["topic"] = err

    # Common optional fields
    if data.get("instructions"):
        err = validate_optional_string(data.get("instructions"), "Instructions", MAX_INSTRUCTIONS_LENGTH)
        if err:
            errors["instructions"] = err

    if data.get("language"):
        err = validate_enum(data.get("language"), "Language", ALLOWED_LANGUAGES, required=False)
        if err:
            errors["language"] = err

    if data.get("genre"):
        err = validate_enum(data.get("genre"), "Genre", ALLOWED_GENRES, required=False)
        if err:
            errors["genre"] = err

    if data.get("tone"):
        err = validate_enum(data.get("tone"), "Tone", ALLOWED_TONES, required=False)
        if err:
            errors["tone"] = err

    if operation == "expand" and data.get("focus_area"):
        err = validate_optional_string(data.get("focus_area"), "Focus area", MAX_INSTRUCTIONS_LENGTH)
        if err:
            errors["focus_area"] = err

    if operation == "continue" and data.get("direction"):
        err = validate_optional_string(data.get("direction"), "Direction", MAX_INSTRUCTIONS_LENGTH)
        if err:
            errors["direction"] = err

    return errors


def validate_export_input(data):
    """
    Validates input for export requests.

    Args:
        data (dict): The JSON request body.

    Returns:
        dict: Field → error message. Empty dict means valid.
    """
    errors = {}

    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    has_project_id = bool(data.get("project_id"))
    content = data.get("content") if "content" in data else data.get("generated_content")

    if not has_project_id:
        err = validate_required_string(content, "Content", MAX_CONTENT_LENGTH)
        if err:
            errors["content"] = err

        if "title" in data and data.get("title") is not None:
            err = validate_optional_string(data.get("title"), "Title", MAX_TITLE_LENGTH)
            if err:
                errors["title"] = err
    else:
        if content is not None:
            err = validate_optional_string(content, "Content", MAX_CONTENT_LENGTH)
            if err:
                errors["content"] = err

        if "title" in data and data.get("title") is not None:
            err = validate_optional_string(data.get("title"), "Title", MAX_TITLE_LENGTH)
            if err:
                errors["title"] = err

    return errors


def sanitize_filename(filename):
    """
    Creates a safe filename from user input.
    Removes special characters and limits length.

    Args:
        filename (str): The original filename.

    Returns:
        str: A safe filename string.
    """
    if not filename:
        return "storyverse_export"
    # Remove any character that isn't alphanumeric, space, dash or underscore
    safe = re.sub(r"[^\w\s\-]", "", filename)
    # Replace spaces with underscores
    safe = re.sub(r"\s+", "_", safe.strip())
    # Limit length
    safe = safe[:100]
    return safe or "storyverse_export"


ALLOWED_RAG_DOC_TYPES = {
    "worldbuilding", "character", "lore", "rules", "reference", "other"
}


def validate_rag_ingest_input(data):
    """
    Validates input for RAG document ingestion.

    Args:
        data (dict): The JSON request body.

    Returns:
        dict: Field → error message. Empty dict means valid.
    """
    errors = {}
    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    err = validate_required_string(data.get("title"), "Title", 200)
    if err:
        errors["title"] = err

    err = validate_required_string(data.get("content"), "Content", MAX_CONTENT_LENGTH)
    if err:
        errors["content"] = err

    doc_type = data.get("doc_type")
    if doc_type:
        if not isinstance(doc_type, str):
            errors["doc_type"] = "Document type must be a string."
        elif doc_type.strip().lower() not in ALLOWED_RAG_DOC_TYPES:
            errors["doc_type"] = (
                f"Invalid document type '{doc_type}'. Allowed: "
                f"{', '.join(sorted(ALLOWED_RAG_DOC_TYPES))}."
            )

    if data.get("genre"):
        genre_err = validate_enum(data.get("genre"), "Genre", ALLOWED_GENRES, required=False)
        if genre_err:
            errors["genre"] = genre_err

    if data.get("language"):
        lang_err = validate_enum(data.get("language"), "Language", ALLOWED_LANGUAGES, required=False)
        if lang_err:
            errors["language"] = lang_err

    project_id = data.get("project_id")
    if project_id is not None and project_id != "":
        try:
            int(project_id)
        except (ValueError, TypeError):
            errors["project_id"] = "project_id must be an integer."

    return errors


def validate_rag_query_input(data):
    """
    Validates input for RAG semantic search / query requests.

    Args:
        data (dict): The JSON request body.

    Returns:
        dict: Field → error message. Empty dict means valid.
    """
    errors = {}
    if not isinstance(data, dict):
        return {"request": "Request body must be a JSON object."}

    err = validate_required_string(data.get("query"), "Query", MAX_TOPIC_LENGTH)
    if err:
        errors["query"] = err

    n_results = data.get("n_results")
    if n_results is not None:
        try:
            val = int(n_results)
            if val < 1 or val > 20:
                errors["n_results"] = "n_results must be between 1 and 20."
        except (ValueError, TypeError):
            errors["n_results"] = "n_results must be an integer."

    project_id = data.get("project_id")
    if project_id is not None and project_id != "":
        try:
            int(project_id)
        except (ValueError, TypeError):
            errors["project_id"] = "project_id must be an integer."

    return errors
