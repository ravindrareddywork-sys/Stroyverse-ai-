# FREE Deployment Feasibility Report — StoryVerse AI

## Executive summary

This project is structurally deployable on a free-tier Docker host, especially Hugging Face Spaces, but not as a fully production-grade multi-user service without some deployment-specific adjustments.

Verified facts from the codebase:
- The backend is a Flask application factory in [backend/app.py](../backend/app.py).
- The app uses SQLite via Flask-SQLAlchemy and local ChromaDB persistence for RAG.
- The app serves the frontend through Flask routes as well as static file delivery, while the frontend JavaScript points to a backend URL at `http://127.0.0.1:5000` by default.
- The backend Dockerfile already installs system fonts and Python dependencies, including `chromadb` and `sentence-transformers`.
- The project has no document upload endpoint or persistent user-file bucket integration at the moment.

The cheapest genuinely free architecture is:
- Hugging Face Spaces (free Docker container)
- Flask app as the single app container
- SQLite file database in a local persistent data directory
- ChromaDB in a local persistent directory
- Gemini API for generation, not built into the free app itself
- No Supabase / no Cloud Storage required for the current app shape

This is the cheapest viable free deployment, but it has real limits: storage is limited, the model may consume a large share of RAM, and database persistence is not guaranteed across rebuilds unless the host provides persistent disk or a managed service.

## 1. Requirements and system-level footprint

### Verified dependency list
From [backend/requirements.txt](../backend/requirements.txt):
- Flask 3.0.3
- Werkzeug 3.0.3
- flask-cors 4.0.1
- Flask-SQLAlchemy 3.1.1
- SQLAlchemy 2.0.35
- Flask-Limiter 3.8.0
- python-dotenv 1.0.1
- google-genai >= 1.0.0
- reportlab 4.2.5
- python-docx 1.1.2
- chromadb >= 1.5.0
- sentence-transformers >= 3.0.0
- pytest 8.3.3
- pytest-flask 1.3.0
- gunicorn 23.0.0

### System-level requirements and package size
Verified by the project configuration:
- The Dockerfile installs system fonts: `fonts-deva`, `fonts-telu`, `fonts-taml`.
- The app expects Python 3.11 in Docker.
- The service uses ReportLab and `python-docx` for document export.
- The app also depends on `chromadb` and `sentence-transformers`, which are significantly heavier than pure Flask packages.

Estimated footprint (not exact, because package sizes depend on OS and cache state):
- Base Python runtime + Flask stack: small to moderate
- `sentence-transformers` + model download: typically several hundred MB to ~1 GB RAM while loaded
- `chromadb`: moderate, often tens to hundreds of MB depending on version and metadata
- SQLite database: trivial in comparison
- Export libraries (`reportlab`, `python-docx`): small to moderate

Overall: this project is not a lightweight hello-world Flask app. It is a full AI + vector-search app and should be treated as a modest memory-intensive web service.

## 2. Database models and database initialization

### Verified database model files
From [backend/models/project.py](../backend/models/project.py):
- `Project` model
- Fields include: `id`, `title`, `content_type`, `genre`, `language`, `tone`, `topic`, `description`, `generated_content`, `created_at`, `updated_at`
- Relationship: one project has many `GenerationHistory` rows

From [backend/models/generation_history.py](../backend/models/generation_history.py):
- `GenerationHistory` model
- Fields include `project_id`, `operation`, `content_type`, `content_snapshot`, `input_summary`, `prompt`, `ai_model`, `tokens_used`, `created_at`
- Foreign key to `project.id` with cascade delete

From [backend/models/__init__.py](../backend/models/__init__.py):
- These models are explicitly imported so SQLAlchemy can discover them before `db.create_all()`.

### Verified database initialization
From [backend/extensions.py](../backend/extensions.py):
- `db = SQLAlchemy()`
- `cors = CORS()`
- `limiter = Limiter(...)`

From [backend/app.py](../backend/app.py):
- `db.init_app(app)`
- `db.create_all()` is run inside `create_app()`
- Safe migration logic checks for a missing `description` column on the `project` table and adds it if needed

### Verified database locations and configuration
From [backend/config.py](../backend/config.py):
- Default SQLite URI is `sqlite:///storyverse.db`.
- The app also creates `backend/instance/` directory automatically.
- The active database path is effectively local to the running container/service filesystem.

Important observation:
- In production mode, the app does not require a separate database server; SQLite is built into the app and is suitable for local or small-scale deploys.
- This design is the opposite of a managed database architecture, so it is not a production-ready replacement for a multi-user SaaS database layer.

## 3. SQLite database locations

Verified database-related paths in the project:
- SQLite file at project root: `instance/storyverse.db` (in the workspace snapshot)
- In the app, the database is typically created under the backend instance directory, such as `backend/instance/storyverse.db`
- This is local to the actual running environment; it is not a hosted database by default

The app also creates a local `generated_files` directory in the backend for exports and artifacts.

### Database practicality
SQLite is enough for:
- local demos
- single-user or very small-scale test deployments
- college-project use
- development and low concurrency use

SQLite is not ideal for:
- concurrent multi-user writes at scale
- automatic scaling
- remote database durability across multiple app instances
- robust backup/restore workflows without external management

## 4. Embedding service and RAG service

### Verified embedding implementation
From [backend/services/embedding_service.py](../backend/services/embedding_service.py):
- It uses `SentenceTransformer` lazily.
- Default model is `intfloat/multilingual-e5-small`.
- Token text is prefixed with `query:` or `passage:` for E5 compatibility.
- It defines a deterministic mock vector fallback when model loading fails.
- Embedding dimension is fixed at 384.

### Verified RAG storage implementation
From [backend/services/rag_service.py](../backend/services/rag_service.py):
- Uses `chromadb.PersistentClient(path=self.persist_directory)`
- Default persistence directory is `backend/instance/chroma_db`
- Uses a collection named `storyverse_knowledge_base`
- Metadata includes `document_id`, `document_title`, `doc_type`, `language`, `genre`, `project_id`, and `created_at`
- Lists, retrieves, and deletes document chunks using Chroma metadata filters
- Uses cosine distance (`hnsw:space`: `cosine`)

### Verified collection and persistence path
- Default collection name: `storyverse_knowledge_base`
- Default persist directory: backend/instance/chroma_db
- This keeps Chroma data local to the container filesystem, not in a managed cloud database

## 5. Multilingual E5 model loading and RAM estimate

### Verified facts from the code
- The configured model is `intfloat/multilingual-e5-small`.
- The embedding dimension is 384.
- The code does lazy loading through `SentenceTransformer(self.model_name)`.

### Reality and estimate
This is a sentence-transformers model and not a minimal library. The E5-small multilingual encoder is usually modest compared with large LLMs, but it is still a real ML model and not trivial on free-tier memory limits.

Estimated runtime memory use (not exact):
- Model weights + runtime overhead: often around 500 MB to 1.2 GB RAM while loaded
- Python + Chroma + Flask app: additional tens to a few hundred MB
- Total active memory in a free container: roughly 1.0 GB to 2.0 GB, depending on load and cache behavior

This means the app can fit into a free Hugging Face CPU container only if it is not under heavy parallel workload and the model is loaded once and reused. It is not a good fit for a free environment if the app is expected to serve many simultaneous AI requests or a large RAG corpus at the same time.

## 6. Document upload, file storage, and export implementation

### Verified facts
The project does not implement a general user file upload flow.
Evidence from the codebase search:
- There is no `request.files` handling in the backend routes.
- There is no `multipart/form-data` upload API in the server.
- There is no cloud storage connector for Supabase Storage or cloud object storage.

### What exists instead
- The app supports text-based ingestion to Chroma via a JSON API, as seen in [backend/routes/rag_routes.py](../backend/routes/rag_routes.py).
- The app exports manuscript content as `.txt`, `.docx`, and `.pdf` using in-memory buffers, not persistent server-side files.
- The `generated_files` directory is created in the app startup, but the actual exports in the code are returned as `BytesIO` streams via Flask `send_file`, not stored long-term.

### Export implementation details
From [backend/services/export_service.py](../backend/services/export_service.py):
- `.txt` export writes UTF-8 text to an in-memory buffer
- `.docx` export uses `python-docx`
- `.pdf` export uses ReportLab and system font detection for Hindi/Tamil/Telugu support
- PDF export explicitly raises an error if unsupported Indic fonts are missing

This is suitable for download generation but not as a persistent document repository.

## 7. Frontend API configuration and CORS

### Verified frontend API configuration
From [frontend/js/api.js](../frontend/js/api.js):
- Default API URL is `http://127.0.0.1:5000`
- The app builds requests as `${API_BASE_URL}/api/...`

### Verified CORS configuration
From [backend/config.py](../backend/config.py):
- Allowed origins are defaulted to many local addresses including `localhost:3000`, `127.0.0.1:3000`, `localhost:5000`, etc.

From [backend/app.py](../backend/app.py):
- `cors.init_app(app, resources={"/api/*": { ... }})`
- It allows API requests from configured frontend origins

### Free deployment implication
For Hugging Face Spaces or any remote deployment, the frontend origin will change and `CORS_ORIGINS` must be updated to include the actual public URL. This is a deployment configuration requirement, not a code-blocking issue.

## 8. Can the complete Flask app run on Hugging Face Spaces with Docker?

### Verified because of the repo
The repo already includes:
- A backend Dockerfile in [backend/Dockerfile](../backend/Dockerfile)
- A Docker Compose setup in [docker-compose.yml](../docker-compose.yml)

This means the backend is already Docker-friendly.

### What must be changed for Spaces
The app can run on Hugging Face Spaces only with a few deployment-level adjustments:
- Use the Docker-based Space setup with the backend container, not the composed `docker-compose.yml` file directly
- Set the web port to the host-specified port (`PORT`, often 7860 for Spaces) instead of assuming 5000
- Ensure `CORS_ORIGINS` includes the Space public URL
- Store API keys in Space secrets, not in versioned `.env` files
- Keep the app self-contained with Flask serving the frontend routes, or use a minimal separate static frontend if desired

### Most important limitation
The current application uses local filesystem storage for SQLite and ChromaDB. That is acceptable for a single container deployment, but it is not durable across rebuilds unless the hosting platform offers persistent storage.

### Conclusion
Yes, the app is deployable in a Dockerized Hugging Face Space, but only with configuration and likely a small port/runtime adaptation. It is not a zero-configuration free deployment.

## 9. Supabase PostgreSQL and pgvector vs SQLite and ChromaDB

### Can Supabase Postgres replace SQLite?
Yes, technically, the app could use PostgreSQL instead of SQLite by changing the SQLAlchemy connection string and using a managed database. But this would require code/configuration changes because the current app relies on a SQLite-specific local default and does not yet support a production DB abstraction layer beyond the standard SQLAlchemy config.

### Can pgvector replace ChromaDB?
Yes, conceptually, pgvector can replace the RAG vector store, but not as a drop-in replacement. The current code is tightly coupled to ChromaDB-specific patterns:
- `chromadb.PersistentClient(...)`
- `get_or_create_collection(...)`
- metadata filter logic specific to Chroma query calls
- `collection.query()` behavior

To use Supabase pgvector properly, the app would need a new storage layer with:
- vector table schema
- embedding index
- similarity query logic
- metadata filters
- document/chunk storage schema

### Will all RAG functionality be preserved?
It can be preserved, but only with code changes. The application’s current behavior is not Swappable-by-config to pgvector without rewriting the RAG service layer. This is a real migration cost, not a small toggle.

### Should Supabase be used here?
Not for the current free deployment recommendation.
- SQLite is sufficient for the project’s current scale.
- ChromaDB is enough for the current app’s local RAG implementation.
- Supabase is only useful if the app needs managed persistence, database backups, and a more robust multi-user environment.

## 10. Is Supabase Storage needed?

No, not for the current app design.

The project does not have:
- a public file upload API
- a user image/media store
- a document bucket requirement
- a persistent export filesystem model

The app stores:
- project data in SQLite
- RAG knowledge in ChromaDB on local filesystem
- exported files in memory and streams them directly to the client

Supabase Storage would be optional only if the project later adds:
- uploaded lore documents
- user-generated media or PDFs
- persistent exported files
- shared project assets

It is not required for the current free deployment.

## 11. Free-tier storage and memory constraints

### Storage
The current architecture keeps data locally in the running environment:
- SQLite database
- ChromaDB vector store
- generated_files directory (created, but mostly used transiently)

This is acceptable only if the deployment host provides stable file persistence or if the app is small and ephemeral.

Free-tier reality:
- Many free deployment hosts provide limited storage and may not guarantee persistence across restarts.
- Hugging Face Spaces free level is suitable for demos and small projects, but not ideal for anything expecting durable multi-user content and large vector indexes.

### Memory
The heavier cost is the multilingual embedding model, not the database.
- SQLite is negligible
- ChromaDB is moderate
- `sentence-transformers` model is the main risk

For a free-tier CPU container, expected working memory is roughly around 1-2 GB, which is usually okay for a moderate demo but tight for large-scale workloads.

### Conclusion on free-tier viability
The app can operate within free-tier constraints for a small demo or hobby deployment, but not as a large, permanent, high-traffic product without paying for managed resources or larger storage/memory.

## 12. Recommended cheapest genuinely free deployment architecture

### Recommended architecture
Hugging Face Spaces (Docker) with:
- Flask backend as the app container
- SQLite database stored in a persistent local directory or mounted volume
- ChromaDB stored in a local persistent directory
- Gemini API for generation (API key from Space secrets)
- No Supabase dependency for the initial free deployment

This is the cheapest genuinely free architecture because:
- it requires no paid database tier
- it avoids Supabase costs
- it aligns with the project’s existing Dockerfile
- it is a direct fit for the current codebase

### Limitations
- Local persistence may not be rebuild-safe unless the platform offers persistent disk or volume support
- Model loading can be memory-intensive at startup and when processing RAG queries
- The app is single-instance and not designed for multi-replica scaling
- The vector DB will grow with user documents and may slow down as the corpus gets larger
- Free hosting is best for demos, prototypes, and small personal use, not large public user traffic

### Required changes before deployment
- Set `PORT` to the hosting environment value, not hardcoded 5000
- Update `CORS_ORIGINS` to the actual public URL
- Store `GEMINI_API_KEY` and all secrets in secure environment variables / Space secrets
- Confirm the app binds to `0.0.0.0` and the right port
- Keep SQLite and Chroma directories in persistent host storage if available
- Avoid committing `.env` or secret values to repo

### Expected monthly cost
- $0.00 for the simplest free deployment on Hugging Face Spaces, assuming the free tier is available and the usage remains modest
- Real limitation: this is not a robust long-term production deployment and may require paid hosting if persistence or scaling is needed

## Final recommendation

The cheapest genuinely free architecture is a single-container Hugging Face Spaces deployment running the existing Flask backend, while keeping SQLite and ChromaDB on local persistent files in the container. This is viable for a small demo or student-project deployment.

It is not the best long-term architecture for production use, because:
- SQLite is not a scaled multi-user database
- ChromaDB on local disk is not a managed vector database
- the embedding model consumes meaningful RAM
- persistence depends on the hosting platform’s free-tier features

If the project later expands beyond a demo, the next step would be to move to:
- managed PostgreSQL (and optional pgvector) for structured data
- dedicated vector storage or pgvector for RAG
- object storage for user-generated files if uploads are added
- a paid hosting plan for persistent storage and better reliability

This would still preserve the same app structure, but it would require a real migration away from the current code’s local SQLite/Chroma design.

## Verified vs estimated

Verified facts:
- The repo uses SQLite, SQLAlchemy, ChromaDB, and `intfloat/multilingual-e5-small`.
- The backend Dockerfile is already present.
- The app has no file upload or Supabase storage integration.
- The app serves the frontend itself and the API defaults to `127.0.0.1:5000`.
- Docker support exists in the codebase.

Estimated figures:
- model RAM usage: roughly 500 MB to 1.2 GB while loaded
- total app memory footprint under moderate load: approximately 1.0 GB to 2.0 GB
- free-tier viability: suitable for small demos and low-traffic personal deployment, not large-scale production

These estimates are operational approximations, not exact benchmark measurements from this environment.
