"""
StoryVerse AI — Writing Assistant Module Tests
===============================================
Comprehensive integration and unit tests for Phase 8:
  1. POST /api/rewrite (clarity, grammar, professional, creative, engaging, simplify)
  2. POST /api/translate (English, Telugu, Tamil, Hindi)
  3. POST /api/summarize (short, medium, detailed)
  4. POST /api/generate-dialogue (characters, context, subtext, tone)
  5. POST /api/generate-plot-twist (premise, genre, logical twists)
  6. POST /api/continue-writing (seamless narrative extension)
  7. Empty content validation (400)
  8. Missing target language validation (400)
  9. Invalid target language validation (400)
  10. Invalid summary length validation (400)
  11. Missing dialogue context validation (400)
  12. Missing plot twist premise validation (400)
  13. Non-JSON request body rejection (400)
  14. Simulated AI rate limit error (429)
  15. Simulated AI timeout error (504)
  16. Simulated AI network error (502)
  17. Simulated AI empty response error (502)
  18. Missing API key in live mode (500)
"""

import json
import pytest
from unittest.mock import patch

from services.writing_assistant_service import writing_assistant_service
from services.ai_provider import (
    MockAIProvider,
    GeminiProvider,
    AIRateLimitError,
    AITimeoutError,
    AINetworkError,
    AIEmptyResponseError,
)
from services.ai_service import AIService
from utils.validators import validate_writing_assistant_input


# ============================================================
# 1. Unit Tests: Validators
# ============================================================

class TestWritingAssistantValidators:
    """Tests for validate_writing_assistant_input across all operations."""

    def test_valid_rewrite_input(self):
        data = {"content": "The cat sat on the mat.", "style": "improve clarity"}
        errors = validate_writing_assistant_input(data, operation="rewrite")
        assert errors == {}

    def test_empty_content_rejected(self):
        errors = validate_writing_assistant_input({"content": "   "}, operation="rewrite")
        assert "content" in errors

    def test_translate_valid_languages(self):
        for lang in ["English", "Telugu", "Tamil", "Hindi"]:
            data = {"content": "Hello world", "target_language": lang}
            errors = validate_writing_assistant_input(data, operation="translate")
            assert errors == {}

    def test_translate_missing_target_language(self):
        errors = validate_writing_assistant_input({"content": "Hello world"}, operation="translate")
        assert "target_language" in errors

    def test_translate_invalid_target_language(self):
        data = {"content": "Hello world", "target_language": "Esperanto"}
        errors = validate_writing_assistant_input(data, operation="translate")
        assert "target_language" in errors

    def test_summarize_valid_lengths(self):
        for length in ["short", "medium", "detailed"]:
            data = {"content": "Long story text...", "length": length}
            errors = validate_writing_assistant_input(data, operation="summarize")
            assert errors == {}

    def test_summarize_invalid_length(self):
        data = {"content": "Long story text...", "length": "super_mega_ultra_long"}
        errors = validate_writing_assistant_input(data, operation="summarize")
        assert "length" in errors

    def test_dialogue_valid_input(self):
        data = {
            "context": "Two spies meeting at a crowded cafe",
            "characters": "Agent A, Agent B",
            "genre": "Thriller"
        }
        errors = validate_writing_assistant_input(data, operation="generate-dialogue")
        assert errors == {}

    def test_dialogue_missing_context(self):
        errors = validate_writing_assistant_input({"characters": "Agent A"}, operation="generate-dialogue")
        assert "context" in errors

    def test_plot_twist_valid_input(self):
        data = {
            "premise": "A detective investigates an art theft",
            "genre": "Mystery"
        }
        errors = validate_writing_assistant_input(data, operation="generate-plot-twist")
        assert errors == {}

    def test_plot_twist_missing_premise(self):
        errors = validate_writing_assistant_input({"genre": "Mystery"}, operation="generate-plot-twist")
        assert "premise" in errors

    def test_continue_valid_input(self):
        data = {"content": "She unlocked the vault door and gasped."}
        errors = validate_writing_assistant_input(data, operation="continue-writing")
        assert errors == {}

    def test_non_dict_rejected(self):
        errors = validate_writing_assistant_input("not a dict", operation="rewrite")
        assert "request" in errors


# ============================================================
# 2. Integration Tests: POST /api/rewrite
# ============================================================

class TestRewriteEndpoint:
    """Integration tests for POST /api/rewrite."""

    @pytest.mark.parametrize("style", [
        "improve clarity",
        "improve grammar",
        "make it professional",
        "make it creative",
        "make it engaging",
        "simplify language"
    ])
    def test_rewrite_styles(self, client, style):
        payload = {
            "content": "The device was not working because of reasons unknown to the engineering staff.",
            "style": style,
            "language": "English"
        }
        res = client.post("/api/rewrite", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "rewritten" in data["data"]
        assert data["data"]["style"] == style

    def test_rewrite_missing_content_error(self, client):
        res = client.post("/api/rewrite", json={"style": "improve clarity"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "content" in data["errors"]


# ============================================================
# 3. Integration Tests: POST /api/translate
# ============================================================

class TestTranslateEndpoint:
    """Integration tests for POST /api/translate."""

    @pytest.mark.parametrize("target_lang", ["English", "Telugu", "Tamil", "Hindi"])
    def test_translate_languages(self, client, target_lang):
        payload = {
            "content": "Dawn broke over the ancient observatory, painting the brass dome in silver light.",
            "target_language": target_lang
        }
        res = client.post("/api/translate", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "translation" in data["data"]
        assert data["data"]["target_language"] == target_lang

    def test_translate_missing_target_language_error(self, client):
        res = client.post("/api/translate", json={"content": "Some text"})
        assert res.status_code == 400
        data = res.get_json()
        assert "target_language" in data["errors"]

    def test_translate_invalid_target_language_error(self, client):
        res = client.post("/api/translate", json={"content": "Some text", "target_language": "Latin"})
        assert res.status_code == 400
        data = res.get_json()
        assert "target_language" in data["errors"]


# ============================================================
# 4. Integration Tests: POST /api/summarize
# ============================================================

class TestSummarizeEndpoint:
    """Integration tests for POST /api/summarize."""

    @pytest.mark.parametrize("length", ["short", "medium", "detailed"])
    def test_summarize_lengths(self, client, length):
        payload = {
            "content": "The voyage began in autumn. Twelve ships sailed into the western passage...",
            "length": length
        }
        res = client.post("/api/summarize", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "summary" in data["data"]
        assert data["data"]["length"] == length

    def test_summarize_missing_content_error(self, client):
        res = client.post("/api/summarize", json={"length": "short"})
        assert res.status_code == 400
        assert "content" in res.get_json()["errors"]


# ============================================================
# 5. Integration Tests: POST /api/generate-dialogue
# ============================================================

class TestDialogueEndpoint:
    """Integration tests for POST /api/generate-dialogue."""

    def test_generate_dialogue_success(self, client):
        payload = {
            "context": "A retired astronaut reveals a hidden message found on lunar dust.",
            "characters": "Commander Ross, Arjun",
            "genre": "Science Fiction",
            "tone": "Tense",
            "language": "English"
        }
        res = client.post("/api/generate-dialogue", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "dialogue" in data["data"]
        last_prompt = writing_assistant_service.ai.provider.last_prompt
        assert "- Language: English" in last_prompt
        assert "Write entirely in English." in last_prompt

    @pytest.mark.parametrize("lang", ["Telugu", "Tamil", "Hindi"])
    def test_generate_dialogue_multilingual(self, client, lang):
        payload = {
            "context": f"Two friends discussing a secret in {lang}.",
            "characters": "Character A, Character B",
            "language": lang
        }
        res = client.post("/api/generate-dialogue", json=payload)
        assert res.status_code == 200
        assert res.get_json()["data"]["metadata"]["language"] == lang
        last_prompt = writing_assistant_service.ai.provider.last_prompt
        assert f"- Language: {lang}" in last_prompt
        assert f"Write entirely in {lang}." in last_prompt

    def test_generate_dialogue_missing_context_error(self, client):
        res = client.post("/api/generate-dialogue", json={"characters": "Ross, Arjun"})
        assert res.status_code == 400
        assert "context" in res.get_json()["errors"]


# ============================================================
# 6. Integration Tests: POST /api/generate-plot-twist
# ============================================================

class TestPlotTwistEndpoint:
    """Integration tests for POST /api/generate-plot-twist."""

    def test_generate_plot_twist_success(self, client):
        payload = {
            "premise": "A submarine crew discovers the surface world went dark 48 hours ago.",
            "genre": "Thriller",
            "tone": "Suspenseful",
            "language": "English"
        }
        res = client.post("/api/generate-plot-twist", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "plot_twists" in data["data"]
        last_prompt = writing_assistant_service.ai.provider.last_prompt
        assert "- Language: English" in last_prompt
        assert "Write entirely in English." in last_prompt

    @pytest.mark.parametrize("lang", ["Telugu", "Tamil", "Hindi"])
    def test_generate_plot_twist_multilingual(self, client, lang):
        payload = {
            "premise": f"A mystery unfolds in {lang}.",
            "language": lang
        }
        res = client.post("/api/generate-plot-twist", json=payload)
        assert res.status_code == 200
        assert res.get_json()["data"]["metadata"]["language"] == lang
        last_prompt = writing_assistant_service.ai.provider.last_prompt
        assert f"- Language: {lang}" in last_prompt
        assert f"Write entirely in {lang}." in last_prompt

    def test_generate_plot_twist_missing_premise_error(self, client):
        res = client.post("/api/generate-plot-twist", json={"genre": "Thriller"})
        assert res.status_code == 400
        assert "premise" in res.get_json()["errors"]


# ============================================================
# 7. Integration Tests: POST /api/continue-writing
# ============================================================

class TestContinueWritingEndpoint:
    """Integration tests for POST /api/continue-writing."""

    def test_continue_writing_success(self, client):
        payload = {
            "content": "The signal spiked once more, then settled into a low rhythmic hum.",
            "direction": "Reveal the satellite's origin",
            "language": "English"
        }
        res = client.post("/api/continue-writing", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "continuation" in data["data"]
        assert "combined_text" in data["data"]
        last_prompt = writing_assistant_service.ai.provider.last_prompt
        assert "Write in English." in last_prompt

    @pytest.mark.parametrize("lang", ["Telugu", "Tamil", "Hindi"])
    def test_continue_writing_multilingual(self, client, lang):
        payload = {
            "content": "A story beginning...",
            "language": lang
        }
        res = client.post("/api/continue-writing", json=payload)
        assert res.status_code == 200
        last_prompt = writing_assistant_service.ai.provider.last_prompt
        assert f"Write in {lang}." in last_prompt

    def test_continue_writing_missing_content_error(self, client):
        res = client.post("/api/continue-writing", json={"direction": "Next scene"})
        assert res.status_code == 400
        assert "content" in res.get_json()["errors"]


# ============================================================
# 8. AI Error Simulation Tests
# ============================================================

class TestWritingAssistantErrors:
    """Verifies that AI provider failures return proper error codes."""

    def test_simulated_rate_limit(self, client):
        with patch.object(
            writing_assistant_service.ai.provider,
            "generate",
            side_effect=AIRateLimitError("Rate limit exceeded.")
        ):
            res = client.post("/api/rewrite", json={"content": "Sample text", "style": "improve clarity"})
            assert res.status_code == 429
            assert "rate limit" in res.get_json()["message"].lower()

    def test_simulated_timeout(self, client):
        with patch.object(
            writing_assistant_service.ai.provider,
            "generate",
            side_effect=AITimeoutError("AI request timed out.")
        ):
            res = client.post("/api/translate", json={"content": "Sample text", "target_language": "Telugu"})
            assert res.status_code == 504

    def test_simulated_network_error(self, client):
        with patch.object(
            writing_assistant_service.ai.provider,
            "generate",
            side_effect=AINetworkError("Network reset.")
        ):
            res = client.post("/api/summarize", json={"content": "Sample text", "length": "short"})
            assert res.status_code == 502

    def test_simulated_empty_response(self, client):
        with patch.object(
            writing_assistant_service.ai.provider,
            "generate",
            side_effect=AIEmptyResponseError("Empty response.")
        ):
            res = client.post("/api/generate-plot-twist", json={"premise": "Sample premise"})
            assert res.status_code == 502

    def test_unconfigured_api_key(self, client):
        with patch.object(writing_assistant_service.ai, "_provider", GeminiProvider(api_key="")):
            res = client.post("/api/rewrite", json={"content": "Sample text"})
            assert res.status_code == 500
            assert "API key is not configured" in res.get_json()["message"]
