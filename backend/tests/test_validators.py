"""
StoryVerse AI — Input Validation Tests
=========================================
Tests for the validator functions in utils/validators.py.

The validators return a plain dict: {} means valid, populated dict means errors.

These tests confirm that:
  - Valid input passes validation cleanly (empty dict).
  - Missing required fields are caught.
  - Out-of-range values are caught.
  - Invalid enum values are caught.
  - sanitize_filename prevents path traversal.
"""

from utils.validators import (
    validate_story_input,
    validate_script_input,
    validate_character_input,
    validate_project_input,
    sanitize_filename,
)


# ---------------------------------------------------------------------------
# Story Validator
# ---------------------------------------------------------------------------

class TestStoryValidator:

    VALID_STORY = {
        "topic": "A dragon who fears fire",
        "genre": "Fantasy",
        "language": "English",
        "tone": "Emotional",
        "length": "medium",
        "audience": "General Audience",
    }

    def test_valid_story_passes(self):
        """A fully valid story input returns an empty errors dict."""
        errors = validate_story_input(self.VALID_STORY)
        assert errors == {}, f"Unexpected errors: {errors}"

    def test_missing_topic(self):
        """Missing 'topic' must be reported as an error."""
        data = {**self.VALID_STORY, "topic": ""}
        errors = validate_story_input(data)
        assert "topic" in errors

    def test_invalid_genre(self):
        """An unrecognized genre must be reported as an error."""
        data = {**self.VALID_STORY, "genre": "InvalidGenre"}
        errors = validate_story_input(data)
        assert "genre" in errors

    def test_invalid_language(self):
        """An unsupported language must be reported as an error."""
        data = {**self.VALID_STORY, "language": "Klingon"}
        errors = validate_story_input(data)
        assert "language" in errors

    def test_missing_all_required_fields(self):
        """Submitting an empty dict must report at least genre and topic errors."""
        errors = validate_story_input({})
        assert len(errors) > 0

    def test_topic_too_long(self):
        """A topic exceeding the max length must be rejected."""
        data = {**self.VALID_STORY, "topic": "x" * 2001}
        errors = validate_story_input(data)
        assert "topic" in errors

    def test_invalid_tone(self):
        """An unrecognized tone must be reported."""
        data = {**self.VALID_STORY, "tone": "Aggressive"}
        errors = validate_story_input(data)
        assert "tone" in errors

    def test_invalid_length(self):
        """An unrecognized length value must be reported."""
        data = {**self.VALID_STORY, "length": "extra-long"}
        errors = validate_story_input(data)
        assert "length" in errors


# ---------------------------------------------------------------------------
# Script Validator
# ---------------------------------------------------------------------------

class TestScriptValidator:

    VALID_SCRIPT = {
        "topic": "A heist in space",
        "genre": "Thriller",
        "language": "English",
        "tone": "Suspenseful",
        "length": "medium",
        "num_scenes": 5,
    }

    def test_valid_script_passes(self):
        errors = validate_script_input(self.VALID_SCRIPT)
        assert errors == {}, f"Unexpected errors: {errors}"

    def test_missing_topic(self):
        data = {**self.VALID_SCRIPT, "topic": ""}
        errors = validate_script_input(data)
        assert "topic" in errors

    def test_num_scenes_out_of_range(self):
        """num_scenes above MAX_SCENES must be rejected."""
        data = {**self.VALID_SCRIPT, "num_scenes": 999}
        errors = validate_script_input(data)
        assert "num_scenes" in errors

    def test_invalid_genre(self):
        data = {**self.VALID_SCRIPT, "genre": "WeirdGenre"}
        errors = validate_script_input(data)
        assert "genre" in errors

    def test_missing_genre(self):
        """genre is required for scripts."""
        data = {k: v for k, v in self.VALID_SCRIPT.items() if k != "genre"}
        errors = validate_script_input(data)
        assert "genre" in errors


# ---------------------------------------------------------------------------
# Character Validator (uses 'description' field)
# ---------------------------------------------------------------------------

class TestCharacterValidator:

    VALID_CHARACTER = {
        "description": "A brave knight from medieval times",
        "genre": "Fantasy",
        "name": "Sir Arthur",
    }

    def test_valid_character_passes(self):
        errors = validate_character_input(self.VALID_CHARACTER)
        assert errors == {}, f"Unexpected errors: {errors}"

    def test_missing_description(self):
        """'description' is the required field for character generation."""
        data = {**self.VALID_CHARACTER, "description": ""}
        errors = validate_character_input(data)
        assert "description" in errors

    def test_invalid_genre(self):
        data = {**self.VALID_CHARACTER, "genre": "Space Opera"}
        errors = validate_character_input(data)
        assert "genre" in errors


# ---------------------------------------------------------------------------
# Project Validator (uses 'content_type' field, not 'project_type')
# ---------------------------------------------------------------------------

class TestProjectValidator:

    VALID_PROJECT = {
        "title": "My New Novel",
        "content_type": "story",
        "genre": "Horror",
        "language": "English",
    }

    def test_valid_project_passes(self):
        errors = validate_project_input(self.VALID_PROJECT)
        assert errors == {}, f"Unexpected errors: {errors}"

    def test_missing_title(self):
        data = {**self.VALID_PROJECT, "title": ""}
        errors = validate_project_input(data)
        assert "title" in errors

    def test_invalid_content_type(self):
        """content_type must be 'story', 'script', or 'character'."""
        data = {**self.VALID_PROJECT, "content_type": "poem"}
        errors = validate_project_input(data)
        assert "content_type" in errors

    def test_missing_title_and_content_type(self):
        """Both title and content_type are required for new projects."""
        errors = validate_project_input({})
        assert len(errors) >= 2


# ---------------------------------------------------------------------------
# Filename Sanitizer
# ---------------------------------------------------------------------------

class TestSanitizeFilename:

    def test_normal_filename(self):
        result = sanitize_filename("My Story Title")
        assert ".." not in result
        assert "/" not in result
        assert "\\" not in result

    def test_path_traversal_blocked(self):
        """../../etc/passwd must not appear as-is in sanitized output."""
        result = sanitize_filename("../../etc/passwd")
        assert ".." not in result
        # Dots and slashes should be stripped
        assert "/" not in result

    def test_special_chars_removed(self):
        """Special shell characters must be stripped or replaced."""
        result = sanitize_filename("story<>|?*file")
        for char in ("<", ">", "|", "?", "*"):
            assert char not in result

    def test_empty_filename_fallback(self):
        """An empty or whitespace-only name must return a safe default."""
        result = sanitize_filename("   ")
        assert len(result.strip()) > 0

    def test_none_filename_fallback(self):
        """None input must return a safe default."""
        result = sanitize_filename(None)
        assert len(result.strip()) > 0
