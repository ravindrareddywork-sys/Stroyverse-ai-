"""
StoryVerse AI — Character Generator Module Tests
=================================================
Comprehensive integration and unit tests for Phase 7:
  1. Protagonist character generation
  2. Antagonist character generation
  3. Supporting / Mentor character generation
  4. Fantasy character generation
  5. Sci-Fi character generation
  6. Multilingual character generation (English, Telugu, Tamil, Hindi)
  7. Character profile bible parsing (19 structured narrative dimensions)
  8. Missing description validation (400)
  9. Invalid genre validation (400)
  10. Invalid character role validation (400)
  11. Invalid language validation (400)
  12. Invalid tone validation (400)
  13. POST /api/generate-character-variations endpoint
  14. Character variations count boundaries (2 to 5)
  15. Character variations parser (multiple concepts)
  16. Missing API key error handling (500)
  17. Simulated AI rate limit error (429)
  18. Simulated AI timeout error (504)
  19. Simulated AI network error (502)
  20. Simulated empty AI response error (502)
  21. Malformed request body rejection (400)
  22. Profile parser unstructured prose fallback
"""

import json
import pytest
from unittest.mock import patch

from services.character_service import CharacterService, character_service
from services.ai_provider import (
    MockAIProvider,
    GeminiProvider,
    AIRateLimitError,
    AITimeoutError,
    AINetworkError,
    AIEmptyResponseError,
)
from services.ai_service import AIService
from utils.validators import validate_character_input, validate_character_variations_input


MOCK_CHARACTER_PROFILE = """1. NAME: Kaelen Vance, The Last Cartographer
2. AGE: 34
3. GENDER: Male
4. ROLE: Protagonist
5. ARCHETYPE: Reluctant Explorer / Seeker
6. PHYSICAL APPEARANCE: Tall and wiry with calloused hands stained with indigo ink. A silver scar cuts across his left eyebrow. Wears a weather-beaten leather coat with hidden parchment pockets.
7. PERSONALITY TRAITS: Observant, quiet, fiercely loyal, stubborn, prone to melancholic isolation.
8. PSYCHOLOGICAL PROFILE:
   - Core Want: To map the uncharted subterranean abyss and prove his father's expedition was not in vain.
   - Core Need: To accept that some losses cannot be charted or recovered, and learn to value living companions.
   - The Lie They Believe: He must carry the burden of his entire family's survival alone.
   - Fatal Flaw & Vulnerability: Obsession with completing old maps blinding him to immediate mortal danger.
9. STRENGTHS: Eidetic geographical recall, master cartographer, calm under extreme pressure.
10. WEAKNESSES: Physically frail under prolonged direct melee combat, deeply mistrustful of local authorities.
11. FATAL FLAW: Consuming guilt that drives him into reckless, suicidal exploration.
12. BACKSTORY: At sixteen, Kaelen drew the map that led his father's expedition into the Sunken Hollows. Only Kaelen returned.
13. MOTIVATIONS AND GOALS: Recover his father's compass from the Sunken Hollows before the imperial legion annexes the territory.
14. FEARS: Claustrophobia in dark water; losing his eyesight; forgetting his father's voice.
15. SECRETS: Stole the imperial archivist's cipher key to enter the forbidden gate.
16. RELATIONSHIPS: Cautious alliance with Maya, a former smuggler; hunted by Commander Corvo.
17. INTERNAL CONFLICT: Duty to keep his younger sister safe versus his compulsive need to venture into the abyss.
18. EXTERNAL CONFLICT: Imperial bounty hunters pursuing him across the borderlands.
19. CHARACTER ARC: Transitions from an isolated, guilt-driven outcast into an empathetic leader who trusts his allies.
20. ROLE IN THE STORY: Catalyzes the expedition into the forbidden frontier, unlocking the ancient world engine.
"""

MOCK_VARIATIONS_OUTPUT = """CONCEPT 1:
NAME: Captain Valen Drake
ROLE: Protagonist
ARCHETYPE: Disillusioned Veteran
LOGLINE: A weary starship commander forced to escort the scientist who built the weapon that destroyed his homeworld.
CORE MOTIVATION: Redeem his fallen crew by preventing another planetary disaster.
FATAL FLAW: Cynicism that prevents him from inspiring his current crew.
KEY TRAIT: Prosthetic cybernetic arm engraved with casualty tally marks.

CONCEPT 2:
NAME: Doctor Lyra Chen
ROLE: Deuteragonist
ARCHETYPE: Obsessive Inventor
LOGLINE: The brilliant astrophysicist whose energy breakthrough was weaponized by the military council.
CORE MOTIVATION: Reverse the quantum chain-reaction before the local star collapses.
FATAL FLAW: Hubris; refuses to admit when her calculations carry human risk.
KEY TRAIT: Speaks at triple speed whenever anxious or excited.

CONCEPT 3:
NAME: Inquisitor Malakor
ROLE: Antagonist
ARCHETYPE: Zealot Inquisitor
LOGLINE: An ideological enforcer convinced that humanity's salvation requires total technological suppression.
CORE MOTIVATION: Eradicate all unchecked artificial intelligence research.
FATAL FLAW: Inability to distinguish innocent curiosity from heretical malice.
KEY TRAIT: Ceremonial porcelain mask hiding extensive blast burns.
"""


@pytest.fixture
def mock_character_svc():
    provider = MockAIProvider(default_response=MOCK_CHARACTER_PROFILE)
    ai_svc = AIService(provider=provider)
    return CharacterService(ai_svc=ai_svc)


# ============================================================
# 1. Unit Tests: Validators
# ============================================================

class TestCharacterValidators:
    """Tests for validate_character_input and validate_character_variations_input."""

    def test_valid_character_full_input(self):
        data = {
            "description": "An archivist seeking redemption",
            "name": "Kaelen",
            "age": "34",
            "gender": "Male",
            "genre": "Fantasy",
            "character_role": "Protagonist",
            "personality_type": "Introverted Scholar",
            "background": "Son of a disgraced cartographer",
            "setting": "Mist-shrouded citadel",
            "language": "English",
            "tone": "Emotional"
        }
        errors = validate_character_input(data)
        assert errors == {}

    def test_empty_description_rejected(self):
        errors = validate_character_input({"description": "   ", "genre": "Drama"})
        assert "description" in errors

    def test_invalid_genre_rejected(self):
        errors = validate_character_input({"description": "A warrior", "genre": "NonExistentGenre"})
        assert "genre" in errors

    def test_invalid_role_rejected(self):
        errors = validate_character_input({
            "description": "A warrior",
            "genre": "Fantasy",
            "character_role": "PresidentOfTheUniverse123"
        })
        assert "character_role" in errors

    def test_invalid_language_rejected(self):
        errors = validate_character_input({
            "description": "A warrior",
            "genre": "Fantasy",
            "language": "Latin"
        })
        assert "language" in errors

    def test_invalid_tone_rejected(self):
        errors = validate_character_input({
            "description": "A warrior",
            "genre": "Fantasy",
            "tone": "UltraViolent"
        })
        assert "tone" in errors

    def test_non_dict_rejected(self):
        errors = validate_character_input("not a dict")
        assert "request" in errors

    def test_valid_variations_input(self):
        data = {
            "premise": "A submarine crew trapped in the Mariana Trench",
            "genre": "Thriller",
            "count": 3,
            "language": "English"
        }
        errors = validate_character_variations_input(data)
        assert errors == {}

    def test_variations_missing_premise_rejected(self):
        errors = validate_character_variations_input({"genre": "Thriller", "count": 3})
        assert "premise" in errors

    def test_variations_count_out_of_range(self):
        # Count 1 (min is 2)
        errors_low = validate_character_variations_input({"premise": "Valid premise", "genre": "Drama", "count": 1})
        assert "count" in errors_low

        # Count 10 (max is 5)
        errors_high = validate_character_variations_input({"premise": "Valid premise", "genre": "Drama", "count": 10})
        assert "count" in errors_high

    @pytest.mark.parametrize(
        ("genre", "count"),
        [("Science Fiction", 2), ("Fantasy", 3), ("Thriller", 5)]
    )
    def test_valid_ensemble_genres_and_counts(self, genre, count):
        errors = validate_character_variations_input({
            "premise": "A crew faces a difficult choice in a changing world.",
            "genre": genre,
            "count": count,
            "character_role": "Ensemble Cast",
            "language": "English",
        })
        assert errors == {}

    @pytest.mark.parametrize("language", ["English", "Tamil", "Telugu", "Hindi"])
    def test_variations_accept_supported_languages(self, language):
        errors = validate_character_variations_input({
            "premise": "A story premise.",
            "genre": "Fantasy",
            "count": 3,
            "language": language,
        })
        assert errors == {}

    @pytest.mark.parametrize(
        "focus_role",
        ["Ensemble Cast", "Protagonists", "Antagonists", "Supporting"]
    )
    def test_variations_accept_frontend_focus_roles(self, focus_role):
        errors = validate_character_variations_input({
            "premise": "A story premise.",
            "genre": "Fantasy",
            "count": 3,
            "character_role": focus_role,
        })
        assert errors == {}

    def test_variations_require_genre(self):
        errors = validate_character_variations_input({
            "premise": "A story premise.",
            "count": 3,
        })
        assert "genre" in errors

    @pytest.mark.parametrize("count", ["3", 2.5, True])
    def test_variations_count_must_be_json_integer(self, count):
        errors = validate_character_variations_input({
            "premise": "A story premise.",
            "genre": "Fantasy",
            "count": count,
        })
        assert "count" in errors

    def test_variations_count_is_required(self):
        errors = validate_character_variations_input({
            "premise": "A story premise.",
            "genre": "Fantasy",
        })
        assert "count" in errors


# ============================================================
# 2. Unit Tests: Character Parsers
# ============================================================

class TestCharacterParsers:
    """Tests for CharacterService.parse_character_profile and parse_character_variations."""

    def test_parse_structured_profile(self):
        parsed = CharacterService.parse_character_profile(MOCK_CHARACTER_PROFILE)
        assert "Kaelen Vance" in parsed["character_name"]
        assert parsed["age"] == "34"
        assert parsed["gender"] == "Male"
        assert parsed["character_role"] == "Protagonist"
        assert "Reluctant Explorer" in parsed["character_archetype"]
        assert "indigo ink" in parsed["physical_appearance"]
        assert "Observant" in parsed["personality_traits"]
        assert "Core Want" in parsed["psychological_profile"]
        assert "Eidetic geographical recall" in parsed["strengths"]
        assert "Consuming guilt" in parsed["fatal_flaw"]
        assert "Sunken Hollows" in parsed["backstory"]
        assert "Maya" in parsed["relationships"]
        assert "Transitions from an isolated" in parsed["character_arc"]

    def test_parse_profile_with_translated_numbered_section_labels(self):
        response = "\n".join(
            f"{number}. தமிழ்ப் பிரிவு: உள்ளடக்கம் {number}"
            for number in range(1, 21)
        )

        parsed = CharacterService.parse_character_profile(response)

        assert parsed["character_name"] == "உள்ளடக்கம் 1"
        assert parsed["age"] == "உள்ளடக்கம் 2"
        assert parsed["gender"] == "உள்ளடக்கம் 3"
        assert parsed["character_role"] == "உள்ளடக்கம் 4"
        assert parsed["physical_appearance"] == "உள்ளடக்கம் 6"
        assert parsed["character_arc"] == "உள்ளடக்கம் 19"
        assert parsed["role_in_story"] == "உள்ளடக்கம் 20"

    def test_parse_empty_profile(self):
        parsed = CharacterService.parse_character_profile("")
        assert parsed["character_name"] == "Unnamed Character"
        assert parsed["backstory"] == ""

    def test_parse_unstructured_profile_fallback(self):
        raw_text = "Once an outlaw in the borderlands, he swore allegiance to the rebellion."
        parsed = CharacterService.parse_character_profile(raw_text)
        assert raw_text in parsed["backstory"]

    def test_parse_variations_output(self):
        variations = CharacterService.parse_character_variations(MOCK_VARIATIONS_OUTPUT)
        assert len(variations) == 3

        v1 = variations[0]
        assert "Valen Drake" in v1["name"]
        assert "Disillusioned Veteran" in v1["archetype"]
        assert "Redeem his fallen crew" in v1["motivation"]
        assert "Cynicism" in v1["fatal_flaw"]

        v2 = variations[1]
        assert "Lyra Chen" in v2["name"]
        assert "Obsessive Inventor" in v2["archetype"]

        v3 = variations[2]
        assert "Malakor" in v3["name"]
        assert "Zealot Inquisitor" in v3["archetype"]


# ============================================================
# 3. Integration Tests: POST /api/generate-character
# ============================================================

class TestGenerateCharacterEndpoint:
    """Integration tests for POST /api/generate-character."""

    def test_generate_protagonist_success(self, client):
        payload = {
            "description": "A disgraced surgeon seeking redemption in a cyberpunk underworld.",
            "name": "Dr. Sarah Lin",
            "genre": "Science Fiction",
            "character_role": "Protagonist",
            "personality_type": "Cynical Idealist",
            "age": "38",
            "language": "English",
            "tone": "Emotional"
        }
        res = client.post("/api/generate-character", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "Character profile generated successfully." in data["message"]
        assert "character_name" in data["data"]
        assert "psychological_profile" in data["data"]
        assert "fatal_flaw" in data["data"]
        assert "full_profile" in data["data"]

    def test_generate_character_accepts_frontend_null_optional_fields(self, client):
        response = client.post("/api/generate-character", json={
            "description": "A mystery protagonist with a hidden past.",
            "character_name": None,
            "genre": "Mystery",
            "character_role": "protagonist",
            "character_archetype": None,
            "age": None,
            "gender": None,
            "language": "English",
            "tone": "Emotional",
            "background": None,
            "additional_instructions": None,
        })

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["metadata"]["language"] == "English"
        assert data["metadata"]["provider"] == "mock"
        assert data["full_profile"]
        assert "psychological_profile" in data
        assert "character_arc" in data

    def test_generate_antagonist_success(self, client):
        payload = {
            "description": "A ruthless corporate CEO orchestrating water shortages.",
            "genre": "Thriller",
            "character_role": "Antagonist",
            "language": "English"
        }
        res = client.post("/api/generate-character", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["metadata"]["character_role"] == "Antagonist"

    def test_generate_supporting_mentor_success(self, client):
        payload = {
            "description": "An ancient retired martial artist who brews herbal tea.",
            "genre": "Fantasy",
            "character_role": "Mentor",
            "language": "English"
        }
        res = client.post("/api/generate-character", json=payload)
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_generate_multilingual_characters(self, client):
        for lang in ["Telugu", "Tamil", "Hindi", "English"]:
            payload = {
                "description": f"A dedicated village schoolteacher facing land corruption in {lang}.",
                "genre": "Drama",
                "character_role": "Protagonist",
                "language": lang
            }
            res = client.post("/api/generate-character", json=payload)
            assert res.status_code == 200
            data = res.get_json()
            assert data["success"] is True
            assert data["data"]["metadata"]["language"] == lang
            last_prompt = character_service.ai.provider.last_prompt
            assert f"- Language: {lang}" in last_prompt
            assert f"Write strictly in {lang}." in last_prompt

    def test_missing_description_error(self, client):
        res = client.post("/api/generate-character", json={"genre": "Fantasy"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "description" in data["errors"]

    def test_missing_genre_error(self, client):
        response = client.post("/api/generate-character", json={
            "description": "A mystery protagonist with a hidden past.",
        })
        assert response.status_code == 400
        assert "genre" in response.get_json()["errors"]

    def test_missing_language_defaults_to_english(self, client):
        response = client.post("/api/generate-character", json={
            "description": "A mystery protagonist with a hidden past.",
            "genre": "Mystery",
        })

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["metadata"]["language"] == "English"

    def test_invalid_genre_error(self, client):
        res = client.post("/api/generate-character", json={
            "description": "A knight",
            "genre": "NotARealGenre"
        })
        assert res.status_code == 400
        data = res.get_json()
        assert "genre" in data["errors"]

    def test_invalid_role_error(self, client):
        res = client.post("/api/generate-character", json={
            "description": "A knight",
            "genre": "Fantasy",
            "character_role": "GalacticEmperor99"
        })
        assert res.status_code == 400
        data = res.get_json()
        assert "character_role" in data["errors"]

    def test_missing_json_body_error(self, client):
        res = client.post("/api/generate-character", data="plain text", content_type="text/plain")
        assert res.status_code == 400
        assert res.get_json()["success"] is False


# ============================================================
# 4. Integration Tests: POST /api/generate-character-variations
# ============================================================

class TestCharacterVariationsEndpoint:
    """Integration tests for POST /api/generate-character-variations."""

    @pytest.mark.parametrize(
        ("genre", "count"),
        [("Science Fiction", 2), ("Fantasy", 3), ("Thriller", 5)]
    )
    def test_ensemble_generation_workflow_accepts_supported_counts(
        self, client, genre, count
    ):
        def generate_exact_count(prompt, **kwargs):
            requested_count = int(prompt.splitlines()[0].split()[2])
            concepts = []
            for number in range(1, requested_count + 1):
                concepts.append(
                    f"CONCEPT {number}:\n"
                    f"NAME: Character {number}\n"
                    "ROLE: Protagonist\n"
                    "ARCHETYPE: Explorer\n"
                    "LOGLINE: A distinct character hook.\n"
                    "CORE MOTIVATION: Protect the group.\n"
                    "FATAL FLAW: Acts too quickly.\n"
                    "KEY TRAIT: Observant"
                )
            return {
                "text": "\n\n".join(concepts),
                "provider": "mock",
                "model": "test-mock",
                "finish_reason": "STOP",
                "tokens_used": 10,
            }

        with patch.object(character_service.ai, "call_ai_model", side_effect=generate_exact_count):
            response = client.post("/api/generate-character-variations", json={
                "premise": "A crew faces a difficult choice in a changing world.",
                "genre": genre,
                "character_role": "Ensemble Cast",
                "count": count,
                "language": "English",
            })

        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["metadata"]["requested_count"] == count
        assert len(data["variations"]) == count

    def test_generate_variations_success(self, client):
        payload = {
            "premise": "An experimental colony on Mars experiences communication blackout.",
            "genre": "Science Fiction",
            "count": 3,
            "character_role": "Protagonist",
            "language": "English"
        }
        res = client.post("/api/generate-character-variations", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "Character variations generated successfully." in data["message"]
        assert "variations" in data["data"]
        assert len(data["data"]["variations"]) >= 1

    def test_variations_missing_premise_error(self, client):
        res = client.post("/api/generate-character-variations", json={"genre": "Drama", "count": 3})
        assert res.status_code == 400
        data = res.get_json()
        assert "premise" in data["errors"]

    def test_variations_missing_genre_error(self, client):
        res = client.post("/api/generate-character-variations", json={
            "premise": "A story premise.",
            "count": 3,
        })
        assert res.status_code == 400
        assert "genre" in res.get_json()["errors"]

    def test_variations_invalid_count_error(self, client):
        res = client.post("/api/generate-character-variations", json={
            "premise": "Valid premise",
            "genre": "Drama",
            "count": 25
        })
        assert res.status_code == 400
        data = res.get_json()
        assert "count" in data["errors"]

    @pytest.mark.parametrize("count", ["3", 2.5, 6])
    def test_variations_invalid_count_types_and_bounds_error(self, client, count):
        res = client.post("/api/generate-character-variations", json={
            "premise": "Valid premise",
            "genre": "Fantasy",
            "count": count,
        })
        assert res.status_code == 400
        assert "count" in res.get_json()["errors"]


# ============================================================
# 5. Error Simulation & Edge Case Tests
# ============================================================

class TestCharacterErrorHandling:
    """Verifies that AI provider failures return standard error responses."""

    def test_simulated_rate_limit_error(self, client):
        with patch.object(
            character_service.ai.provider,
            "generate",
            side_effect=AIRateLimitError("Rate limit exceeded.")
        ):
            res = client.post("/api/generate-character", json={
                "description": "A renegade hacker",
                "genre": "Science Fiction"
            })
            assert res.status_code == 429
            data = res.get_json()
            assert data["success"] is False
            assert "rate limit" in data["message"].lower()

    def test_simulated_authentication_error(self, client):
        from services.ai_provider import AIAuthenticationError

        with patch.object(
            character_service.ai.provider,
            "generate",
            side_effect=AIAuthenticationError("Invalid credentials.")
        ):
            response = client.post("/api/generate-character", json={
                "description": "A detective uncovering an old conspiracy.",
                "genre": "Mystery",
            })

        assert response.status_code == 401
        assert "authentication" in response.get_json()["message"].lower()

    def test_simulated_timeout_error(self, client):
        with patch.object(
            character_service.ai.provider,
            "generate",
            side_effect=AITimeoutError("AI service request timed out.")
        ):
            res = client.post("/api/generate-character", json={
                "description": "A medieval alchemist",
                "genre": "Fantasy"
            })
            assert res.status_code == 504
            data = res.get_json()
            assert "timed out" in data["message"]

    def test_simulated_network_error(self, client):
        with patch.object(
            character_service.ai.provider,
            "generate",
            side_effect=AINetworkError("Network reset.")
        ):
            res = client.post("/api/generate-character", json={
                "description": "A detective",
                "genre": "Mystery"
            })
            assert res.status_code == 502
            data = res.get_json()
            assert "Network" in data["message"]

    def test_simulated_empty_ai_response(self, client):
        with patch.object(
            character_service.ai.provider,
            "generate",
            side_effect=AIEmptyResponseError("Empty AI response.")
        ):
            res = client.post("/api/generate-character", json={
                "description": "A ghost hunter",
                "genre": "Horror"
            })
            assert res.status_code == 502
            data = res.get_json()
            assert "empty response" in data["message"].lower()

    def test_unconfigured_api_key_endpoint_error(self, client):
        with patch.object(character_service.ai, "_provider", GeminiProvider(api_key="")):
            res = client.post("/api/generate-character", json={
                "description": "A cursed sailor",
                "genre": "Fantasy"
            })
            assert res.status_code == 500
            data = res.get_json()
            assert data["success"] is False
            assert "API key is not configured" in data["message"]
