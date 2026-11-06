# StoryVerse AI — Complete System Diagrams
**Project:** Story and Script Generator Using Generative AI  
**Academic Role:** Final Year B.Tech Computer Science Project  
**Date:** November 2026  

---

## 1. System Architecture Diagram

This diagram visualizes the multi-tier client-server architecture of StoryVerse AI, illustrating the presentation layer, the REST routing layer, application services, persistence, and external AI integrations.

```mermaid
flowchart TD
    subgraph ClientLayer["Presentation Layer (Client Browser)"]
        UI_Home["Landing Portal (index.html)"]
        UI_Story["Story Generator (story.html)"]
        UI_Script["Screenplay Studio (script.html)"]
        UI_Char["Character Studio (characters.html)"]
        UI_Dash["Project Portfolio (dashboard.html)"]
        UI_Editor["Workspace Editor (editor.html)"]
        API_JS["Client API Connector (api.js)"]
    end

    subgraph APILayer["REST Routing & Security Layer (Flask)"]
        CORS["CORS Protection & Limiter"]
        Val["Input Validators & Sanitizers"]
        HealthBP["/api/health"]
        StoryBP["/api/generate-story, /expand, /continue"]
        ScriptBP["/api/generate-script, /generate-scene"]
        CharBP["/api/generate-character, /variations"]
        AssistBP["/api/rewrite, /translate, /summarize"]
        ProjBP["/api/projects, /versions, /restore"]
        ExportBP["/api/export/txt, /pdf, /docx"]
        RagBP["/api/rag/ingest, /documents, /query, /status"]
    end

    subgraph ServiceLayer["Business Logic & Service Layer"]
        StorySvc["StoryService"]
        ScriptSvc["ScriptService (Hollywood Formatter)"]
        CharSvc["CharacterService (19-Pt Parser)"]
        AssistSvc["WritingAssistantService"]
        ProjSvc["ProjectService (Version Manager)"]
        ExportSvc["ExportService (ReportLab & docx)"]
        PromptSvc["PromptService (Indic & Creative Templates)"]
        AISvc["AIService (Model Orchestrator)"]
        RAGSvc["RAGService (Chunking & Context Retrieval)"]
        EmbedSvc["EmbeddingService (multilingual-e5-small)"]
    end

    subgraph ProviderLayer["AI Integration Layer"]
        AI_Factory["get_ai_provider() Factory"]
        GeminiProv["GeminiProvider (Google Gen AI SDK)"]
        MockProv["MockAIProvider (Deterministic Testing)"]
    end

    subgraph PersistenceLayer["Data & Persistence Layer"]
        ORM["SQLAlchemy ORM"]
        DB[(SQLite Database: storyverse.db)]
        ProjTable["Project Table"]
        HistTable["GenerationHistory Table"]
        ChromaDB[(ChromaDB Vector Store: HNSW Cosine Index)]
    end

    UI_Story --> API_JS
    UI_Script --> API_JS
    UI_Char --> API_JS
    UI_Dash --> API_JS
    UI_Editor --> API_JS

    API_JS --> CORS
    CORS --> Val
    Val --> HealthBP
    Val --> StoryBP
    Val --> ScriptBP
    Val --> CharBP
    Val --> AssistBP
    Val --> ProjBP
    Val --> ExportBP
    Val --> RagBP

    StoryBP --> StorySvc
    ScriptBP --> ScriptSvc
    CharBP --> CharSvc
    AssistBP --> AssistSvc
    ProjBP --> ProjSvc
    ExportBP --> ExportSvc
    RagBP --> RAGSvc

    StorySvc --> RAGSvc
    ScriptSvc --> RAGSvc
    RAGSvc --> EmbedSvc
    RAGSvc --> ChromaDB

    StorySvc --> PromptSvc
    ScriptSvc --> PromptSvc
    CharSvc --> PromptSvc
    AssistSvc --> PromptSvc

    StorySvc --> AISvc
    ScriptSvc --> AISvc
    CharSvc --> AISvc
    AssistSvc --> AISvc

    AISvc --> AI_Factory
    AI_Factory --> GeminiProv
    AI_Factory --> MockProv

    ProjSvc --> ORM
    ExportSvc --> ORM
    ORM --> DB
    DB --- ProjTable
    DB --- HistTable
```

---

## 2. Use Case Diagram

Visualizes user interactions across creative generation, workspace editing, portfolio management, and multi-format document exporting.

```mermaid
flowchart LR
    User(("Creative Writer / Student"))

    subgraph StoryVerse["StoryVerse AI Platform"]
        UC1["Configure Parameters & Generate Story"]
        UC2["Refine Story (Expand / Shorten / Continue)"]
        UC3["Generate Multi-Scene Screenplay"]
        UC4["Generate Individual Screenplay Scene"]
        UC5["Generate 19-Pt Character Bible"]
        UC6["Generate Character Ensemble Variations"]
        UC7["AI Writing Tools (Rewrite, Translate, Summarize)"]
        UC8["Dialogue & Plot Twist Generation"]
        UC9["Save Creative Work to Portfolio"]
        UC10["Inspect Version History & Restore Snapshot"]
        UC11["Export Document (TXT / PDF / DOCX)"]
        UC12["Search, Filter & Sort Projects"]
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
    User --> UC9
    User --> UC10
    User --> UC11
    User --> UC12
```

---

## 3. Entity-Relationship (ER) Diagram

Details database entities, data types, primary keys, foreign keys, and relationship cardinalities between `project` and `generation_history`.

```mermaid
erDiagram
    PROJECT ||--o{ GENERATION_HISTORY : "maintains version snapshots"
    
    PROJECT {
        int id PK "Auto-incrementing Unique Identifier"
        string title "Project Headline / Title (max 200 chars)"
        string content_type "Type: story | script | character | other"
        string genre "Narrative Genre (Fantasy, Sci-Fi, etc.)"
        string language "Language (English, Telugu, Tamil, Hindi)"
        string tone "Atmospheric Tone (Suspenseful, Emotional, etc.)"
        text target_audience "Target Demographic"
        text generated_content "Current Working Manuscript / Content"
        text prompt_used "Originating Creative Prompt"
        text description "Logline or Brief Summary"
        int word_count "Calculated Length Metrics"
        datetime created_at "Initial Creation Timestamp"
        datetime updated_at "Last Modified Timestamp"
    }

    GENERATION_HISTORY {
        int id PK "Auto-incrementing Snapshot Identifier"
        int project_id FK "References project(id) ON DELETE CASCADE"
        string action "Action: created | updated | expanded | restored"
        text prompt "Prompt executed during generation"
        text result "Snapshot of full generated content"
        text change_summary "Changelog note explaining modification"
        int word_count "Word count at time of snapshot"
        datetime created_at "Snapshot Recording Timestamp"
    }
```

---

## 4. Data Flow Diagram (DFD) Level 0 — Context Diagram

Illustrates the boundary of StoryVerse AI with external entities (User and Generative AI Model).

```mermaid
flowchart LR
    User(("Writer / User"))
    System["StoryVerse AI Core System (Process 0.0)"]
    AI["Google Gemini AI Service"]
    Storage[("Local SQLite Database & File Streams")]

    User -- "1. Creative Prompts & Parameters" --> System
    User -- "2. Project Edits, Filters & Version Restores" --> System
    System -- "3. Prompt Assembly (Indic Rules & Templates)" --> AI
    AI -- "4. Raw Text Generation Stream" --> System
    System -- "5. Formatted Stories, Scripts, Bibles & Exports" --> User
    System -- "6. Read / Write Project Snapshots" --> Storage
    Storage -- "7. Saved Projects & Audit History" --> System
```

---

## 5. Data Flow Diagram (DFD) Level 1 — Subsystem Breakdown

Decomposes the Level 0 process into specific functional sub-processes.

```mermaid
flowchart TD
    User(("User"))
    AI["Google Gemini AI"]
    DB[("SQLite Database")]

    P1["1.0 Input Validation & Sanitization"]
    P2["2.0 Prompt Engineering & Context Assembly"]
    P3["3.0 Model Execution & Response Parsing"]
    P4["4.0 Project & Version State Management"]
    P5["5.0 Document Export Engine (PDF, DOCX, TXT)"]

    User -- "Form Inputs (Genre, Premise, Lang)" --> P1
    P1 -- "Cleaned Parameters" --> P2
    P2 -- "Engineered Prompt" --> P3
    P3 -- "API Request" --> AI
    AI -- "Raw Generation" --> P3
    P3 -- "Structured Story / Script / Character" --> User
    
    User -- "Save / Update / Restore" --> P4
    P3 -- "Content to Persist" --> P4
    P4 -- "CRUD & Version History" --> DB
    DB -- "Retrieved Portfolio" --> P4
    P4 -- "Project Records" --> User

    User -- "Export Request (Format & ID)" --> P5
    P4 -- "Manuscript Content" --> P5
    P5 -- "Streamed Binary File Download" --> User
```

---

## 6. Activity Diagram — Creative Generation Workflow

Visualizes decision logic and operational branches during story/script generation.

```mermaid
flowchart TD
    Start([User Begins Generation]) --> Input[Fill in Premise, Genre, Language, Tone]
    Input --> Validate{Validate Input Schema?}
    
    Validate -- "Validation Failed" --> ErrMsg[Display Inline Field Errors & Toast]
    ErrMsg --> Input

    Validate -- "Input Valid" --> Load[Show Loading State & Clapperboard Animation]
    Load --> BuildPrompt[Build Structured Prompt with Indic & Formatting Rules]
    BuildPrompt --> CheckProv{Select AI Provider}

    CheckProv -- "AI_MOCK_MODE=true" --> ExecMock[Generate Deterministic Mock Content]
    CheckProv -- "AI_MOCK_MODE=false" --> ExecGemini[Execute Google Gen AI SDK Call]

    ExecGemini --> CheckAPI{API Response OK?}
    CheckAPI -- "Rate Limit (429) / Timeout (504)" --> APIErr[Handle Error Gracefully & Show User Toast]
    APIErr --> Stop([End Turn])

    CheckAPI -- "Success" --> ParseResp[Parse Content into Structured Dimensions]
    ExecMock --> ParseResp

    ParseResp --> Render[Render Dynamic UI: Badges, Scenes, Character Cards]
    Render --> Options{User Next Action}

    Options -- "Refine / Expand" --> Expand[Trigger /api/expand or /api/generate-scene]
    Expand --> Load

    Options -- "Save to Database" --> SaveDB[POST /api/projects]
    SaveDB --> Toast[Display Success Toast & Project ID]

    Options -- "Export Document" --> Export[Trigger /api/export/{fmt}]
    Export --> Download[Trigger In-Memory Browser File Download]

    Toast --> End([Complete])
    Download --> End
```

---

## 7. Sequence Diagram — Story Generation & Expansion

Details the chronological message flow between client, routes, services, prompt builder, AI model, and database.

```mermaid
sequenceDiagram
    autonumber
    actor User as Writer (Browser)
    participant UI as story.html / story.js
    participant API as api.js
    participant Route as story_routes.py
    participant Svc as StoryService
    participant Prompt as PromptService
    participant AI as GeminiProvider / MockProvider
    participant DB as SQLite DB

    User->>UI: Clicks "Generate Full Story"
    UI->>UI: Validates premise & activates spinner
    UI->>API: generateStory(payload)
    API->>Route: POST /api/generate-story
    Route->>Svc: generate_story(data)
    Svc->>Prompt: build_story_prompt(topic, genre, lang, ...)
    Prompt-->>Svc: Engineered prompt with 10-act structure
    Svc->>AI: call_ai_model(prompt)
    AI-->>Svc: Generated story text
    Svc->>Svc: parse_story_acts(text)
    Svc-->>Route: Formatted story dictionary
    Route-->>API: 200 OK {"success": true, "data": {...}}
    API-->>UI: Response data
    UI->>User: Displays structured acts, synopsis & manuscript

    opt User Expands Story
        User->>UI: Clicks "Expand Story"
        UI->>API: expandStory(content, instructions)
        API->>Route: POST /api/expand
        Route->>Svc: expand_story(...)
        Svc->>AI: call_ai_model(expand_prompt)
        AI-->>Svc: Expanded story text
        Svc-->>Route: 200 OK with expanded text
        Route-->>UI: Updates manuscript display
    end

    opt User Saves to Project Portfolio
        User->>UI: Clicks "Save Project"
        UI->>API: createProject({title, content, type: "story"})
        API->>Route: POST /api/projects
        Route->>DB: INSERT INTO project & generation_history
        DB-->>Route: Generated project_id: #1
        Route-->>UI: 201 Created {"id": 1, ...}
        UI->>User: Shows "Saved to portfolio! Project #1"
    end
```

---

## 8. Sequence Diagram — Project Persistence & Version Snapshot

Details how workspace revisions, version snapshotting, and snapshot restoration function.

```mermaid
sequenceDiagram
    autonumber
    actor User as Writer (Editor)
    participant Editor as editor.html / editor.js
    participant API as api.js
    participant Route as project_routes.py
    participant Svc as ProjectService
    participant DB as SQLite DB

    User->>Editor: Edits manuscript in workspace
    User->>Editor: Clicks "Save Draft"
    Editor->>API: updateProject(project_id, {title, content})
    API->>Route: PUT /api/projects/<id>
    Route->>Svc: update_project(id, data)
    Svc->>DB: SELECT * FROM project WHERE id = ?
    Svc->>DB: INSERT INTO generation_history (action="updated", result=content)
    Svc->>DB: UPDATE project SET content = ..., updated_at = ...
    DB-->>Svc: Commit transaction
    Svc-->>Route: Updated project object
    Route-->>API: 200 OK
    API-->>Editor: Updated state
    Editor->>User: Displays "Project saved successfully"

    opt User Inspects & Restores Version Snapshot
        User->>Editor: Navigates to Dashboard -> "Versions"
        Editor->>API: getProjectVersions(project_id)
        API->>Route: GET /api/projects/<id>/versions
        Route->>DB: SELECT * FROM generation_history WHERE project_id = ? ORDER BY created_at DESC
        DB-->>Route: List of snapshots (v1, v2, v3)
        Route-->>Editor: 200 OK with snapshot history
        Editor->>User: Displays version modal with diff preview
        User->>Editor: Clicks "Restore Snapshot #1"
        Editor->>API: restoreProjectVersion(project_id, version_id)
        API->>Route: POST /api/projects/<id>/versions/<vid>/restore
        Route->>Svc: restore_version(project_id, version_id)
        Svc->>DB: UPDATE project SET content = snapshot.result
        Svc->>DB: INSERT INTO generation_history (action="restored")
        DB-->>Svc: Commit
        Svc-->>Editor: 200 OK
        Editor->>User: Content reverted to snapshot #1
    end
```

---

## 9. Deployment Architecture Diagram

Illustrates both local standalone deployment and containerized Docker production deployment.

```mermaid
flowchart TD
    subgraph ClientBrowser["Client Environment"]
        Browser["Web Browser (Chrome / Edge / Firefox)"]
    end

    subgraph ProductionContainer["Docker Containerized Infrastructure"]
        subgraph FrontendNginx["Frontend Web Container (Port 3000)"]
            Nginx["Nginx Alpine Web Server"]
            StaticAssets["HTML5 / Modern CSS / Vanilla JS"]
        end

        subgraph BackendGunicorn["Backend API Container (Port 5000)"]
            Gunicorn["Gunicorn WSGI HTTP Server (2 Workers, 4 Threads)"]
            FlaskCore["StoryVerse AI Flask Core (Python 3.11)"]
            FontEngine["System Indic Fonts (Nirmala / fonts-deva)"]
        end

        subgraph StorageVol["Persistent Container Volume"]
            DataVol[("Volume: backend_data (/app/instance)")]
            SQLiteFile["storyverse.db"]
        end
    end

    subgraph ExternalCloud["External Cloud Services"]
        GoogleAI["Google AI Studio (Gemini 2.5 Flash API)"]
    end

    Browser -- "HTTP :3000 (Loads UI)" --> Nginx
    Nginx -- "Serves Static Files" --> StaticAssets
    Browser -- "REST API Requests :5000/api/*" --> Gunicorn
    Gunicorn --> FlaskCore
    FlaskCore --> FontEngine
    FlaskCore -- "SQLAlchemy ORM" --> DataVol
    DataVol --- SQLiteFile
    FlaskCore -- "HTTPS / TLS (Official Google Gen AI SDK)" --> GoogleAI
```

---

## 10. RAG Retrieval & Prompt Grounding Sequence Diagram

Illustrates the end-to-end vector knowledge ingestion, semantic cosine similarity retrieval via ChromaDB and SentenceTransformers, and generative prompt grounding for Google Gemini.

```mermaid
sequenceDiagram
    autonumber
    actor User as Author / Student
    participant Browser as Client Browser (story.html)
    participant Flask as Flask REST API (/api/generate-story)
    participant StorySvc as StoryService
    participant RAG as RAGService
    participant Embed as EmbeddingService (multilingual-e5-small)
    participant Chroma as ChromaDB Vector Store
    participant PromptSvc as PromptService
    participant Gemini as GeminiProvider (Google Gemini API)

    User->>Browser: Enter Premise + Check "Enable RAG Knowledge Grounding"
    Browser->>Flask: POST /api/generate-story {topic, use_rag: true, genre, language}
    Flask->>StorySvc: generate_story(params)
    
    alt use_rag is True
        StorySvc->>RAG: retrieve_context(query=topic, n_results=3, genre, language)
        RAG->>Embed: encode_query(topic)
        Embed-->>RAG: 384-dimensional dense vector
        RAG->>Chroma: query(query_embeddings, n_results=3, where_filter)
        Chroma-->>RAG: Top matching lore chunks with cosine distance
        RAG-->>StorySvc: List of retrieved context chunks
        StorySvc->>PromptSvc: build_rag_context_block(retrieved_chunks)
        PromptSvc-->>StorySvc: Formatted ground-truth instruction block
    end

    StorySvc->>PromptSvc: build_story_prompt(params with rag_context)
    PromptSvc-->>StorySvc: Grounded prompt containing lore facts + mandatory directives
    StorySvc->>Gemini: call_ai_model(grounded_prompt)
    Gemini-->>StorySvc: Generated story strictly adhering to retrieved canon lore
    StorySvc->>StorySvc: parse_story_sections(raw_text)
    StorySvc-->>Flask: Complete story sections + retrieved_context chunks + metadata
    Flask-->>Browser: HTTP 200 OK (JSON response)
    Browser->>User: Displays structured story + RAG Knowledge Grounding Chips

