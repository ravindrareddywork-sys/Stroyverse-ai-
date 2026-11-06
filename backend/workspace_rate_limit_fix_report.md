# StoryVerse AI — Workspace Rate Limiting & Too Many Requests Fix Report

**Date:** November 5, 2026  
**Project:** StoryVerse AI (Phase 8 & 9 Stability Enhancement)  
**Issue:** `429 Too Many Requests: "Too many requests. Please wait a moment and try again."` when accessing the Workspace tab / editor.  
**Resolution Status:** Completely Resolved & Verified  

---

## 1. Exact Root Cause Analysis

Investigation revealed a multi-layered cause rooted in Flask-Limiter configuration and static asset routing:

### Primary Root Cause: Catch-All Route Counting Static Assets Against Global API Quota
1. When the backend was configured to serve the frontend via `serve_frontend` (`@app.route('/<path:path>')`), this catch-all route was created **without** `@limiter.exempt`.
2. Flask-Limiter's default limit was set to `"200 per day, 50 per hour"` across all endpoints in `extensions.py` and `config.py`.
3. In modern web browsers, loading a single page like `pages/editor.html` or `pages/dashboard.html` triggers **9 to 11 separate HTTP requests**:
   - `GET /pages/editor.html`
   - `GET /css/style.css`
   - `GET /css/components.css`
   - `GET /css/responsive.css`
   - `GET /css/editor.css`
   - `GET /js/theme.js`
   - `GET /js/api.js`
   - `GET /js/main.js`
   - `GET /js/editor.js`
   - `GET /favicon.ico`
   - `GET /api/health` (triggered automatically by `initBackendStatus()` on DOMContentLoaded)
4. Because static files were routed through Flask without exemption, every asset download was counted as an API request against the client's IP.
5. In just 4 to 5 tab navigations (Home → Story Generator → Characters → Workspace), the 50-per-hour quota was completely exhausted.
6. The actual Flask server log proved this:
   ```
   2026-11-05 23:32:42,249 [INFO] flask-limiter: ratelimit 50 per 1 hour (127.0.0.1) exceeded at endpoint: serve_frontend
   2026-11-05 23:32:43,516 [INFO] werkzeug: 127.0.0.1 - - [05/Nov/2026 23:32:43] "GET /pages/dashboard.html HTTP/1.1" 429 -
   ```
7. Consequently, clicking "Workspace" returned HTTP 429 with JSON `{"errors": {}, "message": "Too many requests. Please wait a moment and try again.", "success": false}` instead of rendering the page.

### Secondary Contributing Factors
- **Shared IP Key Behind Proxies / Localhost:** All requests over localhost or tunnel proxies shared the `127.0.0.1` client IP bucket because `ProxyFix` was not enabled.
- **Unexempted Health Endpoint:** `GET /api/health` consumed a rate-limit slot on every single page load.
- **Lack of Dedicated Limits for Project CRUD:** Project listing, viewing, and updating in `project_routes.py` had no explicit limits and fell back to the restrictive global 50/hour quota.
- **Frontend Missing Loading Guards & Deduplication:** Rapid clicking on dashboard filters or workspace reloads could issue duplicate concurrent requests without debounce/cancellation.

---

## 2. Files Modified

| File | Type | Changes Made |
|------|------|--------------|
| `backend/extensions.py` | Backend | Updated default limiter limits from `["200 per day", "50 per hour"]` to `["2000 per day", "500 per hour"]`. |
| `backend/config.py` | Backend | Updated `RATELIMIT_DEFAULT` in `BaseConfig` to `"2000 per day, 500 per hour"`. Preserved `RATELIMIT_GENERATION = "10 per minute"`. |
| `backend/app.py` | Backend | Added `ProxyFix` middleware from `werkzeug.middleware.proxy_fix` for accurate client IP resolution; decorated `serve_frontend` catch-all route with `@limiter.exempt`. |
| `backend/routes/health_routes.py` | Backend | Added `@limiter.exempt` to `GET /api/health` to prevent status pings from consuming rate limit quota. |
| `backend/routes/project_routes.py` | Backend | Added explicit, calibrated rate limits to all project and version endpoints (`120 per minute` for reads, `60 per minute` for writes, `30 per minute` for deletes/restores). |
| `backend/utils/error_handler.py` | Backend | Enhanced 429 error handler: extracts `Retry-After` seconds, provides user-friendly countdown message, attaches `rate_limit` details in `errors`, and sets the `Retry-After` HTTP header. |
| `frontend/js/api.js` | Frontend | Added in-flight GET request deduplication (`inFlightGetRequests` cache) and improved 429 error parsing with `Retry-After` extraction. |
| `frontend/js/dashboard.js` | Frontend | Added `isLoadingProjects` loading guard; avoided refetching when clicking already-active filter button; improved error toast handling for 429 warnings. |
| `frontend/js/editor.js` | Frontend | Added `isLoadingProject` guard on initial URL param project load; graceful rate-limit warning toast handling. |
| `frontend/js/main.js` | Frontend | Added single-execution guard `backendStatusChecked` to `initBackendStatus()`. |
| `backend/tests/test_rate_limits.py` | Tests | Created comprehensive test suite for rate limiting, 429 responses, exemptions, and workspace navigation. |

---

## 3. Before-and-After Behavior

| Metric / Behavior | Before Fix | After Fix |
|-------------------|------------|-----------|
| **Static files (HTML, JS, CSS, Favicon)** | Counted against 50/hour API limit | `@limiter.exempt` (never counted, unlimited) |
| **Backend Health Check (`/api/health`)** | Counted against 50/hour API limit | `@limiter.exempt` (never counted, unlimited) |
| **Global Default API Limit** | 50 per hour (~0.8 requests/min) | 500 per hour / 2000 per day (~8.3 requests/min) |
| **Workspace & Project Reads (`/api/projects`)** | Shared restrictive 50/hour quota | Dedicated `120 per minute` limit |
| **Workspace & Project Writes (`POST/PUT`)** | Shared restrictive 50/hour quota | Dedicated `60 per minute` limit |
| **AI Generation (`/api/generate-*`)** | Protected at 10/min | Protected at 10/min (unchanged) |
| **429 Response Headers** | Generic message, no `Retry-After` | Sets `Retry-After: <seconds>`, clear explanation |
| **Rapid Workspace Navigation (15 clicks)** | Exceeded limit at 5th click (429) | All 15 clicks succeed with HTTP 200 |
| **Concurrent Duplicate In-Flight GETs** | Issued multiple identical HTTP requests | Deduplicated via `inFlightGetRequests` map |

---

## 4. Test Results

### Automated Backend Tests (Pytest)
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-8.3.3
rootdir: StoryVerse-AI/backend, configfile: pytest.ini
collected 342 items

tests/test_ai_assistant.py ..................................            [ 10%]
tests/test_characters.py ....................................            [ 20%]
tests/test_exports.py ....................                              [ 26%]
tests/test_health.py ......                                              [ 28%]
tests/test_integration_e2e.py ...............................             [ 37%]
tests/test_projects.py ................................................. [ 51%]
tests/test_rag.py ............................................           [ 64%]
tests/test_rate_limits.py .......                                        [ 66%]
tests/test_script.py ................................................... [ 81%]
tests/test_story.py .................................................... [ 97%]
tests/test_writing_assistant.py .................                       [100%]

============================ 342 passed in 23.95s =============================
```
- **Tests Collected:** 342
- **Tests Passed:** 342 (100%)
- **Tests Failed:** 0
- **Tests Skipped:** 0
- **Execution Time:** 23.95 seconds

### Frontend JavaScript Syntax Validation (`node -c`)
All 8 frontend JavaScript files validated cleanly with zero syntax errors:
- `api.js`: OK
- `characters.js`: OK
- `dashboard.js`: OK
- `editor.js`: OK
- `main.js`: OK
- `script.js`: OK
- `story.js`: OK
- `theme.js`: OK

### Live Verification (Simulated Browser Clicks)
1. **Workspace Page Load:** `GET /pages/editor.html` → HTTP 200 (21,867 bytes).
2. **Rapid Click Test (15 consecutive requests):** All 15 returned HTTP 200 without a single 429.
3. **Cross-Tab Navigation:** Story Generator (`/pages/story.html`) → Workspace (`/pages/editor.html`) → both returned HTTP 200.
4. **Project API Calls (10 rapid calls):** All 10 returned HTTP 200 with valid JSON.
5. **Health Endpoint:** Returned `status: healthy` without depleting rate limits.
6. **Public Tunnel (`famous-lies-behave.loca.lt`):** Verified HTTP 200 on Workspace and healthy status.

---

## 5. Remaining Limitations & Recommendations

1. **Proxy Headers in Multi-Hop Networks:** `ProxyFix(x_for=1)` assumes a single trusted reverse proxy. If deploying to multi-tier infrastructure (e.g. Cloudflare + AWS ALB + Nginx), adjust `x_for` count accordingly.
2. **In-Memory Storage for Development:** Flask-Limiter is currently using `memory://` storage. In multi-process production deployments (e.g. Gunicorn with multiple workers), a Redis-backed storage (`redis://localhost:6379/0`) should be configured in `ProductionConfig`.
3. **Multilingual Script Support:** English remains the default language; Tamil, Telugu, and Hindi options remain fully available and are completely unaffected by the rate limiting changes.
