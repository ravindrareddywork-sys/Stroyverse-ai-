# Single Character Generation Fix Report

**Date:** 2026-11-06  
**Workflow:** Character Forge → Forge Character Profile → `POST /api/generate-character`

## Exact root cause and reproduced exception

The browser form submits optional blank fields as explicit JSON `null` values, including `gender`, `background`, `setting`, and `additional_instructions`. `build_character_prompt()` treated these values as strings and called `.strip()` directly. Reproducing the full frontend payload returned HTTP 500. The corresponding prompt-builder traceback was:

```text
File "backend/services/prompt_service.py", line 222, in build_character_prompt
    gender = params.get("gender", "").strip()
AttributeError: 'NoneType' object has no attribute 'strip'
```

The reduced request without nullable optional properties succeeded, which initially hid the issue. This was an application-side prompt construction error, not a Gemini authentication, quota, timeout, token-limit, or database error.

## Workflow findings

- The frontend and route use the expected property names: `description`, `character_name`, `genre`, `character_role`, `character_archetype`, `age`, `gender`, `language`, `tone`, `background`, and `additional_instructions`.
- The request targets the correct `/api/generate-character` endpoint.
- The provided genre, role, language, and tone values pass backend validation. Character description and genre are required; omitted language defaults to English.
- Gemini returns plain text, not JSON. `AIService` validates the provider text payload; `CharacterService` parses the numbered character-profile sections.
- A live Tamil request returned `FinishReason.STOP` and 2,463 reported tokens with the prior 4,096-token setting, so the observed shorter localized text was not a token-limit truncation. The parser previously relied on English heading names, however, and missed sections when headings were translated.
- Generation itself does not write to the database. The separate “Save as Project” action persists a generated profile; it was not invoked during these generation tests.
- RAG retrieval is unchanged and remains opt-in for this workflow (`use_rag`, a RAG query, or project ID). The tested single-character form does not request RAG context.

## Fixes and files modified

- `backend/services/prompt_service.py`
  - Normalize nullable optional strings before trimming.
  - Apply English and other existing defaults when optional language/tone/role/genre values are `null`.
  - Instruct Gemini to keep numbered section labels in English while generating section content in the selected language.
- `backend/services/character_service.py`
  - Retain the existing label-based parser and add a numbered-section fallback so translated labels do not discard structured profile fields.
- `backend/utils/validators.py`
  - Require a valid genre for the single-character endpoint, matching the required form field; preserve English as the default when language is omitted.
- `backend/routes/character_routes.py`
  - Log unexpected single-character processing exceptions with a traceback, without logging request contents or credentials. Existing typed AI error mappings remain in use.
- `frontend/pages/characters.html`
  - Mark genre and language selectors required and add an accessible validation error area.
- `frontend/js/characters.js`
  - Display backend field-specific validation errors for the single-character form.
- `backend/tests/test_characters.py`
  - Cover the exact browser payload with null optional fields, missing required values, English language default, translated numbered labels, and AI authentication failures.
- `backend/SINGLE_CHARACTER_GENERATION_FIX_REPORT.md`

## Live Gemini results

These requests used the real configured `GeminiProvider` (`AI_PROVIDER=gemini`, mock mode disabled) and model `gemini-3.5-flash-lite`. Key presence was checked without printing its value.

| Test | Result | Output |
|---|---|---|
| Mystery / Protagonist / English — submitted from the browser form with blank optional fields | **PASS** | Result rendered; 7,590-character profile; visible narrative sections populated |
| Fantasy / Antagonist / English | **PASS** | HTTP 200; 9,393-character profile; 15/15 narrative sections populated |
| Science Fiction / Protagonist / Tamil | **PASS** | HTTP 200; 4,495-character profile; 15/15 narrative sections populated |
| Thriller / Protagonist / Telugu | **PASS** | HTTP 200; 4,860-character profile; 15/15 narrative sections populated |
| Drama / Protagonist / Hindi | **PASS** | HTTP 200; 5,840-character profile; 15/15 narrative sections populated |
| Minimal live provider request | **PASS** | Real Gemini response received |

No API key or generated profile text was written to this report.

## Mock/regression results (separate from live requests)

- Full backend suite: `python -m pytest -q` — **372 passed**.
- Focused character, integration, and RAG suite: **102 passed**.
- Frontend JavaScript syntax: `node --check` — **8 files passed**.
- Python compilation of changed backend and test modules — **passed**.
- Missing description and missing genre are rejected with field-specific 400 errors.
- Authentication, quota/rate-limit, timeout, network, and empty-response handling remain mapped to safe, specific API errors; error-path tests use simulated/mock failures, not real provider failures.
- Ensemble generator and RAG regressions passed in the full and focused suites.

## Remaining issues

- No known generation issue remains in the tested workflow.
- Saving a generated profile to the project database remains a separate explicit user action.
- Live API error conditions such as invalid credentials and exhausted quota were not intentionally triggered; their response mappings were tested with simulated failures.
