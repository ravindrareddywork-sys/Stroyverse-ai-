# A PROJECT REPORT ON
# STORY AND SCRIPT GENERATOR USING GENERATIVE AI
### (StoryVerse AI)

*A dissertation submitted in partial fulfillment of the requirements for the award of the degree of*

**BACHELOR OF TECHNOLOGY**  
*in*  
**COMPUTER SCIENCE AND ENGINEERING**

---

**Submitted by:**  
**`[STUDENT_NAME_PLACEHOLDER]`**  
**(Roll No: `[ROLL_NUMBER_PLACEHOLDER]`)**

**Under the Esteemed Guidance of:**  
**`[GUIDE_NAME_PLACEHOLDER]`**  
`[GUIDE_DESIGNATION_PLACEHOLDER]`  
Department of Computer Science & Engineering  

**DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING**  
**`[COLLEGE_NAME_PLACEHOLDER]`**  
*(Affiliated to `[UNIVERSITY_NAME_PLACEHOLDER]`, Approved by AICTE, Accredited by NBA & NAAC)*  
`[COLLEGE_LOCATION_PLACEHOLDER]`  
**ACADEMIC YEAR: 2026–2027**

---

## CERTIFICATE

This is to certify that the project report entitled **"STORY AND SCRIPT GENERATOR USING GENERATIVE AI (StoryVerse AI)"** is a bonafide record of work carried out by **`[STUDENT_NAME_PLACEHOLDER]`** (Roll No: **`[ROLL_NUMBER_PLACEHOLDER]`**) in partial fulfillment of the requirements for the award of the degree of **Bachelor of Technology in Computer Science and Engineering** from **`[COLLEGE_NAME_PLACEHOLDER]`**, affiliated to **`[UNIVERSITY_NAME_PLACEHOLDER]`**, during the academic year 2026–2027.

The results embodied in this report have been verified and have not been submitted to any other University or Institution for the award of any degree or diploma.

<br><br><br>

------------------------------------ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ------------------------------------  
**Internal Guide** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Head of the Department**  
`[GUIDE_NAME_PLACEHOLDER]` &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `[HOD_NAME_PLACEHOLDER]`  
`[GUIDE_DESIGNATION_PLACEHOLDER]` &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Department of CSE  

<br><br>

**External Examiner:** __________________________________  
**Date of Examination:** _______________________________

---

## DECLARATION

I, **`[STUDENT_NAME_PLACEHOLDER]`**, student of Bachelor of Technology in Computer Science and Engineering, hereby declare that the project entitled **"STORY AND SCRIPT GENERATOR USING GENERATIVE AI (StoryVerse AI)"** submitted to **`[COLLEGE_NAME_PLACEHOLDER]`** is an original work done by me under the guidance of **`[GUIDE_NAME_PLACEHOLDER]`**, `[GUIDE_DESIGNATION_PLACEHOLDER]`, Department of Computer Science and Engineering.

I further declare that this report has not been submitted previously in part or in full to any other university or institution for the award of any degree, diploma, or fellowship.

<br><br>
**Place:** `[COLLEGE_LOCATION_PLACEHOLDER]`  
**Date:** `[SUBMISSION_DATE_PLACEHOLDER]`  

<br>
**`[STUDENT_NAME_PLACEHOLDER]`**  
**(Roll No: `[ROLL_NUMBER_PLACEHOLDER]`)**

---

## ACKNOWLEDGEMENT

First and foremost, I express my profound gratitude to the Almighty for bestowing upon me the strength, wisdom, and perseverance necessary to complete this project successfully.

I wish to express my deepest sense of gratitude and respect to my project guide, **`[GUIDE_NAME_PLACEHOLDER]`**, `[GUIDE_DESIGNATION_PLACEHOLDER]`, Department of Computer Science and Engineering, for their invaluable guidance, constructive criticism, and unwavering encouragement throughout the development of this project.

I extend my sincere thanks to **`[HOD_NAME_PLACEHOLDER]`**, Head of the Department of Computer Science and Engineering, for providing the necessary facilities and a supportive environment.

I am immensely grateful to **`[PRINCIPAL_NAME_PLACEHOLDER]`**, Principal of **`[COLLEGE_NAME_PLACEHOLDER]`**, for their constant support and administrative facilities.

Finally, I convey my heartfelt appreciation to my parents, family members, and friends for their continuous moral support and encouragement during the course of my engineering studies.

<br><br>
**`[STUDENT_NAME_PLACEHOLDER]`**

---

## ABSTRACT

The rapid evolution of Large Language Models (LLMs) and Generative Artificial Intelligence (GenAI) has transformed creative industries, yet existing tools often fail creative writers and screenwriters who require rigid structural pacing, industry-standard formatting, deep character psychological profiles, and native Indic language support. Generic chat-based AI tools output unstructured blocks of text lacking narrative continuity, provide no screenplay typesetting (sluglines, cues, dialogue indentations), lack snapshot revision control, and force users to manually copy-paste text without native publication export capabilities.

To resolve these challenges, this project presents **StoryVerse AI**, a full-stack, decoupled generative creative writing suite. Built with a Python Flask RESTful backend and a lightweight Vanilla JavaScript presentation layer, StoryVerse AI orchestrates the Google Gemini Generative AI model through the official Google Gen AI SDK. The platform incorporates a modular **Provider Abstraction Layer** supporting both live Gemini execution and a deterministic **Mock AI Engine** for quota-free, offline testing and evaluation.

StoryVerse AI integrates five specialized subsystems:
1. A **Story Generator** that decomposes narrative premises into structured 10-act outlines across 9 literary genres.
2. A **Screenplay Studio** that generates and formats multi-scene scripts following Hollywood Courier screenplay standards.
3. A **Character Studio** that synthesizes 19-dimensional psychological character bibles and ensemble candidate variations.
4. An **AI Writing Assistant** providing in-workspace style rewriting, multilingual translation (English as default; optional Telugu, Tamil, and Hindi), text summarization, dialogue generation, and plot twists.
5. A **Project Portfolio & Document Export Engine** powered by SQLite and SQLAlchemy ORM, providing snapshot version control with 1-click restore, and streaming in-memory document exports in Plain Text (`.txt`), Adobe PDF (`.pdf` with ReportLab and embedded `NirmalaUI` Indic TrueType font), and Microsoft Word (`.docx`).
6. A **Retrieval-Augmented Generation (RAG) & Vector Knowledge Engine** integrating ChromaDB and Sentence Transformers (`intfloat/multilingual-e5-small`) to index and ground storytelling, screenplays, character bibles, and writing assistant tools in verified canon rules, character dossiers, and worldbuilding lore with project-level isolation.

The software has been rigorously evaluated through an automated test suite of **335 test cases** achieving a 100% pass rate in 17.64 seconds, complemented by automated headless Google Chrome browser audits with zero runtime console errors. The resulting platform delivers an accessible, robust, and academically rigorous creative writing workstation for modern narrative artists.

---

## TABLE OF CONTENTS

| Chapter No. | Title |
|---|---|
| 1 | Title Page |
| 2 | Certificate |
| 3 | Declaration |
| 4 | Acknowledgement |
| 5 | Abstract |
| 6 | Table of Contents |
| 7 | Introduction |
| 8 | Problem Statement |
| 9 | Objectives |
| 10 | Existing System |
| 11 | Proposed System |
| 12 | Literature Survey |
| 13 | Feasibility Study |
| 14 | System Requirements |
| 15 | Software Requirements |
| 16 | Hardware Requirements |
| 17 | System Architecture |
| 18 | Module Description |
| 19 | Database Design |
| 20 | Entity-Relationship (ER) Diagram |
| 21 | Data Flow Diagrams (Level 0 and Level 1) |
| 22 | UML Diagrams (Use Case, Sequence, Activity) |
| 23 | Technology Stack & Rationale |
| 24 | Implementation Details |
| 25 | User Interface & Design System |
| 26 | Testing Methodology |
| 27 | Test Cases and Automated Results |
| 28 | Results and Discussion |
| 29 | Limitations |
| 30 | Future Enhancements |
| 31 | Conclusion |
| 32 | References |

---

## 7. INTRODUCTION

Narrative art is central to human communication, literature, and cinema. However, creative writing and screenwriting involve intense cognitive overhead: maintaining character motivations across dozens of scenes, adhering to industry formatting standards (such as screenplay sluglines, centered character cues, and parentheticals), and managing multi-draft revisions.

The emergence of Generative Artificial Intelligence and Transformer-based Large Language Models provides unprecedented opportunities to assist human writers. Rather than replacing the author, generative models serve as collaborative creative catalysts. However, harnessing these models requires specialized software architecture: disciplined prompt engineering, robust input validation, output parsing, snapshot version tracking, and native document generation.

**StoryVerse AI** was developed to bridge the gap between raw LLM capabilities and practical creative workflows. Operating as an end-to-end creative workstation, the platform enables authors, screenwriters, and literature students to ideate, draft, refine, preserve, and export narrative works seamlessly.

---

## 8. PROBLEM STATEMENT

Despite widespread access to general-purpose AI conversational tools (such as ChatGPT or basic LLM wrappers), creative writers encounter severe practical limitations:
1. **Lack of Narrative Structure:** Generalist conversational models output monolithic text without act pacing, dramatic tension arcs, or multi-scene continuity.
2. **Strict Screenplay Formatting Deficits:** Novice writers lack access to expensive dedicated screenplay software (e.g. Final Draft) and struggle to format standard sluglines (`INT./EXT.`), character cues, and parentheticals.
3. **Absence of Regional Indic Language Support:** Most writing tools are English-centric, offering poor typography or translation fidelity for major regional languages such as Telugu, Tamil, and Hindi.
4. **Data Ephemerality & Lack of Snapshot Control:** Conversations with typical AI chatbots vanish or drift over time. There is no automated snapshot version control to compare drafts or revert to earlier narrative variations.
5. **Format Trapping:** Creative drafts generated in web tools cannot be directly exported into publication-ready files (such as Adobe PDF with running headers and page numbers, or Microsoft Word `.docx`) with native Unicode typography.

---

## 9. OBJECTIVES

The primary engineering objectives of the StoryVerse AI platform include:
1. **Modular AI Pipeline Architecture:** Design a provider-agnostic AI integration layer using the official Google Gen AI SDK with fallback to deterministic mock providers for offline testing.
2. **Automated 10-Act Story Decomposition:** Implement a structured story engine that decomposes premises into 10 dramatic acts across 9 genres.
3. **Hollywood Screenplay Engine:** Build an automated screenplay formatting engine utilizing monospace Courier Prime typography with centered character cues and slugline recognition.
4. **19-Dimensional Character Synthesis:** Create a character generator that synthesizes detailed 19-point psychological matrices and ensemble candidate concepts.
5. **Interactive Writing Assistant:** Provide in-workspace style rewriting, Indic translation, summarization, natural dialogue generation, and plot-twist synthesis.
6. **Relational Persistence & Version Control:** Implement an SQLite database via SQLAlchemy ORM with foreign-key cascade deletion, snapshot creation, and 1-click version restoration.
7. **In-Memory Streaming Document Exports:** Deliver instant binary downloads for `.txt`, `.pdf` (with ReportLab two-pass `NumberedCanvas` and embedded Indic fonts), and `.docx` (via `python-docx`).
8. **Comprehensive Quality Assurance:** Verify 100% of functional paths using an automated regression test suite exceeding 250 tests and headless browser audits.

---

## 10. EXISTING SYSTEM

Conventional approaches to digital creative writing rely on two disparate categories:
1. **General Chatbot Interfaces (e.g. ChatGPT, Claude web interfaces):**
   - *Strengths:* Flexible natural language understanding.
   - *Weaknesses:* Monolithic outputs; zero screenplay typography; no database portfolio; loss of work on browser refresh; no multi-version restoration; no direct PDF/Word export.
2. **Traditional Screenwriting Software (e.g. Final Draft, Scrivener):**
   - *Strengths:* Industry formatting standards.
   - *Weaknesses:* Expensive proprietary licensing; zero generative AI integration; steep learning curve; lack of automated character psychology synthesis.

---

## 11. PROPOSED SYSTEM

StoryVerse AI combines the generative intelligence of state-of-the-art LLMs with the structured discipline of dedicated authoring suites.

### Key Innovations of the Proposed System:
- **Decoupled Client-Server Architecture:** Lightweight HTML5/CSS3/ES6 frontend communicating via REST JSON with a modular Python Flask backend.
- **Provider Abstraction Layer:** Enables seamless switching between live Google Gemini (`gemini-2.5-flash`) and an internal `MockAIProvider` for test isolation.
- **Multi-Modal Narrative Decomposition:** Structured parsers break raw text into act accordions, screenplay scene cards, and psychological matrix quadrants.
- **Snapshot Revision Engine:** Every save or update records an immutable history snapshot, enabling 1-click historical restoration.
- **In-Memory Multi-Format Export:** Binary generation of TXT, PDF (Page X of Y), and DOCX without creating temporary server files.

---

## 12. LITERATURE SURVEY

1. **Vaswani et al. (2017) — "Attention Is All You Need":** Established the Transformer deep learning architecture. Self-attention mechanisms enable neural networks to process long-range contextual relationships, forming the foundation of modern Large Language Models.
2. **Brown et al. (2020) — "Language Models are Few-Shot Learners":** Demonstrated that scaling autoregressive models enables few-shot in-context learning. This underpins our approach of structured system instructions and delimiter-guided prompt engineering.
3. **Field, Syd (2005) — "Screenplay: The Foundations of Screenwriting":** Defined standard three-act dramatic structure and screenplay formatting standards (sluglines, character dialogue margins), which our screenplay parser and prompt rules programmatically emulate.
4. **McKee, Robert (1997) — "Story: Substance, Structure, Style and the Principles of Screenwriting":** Explores character psychology, distinguishing between external "Want" and internal "Need", directly implemented in our 19-dimensional character profile matrix.

---

## 13. FEASIBILITY STUDY

### 13.1 Technical Feasibility
Python 3.11, Flask 3.0, and SQLAlchemy 2.0 provide a mature, stable backend ecosystem. Google's Gen AI Python SDK provides official, stable access to Gemini 2.5 Flash models. ReportLab and python-docx offer robust programmatic document generation. The system operates on standard personal computers without specialized GPU hardware.

### 13.2 Operational Feasibility
The platform features an intuitive, zero-install web interface. Users interact via standard browser forms, buttons, and responsive controls. The inclusion of a mock provider ensures operational independence even when internet connectivity or API quota is unavailable.

### 13.3 Economic Feasibility
The entire software stack is built using open-source frameworks (Flask, SQLite, ReportLab, Vanilla JS). Google AI Studio provides generous free-tier API quotas for Gemini models. Storage and computational requirements are minimal, resulting in zero software licensing expenses.

---

## 14. SYSTEM REQUIREMENTS

The system requires a distributed client-server environment capable of handling HTTP REST communication, in-memory binary buffering, and relational database operations.

---

## 15. SOFTWARE REQUIREMENTS

- **Operating System:** Windows 10/11, macOS 12+, or modern Linux (Ubuntu 22.04 LTS).
- **Backend Language & Framework:** Python 3.11+, Flask 3.0.3, Werkzeug 3.0.3.
- **Database Engine:** SQLite 3 with SQLAlchemy 2.0 / Flask-SQLAlchemy 3.1.
- **Vector Database (RAG):** ChromaDB 1.5.x (HNSW Cosine Metric Indexing).
- **Embedding Models:** Sentence Transformers 6.2.x (`intfloat/multilingual-e5-small` 384-dimensional dense vectors with query/passage prefixing across 100+ languages including English, Telugu, Tamil, and Hindi).
- **AI SDK:** `google-genai` (Official Google Gen AI Python SDK).
- **Document Generation:** ReportLab 4.2.5, `python-docx` 1.1.2.
- **Testing Framework:** `pytest` 8.3.3, `pytest-flask` 1.3.0.
- **Frontend Technologies:** HTML5, CSS3 Custom Properties (Variables), ECMAScript 6+ Vanilla JavaScript.
- **Web Browser:** Any modern evergreen browser (Chrome, Edge, Firefox, Safari).

---

## 16. HARDWARE REQUIREMENTS

- **Processor:** Dual-Core x86_64 or ARM64 CPU (2.0 GHz or higher).
- **RAM:** Minimum 4 GB (8 GB recommended for development and automated testing).
- **Storage:** Minimum 500 MB free hard disk space.
- **Network Interface:** Standard Ethernet or Wi-Fi adapter (required for live Gemini API calls).

---

## 17. SYSTEM ARCHITECTURE

The application adopts a 5-tier modular architecture:
1. **Presentation Layer (Frontend):** 6 responsive HTML5 pages with dedicated JavaScript controllers communicating with `api.js`.
2. **REST Routing Layer (Flask Blueprints):** 7 modular route files providing request validation, error masking, and HTTP status codes.
3. **Service Layer (Business Logic):** Stateless service classes (`StoryService`, `ScriptService`, `CharacterService`, `WritingAssistantService`, `ProjectService`, `ExportService`).
4. **AI Abstraction Layer:** `BaseAIProvider` interface with `GeminiProvider` and `MockAIProvider` implementations.
5. **Persistence Layer:** SQLite database managed through SQLAlchemy ORM models with cascade deletion.

---

## 18. MODULE DESCRIPTION

### 18.1 Module 1: Story Generator
Generates multi-act structured stories based on user parameters (Topic, Genre, Language, Tone, Length, Audience). Includes regex-based act parsers, sensory detail expansion (`/api/expand`), narrative shortening (`/api/shorten`), and narrative continuation (`/api/continue`).

### 18.2 Module 2: Screenplay Studio
Formats scripts according to Hollywood industry conventions in Courier Prime monospace typography. Identifies sluglines (`INT./EXT.`), uppercase centered character cues, parentheticals, and dialogue blocks. Supports single-scene additions (`/api/generate-scene`).

### 18.3 Module 3: Character Studio
Generates comprehensive 19-dimensional psychological character bibles and multi-concept ensemble variations (`/api/generate-character-variations`).

### 18.4 Module 4: AI Writing Assistant
In-editor writing suite featuring:
- Style Rewriting (6 selectable modes).
- Indic Translation (English, Telugu, Tamil, Hindi).
- Summarization (Short, Medium, Detailed).
- Contextual Dialogue Generation.
- Unexpected Plot Twist Generation.
- Narrative Continuation.

### 18.5 Module 5: Project Management & Export Engine
Manages project CRUD operations, multi-field search/filtering/sorting, explicit version snapshots, and 1-click snapshot restoration. Delivers in-memory streaming exports in TXT, PDF (ReportLab with `NirmalaUI` font), and DOCX (`python-docx`).

### 18.6 Module 6: Retrieval-Augmented Generation (RAG) & Vector Engine
Provides persistent domain grounding to eliminate generative hallucination across extended storytelling:
- **Document Ingestion & Chunking:** Ingests canon rules, character dossiers, worldbuilding bibles, and historical context; parses content into coherent chunks respecting paragraph and sentence boundaries with configurable overlap.
- **Multilingual Vector Embeddings:** Encodes text passages into 384-dimensional dense vectors using Sentence Transformers (`intfloat/multilingual-e5-small`) with query/passage prefixing and genuine semantic retrieval support for English, Telugu, Tamil, and Hindi.
- **ChromaDB Vector Store:** Houses persistent vector embeddings indexed with Hierarchical Navigable Small World (HNSW) graphs under cosine distance metrics.
- **Metadata Filtering & Project Lore Isolation:** Filters search space by `genre`, `language`, `doc_type`, and isolates private project lore (`project_id`) while allowing global lore sharing across projects.
- **Prompt Grounding Integration:** Constructs standardized ground-truth instruction blocks injected into Story, Script, Character, and Writing Assistant prompts, with automated tests proving that retrieved lore is physically present in generative prompts.


---

## 19. DATABASE DESIGN

The relational schema is implemented in SQLite 3 with two primary tables:

### Table 1: `project`
- `id` (INTEGER, Primary Key, Auto Increment)
- `title` (VARCHAR(200), Not Null)
- `content_type` (VARCHAR(50), Not Null: `story` | `script` | `character` | `other`)
- `genre` (VARCHAR(50), Nullable)
- `language` (VARCHAR(50), Default 'English')
- `tone` (VARCHAR(50), Nullable)
- `target_audience` (TEXT, Nullable)
- `generated_content` (TEXT, Not Null)
- `prompt_used` (TEXT, Nullable)
- `description` (TEXT, Nullable)
- `word_count` (INTEGER, Default 0)
- `created_at` (DATETIME, Default UTC Now)
- `updated_at` (DATETIME, Default UTC Now)

### Table 2: `generation_history`
- `id` (INTEGER, Primary Key, Auto Increment)
- `project_id` (INTEGER, Foreign Key -> `project.id` ON DELETE CASCADE, Not Null)
- `action` (VARCHAR(50), Default 'created')
- `prompt` (TEXT, Nullable)
- `result` (TEXT, Not Null)
- `change_summary` (TEXT, Nullable)
- `word_count` (INTEGER, Default 0)
- `created_at` (DATETIME, Default UTC Now)

---

## 20. ENTITY-RELATIONSHIP (ER) DIAGRAM

A 1-to-Many relationship exists between `PROJECT` and `GENERATION_HISTORY`. One project can have zero or many historical version snapshots. When a project is deleted, all associated history rows are automatically removed via database cascading.

*(Refer to `docs/diagrams/ALL_DIAGRAMS.md` for complete visual Mermaid diagram.)*

---

## 21. DATA FLOW DIAGRAMS

- **DFD Level 0 (Context Level):** Represents the boundary of StoryVerse AI interacting with external entities (Users, Google Gemini API, and Persistent Storage).
- **DFD Level 1 (Subsystem Decomposition):** Breaks down the core process into 5 sub-processes: Input Validation, Prompt Engineering, Model Execution, State Management, and Document Export.

*(Refer to `docs/diagrams/ALL_DIAGRAMS.md` for complete visual Mermaid diagrams.)*

---

## 22. UML DIAGRAMS

- **Use Case Diagram:** Depicts the actor (Writer/Student) executing 12 core operations including generation, refinement, portfolio management, version restoration, and document exporting.
- **Sequence Diagrams:** Chronological object interaction traces for Story Generation & Expansion and Project Version Restoration.
- **Activity Diagram:** Decision flow covering validation, loading animations, mock/live provider routing, error handling, and document export.

*(Refer to `docs/diagrams/ALL_DIAGRAMS.md` for complete visual Mermaid diagrams.)*

---

## 23. TECHNOLOGY STACK & RATIONALE

- **Python & Flask:** Offers unmatched NLP library support, rapid prototyping, and clean Blueprint modularity without monolithic overhead.
- **Google Gemini Generative AI:** State-of-the-art context window, high reasoning capability, and superior multilingual comprehension for Indic languages.
- **SQLAlchemy ORM:** Guarantees database portability, automated migration safety, and protection against SQL injection attacks.
- **ReportLab & python-docx:** Mature, industry-standard programmatic document rendering engines.
- **Vanilla JavaScript:** High-performance browser execution, zero build steps, and complete immunity to frontend dependency vulnerabilities.

---

## 24. IMPLEMENTATION DETAILS

### 24.1 AI Provider Factory & Error Masking
The `get_ai_provider()` factory dynamically returns either `GeminiProvider` or `MockAIProvider` based on environment variables (`AI_MOCK_MODE`). All API exceptions (HTTP 429 rate limits, 504 timeouts, 502 network errors) are intercepted, scrubbed of API keys, and returned as standardized JSON envelopes.

### 24.2 Indic Unicode Typography in PDF Export
ReportLab relies on Type 1 fonts by default, which cannot render complex South Asian scripts. In `ExportService`, we register the TrueType Collection `Nirmala.ttc` from `C:\WINDOWS\Fonts\Nirmala.ttc` (subfont index 0: `NirmalaUI`). This provides native typographic rendering for Telugu (తెలుగు), Tamil (தமிழ்), and Hindi (हिंदी).

### 24.3 Security & Input Sanitization
- All client-side text rendering is executed via `element.textContent` to prevent XSS.
- All export filenames are sanitized via regex `[^a-zA-Z0-9_\-\. ]` to prevent path traversal (`../../`).
- Database operations utilize SQLAlchemy parameterized statements to prevent SQL injection.

---

## 25. USER INTERFACE & DESIGN SYSTEM

The presentation layer utilizes a modern, accessible design system:
- **Responsive Layout:** CSS Flexbox and Grid layouts optimized for desktop, tablet, and mobile displays.
- **Dark & Light Mode:** Managed via CSS variables (`--bg-primary`, `--surface`, `--text-primary`) and `theme.js` using `localStorage`.
- **Feedback & States:** Clapperboard and quill spinner overlays, non-blocking toast notifications, and empty state placeholders.

---

## 26. TESTING METHODOLOGY

Testing was conducted across four structured tiers:
1. **Unit Testing:** Validating schema bounds, field types, and enumerations in `test_validators.py`.
2. **Component & Service Testing:** Testing isolated parsing logic and mock AI provider responses.
3. **Integration & E2E Testing:** Programmatic verification of full user workflows across all 21 REST endpoints.
4. **Browser Testing:** Headless Google Chrome execution auditing DOM rendering, asset resolution, and console error logs.

---

## 27. TEST CASES AND AUTOMATED RESULTS

The complete automated regression suite was executed using `pytest 8.3.3` on Python 3.14:

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-8.3.3, pluggy-1.7.0 -- python.exe
collected 335 items

tests/test_ai_assistant.py ............................................. [ 14%]
......                                                                   [ 15%]
tests/test_characters.py ..............................                  [ 24%]
tests/test_database.py .............                                     [ 28%]
tests/test_exports.py ...................                                [ 34%]
tests/test_health.py .........                                           [ 37%]
tests/test_integration_e2e.py ..............                             [ 41%]
tests/test_projects.py ...................................               [ 51%]
tests/test_rag.py ..............................                         [ 60%]
tests/test_script.py ..................................                  [ 70%]
tests/test_story.py .........................                            [ 78%]
tests/test_validators.py .........................                       [ 85%]
tests/test_writing_assistant.py ........................................ [ 97%]
..........                                                               [100%]

============================ 335 passed in 17.64s =============================
```

- **Total Test Cases:** 335
- **Passed:** 335 (100% Pass Rate)
- **Failed:** 0
- **Regressions:** 0

---

## 28. RESULTS AND DISCUSSION

The experimental results validate that StoryVerse AI meets all engineering and creative objectives:
- **Structural Integrity:** Stories consistently output 10 structured acts, scripts consistently format sluglines and dialogue cues, and characters conform to 19 psychological dimensions.
- **Persistence & Auditability:** Full version history trails are recorded automatically upon project creation, manual saving, and version restoration.
- **Export Fidelity:** Document streams generate valid `.txt`, `.pdf` (with "Page X of Y" and Unicode Indic characters), and `.docx` files streamed directly to browser downloads without disk latency.

---

## 29. LIMITATIONS

1. **AI Quota & Network Dependency:** Live Gemini mode requires active internet and valid Google AI Studio credentials (mitigated by the offline Mock AI Provider).
2. **Linux Font Fallback:** In non-Windows Linux servers without pre-installed Indic fonts, ReportLab PDFs gracefully fall back to standard Latin typography (mitigated via containerized Docker font packages).
3. **Single-User Architecture:** Designed as an author's personal creative workstation without multi-user tenant login.

---

## 30. FUTURE ENHANCEMENTS

1. **Multimodal Concept Art:** Integrating Gemini image generation models to generate character concept art and visual storyboards.
2. **Voice Narration & Speech-to-Script:** Adding text-to-speech audio narration and real-time voice dictation.
3. **Collaborative Cloud Synchronization:** Real-time multi-user collaborative editing via WebSockets and cloud database persistence.
4. **Final Draft (`.fdx`) Export:** Adding native `.fdx` XML export for direct compatibility with professional screenwriting hardware.

---

## 31. CONCLUSION

The **StoryVerse AI** project successfully demonstrates the design, implementation, and evaluation of an advanced generative AI platform tailored for literature and cinema. By harmonizing Google Gemini LLM intelligence with disciplined prompt engineering, screenplay typesetting standards, Indic multilingual typography, relational version snapshotting, and publication-ready multi-format document exporting, the application elevates AI from a generic conversational chatbot into a professional creative workstation.

With **285 passing automated test cases**, production-ready containerization, and zero-defect browser execution, StoryVerse AI represents a comprehensive, technically sound, and academically rigorous final-year Computer Science project.

---

## 32. REFERENCES

1. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). "Attention Is All You Need." *Advances in Neural Information Processing Systems (NeurIPS 2017)*, 30, 5998–6008.
2. Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J. D., Dhariwal, P., ... & Amodei, D. (2020). "Language Models are Few-Shot Learners." *Advances in Neural Information Processing Systems (NeurIPS 2020)*, 33, 1877–1901.
3. Field, Syd. (2005). *Screenplay: The Foundations of Screenwriting*. Delta Trade Paperbacks, New York.
4. McKee, Robert. (1997). *Story: Substance, Structure, Style and the Principles of Screenwriting*. HarperCollins, New York.
5. Grinberg, Miguel. (2018). *Flask Web Development: Developing Web Applications with Python*. O'Reilly Media, 2nd Edition.
6. Bayer, Mike. (2020). *SQLAlchemy Documentation and Architectural Guide*. SQLAlchemy Authors.
7. ReportLab Europe Ltd. (2024). *ReportLab PDF Generation User Guide*. Version 4.x Documentation.
8. Google DeepMind & Google Cloud. (2024). *Google Gen AI SDK and Gemini Model Documentation*. Google AI Studio.
