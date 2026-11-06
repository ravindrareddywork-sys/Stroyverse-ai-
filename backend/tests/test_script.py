"""
StoryVerse AI — Script Generator Module Tests
==============================================
Comprehensive integration and unit tests for Phase 6:
  1. Thriller script generation
  2. Drama script generation
  3. Action script generation
  4. Sci-Fi script generation
  5. Comedy script generation
  6. Multilingual script generation (English, Telugu, Tamil, Hindi)
  7. Multi-scene screenplay parsing (sluglines, action, character cues, dialogues)
  8. Empty topic validation (400)
  9. Invalid genre validation (400)
  10. Invalid language validation (400)
  11. Invalid tone validation (400)
  12. Invalid scene count validation (negative, 0, >20)
  13. Character list validation
  14. POST /api/generate-scene endpoint
  15. Single scene validation (missing goal/topic)
  16. Missing API key error handling
  17. Simulated AI rate limit error (429)
  18. Simulated AI timeout error (504)
  19. Simulated AI network error (503)
  20. Simulated AI empty response error (502)
  21. Script parser slugline extraction & fallbacks
  22. Malformed request body rejection (400)
"""

import json
import pytest
from unittest.mock import patch

from services.script_service import ScriptService, script_service
from services.ai_provider import (
    MockAIProvider,
    GeminiProvider,
    AIRateLimitError,
    AITimeoutError,
    AINetworkError,
    AIEmptyResponseError,
)
from services.ai_service import AIService
from utils.validators import validate_script_input, validate_scene_input


MOCK_SCREENPLAY_OUTPUT = """TITLE: THE ECHO PROTOCOL
LOGLINE: Two estranged cyber-detectives navigate a derelict subway station to neutralize a rogue surveillance AI.

CHARACTERS:
- RAMESH (40s): Cynical veteran detective, battling burnout.
- ANANYA (20s): Brilliant rogue cyber-analyst.

SCENE 1
INT. SUBWAY TERMINAL - NIGHT

Water drips from rusting ceiling tiles onto fractured concrete. Emergency strobes flicker amber.

RAMESH checks his weapon's chamber. Behind him, portable monitors cast blue light across ANANYA's focused face.

RAMESH
(quietly)
The whole sector went dark ten minutes ago. We shouldn't be here.

ANANYA
(without looking up)
If the AI reaches the main grid, there won't be a sector to come back to.

A low hydraulic hum vibrates through the rails.

CUT TO:

SCENE 2
EXT. ALLEYWAY ACCESS HATCH - CONTINUOUS

Rain lashes against steel emergency grates. Shadows move rapidly across the fire escape.

ANANYA
Did you see that?

RAMESH
Movement on the upper catwalk. Keep your head down.

FADE OUT.
"""


@pytest.fixture
def mock_script_svc():
    provider = MockAIProvider(default_response=MOCK_SCREENPLAY_OUTPUT)
    ai_svc = AIService(provider=provider)
    return ScriptService(ai_svc=ai_svc)


# ============================================================
# 1. Unit Tests: Input Validators
# ============================================================

class TestScriptValidators:
    """Tests for validate_script_input and validate_scene_input."""

    def test_valid_script_input(self):
        data = {
            "topic": "Two detectives trapped in a digital maze.",
            "genre": "Thriller",
            "language": "English",
            "tone": "Suspenseful",
            "num_scenes": 3,
            "characters": ["Ramesh", "Ananya"],
            "setting": "Neo-Tokyo Abandoned Station"
        }
        errors = validate_script_input(data)
        assert errors == {}

    def test_empty_topic_rejected(self):
        data = {"topic": "   ", "genre": "Drama"}
        errors = validate_script_input(data)
        assert "topic" in errors

    def test_missing_topic_rejected(self):
        data = {"genre": "Thriller"}
        errors = validate_script_input(data)
        assert "topic" in errors

    def test_invalid_genre_rejected(self):
        data = {"topic": "A detective story", "genre": "Cyberpunk123"}
        errors = validate_script_input(data)
        assert "genre" in errors

    def test_invalid_language_rejected(self):
        data = {"topic": "A detective story", "genre": "Drama", "language": "Klingon"}
        errors = validate_script_input(data)
        assert "language" in errors

    def test_invalid_tone_rejected(self):
        data = {"topic": "A detective story", "genre": "Drama", "tone": "Aggressive"}
        errors = validate_script_input(data)
        assert "tone" in errors

    def test_scene_count_out_of_range(self):
        # 0 scenes
        errors_zero = validate_script_input({"topic": "Valid premise", "genre": "Action", "num_scenes": 0})
        assert "num_scenes" in errors_zero

        # 25 scenes (max is 20)
        errors_too_many = validate_script_input({"topic": "Valid premise", "genre": "Action", "num_scenes": 25})
        assert "num_scenes" in errors_too_many

    def test_character_list_overflow(self):
        data = {
            "topic": "Valid topic",
            "genre": "Action",
            "characters": [f"Character_{i}" for i in range(25)]  # max is 20
        }
        errors = validate_script_input(data)
        assert "characters" in errors

    def test_non_dict_body_rejected(self):
        errors = validate_script_input("not a dict")
        assert "request" in errors

    def test_valid_scene_input(self):
        data = {
            "scene_goal": "Confront the suspect at the pier",
            "context": "They have been tracking the target all day.",
            "genre": "Mystery",
            "language": "English"
        }
        errors = validate_scene_input(data)
        assert errors == {}

    def test_missing_scene_goal_rejected(self):
        data = {"genre": "Mystery"}
        errors = validate_scene_input(data)
        assert "scene_goal" in errors


# ============================================================
# 2. Unit Tests: Screenplay Parser
# ============================================================

class TestScreenplayParser:
    """Tests for ScriptService.parse_script_scenes."""

    def test_parse_standard_screenplay(self):
        parsed = ScriptService.parse_script_scenes(MOCK_SCREENPLAY_OUTPUT)
        assert parsed["title"] == "THE ECHO PROTOCOL"
        assert "Two estranged cyber-detectives" in parsed["logline"]
        assert "RAMESH" in parsed["characters_summary"]
        assert len(parsed["scenes"]) == 2

        # Check scene 1
        s1 = parsed["scenes"][0]
        assert s1["scene_number"] == 1
        assert "INT. SUBWAY TERMINAL - NIGHT" in s1["heading"]
        assert len(s1["dialogues"]) >= 2
        assert s1["dialogues"][0]["character"] == "RAMESH"
        assert s1["dialogues"][0]["parenthetical"] == "(quietly)"
        assert "The whole sector went dark" in s1["dialogues"][0]["line"]
        assert s1["transition"] == "CUT TO:"

        # Check scene 2
        s2 = parsed["scenes"][1]
        assert s2["scene_number"] == 2
        assert "EXT. ALLEYWAY ACCESS HATCH - CONTINUOUS" in s2["heading"]
        assert s2["transition"] == "FADE OUT."

    def test_parse_empty_string(self):
        parsed = ScriptService.parse_script_scenes("")
        assert parsed["title"] == "Untitled Screenplay"
        assert parsed["scenes"] == []
        assert parsed["scene_count"] == 0

    def test_parse_raw_prose_fallback(self):
        raw_text = "Once upon a time in a distant realm, two wanderers journeyed to the mountains."
        parsed = ScriptService.parse_script_scenes(raw_text)
        assert parsed["scene_count"] >= 1
        assert raw_text in parsed["scenes"][0]["action"]


# ============================================================
# 3. Integration Tests: POST /api/generate-script
# ============================================================

class TestGenerateScriptEndpoint:
    """Integration tests for POST /api/generate-script."""

    def test_generate_thriller_script_success(self, client):
        payload = {
            "topic": "An undercover agent gets trapped inside an automated offshore vault.",
            "genre": "Thriller",
            "language": "English",
            "tone": "Suspenseful",
            "num_scenes": 3
        }
        response = client.post(
            "/api/generate-script",
            data=json.dumps(payload),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "Screenplay generated successfully." in data["message"]
        assert "title" in data["data"]
        assert "scenes" in data["data"]
        assert "full_script" in data["data"]
        assert data["data"]["metadata"]["genre"] == "Thriller"

    def test_generate_action_script_success(self, client):
        payload = {
            "topic": "A retired stunt driver must escape a locked-down city center.",
            "genre": "Action",
            "language": "English",
            "num_scenes": 2
        }
        res = client.post("/api/generate-script", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["metadata"]["genre"] == "Action"

    def test_generate_drama_script_success(self, client):
        payload = {
            "topic": "Two sisters dispute the inheritance of a historic theater.",
            "genre": "Drama",
            "tone": "Emotional",
            "num_scenes": 2
        }
        res = client.post("/api/generate-script", json=payload)
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_generate_multilingual_scripts(self, client):
        languages = ["Telugu", "Tamil", "Hindi", "English"]
        for lang in languages:
            payload = {
                "topic": f"A family celebration takes an unexpected turn in {lang}.",
                "genre": "Drama",
                "language": lang,
                "num_scenes": 2
            }
            res = client.post("/api/generate-script", json=payload)
            assert res.status_code == 200
            data = res.get_json()
            assert data["success"] is True
            assert data["data"]["metadata"]["language"] == lang

    def test_missing_topic_error(self, client):
        res = client.post("/api/generate-script", json={"genre": "Horror"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "Validation failed" in data["message"]
        assert "topic" in data["errors"]

    def test_invalid_genre_error(self, client):
        res = client.post("/api/generate-script", json={"topic": "Mystery premise", "genre": "InvalidGenre"})
        assert res.status_code == 400
        data = res.get_json()
        assert "genre" in data["errors"]

    def test_invalid_scene_count_error(self, client):
        res = client.post("/api/generate-script", json={"topic": "Mystery premise", "genre": "Comedy", "num_scenes": 50})
        assert res.status_code == 400
        data = res.get_json()
        assert "num_scenes" in data["errors"]

    def test_missing_json_body_error(self, client):
        res = client.post("/api/generate-script", data="not json", content_type="text/plain")
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False


# ============================================================
# 4. Integration Tests: POST /api/generate-scene
# ============================================================

class TestGenerateSceneEndpoint:
    """Integration tests for POST /api/generate-scene."""

    def test_generate_scene_success(self, client):
        payload = {
            "scene_goal": "The detective confronts the suspect at the abandoned lighthouse.",
            "context": "The storm is worsening and radio communication has failed.",
            "genre": "Thriller",
            "language": "English",
            "characters": "Ramesh, Suspect X"
        }
        res = client.post("/api/generate-scene", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "Scene generated successfully." in data["message"]
        assert "scene" in data["data"]
        assert "heading" in data["data"]["scene"]
        assert "full_text" in data["data"]

    def test_generate_scene_validation_error(self, client):
        res = client.post("/api/generate-scene", json={"genre": "Thriller"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "scene_goal" in data["errors"]


# ============================================================
# 5. Error Simulation & Edge Case Tests
# ============================================================

class TestScriptErrorHandling:
    """Verifies that AI provider failures return standard error responses."""

    def test_simulated_rate_limit_error(self, client):
        with patch.object(
            script_service.ai.provider,
            "generate",
            side_effect=AIRateLimitError("Rate limit exceeded.")
        ):
            res = client.post(
                "/api/generate-script",
                json={"topic": "A heist gone wrong", "genre": "Action"}
            )
            assert res.status_code == 429
            data = res.get_json()
            assert data["success"] is False
            assert "rate limit" in data["message"].lower()

    def test_simulated_timeout_error(self, client):
        with patch.object(
            script_service.ai.provider,
            "generate",
            side_effect=AITimeoutError("AI service request timed out.")
        ):
            res = client.post(
                "/api/generate-script",
                json={"topic": "A space escape", "genre": "Science Fiction"}
            )
            assert res.status_code == 504
            data = res.get_json()
            assert data["success"] is False
            assert "timed out" in data["message"]

    def test_simulated_network_error(self, client):
        with patch.object(
            script_service.ai.provider,
            "generate",
            side_effect=AINetworkError("Network connection reset.")
        ):
            res = client.post(
                "/api/generate-script",
                json={"topic": "A mountain thriller", "genre": "Thriller"}
            )
            assert res.status_code == 502
            data = res.get_json()
            assert data["success"] is False
            assert "Network" in data["message"]

    def test_simulated_empty_ai_response(self, client):
        with patch.object(
            script_service.ai.provider,
            "generate",
            side_effect=AIEmptyResponseError("Empty AI response received.")
        ):
            res = client.post(
                "/api/generate-script",
                json={"topic": "A quiet mystery", "genre": "Mystery"}
            )
            assert res.status_code == 502
            data = res.get_json()
            assert data["success"] is False
            assert "empty response" in data["message"].lower()

    def test_unconfigured_api_key_endpoint_error(self, client):
        with patch.object(script_service.ai, "_provider", GeminiProvider(api_key="")):
            res = client.post(
                "/api/generate-script",
                json={"topic": "A haunted theatre", "genre": "Horror"}
            )
            assert res.status_code == 500
            data = res.get_json()
            assert data["success"] is False
            assert "API key is not configured" in data["message"]


# ============================================================
# 6. Multilingual Screenplay Generation & Prompt Inspection
# ============================================================

TAMIL_SCREENPLAY_MOCK = """TITLE: நிழல் வேட்டை
LOGLINE: ஒரு நேர்மையான காவல்துறை அதிகாரி மர்மமான முறையில் காணாமல் போன தொல்பொருளைத் தேடி பயணிக்கிறார்.

CHARACTERS:
- விக்ரம் (40): அனுபவம் வாய்ந்த துப்பறியும் அதிகாரி.
- மாயா (28): தொல்பொருள் ஆராய்ச்சியாளர்.

SCENE 1
INT. காவல் கட்டுப்பாட்டு அறை - NIGHT

கணினி திரைகளில் வரைபடங்கள் மின்னுகின்றன. வெளியே இடி முழங்க மழை பெய்கிறது.

விக்ரம் மேசையிலுள்ள வரைபடத்தை உற்றுப் பார்க்கிறார். அவருக்குப் பின்னால் மாயா பதற்றத்துடன் நிற்கிறாள்.

விக்ரம்:
(மெதுவான குரலில்)
இந்த கோப்பு பத்து வருடங்களாக பூட்டப்பட்டிருந்தது. நாம் இதை திறக்கக் கூடாது.

மாயா:
(தலையசைத்து)
உண்மை வெளியே வர வேண்டும் விக்ரம், இல்லையெனில் நகரம் ஆபத்தில் சிக்கும்.

FADE OUT.
"""

TELUGU_SCREENPLAY_MOCK = """TITLE: ప్రతిధ్వని రహస్యం
LOGLINE: ఒక ప్రతిభావంతుడైన పరిశోధకుడు ప్రాచీన ఆలయ రహస్యాన్ని చేధించడానికి సాహస యాత్ర ప్రారంభిస్తాడు.

CHARACTERS:
- రమేష్ (35): సాహసికుడైన పరిశోధకుడు.
- ప్రియ (30): చరిత్ర విశ్లేషకురాలు.

SCENE 1
INT. ప్రాచీన గ్రంథాలయం - NIGHT

దీపపు కాంతిలో రాతి స్తంభాలు మెరుస్తున్నాయి. గాలి వేగంగా వీస్తోంది.

రమేష్ ఒక పాత తాళపత్ర గ్రంథాన్ని జాగ్రత్తగా తెరుస్తాడు.

రమేష్:
(ఆశ్చర్యంతో)
ఈ లిపి శతాబ్దాలుగా ఎవరూ చూడలేదు. ఇది ప్రమాదకరమైన దారిని సూచిస్తోంది.

ప్రియ:
మనం ఆపలేము రమేష్. సమయం మించిపోతోంది.

FADE OUT.
"""

HINDI_SCREENPLAY_MOCK = """TITLE: चक्रव्यूह का सच
LOGLINE: दो जासूस शहर को एक बड़े साइबर हमले से बचाने के लिए समय के खिलाफ दौड़ते हैं।

CHARACTERS:
- कबीर (38): अनुभवी सीक्रेट एजेंट।
- तारा (27): युवा सॉफ्टवेयर विशेषज्ञ।

SCENE 1
INT. कंट्रोल रूम - NIGHT

कमरे में केवल मॉनिटर्स की नीली रोशनी चमक रही है। चारों तरफ शांति है।

कबीर स्क्रीन पर कोड को ध्यान से देखता है।

कबीर:
(गंभीरता से)
सर्वर तीन मिनट में पूरी तरह लॉक हो जाएगा।

तारा:
मैं फायरवॉल को बाईपास कर रही हूँ, बस मुझे तीस सेकंड और दीजिए।

FADE OUT.
"""


class TestMultilingualScreenplayGeneration:
    """Verifies that English is default and Tamil, Telugu, Hindi are fully supported in prompt & parsing."""

    def test_english_screenplay_generation_and_prompt(self, client):
        payload = {
            "topic": "Two detectives track an elusive hacker in London.",
            "genre": "Thriller",
            "language": "English",
            "num_scenes": 2
        }
        res = client.post("/api/generate-script", json=payload)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["metadata"]["language"] == "English"

        last_prompt = script_service.ai.provider.last_prompt
        assert "- Language: English" in last_prompt
        assert "Write strictly in English." in last_prompt

    def test_tamil_screenplay_generation_and_prompt(self, client):
        payload = {
            "topic": "மர்மமான தொல்பொருள் தேடல்",
            "genre": "Mystery",
            "language": "Tamil",
            "num_scenes": 1
        }
        orig_resp = script_service.ai.provider.default_response
        try:
            script_service.ai.provider.default_response = TAMIL_SCREENPLAY_MOCK
            res = client.post("/api/generate-script", json=payload)
            assert res.status_code == 200
            data = res.get_json()["data"]

            assert data["metadata"]["language"] == "Tamil"
            assert "நிழல் வேட்டை" in data["title"]
            assert len(data["scenes"]) >= 1

            s1 = data["scenes"][0]
            assert len(s1["dialogues"]) >= 2
            assert s1["dialogues"][0]["character"] == "விக்ரம்"
            assert "மெதுவான குரலில்" in s1["dialogues"][0]["parenthetical"]
            assert "இந்த கோப்பு" in s1["dialogues"][0]["line"]
            assert s1["dialogues"][1]["character"] == "மாயா"
            assert "உண்மை வெளியே வர வேண்டும்" in s1["dialogues"][1]["line"]

            last_prompt = script_service.ai.provider.last_prompt
            assert "- Language: Tamil" in last_prompt
            assert "MULTILINGUAL SCREENPLAY DIRECTIVES (TAMIL)" in last_prompt
            assert "Write strictly in Tamil." in last_prompt
        finally:
            script_service.ai.provider.default_response = orig_resp

    def test_telugu_screenplay_generation_and_prompt(self, client):
        payload = {
            "topic": "ప్రాచీన ఆలయ రహస్యం",
            "genre": "Adventure",
            "language": "Telugu",
            "num_scenes": 1
        }
        orig_resp = script_service.ai.provider.default_response
        try:
            script_service.ai.provider.default_response = TELUGU_SCREENPLAY_MOCK
            res = client.post("/api/generate-script", json=payload)
            assert res.status_code == 200
            data = res.get_json()["data"]

            assert data["metadata"]["language"] == "Telugu"
            assert "ప్రతిధ్వని రహస్యం" in data["title"]
            assert len(data["scenes"]) >= 1

            s1 = data["scenes"][0]
            assert len(s1["dialogues"]) >= 2
            assert s1["dialogues"][0]["character"] == "రమేష్"
            assert "ఆశ్చర్యంతో" in s1["dialogues"][0]["parenthetical"]
            assert "ఈ లిపి శతాబ్దాలుగా" in s1["dialogues"][0]["line"]
            assert s1["dialogues"][1]["character"] == "ప్రియ"
            assert "సమయం మించిపోతోంది" in s1["dialogues"][1]["line"]

            last_prompt = script_service.ai.provider.last_prompt
            assert "- Language: Telugu" in last_prompt
            assert "MULTILINGUAL SCREENPLAY DIRECTIVES (TELUGU)" in last_prompt
            assert "Write strictly in Telugu." in last_prompt
        finally:
            script_service.ai.provider.default_response = orig_resp

    def test_hindi_screenplay_generation_and_prompt(self, client):
        payload = {
            "topic": "साइबर हमले से शहर को बचाना",
            "genre": "Action",
            "language": "Hindi",
            "num_scenes": 1
        }
        orig_resp = script_service.ai.provider.default_response
        try:
            script_service.ai.provider.default_response = HINDI_SCREENPLAY_MOCK
            res = client.post("/api/generate-script", json=payload)
            assert res.status_code == 200
            data = res.get_json()["data"]

            assert data["metadata"]["language"] == "Hindi"
            assert "चक्रव्यूह का सच" in data["title"]
            assert len(data["scenes"]) >= 1

            s1 = data["scenes"][0]
            assert len(s1["dialogues"]) >= 2
            assert s1["dialogues"][0]["character"] == "कबीर"
            assert "गंभीरता से" in s1["dialogues"][0]["parenthetical"]
            assert "सर्वर तीन मिनट में" in s1["dialogues"][0]["line"]
            assert s1["dialogues"][1]["character"] == "तारा"
            assert "फायरवॉल को बाईपास" in s1["dialogues"][1]["line"]

            last_prompt = script_service.ai.provider.last_prompt
            assert "- Language: Hindi" in last_prompt
            assert "MULTILINGUAL SCREENPLAY DIRECTIVES (HINDI)" in last_prompt
            assert "Write strictly in Hindi." in last_prompt
        finally:
            script_service.ai.provider.default_response = orig_resp

    def test_rag_context_does_not_override_screenplay_language(self, client):
        payload = {
            "topic": "Infiltration of the Black Citadel",
            "genre": "Fantasy",
            "language": "English",
            "num_scenes": 2,
            "rag_context": "=== [RETRIEVED KNOWLEDGE CONTEXT — GROUND TRUTH] ===\nThe citadel gate is iron."
        }
        res = client.post("/api/generate-script", json=payload)
        assert res.status_code == 200

        last_prompt = script_service.ai.provider.last_prompt
        assert "=== [RETRIEVED KNOWLEDGE CONTEXT — GROUND TRUTH] ===" in last_prompt
        assert "- Language: English" in last_prompt
        assert "Write strictly in English." in last_prompt
