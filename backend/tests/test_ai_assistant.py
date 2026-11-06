"""
StoryVerse AI — AI Assistant & Provider Unit Tests
===================================================
Comprehensive tests for:
  1. Mock provider success
  2. Gemini provider initialization
  3. Missing API key handling
  4. Invalid credentials simulation
  5. Empty AI response handling
  6. Malformed response handling
  7. Rate limit simulation
  8. Network failure simulation
  9. Timeout simulation
  10. Prompt builder validation (all 11 builders)
  11. Language instruction verification
  12. Genre instruction verification
  13. Tone instruction verification
  14. Model configuration
  15. Provider selection logic
  16. Secret sanitization (never leaking API keys in error strings)
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from services.ai_provider import (
    BaseAIProvider,
    GeminiProvider,
    MockAIProvider,
    get_ai_provider,
    AIError,
    AIConfigurationError,
    AIAuthenticationError,
    AIModelNotFoundError,
    AIRateLimitError,
    AINetworkError,
    AITimeoutError,
    AIEmptyResponseError,
    AIMalformedResponseError,
    sanitize_error_message,
)
from services.ai_service import AIService
from services.prompt_service import (
    build_story_prompt,
    build_script_prompt,
    build_character_prompt,
    build_scene_prompt,
    build_dialogue_prompt,
    build_rewrite_prompt,
    build_expand_prompt,
    build_shorten_prompt,
    build_continue_prompt,
    build_translate_prompt,
    build_summarize_prompt,
)


# ============================================================
# 1. Mock Provider Success Tests
# ============================================================

class TestMockProvider:
    """Verifies that the MockAIProvider works predictably for offline tests."""

    def test_mock_provider_success(self):
        provider = MockAIProvider()
        assert provider.is_available() is True
        assert provider.get_provider_name() == "mock"

        result = provider.generate("Write a story about a brave knight.")
        assert isinstance(result, dict)
        assert "text" in result
        assert len(result["text"]) > 0
        assert result["provider"] == "mock"
        assert result["finish_reason"] == "STOP"

    def test_mock_provider_custom_response(self):
        provider = MockAIProvider(default_response="Custom story text")
        result = provider.generate("Any prompt")
        assert result["text"] == "Custom story text"


# ============================================================
# 2. Gemini Provider Initialization & Config
# ============================================================

class TestGeminiProviderInit:
    """Tests Gemini provider configuration and initialization."""

    def test_gemini_init_with_key(self):
        provider = GeminiProvider(api_key="dummy_test_key_xyz", model="gemini-2.5-flash")
        assert provider.is_available() is True
        assert provider.model_name == "gemini-2.5-flash"
        assert provider.get_provider_name() == "gemini"

    def test_missing_api_key_raises_config_error(self):
        """When no key is configured, calling generate must raise AIConfigurationError."""
        provider = GeminiProvider(api_key="")
        assert provider.is_available() is False
        with pytest.raises(AIConfigurationError) as exc_info:
            provider.generate("Generate a tale")
        assert "GEMINI_API_KEY" in str(exc_info.value)

    def test_custom_model_configuration(self):
        provider = GeminiProvider(api_key="valid_format_key", model="gemini-1.5-pro")
        assert provider.model_name == "gemini-1.5-pro"

    def test_client_uses_timeout_in_milliseconds(self, monkeypatch):
        from google import genai

        captured = {}
        monkeypatch.setattr(
            genai,
            "Client",
            lambda **kwargs: captured.update(kwargs) or object()
        )

        GeminiProvider(api_key="test-key", timeout=7)

        assert captured["http_options"].timeout == 7000


# ============================================================
# 3. Provider Selection Factory Logic
# ============================================================

class TestProviderSelection:
    """Tests factory function get_ai_provider()."""

    def test_select_mock_explicitly(self):
        provider = get_ai_provider(provider_name="mock")
        assert isinstance(provider, MockAIProvider)

    def test_select_mock_via_mock_mode_flag(self):
        provider = get_ai_provider(mock_mode=True)
        assert isinstance(provider, MockAIProvider)

    def test_select_gemini_provider(self):
        provider = get_ai_provider(provider_name="gemini", mock_mode=False, api_key="dummy_key")
        assert isinstance(provider, GeminiProvider)

    def test_gemini_timeout_comes_from_app_config(self):
        from flask import Flask

        app = Flask(__name__)
        app.config.update(
            AI_PROVIDER="gemini",
            AI_MOCK_MODE=False,
            GEMINI_API_KEY="test-key",
            GEMINI_MODEL="test-model",
            AI_REQUEST_TIMEOUT=11,
        )

        with app.app_context():
            provider = get_ai_provider()

        assert isinstance(provider, GeminiProvider)
        assert provider.timeout == 11

    def test_env_override_to_mock(self, monkeypatch):
        monkeypatch.setenv("AI_MOCK_MODE", "true")
        provider = get_ai_provider()
        assert isinstance(provider, MockAIProvider)


# ============================================================
# 4. Error Simulation & Handling in AI Service
# ============================================================

class TestAIServiceErrorHandling:
    """Verifies that AIService catches and standardizes all domain AI exceptions."""

    def setup_method(self):
        self.mock_provider = MockAIProvider()
        self.service = AIService(provider=self.mock_provider)

    def test_generate_text_success(self):
        text = self.service.generate_text("A prompt for testing")
        assert isinstance(text, str)
        assert len(text) > 0

    def test_empty_prompt_raises_empty_response_error(self):
        with pytest.raises(AIEmptyResponseError):
            self.service.call_ai_model("   ")

    def test_simulated_empty_response(self):
        self.mock_provider.simulate_error("empty")
        with pytest.raises(AIEmptyResponseError):
            self.service.call_ai_model("Hello world")

    def test_simulated_malformed_response(self):
        self.mock_provider.simulate_error("malformed")
        with pytest.raises(AIMalformedResponseError):
            self.service.call_ai_model("Hello world")

    def test_simulated_rate_limit(self):
        self.mock_provider.simulate_error("rate_limit")
        with pytest.raises(AIRateLimitError):
            self.service.call_ai_model("Hello world")

    def test_simulated_network_error(self):
        self.mock_provider.simulate_error("network_error")
        with pytest.raises(AINetworkError):
            self.service.call_ai_model("Hello world")

    def test_simulated_timeout(self):
        self.mock_provider.simulate_error("timeout")
        with pytest.raises(AITimeoutError):
            self.service.call_ai_model("Hello world")

    def test_simulated_auth_error(self):
        self.mock_provider.simulate_error("auth_error")
        with pytest.raises(AIAuthenticationError):
            self.service.call_ai_model("Hello world")

    def test_simulated_model_not_found(self):
        self.mock_provider.simulate_error("model_not_found")
        with pytest.raises(AIModelNotFoundError):
            self.service.call_ai_model("Hello world")


# ============================================================
# 5. HTTP Error Response Mapping & Secret Sanitization
# ============================================================

class TestHTTPErrorResponseMapping:
    """Verifies that handle_api_error outputs safe JSON and correct HTTP status codes."""

    def test_rate_limit_status_code(self, app):
        with app.app_context():
            resp, status = AIService.handle_api_error(AIRateLimitError())
            assert status == 429
            data = resp.get_json()
            assert data["success"] is False

    def test_auth_error_status_code(self, app):
        with app.app_context():
            resp, status = AIService.handle_api_error(AIAuthenticationError())
            assert status == 401
            data = resp.get_json()
            assert data["success"] is False

    def test_timeout_error_status_code(self, app):
        with app.app_context():
            resp, status = AIService.handle_api_error(AITimeoutError())
            assert status == 504

    def test_network_error_status_code(self, app):
        with app.app_context():
            resp, status = AIService.handle_api_error(AINetworkError())
            assert status == 502

    def test_empty_response_status_code(self, app):
        with app.app_context():
            resp, status = AIService.handle_api_error(AIEmptyResponseError())
            assert status == 502

    def test_config_error_status_code(self, app):
        with app.app_context():
            resp, status = AIService.handle_api_error(AIConfigurationError())
            assert status == 500

    def test_sanitize_error_message_strips_api_keys(self):
        leaked_key = "AIzaSyD-1234567890abcdefghijklmnopqrstuv"
        raw_error = f"Error calling Google API with key {leaked_key} at endpoint https://..."
        sanitized = sanitize_error_message(raw_error)
        assert leaked_key not in sanitized
        assert "[REDACTED" in sanitized


# ============================================================
# 6. Prompt Engineering & Builder Tests
# ============================================================

class TestPromptBuilders:
    """Tests all 11 prompt builders for content, language, genre, and tone adherence."""

    def test_story_prompt_builder(self):
        params = {
            "topic": "A forgotten astronaut returns to Earth",
            "genre": "Science Fiction",
            "language": "Telugu",
            "tone": "Emotional",
            "length": "Medium",
            "audience": "Adults",
            "character_count": 3
        }
        prompt = build_story_prompt(params)
        assert "A forgotten astronaut returns to Earth" in prompt
        assert "Science Fiction" in prompt
        assert "Telugu" in prompt
        assert "Emotional" in prompt
        assert "ACT I" in prompt
        assert "ACT II" in prompt
        assert "ACT III" in prompt
        assert "CLIMAX" in prompt

    def test_script_prompt_builder(self):
        params = {
            "topic": "Bank vault heist at midnight",
            "genre": "Thriller",
            "language": "Hindi",
            "tone": "Suspenseful",
            "num_scenes": 4,
            "characters": "KABIR, TARA",
            "setting": "INT. BANK VAULT - NIGHT"
        }
        prompt = build_script_prompt(params)
        assert "Bank vault heist at midnight" in prompt
        assert "Thriller" in prompt
        assert "Hindi" in prompt
        assert "4 distinct scenes" in prompt
        assert "SCENE HEADINGS" in prompt
        assert "ACTION BLOCKS" in prompt

    def test_character_prompt_builder(self):
        params = {
            "description": "An aging samurai who took a vow of nonviolence",
            "name": "Kenshin",
            "genre": "Historical Drama",
            "language": "English",
            "archetype": "Antihero"
        }
        prompt = build_character_prompt(params)
        assert "nonviolence" in prompt
        assert "Kenshin" in prompt
        assert "Core Want" in prompt
        assert "Core Need" in prompt
        assert "Fatal Flaw" in prompt

    def test_scene_prompt_builder(self):
        prompt = build_scene_prompt({
            "context": "After the courtroom verdict",
            "scene_goal": "Confrontation between lawyer and client",
            "genre": "Drama",
            "language": "Tamil",
            "characters": "Arun, Priya"
        })
        assert "Tamil" in prompt
        assert "Arun, Priya" in prompt
        assert "Confrontation" in prompt

    def test_dialogue_prompt_builder(self):
        prompt = build_dialogue_prompt({
            "characters": "Two estranged sisters",
            "topic": "Dividing their mother's inheritance",
            "subtext": "Bitter rivalry from childhood",
            "language": "English",
            "tone": "Tense"
        })
        assert "Two estranged sisters" in prompt
        assert "inheritance" in prompt
        assert "Subtext" in prompt

    def test_rewrite_prompt_builder(self):
        prompt = build_rewrite_prompt(
            content="The boy walked into the dark room. He was scared.",
            style_instructions="Make it atmospheric and gothic horror",
            language="English"
        )
        assert "atmospheric and gothic horror" in prompt
        assert "The boy walked into the dark room." in prompt

    def test_expand_prompt_builder(self):
        prompt = build_expand_prompt(
            content="Rain fell on the rooftops of Mumbai.",
            focus_area="Sensory smells and neon reflections",
            language="Hindi"
        )
        assert "Sensory smells" in prompt
        assert "Rain fell on the rooftops" in prompt
        assert "Hindi" in prompt

    def test_shorten_prompt_builder(self):
        prompt = build_shorten_prompt(
            content="A very long verbose paragraph with redundant details.",
            target_reduction="50%"
        )
        assert "50%" in prompt
        assert "redundant details" in prompt

    def test_continue_prompt_builder(self):
        prompt = build_continue_prompt(
            content="She opened the mysterious envelope and gasped.",
            direction="Reveal an old photograph with an impossible date",
            language="English"
        )
        assert "mysterious envelope" in prompt
        assert "old photograph" in prompt

    def test_translate_prompt_builder(self):
        prompt = build_translate_prompt(
            content="Once upon a time in a tranquil valley.",
            target_language="Telugu"
        )
        assert "Telugu" in prompt
        assert "literary translation" in prompt
        assert "tranquil valley" in prompt

    def test_summarize_prompt_builder(self):
        prompt = build_summarize_prompt(
            content="Full novel transcript text here...",
            summary_format="bullet_points"
        )
        assert "bullet points" in prompt
        assert "Full novel transcript" in prompt


# ============================================================
# 7. Language & Genre Adherence in Prompts
# ============================================================

class TestPromptLanguageAndGenreRules:
    """Verifies that all 4 supported languages and all genres are enforced."""

    @pytest.mark.parametrize("lang", ["English", "Telugu", "Tamil", "Hindi"])
    def test_supported_languages_in_story_prompt(self, lang):
        prompt = build_story_prompt({"topic": "Adventure", "language": lang})
        assert lang in prompt
        assert f"write the ENTIRE story in {lang}" in prompt

    @pytest.mark.parametrize("genre", ["Horror", "Romance", "Comedy", "Thriller", "Fantasy", "Science Fiction"])
    def test_genres_in_story_prompt(self, genre):
        prompt = build_story_prompt({"topic": "Journey", "genre": genre})
        assert genre in prompt

    @pytest.mark.parametrize("tone", ["Emotional", "Suspenseful", "Inspirational", "Funny", "Dark"])
    def test_tones_in_story_prompt(self, tone):
        prompt = build_story_prompt({"topic": "Journey", "tone": tone})
        assert tone in prompt
