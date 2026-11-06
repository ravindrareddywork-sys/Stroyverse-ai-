# Phase 6 Completion Report — Screenplay & Script Generator Module
**Project:** StoryVerse AI — Story and Script Generator Using Generative AI  
**Academic Role:** Final Year B.Tech Computer Science Project  
**Date:** November 5, 2026  
**Status:** Completed & Fully Verified (151/151 Automated Tests Passing)

---

## 1. Executive Summary

Phase 6 implements the **Screenplay & Script Generator Module** for StoryVerse AI. This module bridges high-level generative AI prompts with strict Hollywood industry screenplay formatting standards. It provides screenwriters, directors, and students with production-ready screenplay scripts containing standard sluglines, present-tense action paragraphs, centered character cues, parentheticals, formatted dialogues, and scene transitions (`CUT TO:`, `FADE OUT:`).

The module provides both backend REST API endpoints (`POST /api/generate-script` and `POST /api/generate-scene`) and a rich frontend interactive studio (`script.html`, `script.js`, `script.css`) featuring three synchronized views:
1. **Industry Screenplay View**: Authentically rendered with `Courier Prime` typography, standard margins, centered character cues, and indented dialogues.
2. **Scene Breakdown Cards View**: Modular card breakdown of every generated scene with sluglines, action summaries, and dialogue counts.
3. **Editable Manuscript View**: Full monospace editor allowing live edits, clipboard copying, and export preparation.

---

## 2. Files Created & Modified

### New Backend Files:
1. **`backend/services/script_service.py`**:
   - `ScriptService` class managing screenplay generation, scene generation, and screenplay parsing.
   - `parse_script_scenes()`: Regular-expression engine identifying sluglines (`INT./EXT.`), action blocks, capitalized character cues, parentheticals, dialogues, and transitions.
   - Fallback mechanism preserving raw text even when unformatted text is generated.
2. **`backend/routes/script_routes.py`**:
   - Flask Blueprint `script_bp` defining `POST /api/generate-script` and `POST /api/generate-scene`.
   - Validates requests, delegates to `script_service`, and maps domain errors to standard HTTP response codes.
3. **`backend/tests/test_script.py`**:
   - 29 unit and integration tests covering validators, parsers, multi-genre/multilingual scripts, single scene endpoints, and error simulation.

### Modified Backend Files:
1. **`backend/routes/__init__.py`**:
   - Registered `script_bp` under `/api` (`POST /api/generate-script`, `POST /api/generate-scene`).
2. **`backend/services/__init__.py`**:
   - Exported `ScriptService` and singleton instance `script_service`.
3. **`backend/services/prompt_service.py`**:
   - Enhanced `build_script_prompt()` to safely format character lists, settings, and directives.
4. **`backend/utils/validators.py`**:
   - Added `"action"`, `"historical"`, `"animation"` to `ALLOWED_GENRES`.
   - Added `characters` list/string validation to `validate_script_input()`.
   - Added `validate_scene_input()` for single scene generation requests.
5. **`backend/utils/__init__.py`**:
   - Exported `validate_scene_input`.

### Modified Frontend Files:
1. **`frontend/pages/script.html`**:
   - Screenplay Studio layout with full parameter inputs (logline, genre, language, scene count, tone, characters, settings, custom directives).
   - Real-time parameter summary sidebar and screenplay formatting guide.
   - Animated loading overlay (`#scriptLoadingState`) with clapperboard icon and progress animation.
   - Screenplay Results section with title, badges, logline banner, characters banner, view switcher, and action buttons.
2. **`frontend/css/script.css`**:
   - Complete screenplay stylesheet with `Courier Prime` font stack, responsive margins, slugline badges, centered character cues, parentheticals, dialogue indentation, scene cards, and dark/light mode compatibility.
3. **`frontend/js/api.js`**:
   - Added `StoryVerseAPI.generateScript(payload)` and `StoryVerseAPI.generateScene(payload)`.
4. **`frontend/js/script.js`**:
   - Form submission controller connecting to `generateScript()`.
   - Dynamic real-time parameter counter and summary display.
   - Secure DOM creation (`textContent` only, zero `innerHTML` injection) preventing Cross-Site Scripting (XSS).
   - Three-way view toggling (Screenplay Format, Scene Cards, Editable Manuscript).
   - Clipboard copy and "Add Scene" continuation via `generateScene()`.

---

## 3. API Endpoints Specification

### Endpoint 1: Complete Screenplay Generation
- **Route:** `POST /api/generate-script`
- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
```json
{
  "topic": "Two rival astronauts encounter an uncharted distress beacon near Saturn.",
  "genre": "Science Fiction",
  "language": "English",
  "tone": "Suspenseful",
  "num_scenes": 3,
  "characters": ["Kaelen", "Vance"],
  "setting": "INT. AIRLOCK - DAY",
  "additional_instructions": "Focus on escalating paranoia"
}
```
- **Response (200 OK):**
```json
{
  "success": true,
  "message": "Screenplay generated successfully.",
  "data": {
    "title": "THE ECHO PROTOCOL",
    "logline": "Two rival astronauts encounter an uncharted distress beacon...",
    "characters_summary": "Kaelen (Commander), Vance (Navigator)",
    "scenes": [
      {
        "scene_number": 1,
        "heading": "INT. AIRLOCK - DAY",
        "action": "Steam vents from the decontamination unit...",
        "dialogues": [
          {
            "character": "KAELEN",
            "parenthetical": "(checking scanner)",
            "line": "The frequency isn't human."
          }
        ],
        "transition": "CUT TO:",
        "raw_text": "..."
      }
    ],
    "scene_count": 1,
    "full_script": "TITLE: THE ECHO PROTOCOL\n...",
    "metadata": {
      "genre": "Science Fiction",
      "language": "English",
      "tone": "Suspenseful",
      "requested_scenes": 3,
      "detected_scenes": 1,
      "provider": "gemini",
      "model": "gemini-2.5-flash",
      "tokens_used": 128
    }
  }
}
```

### Endpoint 2: Individual Scene Generation
- **Route:** `POST /api/generate-scene`
- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
```json
{
  "scene_goal": "Confrontation inside the airlock after discovering the sabotage",
  "context": "Previous scene in the command bridge where oxygen levels dropped.",
  "genre": "Thriller",
  "language": "English",
  "characters": "Kaelen, Vance"
}
```
- **Response (200 OK):**
```json
{
  "success": true,
  "message": "Scene generated successfully.",
  "data": {
    "scene": {
      "scene_number": 1,
      "heading": "INT. AIRLOCK - NIGHT",
      "action": "Red warning beacons pulse against frost-covered glass...",
      "dialogues": [],
      "transition": "FADE OUT.",
      "raw_text": "..."
    },
    "full_text": "...",
    "metadata": {
      "scene_goal": "Confrontation inside the airlock after discovering the sabotage",
      "genre": "Thriller",
      "language": "English",
      "provider": "mock",
      "model": "mock-model-v1"
    }
  }
}
```

---

## 4. Test Verification & Results

### Automated Pytest Suite:
```text
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-8.3.3, pluggy-1.7.0
rootdir: C:\Users\djana\Downloads\STORYVERSE AI final\StoryVerse-AI\backend
configfile: pytest.ini
collected 151 items

tests\test_ai_assistant.py ............................................. [ 29%]
......                                                                   [ 33%]
tests\test_database.py .............                                     [ 42%]
tests\test_health.py .........                                           [ 48%]
tests\test_script.py .............................                       [ 67%]
tests\test_story.py ........................                             [ 83%]
tests\test_validators.py .........................                       [100%]

============================= 151 passed in 2.90s =============================
```

### Test Coverage Highlights (`tests/test_script.py`):
1. **Input Validators:**
   - Valid full parameter sets.
   - Missing or empty topic rejection (400).
   - Invalid genre / language / tone validation (400).
   - Scene count boundary enforcement (must be integer between 1 and 20).
   - Character count list bounds (max 20 characters).
   - Scene goal validation for single scenes.
2. **Screenplay Parser:**
   - Accurate slugline identification (`INT.`, `EXT.`, `INT./EXT.`, `I/E.`).
   - Character cue extraction (centered uppercase names).
   - Parenthetical capture (e.g. `(quietly)`).
   - Dialogue association to speaking characters.
   - Transitions recognition (`CUT TO:`, `FADE OUT.`, `DISSOLVE TO:`).
   - Graceful fallback for unstructured raw text.
3. **API Integration:**
   - All major genres: Thriller, Action, Drama, Comedy, Sci-Fi.
   - Multilingual support: English, Telugu, Tamil, Hindi.
   - Invalid JSON payload handling (400).
4. **Resilience & Error Handling:**
   - Rate limit error simulation -> 429 Too Many Requests.
   - Timeout error simulation -> 504 Gateway Timeout.
   - Network error simulation -> 502 Bad Gateway.
   - Empty response simulation -> 502 Bad Gateway.
   - Missing API key simulation -> 500 with user-actionable guidance.

---

## 5. Viva & Project Review Preparation

When presenting Phase 6 to the external college examiner:
1. **How does the system ensure industry-standard screenplay formatting?**
   - *Answer:* Through prompt engineering with specific formatting rules (sluglines in uppercase, present-tense action, centered cues, indented dialogues) combined with a deterministic regex parser (`ScriptService.parse_script_scenes()`) that breaks the output into distinct structural components.
2. **How does the frontend render screenplay text authentically?**
   - *Answer:* The frontend provides three specialized views. The primary Screenplay View formats the page using `Courier Prime` monospace typography, 36% left margins for character cues, 20% left/right margins for dialogues, and bold sluglines matching Final Draft and Hollywood standard script layouts.
3. **How does the application prevent XSS attacks when rendering scripts?**
   - *Answer:* All text from AI generation or user input is placed into DOM nodes exclusively using `Node.textContent` or `document.createElement()`, never `element.innerHTML`.
