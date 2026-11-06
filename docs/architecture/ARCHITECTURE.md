# ============================================================
# StoryVerse AI — System Architecture Document
# Phase 1 — Initial Architecture Design
# ============================================================

## 1. Overview

StoryVerse AI is a web application that uses Google's Gemini Generative AI to create
stories, scripts and characters. It is designed as a single-user local application
that can later be extended with authentication for multi-user support.

---

## 2. Architecture Style

Client-Server Architecture with REST API communication.

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT SIDE                          │
│                                                             │
│   Browser (http://localhost:3000)                           │
│   ┌─────────────────────────────────────────────────┐       │
│   │  HTML5 Pages  │  CSS3 Styles  │  JavaScript     │       │
│   │  index.html   │  style.css    │  main.js        │       │
│   │  story.html   │  story.css    │  story.js       │       │
│   │  script.html  │  script.css   │  script.js      │       │
│   │  ...          │  ...          │  ...            │       │
│   └───────────────────────────────┬─────────────────┘       │
│                                   │  Fetch API              │
│                                   │  HTTP REST Calls        │
└───────────────────────────────────┼─────────────────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │   CORS Middleware      │
                        │   (Flask-CORS)         │
                        └───────────┬───────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────┐
│                       SERVER SIDE                            │
│                                                             │
│   Flask Application (http://localhost:5000)                 │
│                                                             │
│   ┌─────────────────────────────────────────────────┐       │
│   │              Flask Blueprints (Routes)           │       │
│   │  story_routes  │  script_routes  │  ai_routes   │       │
│   │  character_routes  │  project_routes  │  export  │       │
│   └────────────────────────┬────────────────────────┘       │
│                            │                                 │
│   ┌────────────────────────▼────────────────────────┐       │
│   │              Services Layer                      │       │
│   │  ai_service  │  story_service  │  script_service │       │
│   │  character_service  │  export_service            │       │
│   │  prompt_service                                  │       │
│   └────────┬───────────────────────┬────────────────┘       │
│            │                       │                         │
│   ┌────────▼──────┐    ┌──────────▼──────────┐             │
│   │  SQLAlchemy   │    │  Google Gemini SDK   │             │
│   │  ORM Layer    │    │  (AI Provider)       │             │
│   └────────┬──────┘    └──────────┬──────────┘             │
│            │                       │                         │
│   ┌────────▼──────┐    ┌──────────▼──────────┐             │
│   │   SQLite DB   │    │  Gemini API          │             │
│   │   (instance/) │    │  (External Service)  │             │
│   └───────────────┘    └─────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Component Description

### Frontend (Client)
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Port**: 3000 (served by Python http.server)
- **Communication**: Uses `fetch()` API to call backend REST endpoints
- **Configuration**: API base URL is configurable (`API_BASE_URL` in `js/api.js`)
- **State**: Client-side state only (no React state management needed)

### Backend (Server)
- **Technology**: Python 3, Flask
- **Port**: 5000
- **Pattern**: Flask Blueprints for modular route organization
- **Layers**:
  1. **Routes** — HTTP request handling, input parsing, response formatting
  2. **Services** — Business logic, AI orchestration, data operations
  3. **Models** — SQLAlchemy database models
  4. **Utils** — Shared helpers (validators, response formatters, error handlers)

### Database
- **Engine**: SQLite (file-based, no server required)
- **ORM**: Flask-SQLAlchemy
- **Location**: `backend/instance/storyverse.db`
- **Models**:
  - `Project` — Stores user projects
  - `GenerationHistory` — Stores AI generation history per project

### AI Provider
- **Provider**: Google Gemini API
- **SDK**: `google-generativeai` Python package
- **Model**: Configurable via `GEMINI_MODEL` environment variable
- **Key**: Stored in `.env` file, never in code

---

## 4. API Architecture

All API endpoints follow the prefix: `/api/`

### Response Format (Standard)
```json
{
  "success": true,
  "message": "Description of what happened",
  "data": { ... }
}
```

### Error Format (Standard)
```json
{
  "success": false,
  "message": "Human-readable error message",
  "errors": {
    "field_name": "Specific error for this field"
  }
}
```

### HTTP Status Codes Used
- 200 — Success (GET, PUT operations)
- 201 — Created (POST that creates a resource)
- 400 — Bad Request (validation failure)
- 404 — Not Found (resource not found)
- 429 — Too Many Requests (rate limit)
- 500 — Internal Server Error
- 502 — Bad Gateway (AI provider failure)

---

## 5. Security Architecture

| Concern | Solution |
|---------|----------|
| API Key exposure | Stored in `.env`, never in frontend or Git |
| SQL Injection | SQLAlchemy ORM with parameterized queries |
| XSS | Frontend sanitizes AI output before rendering |
| CORS | Only frontend origin `localhost:3000` allowed |
| Rate Limiting | Flask-Limiter on AI generation endpoints |
| Input Validation | Backend validators check all user inputs |
| File Safety | Generated files stored in `generated_files/` with safe names |
| Error Info | Stack traces never sent to frontend |

---

## 6. Data Flow — Story Generation

```
User fills form → JS collects form data
    ↓
JS calls: POST /api/generate-story  (json body)
    ↓
Flask route receives request
    ↓
Validator checks all inputs
    ↓
prompt_service.build_story_prompt(params)
    ↓
ai_service.call_ai_model(prompt)
    ↓
Google Gemini API processes request
    ↓
AI response returned
    ↓
ai_service.parse_ai_response(raw_response)
    ↓
story_service.format_story(parsed_response)
    ↓
JSON response sent to frontend
    ↓
JS receives response → renders story in editor
    ↓
User can save → POST /api/projects (saves to SQLite)
    ↓
User can export → POST /api/export/pdf (generates PDF)
```

---

## 7. Database Schema

```
┌─────────────────────────────────────────────────────┐
│                    Project                           │
├─────────────────────────────────────────────────────┤
│  id           INTEGER  PRIMARY KEY AUTOINCREMENT     │
│  title        VARCHAR(500)  NOT NULL                 │
│  content_type VARCHAR(50)   NOT NULL  (story/script) │
│  genre        VARCHAR(100)                           │
│  language     VARCHAR(50)                            │
│  tone         VARCHAR(50)                            │
│  topic        TEXT                                   │
│  generated_content TEXT                              │
│  created_at   DATETIME  NOT NULL  (UTC)              │
│  updated_at   DATETIME  NOT NULL  (UTC)              │
└─────────────────────────┬───────────────────────────┘
                          │ 1
                          │
                          │ MANY
┌─────────────────────────▼───────────────────────────┐
│                 GenerationHistory                    │
├─────────────────────────────────────────────────────┤
│  id               INTEGER  PRIMARY KEY               │
│  project_id       INTEGER  FOREIGN KEY → Project.id  │
│  prompt           TEXT                               │
│  generated_content TEXT                              │
│  operation        VARCHAR(100)  (generate/rewrite)   │
│  created_at       DATETIME  NOT NULL  (UTC)          │
└─────────────────────────────────────────────────────┘
```

---

## 8. File Structure Rationale

| Folder | Reason |
|--------|--------|
| `frontend/` | Frontend is completely separate from backend |
| `frontend/pages/` | Each major page in its own HTML file |
| `frontend/css/` | Separate CSS per page for maintainability |
| `frontend/js/` | Separate JS module per page |
| `backend/models/` | Database models isolated for reuse |
| `backend/routes/` | Each Flask Blueprint in its own file |
| `backend/services/` | Business logic separate from routing |
| `backend/utils/` | Reusable helper functions |
| `backend/tests/` | All tests in one place |
| `backend/instance/` | SQLite database (auto-created by Flask) |
| `backend/generated_files/` | Temporary export files |
| `docs/` | All documentation for college submission |

---

*Document created: 2026-10-14*
*Phase: 1 — Architecture & Setup*
