"""
StoryVerse AI — Story Generator Module Tests
=============================================
Comprehensive integration and unit tests for Phase 5:
  1. Horror story generation
  2. Romantic story generation
  3. Comedy story generation
  4. Science-fiction story generation
  5. English story
  6. Telugu story
  7. Tamil story
  8. Hindi story
  9. Character names inclusion
  10. Empty topic validation (400)
  11. Invalid genre validation (400)
  12. Invalid language validation (400)
  13. Invalid tone validation (400)
  14. Invalid length validation (400)
  15. Excessive character count validation (400)
  16. POST /api/expand
  17. POST /api/shorten
  18. POST /api/continue
  19. POST /api/regenerate
  20. Missing API key handling
  21. Simulated AI failure handling
  22. Malformed AI response handling
"""

import json
import pytest
from unittest.mock import patch

from services.story_service import StoryService, story_service
from services.ai_provider import (
    MockAIProvider,
    GeminiProvider,
    AIConfigurationError,
    AIRateLimitError,
    AIMalformedResponseError
)
from services.ai_service import AIService


MOCK_STORY_OUTPUT = """1. TITLE: Shadows of the Eldermoor
2. SYNOPSIS: A young scholar uncovers a forbidden tome in the mist-veiled ruins of Eldermoor, unlocking an ancient secret.
3. SETTING: Eldermoor, an overgrown gothic valley shrouded in perpetual silver fog and crumbling marble towers.
4. CHARACTERS: 
- Arun (24): An inquisitive archivist driven by curiosity.
- Maya (22): A cautious cartographer with a hidden family secret.
5. ACT I - THE BEGINNING:
Arun brushed centuries of cobwebs off the bronze-bound grimoire. Beside him, Maya whispered a warning that went unheeded.
6. ACT II - THE CONFLICT:
As the runes flared to life, whispers echoed from the stone walls. The valley began shifting, trapping them inside the archives.
7. CONFLICT:
The spectral guardians demanded a memory as tribute for each answered question, threatening their very identities.
8. ACT III - THE CLIMAX:
Cornered by the shade of the grand archivist, Arun chose to sacrifice his recollection of finding the book, breaking the cycle.
9. CONCLUSION:
The mist lifted. Arun and Maya stepped out into dawn, scarred but free, having preserved the valley's secrets.
10. MORAL / CORE THEME:
True wisdom lies not in possessing forbidden power, but in knowing when to let it rest."""


@pytest.fixture
def mock_story_svc():
    provider = MockAIProvider(default_response=MOCK_STORY_OUTPUT)
    ai_svc = AIService(provider=provider)
    return StoryService(ai_svc=ai_svc)


# ============================================================
# 1. Story Generation Tests (Genres, Languages, Characters)
# ============================================================

class TestStoryGenerationEndpoints:

    def test_horror_story_generation(self, client):
        payload = {
            "topic": "An abandoned asylum at midnight",
            "genre": "Horror",
            "language": "English",
            "tone": "Dark",
            "length": "Short"
        }
        res = client.post("/api/generate-story", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "data" in data
        assert "title" in data["data"]
        assert "summary" in data["data"]
        assert "full_text" in data["data"]

    def test_romance_story_generation(self, client):
        payload = {
            "topic": "Reunited at a Parisian café after ten years",
            "genre": "Romance",
            "language": "English",
            "tone": "Romantic"
        }
        res = client.post("/api/generate-story", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["data"]["metadata"]["genre"] == "Romance"

    def test_comedy_story_generation(self, client):
        payload = {
            "topic": "A royal chef accidentally puts sleeping potion in the coronation soup",
            "genre": "Comedy",
            "language": "English",
            "tone": "Funny"
        }
        res = client.post("/api/generate-story", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["data"]["metadata"]["genre"] == "Comedy"

    def test_scifi_story_generation(self, client):
        payload = {
            "topic": "First contact on Europa's subsurface ocean",
            "genre": "Science Fiction",
            "language": "English",
            "tone": "Suspenseful"
        }
        res = client.post("/api/generate-story", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["data"]["metadata"]["genre"] == "Science Fiction"

    def test_telugu_story_generation(self, client):
        payload = {
            "topic": "A brave farmer defends his village from bandits",
            "genre": "Adventure",
            "language": "Telugu"
        }
        res = client.post("/api/generate-story", json=payload)
        assert res.status_code == 200
        assert res.get_json()["data"]["metadata"]["language"] == "Telugu"
        last_prompt = story_service.ai.provider.last_prompt
        assert "- Language: Telugu" in last_prompt
        assert "Write exclusively in Telugu." in last_prompt

    def test_tamil_story_generation(self, client):
        payload = {
            "topic": "An ancient temple inscription unlocks a hidden chamber",
            "genre": "Mystery",
            "language": "Tamil"
        }
        res = client.post("/api/generate-story", json=payload)
        assert res.status_code == 200
        assert res.get_json()["data"]["metadata"]["language"] == "Tamil"
        last_prompt = story_service.ai.provider.last_prompt
        assert "- Language: Tamil" in last_prompt
        assert "Write exclusively in Tamil." in last_prompt

    def test_hindi_story_generation(self, client):
        payload = {
            "topic": "A train journey across the Himalayas brings together strangers",
            "genre": "Drama",
            "language": "Hindi"
        }
        res = client.post("/api/generate-story", json=payload)
        assert res.status_code == 200
        assert res.get_json()["data"]["metadata"]["language"] == "Hindi"
        last_prompt = story_service.ai.provider.last_prompt
        assert "- Language: Hindi" in last_prompt
        assert "Write exclusively in Hindi." in last_prompt

    def test_story_generation_with_and_without_rag_preserves_language(self, client):
        # 1. With RAG disabled (pure parametric)
        res_no_rag = client.post("/api/generate-story", json={
            "topic": "An astronomer hears signals from a distant pulsar",
            "genre": "Science Fiction",
            "language": "English",
            "use_rag": False
        })
        assert res_no_rag.status_code == 200
        prompt_no_rag = story_service.ai.provider.last_prompt
        assert "- Language: English" in prompt_no_rag
        assert "Write exclusively in English." in prompt_no_rag
        assert "=== [RETRIEVED KNOWLEDGE CONTEXT — GROUND TRUTH] ===" not in prompt_no_rag

        # 2. With RAG enabled
        res_rag = client.post("/api/generate-story", json={
            "topic": "An astronomer hears signals from a distant pulsar",
            "genre": "Science Fiction",
            "language": "English",
            "use_rag": True,
            "rag_context": "=== [RETRIEVED KNOWLEDGE CONTEXT — GROUND TRUTH] ===\nPulsar frequency is 11.4s"
        })
        assert res_rag.status_code == 200
        prompt_rag = story_service.ai.provider.last_prompt
        assert "=== [RETRIEVED KNOWLEDGE CONTEXT — GROUND TRUTH] ===" in prompt_rag
        assert "- Language: English" in prompt_rag
        assert "Write exclusively in English." in prompt_rag

    def test_character_names_parameter(self, client):
        payload = {
            "topic": "Two detectives solving an impossible burglary",
            "genre": "Mystery",
            "character_names": ["Vikram", "Ananya"],
            "character_count": 2
        }
        res = client.post("/api/generate-story", json=payload)
        assert res.status_code == 200
        assert res.get_json()["success"] is True


# ============================================================
# 2. Input Validation Tests
# ============================================================

class TestStoryValidation:

    def test_empty_topic_rejected(self, client):
        res = client.post("/api/generate-story", json={"topic": "", "genre": "Fantasy"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "topic" in data["errors"]

    def test_invalid_genre_rejected(self, client):
        res = client.post("/api/generate-story", json={"topic": "Magic wand", "genre": "SuperficialGenre"})
        assert res.status_code == 400
        assert "genre" in res.get_json()["errors"]

    def test_invalid_language_rejected(self, client):
        res = client.post("/api/generate-story", json={"topic": "Voyage", "genre": "Adventure", "language": "Latin"})
        assert res.status_code == 400
        assert "language" in res.get_json()["errors"]

    def test_invalid_tone_rejected(self, client):
        res = client.post("/api/generate-story", json={"topic": "Tale", "genre": "Drama", "tone": "Extravagant"})
        assert res.status_code == 400
        assert "tone" in res.get_json()["errors"]

    def test_invalid_length_rejected(self, client):
        res = client.post("/api/generate-story", json={"topic": "Tale", "genre": "Drama", "length": "SuperGigantic"})
        assert res.status_code == 400
        assert "length" in res.get_json()["errors"]

    def test_excessive_character_count_rejected(self, client):
        res = client.post("/api/generate-story", json={"topic": "Tale", "genre": "Drama", "character_count": 99})
        assert res.status_code == 400
        assert "character_count" in res.get_json()["errors"]

    def test_missing_json_body_rejected(self, client):
        res = client.post("/api/generate-story", data="not json", content_type="text/plain")
        assert res.status_code == 400
        assert res.get_json()["success"] is False


# ============================================================
# 3. Story Editing Operations (Expand, Shorten, Continue, Regenerate)
# ============================================================

class TestStoryEditingOperations:

    def test_expand_story(self, client):
        payload = {
            "content": "The knight stepped into the dark cavern. Water dripped from stalactites.",
            "focus_area": "Sensory sounds and the ancient scent of damp moss"
        }
        res = client.post("/api/expand", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "full_text" in data["data"]

    def test_shorten_story(self, client):
        payload = {
            "content": "A very long detailed story about a traveler wandering the vast deserts...",
            "target_reduction": "50%"
        }
        res = client.post("/api/shorten", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "full_text" in data["data"]

    def test_continue_story(self, client):
        payload = {
            "content": "The key turned in the heavy iron lock. The door slowly creaked open.",
            "direction": "Reveal what lies inside the vault"
        }
        res = client.post("/api/continue", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "full_text" in data["data"]
        assert "continuation" in data["data"]

    def test_regenerate_story(self, client):
        payload = {
            "content": "Original draft of the mystery story.",
            "instructions": "Increase the suspense and add rain."
        }
        res = client.post("/api/regenerate", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "full_text" in data["data"]


# ============================================================
# 4. Error Scenarios & Section Parsing
# ============================================================

class TestStoryServiceErrorScenarios:

    def test_missing_api_key_handling(self):
        """GeminiProvider with empty key must raise AIConfigurationError."""
        gemini = GeminiProvider(api_key="")
        with pytest.raises(AIConfigurationError):
            gemini.generate("Write a story")

    def test_missing_api_key_endpoint_error(self, client):
        """When GeminiProvider has no key, the API endpoint returns 500 with configuration message."""
        with patch.object(story_service.ai, "_provider", GeminiProvider(api_key="")):
            payload = {"topic": "Valid Topic", "genre": "Horror"}
            res = client.post("/api/generate-story", json=payload)
            assert res.status_code == 500
            data = res.get_json()
            assert data["success"] is False
            assert "gemini api key is not configured" in data["message"].lower()

    def test_simulated_ai_failure(self, client):
        """Simulated rate limit returns 429 JSON response."""
        with patch("services.story_service.story_service.ai.call_ai_model") as mock_call:
            mock_call.side_effect = AIRateLimitError("Quota exhausted")
            payload = {"topic": "Valid Topic", "genre": "Horror"}
            res = client.post("/api/generate-story", json=payload)
            assert res.status_code == 429
            data = res.get_json()
            assert data["success"] is False
            assert "rate limit" in data["message"].lower()

    def test_malformed_ai_response_handling(self, client):
        """Malformed AI response returns 502 Bad Gateway JSON response."""
        with patch("services.story_service.story_service.ai.call_ai_model") as mock_call:
            mock_call.side_effect = AIMalformedResponseError("Invalid structure")
            payload = {"topic": "Valid Topic", "genre": "Fantasy"}
            res = client.post("/api/generate-story", json=payload)
            assert res.status_code == 502
            assert res.get_json()["success"] is False

    def test_parse_story_sections_unstructured_fallback(self):
        """If AI output lacks numbered headers, full text is preserved cleanly."""
        raw_story = "Once upon a time in a distant kingdom, there lived a clockmaker who built birds of bronze."
        sections = StoryService.parse_story_sections(raw_story)
        assert sections["main_plot"] == raw_story
        assert sections["title"] != ""
