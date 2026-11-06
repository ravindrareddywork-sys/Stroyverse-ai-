# StoryVerse AI 🌌✍️

> **Story and Script Generator Using Generative AI**
> BTech Computer Science — Final Year Project

---

## 📖 About

**StoryVerse AI** is a professional web application that uses Google's Gemini Generative AI to help users create:

- 📚 **Full-length stories** in multiple genres, languages and tones
- 🎬 **Screenplays and scripts** in proper screenplay format
- 👥 **Detailed character profiles**
- ✏️ **AI-powered writing assistance** (rewrite, expand, shorten, translate, etc.)
- 📁 **Project management** to save, organize and revisit creative work
- 📄 **Export** to TXT, PDF, and DOCX formats

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| Story Generator | Generate structured stories with title, plot, characters, climax and moral |
| Script Generator | Generate properly formatted screenplays with scenes, dialogue and transitions |
| Character Generator | Create rich, consistent character profiles |
| AI Writing Assistant | Rewrite, expand, shorten, translate and improve your content |
| Retrieval-Augmented Generation (RAG) | Vector knowledge base indexing worldbuilding lore & canon rules via ChromaDB and Sentence Transformers |
| Project Management | Save, search, edit and delete your creative projects |
| Export | Download as TXT, PDF or DOCX |
| Multi-language Support | English (Primary & Default), Telugu, Tamil, Hindi (Optional) |
| Multi-genre Support | Horror, Romance, Comedy, Thriller, Fantasy, Sci-Fi, Drama, Mystery, Adventure |
| Theme Switch | Light and dark mode |
| Responsive Layout | Desktop, tablet, and mobile interfaces |

---

## 🚀 Development Status

- [x] **Phase 1: Architecture & Setup** (Complete)
- [x] **Phase 2: Backend Foundation** (Complete — 47/47 Tests Passing)
- [x] **Phase 3: Frontend Foundation** (Complete — 21/21 Files Verified)
- [x] **Phase 4: Gemini AI Integration** (Complete — 98/98 Tests Passing)
- [x] **Phase 5: Story Generator** (Complete — 122/122 Tests Passing)
- [x] **Phase 6: Script Generator** (Complete — 151/151 Tests Passing)
- [x] **Phase 7: Character Generator** (Complete — 181/181 Tests Passing)
- [x] **Phase 8: AI Writing Assistant** (Complete — 222/222 Tests Passing)
- [x] **Phase 9: Database & Project Management** (Complete — 256/256 Tests Passing)
- [x] **Phase 10: Export Features** (Complete — 271/271 Tests Passing)
- [x] **Phase 11: Integration & QA** (Complete — 285/285 Tests Passing)
- [x] **Phase 12: Deployment & College Documentation** (Complete — Production & Academic Deliverables Ready)
- [x] **Phase RAG: Retrieval-Augmented Generation & Vector Storage** (Complete — 313/313 Tests Passing)
- [x] **Phase Final: Language Configuration, PDF Indic TrueType Resolution, Workspace Rate-Limit Fix & Full QA** (Complete — 342/342 Tests Passing, 100% Pass Rate)

---

## 🛠️ Technology Stack

### Frontend
- HTML5, CSS3, Vanilla JavaScript
- Fetch API for backend communication
- Responsive CSS (mobile, tablet, desktop)

### Backend
- Python 3.10+
- Flask + Flask Blueprints
- Flask-CORS, Flask-Limiter
- Flask-SQLAlchemy (SQLite)
- ReportLab (PDF), python-docx (DOCX)

### AI & Vector Storage (RAG)
- Google Gemini API (`gemini-2.5-flash`)
- Official `google-genai` Python SDK
- ChromaDB (Persistent Vector Storage & Cosine Similarity)
- Sentence Transformers (`intfloat/multilingual-e5-small` 384-dimensional dense multilingual embeddings across 100+ languages including English, Telugu, Tamil, Hindi)


---

## 🗂️ Project Structure

```
StoryVerse-AI/
├── frontend/              # HTML, CSS, JS (served by dev HTTP server)
│   ├── index.html         # Home page
│   ├── pages/             # Feature pages
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript modules
│   └── assets/            # Images & icons
│
├── backend/               # Flask API server
│   ├── app.py             # Flask application entry point
│   ├── config.py          # Configuration (dev/prod)
│   ├── extensions.py      # Flask extensions (db, limiter, cors)
│   ├── models/            # SQLAlchemy models
│   ├── routes/            # Flask Blueprints (API endpoints)
│   ├── services/          # Business logic & AI service
│   ├── utils/             # Validators, response helpers
│   ├── tests/             # pytest test suite
│   └── requirements.txt   # Python dependencies
│
└── docs/                  # Project documentation
    ├── architecture/
    ├── diagrams/
    ├── project_report/
    ├── presentation/
    ├── testing/
    └── viva/
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10 or higher
- pip
- A Google Gemini API key (get it free at https://aistudio.google.com)

### 1. Clone or Download the Project
```bash
cd "STORYVERSE AI final"
```

### 2. Set Up the Backend
```bash
cd StoryVerse-AI/backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Start the Backend Server
```bash
python app.py
```
Backend runs at: **http://localhost:5000**

### 5. Start the Frontend Dev Server
Open a new terminal:
```bash
cd StoryVerse-AI/frontend
python -m http.server 3000
```
Frontend runs at: **http://localhost:3000**

### 6. Open Your Browser
Go to: **http://localhost:3000**

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes (for live AI) | Your Google Gemini API key |
| `FLASK_ENV` | No | `development` or `production` |
| `FLASK_DEBUG` | No | `1` for debug mode (dev only) |
| `SECRET_KEY` | No | Flask secret key |
| `DATABASE_URL` | No | SQLite path (default: instance/storyverse.db) |
| `GEMINI_MODEL` | No | Model name (default: gemini-1.5-flash) |
| `CORS_ORIGINS` | No | Allowed frontend origins |

**⚠️ Never commit your `.env` file or expose your API key.**

---

## 🧪 Running Tests

```bash
cd StoryVerse-AI/backend
pytest tests/ -v
```

Tests use **mocked AI responses** and do NOT consume your Gemini API quota.

---

## 📡 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Health check |
| POST | /api/generate-story | Generate a full story |
| POST | /api/generate-script | Generate a screenplay |
| POST | /api/generate-character | Generate character profiles |
| POST | /api/generate-scene | Generate a single scene |
| POST | /api/rewrite | Rewrite content |
| POST | /api/expand | Expand content |
| POST | /api/shorten | Shorten content |
| POST | /api/continue | Continue a story or script |
| POST | /api/translate | Translate content |
| POST | /api/summarize | Summarize content |
| POST | /api/generate-dialogue | Generate dialogue |
| POST | /api/generate-plot-twist | Generate a plot twist |
| GET | /api/projects | List all projects |
| POST | /api/projects | Create a project |
| GET | /api/projects/:id | Get a project |
| PUT | /api/projects/:id | Update a project |
| DELETE | /api/projects/:id | Delete a project |
| POST | /api/export/txt | Export as TXT |
| POST | /api/export/pdf | Export as PDF |
| POST | /api/export/docx | Export as DOCX |
| POST | /api/rag/ingest | Ingest reference document into ChromaDB vector store |
| GET | /api/rag/documents | List ingested knowledge documents (with project filter) |
| GET | /api/rag/documents/:id | Retrieve document chunks and details |
| DELETE | /api/rag/documents/:id | Delete document from vector database |
| POST | /api/rag/query | Test semantic vector retrieval |
| GET | /api/rag/status | Vector database health and embedding statistics |

---

## 📚 Academic & Deployment Documentation

Comprehensive college deliverables and production guides are located in the [`docs/`](docs/) directory:
- 📖 [College Project Report (32 Chapters)](docs/project_report/PROJECT_REPORT.md)
- 📊 [Final Project Status Report](docs/project_report/FINAL_PROJECT_STATUS.md)
- 📐 [All System & UML Diagrams (Mermaid)](docs/diagrams/ALL_DIAGRAMS.md)
- 📽️ [PowerPoint Presentation Deck (18 Slides)](docs/presentation/PRESENTATION_SLIDES.md)
- 🎓 [Viva Voce Preparation Guide (50 Questions & Pitches)](docs/viva/VIVA_PREPARATION_GUIDE.md)
- 📘 [Official User & Operations Manual](docs/user_manual/USER_MANUAL.md)

---

## 🐳 Docker Production Deployment

To run the full stack containerized with backend Gunicorn and frontend Nginx:

```bash
# Set your Gemini API key in backend/.env or export it
export GEMINI_API_KEY="your-api-key"

# Build and start both containers
docker-compose up --build
```
- Frontend will be available at: `http://localhost:3000`
- Backend API will be available at: `http://localhost:5000`

---

## 👨‍💻 Developer

**BTech Computer Science — Final Year Project**

---

## 📄 License

This project is developed for academic purposes as a final year project submission.
