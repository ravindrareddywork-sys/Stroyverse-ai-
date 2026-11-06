# StoryVerse AI — B.Tech Final Year Project Presentation
**Project Title:** Story and Script Generator Using Generative AI  
**Academic Degree:** Bachelor of Technology (B.Tech) in Computer Science & Engineering  
**Academic Year:** 2026–2027  
**Platform Name:** StoryVerse AI  

---

## Slide 1: Title Slide
### STORYVERSE AI: Story and Script Generator Using Generative AI
- **Project Domain:** Artificial Intelligence / Natural Language Processing / Full-Stack Web Development
- **Student Name:** `[STUDENT_NAME_PLACEHOLDER]`
- **Hall Ticket / Roll No:** `[ROLL_NUMBER_PLACEHOLDER]`
- **Project Guide:** `[GUIDE_NAME_PLACEHOLDER]`, `[GUIDE_DESIGNATION_PLACEHOLDER]`
- **Department:** Department of Computer Science & Engineering
- **Institution:** `[COLLEGE_NAME_PLACEHOLDER]`

---

## Slide 2: Introduction
### The Evolution of Narrative Generation
- Creative writing and screenwriting traditionally require significant time for outlining, character conceptualization, and scene formatting.
- Large Language Models (LLMs) such as Google Gemini offer capabilities for real-time text generation, contextual style transformation, and creative brainstorming.
- **StoryVerse AI** is an intelligent creative platform providing end-to-end writing assistance:
  - Long-form structured story generation (10-act outlines).
  - Industry-standard Hollywood screenplay formatting.
  - 19-dimensional psychological character bibles.
  - In-browser AI assistant tools and document persistence with revision version control.
  - Native multi-language generation in English, Telugu (తెలుగు), Tamil (தமிழ்), and Hindi (हिंदी).

---

## Slide 3: Problem Statement
### Core Challenges in Modern Creative Software
1. **Formatting Burden:** Novice screenwriters struggle with strict Hollywood screenplay standards (sluglines, character cues, dialogue margins, parentheticals).
2. **Shallow AI Generations:** Generic AI prompts produce unstructured blocks of text lacking narrative continuity, character depth, or distinct pacing.
3. **Lack of Indic Language Support:** Most writing platforms only support English, neglecting regional Indian languages like Telugu, Tamil, and Hindi.
4. **Data Isolation:** Generated content is frequently lost upon page refresh without native project persistence or snapshot version control.
5. **Format Trapping:** Creative drafts cannot be easily exported directly to standard editable formats (Word `.docx`, Adobe `.pdf`, and `.txt`) with proper Unicode fonts.

---

## Slide 4: Objectives
### Primary Project Goals
- **Architect Modular AI Pipeline:** Integrate Google Gemini AI via the official Google Gen AI SDK with an abstraction layer supporting deterministic mock testing.
- **Structured Storytelling:** Implement automated multi-act narrative decomposition (Act 1 Setup to Act 10 Resolution).
- **Screenplay Engine:** Format multi-scene scripts following Hollywood scriptwriting conventions.
- **Deep Character Synthesis:** Generate 3D character bibles across 19 psychological, physical, and narrative dimensions.
- **Versatile Writing Assistant:** Build interactive rewriting, translation, summarization, dynamic dialogue, and plot-twist modules.
- **Database Persistence & Versioning:** Store projects with complete revision history and snapshot restoration in SQLite.
- **Publication-Ready Export:** Deliver streaming in-memory exports to TXT, PDF (ReportLab with Unicode), and DOCX (python-docx).

---

## Slide 5: Existing System vs. Proposed System
### Comparative Analysis

| Feature | Existing Conventional Tools (e.g. ChatGPT, Word) | Proposed System (StoryVerse AI) |
|---|---|---|
| **Specialized UI** | Generic chat box or blank document | Dedicated forms for Stories, Screenplays, Characters, and Workspace |
| **Output Structure** | Unstructured prose paragraphs | 10-act story outlines, courier screenplay format, 19-pt character matrix |
| **Indic Languages** | English-centric; poor Indic typography | Native multilingual generation & font-embedded exports (Telugu, Tamil, Hindi) |
| **Formatting** | Manual indentation and styling required | Automated Hollywood screenplay formatting with monospace styling |
| **Version History** | Third-party git or paid cloud subscriptions | Built-in snapshot versioning with 1-click restore |
| **Document Export** | Manual copy-pasting required | In-memory 1-click export to TXT, PDF (Page X of Y), and DOCX |

---

## Slide 6: System Architecture
### Multi-Tier Distributed Design
- **Presentation Tier:** Vanilla JavaScript, HTML5, Modular CSS3 with responsive dark/light theme switching.
- **REST API Tier:** Flask Application Factory with Blueprint routing, CORS security, and rate limiting.
- **Service Tier:** Decoupled business logic (`StoryService`, `ScriptService`, `CharacterService`, `WritingAssistantService`, `ProjectService`, `ExportService`).
- **AI Integration Layer:** `BaseAIProvider` abstraction with `GeminiProvider` and `MockAIProvider`.
- **Persistence Tier:** SQLAlchemy ORM managing SQLite with relational integrity and cascade deletions.

---

## Slide 7: Technology Stack
### Production-Grade Technologies

- **Backend Framework:** Python 3.11+ / Flask 3.0.x
- **AI Engine:** Google Gemini Generative AI (`google-genai` SDK / `gemini-2.5-flash`)
- **Vector Storage (RAG):** ChromaDB (Persistent Vector Storage & HNSW Cosine Indexing)
- **Embedding Models:** Sentence Transformers (`intfloat/multilingual-e5-small` 384-dimensional multilingual embeddings)
- **Database & ORM:** SQLite 3 with Flask-SQLAlchemy / SQLAlchemy 2.0
- **Document Exporting:** ReportLab 4.x (PDF) & `python-docx` 1.1.x (Word)
- **Frontend Core:** HTML5, CSS3 Variables, ES6+ Vanilla JavaScript (zero heavy framework overhead)
- **Typography:** Courier Prime (Screenplays), Inter (UI), Nirmala UI (Indic Unicode)
- **Testing & QA:** `pytest` (331 automated tests, 100% pass rate), Headless Google Chrome
- **Language Standard:** English (Primary & Default everywhere); Telugu, Tamil, Hindi (Optional)

---

## Slide 8: Functional Modules Overview
### Five Integrated Subsystems
1. **Story Generator:** Topic-driven story generator across 9 genres and 4 languages with interactive expansion.
2. **Script Generator:** Multi-scene screenplay creator supporting 1 to 20 scenes and incremental scene generation.
3. **Character Studio:** 19-point character matrix generator and ensemble concept ideator.
4. **AI Writing Assistant:** In-editor toolkit for rewriting, translating, summarizing, dialogue generation, and plot twists.
5. **Project Portfolio & Export Engine:** CRUD operations, snapshot versioning, keyword search, and TXT/PDF/DOCX exports.

---

## Slide 9: Module 1 — Story Generator
### Narrative Structure & Act Decomposition
- **Input Parameters:** Topic/Premise, Genre (Horror, Fantasy, Sci-Fi, etc.), Language, Tone, Length, Audience, Character count.
- **Narrative Decomposition:** Automatically generates and parses a 10-act structure:
  - *Act 1: Exposition* | *Act 2: Inciting Incident* | *Act 3: Rising Action*
  - *Act 4: Midpoint Climax* | *Act 5: Crisis & Dark Night* | *Act 6: Climax & Resolution*
- **Interactive Refinement:** In-place expansion with sensory details, shortening/condensing, and narrative continuation.
- **Dual Presentation:** Toggle between Structured 10-Act Accordions and Editable Full Manuscript.

---

## Slide 10: Module 2 — Screenplay Studio
### Industry-Standard Screenplay Formatting
- **Hollywood Standard Adherence:**
  - `INT.` / `EXT.` Scene Headings (Sluglines) with time and location.
  - Uppercase Centered Character Speaking Cues.
  - Indented Actor Parentheticals and Dialogue Blocks.
  - Scene Transitions (`CUT TO:`, `FADE OUT:`).
- **Courier Prime Monospace Engine:** Emulates authentic typewriter screenplay pages.
- **Incremental Scene Builder:** Generate initial scenes (1–20) and append follow-up scenes sequentially.

---

## Slide 11: Module 3 — Character Studio
### 3D Character Bible Synthesis
- **19 Narrative Dimensions Generated:**
  1. Name | 2. Age | 3. Role | 4. Archetype | 5. Appearance | 6. Traits | 7. Psychology
  8. Strengths | 9. Weaknesses | 10. Fatal Flaw | 11. Backstory | 12. Motivations & Goals
  13. Fears | 14. Secrets | 15. Relationships | 16. Internal Conflict | 17. External Conflict
  18. Character Development Arc | 19. Role in Narrative
- **Ensemble Concept Variations:** Generates 2 to 5 diverse candidate character concepts with contrasting motivations and flaws.

---

## Slide 12: Module 4 — AI Writing Assistant
### Multi-Tool Writing Workspace
- **Rewrite Engine:** 6 selectable style directives (improve clarity, improve grammar, make it professional, make it creative, make it engaging, simplify language).
- **Translation Engine:** Nuanced cross-lingual translation between English, Telugu, Tamil, and Hindi.
- **Summarization Engine:** Concise, medium, or detailed document summaries.
- **Dynamic Dialogue Generator:** Generates natural character interaction based on scene tension and character traits.
- **Plot Twist Generator:** Synthesizes unexpected yet logically grounded plot twists tailored to genre and tone.
- **Narrative Continuation:** Continues storylines seamlessly from existing text.

---

## Slide 13: Module 5 — Project Management & Export
### Portfolio Persistence & Document Generation
- **Centralized Dashboard:** Real-time metrics, debounce search, genre/type filtering, and date/title sorting.
- **Snapshot Version Control:** Explicit snapshotting with changelog notes and 1-click restoration of older versions.
- **Multi-Format Export Engine:**
  - **Plain Text (`.txt`)**: Clean UTF-8 formatted text with metadata headers.
  - **Adobe PDF (`.pdf`)**: ReportLab engine with two-pass `NumberedCanvas` (Page X of Y) and embedded `Nirmala.ttc` Unicode font.
  - **Word (`.docx`)**: Styled Microsoft Word headings, callouts, and formatted paragraphs.

---

## Slide 14: Module 6 — Retrieval-Augmented Generation (RAG) Architecture
### Domain Knowledge Grounding & Vector Storage
- **The Grounding Challenge:** Standard LLMs hallucinate fictional lore, alter established canon rules, and forget character backstories across multiple chapters.
- **StoryVerse RAG Pipeline:**
  - **Document Ingestion & Chunking:** Ingests worldbuilding bibles, character dossiers, magic rules, and style guides; splits by paragraph/sentence boundaries with configurable overlap.
  - **Dense Multilingual Vector Embeddings:** Generated using `sentence-transformers` (`intfloat/multilingual-e5-small`) producing 384-dimensional dense vectors across English, Telugu, Tamil, and Hindi with query/passage prefixing.
  - **ChromaDB Persistent Vector Store:** Persistent vector database with HNSW cosine similarity indexing (`hnsw:space: cosine`).
  - **Metadata Filtering & Project Lore Isolation:** Filters by genre, language, doc type, and isolates private project lore (`project_id`) while allowing global lore sharing.
  - **Mandatory Grounding Directives:** Injects retrieved context into Story, Script, Character, and Writing Assistant prompts with explicit constraints forbidding factual contradiction.
  - **Automated Verification:** Verified with 28 automated tests asserting that unique knowledge facts from ChromaDB are physically present in model prompts across all 4 generation modules.

---

## Slide 15: Testing & Quality Assurance
### Comprehensive Verification Methodology

- **Automated Regression Suite:** **335 passed tests in 17.64 seconds (100% pass rate)**.
  - *Health & Validators:* 34 tests | *Database:* 13 tests
  - *AI Provider & Mock:* 51 tests | *Story Module:* 25 tests
  - *Script Module:* 34 tests | *Character Studio:* 30 tests
  - *Writing Assistant:* 50 tests | *Project Persistence:* 35 tests
  - *Document Exports:* 19 tests | *E2E Workflows & Security:* 14 tests
  - *RAG & Vector Grounding:* 30 tests
- **Browser Quality Assurance:** Headless Google Chrome executed across all 6 pages with **0 JavaScript runtime errors**.
- **Security Audits:** Verified parameterized queries (SQL injection proof), safe `textContent` rendering (XSS safe), and path traversal filename sanitization.

---

## Slide 16: Screenshots & Demonstration
### Live Application Interface
- **Slide Placeholder 1:** *Landing Portal (`index.html`)* — Feature cards, navigation header, and theme toggle.
- **Slide Placeholder 2:** *Story Generator (`story.html`)* — Parameter configuration form, act structure breakdown, and action toolbar.
- **Slide Placeholder 3:** *Screenplay Studio (`script.html`)* — Monospace Courier screenplay formatting and scene breakdown.
- **Slide Placeholder 4:** *Character Studio (`characters.html`)* — 19-point psychological profile matrix and ensemble variations.
- **Slide Placeholder 5:** *Project Dashboard (`dashboard.html`)* — Portfolio metrics, search/filter controls, and version history modal.
- **Slide Placeholder 6:** *Workspace Editor (`editor.html`)* — Real-time editing, writing assistant panels, and export dropdown.

*(Note: Live demonstration will be performed during viva examination.)*

---

## Slide 17: Limitations
### Honest Technical Boundary Assessment
- **AI Quota & Network Dependency:** Live Gemini mode requires active internet and valid Google AI Studio API credentials; fallback is provided by the mock provider.
- **Indic PDF Fallback:** Embedded `NirmalaUI` font is registered from Windows system fonts; on non-Windows servers without Indic font packages, PDFs fall back to Helvetica.
- **Single-User Architecture:** Designed as a localized creative workstation without multi-tenant authentication or cloud synchronization.
- **Context Window Constraints:** Very long manuscripts (>50,000 words) are processed in chapters/scenes rather than single monolithic requests.

---

## Slide 18: Future Scope
### Roadmap for Future Enhancements
- **Multi-Modal AI Integration:** Incorporate Gemini Image Generation to produce visual character portraits and scene concept art.
- **Audio & Speech-to-Script:** Add voice narration using Text-to-Speech (TTS) and voice dictation for writers.
- **Collaborative Writing:** Real-time multi-user editing using WebSockets.
- **Cloud Synchronization & Auth:** Integration of OAuth2 / JWT authentication with cloud database backends.
- **Advanced Export Formats:** Direct export to Final Draft (`.fdx`) and ePub formats.

---

## Slide 19: Conclusion & Thank You
### Summary of Project Impact
- **StoryVerse AI** demonstrates the practical, ethical, and structured application of Generative AI in the creative arts.
- Successfully integrates multi-act story outlining, Hollywood screenplay formatting, psychological character creation, vector knowledge retrieval (RAG with ChromaDB), and multi-format document exporting into a unified, high-performance platform.
- Rigorously tested with **335 automated tests** and production-ready containerization.
- Established English as the primary and default language across all modules, with complete optional multilingual generation for Telugu, Tamil, and Hindi.

### Thank You!
**Questions & Discussion are welcome.**  
*Demonstration of live application follows.*
