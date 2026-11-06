"""
StoryVerse AI — RAG (Retrieval-Augmented Generation) Unit & Integration Tests
=============================================================================
Comprehensive test suite validating:
  1. Multilingual embeddings via SentenceTransformers & EmbeddingService
  2. Document chunking with paragraph/sentence boundary awareness and overlap
  3. ChromaDB persistent vector storage & collection operations
  4. Semantic vector search & cosine similarity retrieval
  5. Metadata filtering (project_id, genre, language, doc_type)
  6. Project isolation (lore belonging to project A vs B vs global)
  7. RAG REST API endpoints (ingest, list, get, delete, query, status)
  8. CRITICAL GROUNDING PROOF: Demonstrates that retrieved knowledge base
     chunks are genuinely injected into the prompt received by the AI generation provider!
"""

import os
import pytest
from services.embedding_service import EmbeddingService
from services.rag_service import RAGService, ChromaEmbeddingAdapter
from services.rag_errors import RAGUnavailableError
from services.prompt_service import (
    build_rag_context_block,
    build_story_prompt,
    build_script_prompt,
    build_continue_prompt
)
from services.story_service import StoryService
from services.script_service import ScriptService
from services.ai_service import ai_service
from services.ai_provider import MockAIProvider


# ============================================================
# 1. Embedding Service Tests
# ============================================================

class TestEmbeddingService:
    """Verifies vector embedding generation and multilingual support."""

    def test_mock_embedding_generation_dimension(self):
        """Mock/deterministic embedding must produce 384-dimensional unit vectors."""
        embedder = EmbeddingService(force_mock=True)
        vec = embedder.get_embedding("The ancient library was silent.")
        assert len(vec) == 384
        assert isinstance(vec[0], float)

    def test_mock_batch_embeddings(self):
        """Batch embedding must return a list of 384-dimensional vectors."""
        embedder = EmbeddingService(force_mock=True)
        texts = ["Text one", "Text two", "Text three"]
        vectors = embedder.get_embeddings(texts)
        assert len(vectors) == 3
        for v in vectors:
            assert len(v) == 384

    def test_mock_multilingual_text_embedding_dimensions(self):
        """Explicit test embeddings must handle multilingual input at the expected dimension."""
        embedder = EmbeddingService(force_mock=True)
        multilingual_samples = [
            "The warrior held a blazing sword.",
            "పురాతన దేవాలయంలో ఒక రహస్య గ్రంథం దాగి ఉంది.",
            "பண்டைய கோவிலில் ஒரு ரகசிய சுவடி மறைக்கப்பட்டுள்ளது.",
            "प्राचीन मंदिर में एक गुप्त ग्रन्थ छिपा हुआ है।"
        ]
        vectors = embedder.get_embeddings(multilingual_samples)
        assert len(vectors) == 4
        for vec in vectors:
            assert len(vec) == 384

    def test_e5_prefix_formatting(self):
        """E5 models must prepend 'query: ' for queries and 'passage: ' for passages."""
        embedder = EmbeddingService(model_name="intfloat/multilingual-e5-small")
        assert embedder._format_text("hello", is_query=True) == "query: hello"
        assert embedder._format_text("hello", is_query=False) == "passage: hello"
        # Must not double-prefix
        assert embedder._format_text("query: hello", is_query=True) == "query: hello"
        assert embedder._format_text("passage: hello", is_query=False) == "passage: hello"

    @pytest.mark.skipif(
        os.environ.get("RUN_RAG_MODEL_INTEGRATION_TESTS") != "1",
        reason="Set RUN_RAG_MODEL_INTEGRATION_TESTS=1 to run the real E5 model integration test."
    )
    def test_real_multilingual_e5_semantic_similarity_ranking(self):
        """
        Tests semantic retrieval across English, Telugu, Tamil, and Hindi.
        Verifies that relevant query embeddings match target passages closer than unrelated passages.
        """
        import numpy as np
        embedder = EmbeddingService(model_name="intfloat/multilingual-e5-small", mock_mode=False)
        assert not embedder.is_mock_mode

        def cosine_sim(v1, v2):
            a = np.array(v1)
            b = np.array(v2)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

        # 1. English
        q_en = embedder.encode_query("ancient magic crystal")
        p_en_match = embedder.encode_passages(["The obsidian obelisk houses a luminescent crystal of ancient sorcery."])[0]
        p_en_diff = embedder.encode_passages(["Cooking pasta requires boiling water and olive oil."])[0]
        assert cosine_sim(q_en, p_en_match) > cosine_sim(q_en, p_en_diff)

        # 2. Telugu
        q_te = embedder.encode_query("రాజు కిరీటం మరియు కోట")
        p_te_match = embedder.encode_passages(["పురాతన సామ్రాజ్యంలో చక్రవర్తి బంగారు కిరీటాన్ని ధరించి తన రాతి కోటలో పాలించాడు."])[0]
        p_te_diff = embedder.encode_passages(["వంటగదిలో కూరగాయలు కోయడం ఎలా."])[0]
        assert cosine_sim(q_te, p_te_match) > cosine_sim(q_te, p_te_diff)

        # 3. Tamil
        q_ta = embedder.encode_query("சோழ மன்னனின் அரண்மனை மற்றும் கிரீடம்")
        p_ta_match = embedder.encode_passages(["சோழ பேரரசர் ராஜராஜ சோழன் தனது தங்க கிரீடத்தை அணிந்து தஞ்சை பெரிய அரண்மனையில் வீற்றிருந்தார்."])[0]
        p_ta_diff = embedder.encode_passages(["கணினி நிரலாக்கம் மற்றும் மென்பொருள் உருவாக்கம் பற்றிய வழிகாட்டி."])[0]
        assert cosine_sim(q_ta, p_ta_match) > cosine_sim(q_ta, p_ta_diff)

        # 4. Hindi
        q_hi = embedder.encode_query("राजा का मुकुट और किला")
        p_hi_match = embedder.encode_passages(["प्राचीन साम्राज्य के सम्राट ने सोने का मुकुट पहनकर अपने विशाल किले में शासन किया।"])[0]
        p_hi_diff = embedder.encode_passages(["रसोई में चाय बनाने का तरीका।"])[0]
        assert cosine_sim(q_hi, p_hi_match) > cosine_sim(q_hi, p_hi_diff)



# ============================================================
# 2. Document Chunking Tests
# ============================================================

class TestDocumentChunking:
    """Verifies chunking logic, boundary handling, and overlap."""

    def test_short_document_single_chunk(self):
        rag = RAGService()
        short_text = "This is a brief worldbuilding note under 100 characters."
        chunks = rag.chunk_document(short_text, chunk_size=500, chunk_overlap=50)
        assert len(chunks) == 1
        assert chunks[0] == short_text

    def test_empty_document_handling(self):
        rag = RAGService()
        assert rag.chunk_document("") == []
        assert rag.chunk_document("   ") == []
        assert rag.chunk_document(None) == []

    def test_paragraph_boundary_chunking_with_overlap(self):
        rag = RAGService()
        paragraphs = [
            "Paragraph one introduces the city of Aethelgard with towering obsidian walls.",
            "Paragraph two describes the inner sanctum where the crystal of tides is kept.",
            "Paragraph three warns of the shadow guild seeking to extinguish the lunar flame."
        ]
        full_text = "\n\n".join(paragraphs)
        chunks = rag.chunk_document(full_text, chunk_size=120, chunk_overlap=30)
        assert len(chunks) >= 2
        # Verify text content from first and last paragraphs is preserved
        combined_chunks = " ".join(chunks)
        assert "Aethelgard" in combined_chunks
        assert "lunar flame" in combined_chunks


# ============================================================
# 3. ChromaDB Vector Store & Isolation Tests
# ============================================================

class TestRAGVectorStore:
    """Verifies ChromaDB ingestion, retrieval, filtering, and isolation."""

    @pytest.fixture(autouse=True)
    def setup_rag(self, tmp_path):
        """Initializes a clean RAG service collection for tests."""
        self.rag = RAGService(
            persist_directory=str(tmp_path / "chroma"),
            collection_name="test_storyverse_kb",
            embed_service=EmbeddingService(force_mock=True)
        )

    def test_ingest_and_retrieve_document(self):
        """Document must be indexed in vector store and retrievable by similarity."""
        ingest_result = self.rag.ingest_document(
            title="Aethelgard Lore",
            content="The obsidian walls of Aethelgard were forged by dragonfire in the First Age.",
            doc_type="worldbuilding",
            genre="fantasy",
            language="English"
        )
        assert ingest_result["document_id"].startswith("doc_")
        assert ingest_result["chunk_count"] >= 1

        results = self.rag.retrieve_context("dragonfire walls", n_results=2)
        assert len(results) >= 1
        assert "obsidian walls of Aethelgard" in results[0]["text"]
        assert results[0]["document_title"] == "Aethelgard Lore"

    def test_metadata_filtering_by_genre(self):
        """Query with genre filter must only return matching genre lore."""
        self.rag.ingest_document(
            title="Cyberpunk Tech",
            content="Neural link version 4 enables direct cybernetic matrix interfacing.",
            doc_type="lore",
            genre="sci-fi",
            language="English"
        )
        self.rag.ingest_document(
            title="Necromancy Rules",
            content="Reanimating skeletal thralls requires grave dust and blackened bone.",
            doc_type="rules",
            genre="horror",
            language="English"
        )

        sci_fi_results = self.rag.retrieve_context("technology device", genre="sci-fi")
        assert len(sci_fi_results) >= 1
        for res in sci_fi_results:
            assert res["genre"] == "sci-fi"

    def test_metadata_filtering_by_language(self):
        self.rag.ingest_document(
            title="English Notes",
            content="The western tower hides a silver key beneath its foundation.",
            language="English"
        )
        self.rag.ingest_document(
            title="Telugu Notes",
            content="ఈ కథలోని పాత్రలు ఒక రహస్యమైన కోటలో ప్రయాణిస్తారు.",
            language="Telugu"
        )

        results = self.rag.retrieve_context("tower silver key", language="English")

        assert results
        assert all(result["language"] == "English" for result in results)

    def test_project_lore_isolation(self):
        """
        Project A's private lore must be accessible to Project A,
        while Project B cannot access Project A's private lore.
        Global lore (project_id=0) is accessible to all.
        """
        # Ingest Project 100 private lore
        self.rag.ingest_document(
            title="Project 100 Secret",
            content="The secret cipher key for Project 100 is Omega-779.",
            project_id=100
        )
        # Ingest Project 200 private lore
        self.rag.ingest_document(
            title="Project 200 Secret",
            content="The hidden warp portal for Project 200 is located under Sector 9.",
            project_id=200
        )
        # Ingest Global lore
        self.rag.ingest_document(
            title="Global Lore",
            content="The kingdom calendar has 13 solar months.",
            project_id=0
        )

        # 1. Query as Project 100 -> sees Project 100 + Global, but NOT Project 200
        res_p100 = self.rag.retrieve_context("cipher key portal calendar", project_id=100, n_results=10)
        titles_p100 = [r["document_title"] for r in res_p100]
        assert "Project 100 Secret" in titles_p100
        assert "Global Lore" in titles_p100
        assert "Project 200 Secret" not in titles_p100

        # 2. Query as Project 200 -> sees Project 200 + Global, but NOT Project 100
        res_p200 = self.rag.retrieve_context("cipher key portal calendar", project_id=200, n_results=10)
        titles_p200 = [r["document_title"] for r in res_p200]
        assert "Project 200 Secret" in titles_p200
        assert "Global Lore" in titles_p200
        assert "Project 100 Secret" not in titles_p200

        # 3. Query as Global only (project_id=0) -> sees Global, but neither private project lore
        res_global = self.rag.retrieve_context("cipher key portal calendar", project_id=0, n_results=10)
        titles_global = [r["document_title"] for r in res_global]
        assert "Global Lore" in titles_global
        assert "Project 100 Secret" not in titles_global
        assert "Project 200 Secret" not in titles_global

    def test_persistent_storage_across_client_restarts(self, tmp_path):
        """
        Verifies persistent storage:
        Ingests a document into ChromaDB, deletes the service instance,
        spawns a brand-new instance pointing to the same directory,
        and confirms the document remains retrievable.
        """
        persist_dir = str(tmp_path / "chroma_persist_test")
        rag_instance1 = RAGService(
            persist_directory=persist_dir,
            collection_name="persist_col",
            embed_service=EmbeddingService(force_mock=True)
        )
        ingest_res = rag_instance1.ingest_document(
            title="Durable Archive",
            content="The ancient obsidian tablets survived the fire of Mount Vesuvius.",
            doc_type="lore"
        )
        doc_id = ingest_res["document_id"]
        assert doc_id is not None

        # Simulate application restart: dereference first client
        del rag_instance1

        # Recreate application / RAGService pointing to exact same directory
        rag_instance2 = RAGService(
            persist_directory=persist_dir,
            collection_name="persist_col",
            embed_service=EmbeddingService(force_mock=True)
        )
        
        # Verify document still exists by ID
        doc = rag_instance2.get_document(doc_id)
        assert doc is not None
        assert doc["title"] == "Durable Archive"
        assert "obsidian tablets" in doc["content"]

        # Verify semantic retrieval from restarted instance
        query_results = rag_instance2.retrieve_context("obsidian tablets fire", n_results=2)
        assert len(query_results) >= 1
        assert "obsidian tablets" in query_results[0]["text"]

    def test_document_listing_and_deletion(self):
        """Verifies list_documents, get_document, and delete_document."""
        ingest_res = self.rag.ingest_document(
            title="Temporary Myth",
            content="A transient legend that will be removed from the archive.",
            doc_type="lore"
        )
        doc_id = ingest_res["document_id"]

        # List
        docs = self.rag.list_documents()
        assert any(d["document_id"] == doc_id for d in docs)

        # Get
        fetched = self.rag.get_document(doc_id)
        assert fetched is not None
        assert fetched["title"] == "Temporary Myth"
        assert "transient legend" in fetched["content"]

        # Delete
        deleted = self.rag.delete_document(doc_id)
        assert deleted is True

        # Verify gone
        assert self.rag.get_document(doc_id) is None

    def test_status_endpoint_data(self):
        """get_status must report collection name, model name, and dimensions."""
        status = self.rag.get_status()
        assert status["status"] == "ready"
        assert "collection_name" in status
        assert status["embedding_dimension"] == 384
        assert status["distance_metric"] == "cosine"
        assert status["embedding_mode"] == "deterministic_mock"

    def test_retrieval_filter_failure_does_not_retry_unfiltered(self, monkeypatch):
        self.rag.ingest_document(
            title="Private project lore",
            content="The private silver key is hidden under the western tower.",
            project_id=100
        )
        collection = self.rag.collection
        query_calls = []

        def fail_filtered_query(**kwargs):
            query_calls.append(kwargs)
            raise RuntimeError("unsupported filter")

        monkeypatch.setattr(collection, "query", fail_filtered_query)

        with pytest.raises(RAGUnavailableError, match="project and metadata filters"):
            self.rag.retrieve_context("silver key", project_id=100)

        assert len(query_calls) == 1
        assert query_calls[0]["where"] is not None

    def test_document_listing_filter_failure_does_not_retry_unfiltered(self, monkeypatch):
        self.rag.ingest_document(
            title="Private project lore",
            content="The private silver key is hidden under the western tower.",
            project_id=100
        )
        collection = self.rag.collection
        get_calls = []

        def fail_filtered_get(**kwargs):
            get_calls.append(kwargs)
            raise RuntimeError("unsupported filter")

        monkeypatch.setattr(collection, "get", fail_filtered_get)

        with pytest.raises(RAGUnavailableError, match="project filters"):
            self.rag.list_documents(project_id=100)

        assert len(get_calls) == 1
        assert get_calls[0]["where"] is not None

    def test_environment_configuration_is_applied(self, monkeypatch, tmp_path):
        persist_directory = str(tmp_path / "configured-chroma")
        monkeypatch.setenv("CHROMA_PERSIST_DIRECTORY", persist_directory)
        monkeypatch.setenv("RAG_COLLECTION_NAME", "configured_collection")
        monkeypatch.setenv("RAG_DEFAULT_TOP_K", "7")
        monkeypatch.setenv("RAG_ENABLED", "false")

        rag = RAGService(embed_service=EmbeddingService(force_mock=True))

        assert rag.persist_directory == persist_directory
        assert rag.collection_name == "configured_collection"
        assert rag.default_top_k == 7
        assert rag.get_status()["status"] == "disabled"
        with pytest.raises(RAGUnavailableError, match="disabled"):
            _ = rag.collection


class TestRAGModelFailure:
    def test_model_load_failure_is_not_replaced_with_mock_embeddings(self, monkeypatch):
        embedder = EmbeddingService(force_mock=False)

        def fail_model_load():
            raise RuntimeError("model unavailable")

        monkeypatch.setattr(embedder, "_get_model", fail_model_load)

        with pytest.raises(RAGUnavailableError, match="failed to encode text"):
            embedder.encode(["test text"])


# ============================================================
# 4. Prompt Construction & Grounding Tests
# ============================================================

class TestRAGPromptConstruction:
    """Verifies that RAG context is correctly embedded into model prompts."""

    def test_build_rag_context_block_formatting(self):
        chunks = [
            {
                "document_title": "Magic Rules",
                "doc_type": "rules",
                "text": "Spells require verbal incantations."
            },
            {
                "document_title": "Geography",
                "doc_type": "worldbuilding",
                "text": "The Whispering Mountains lie north."
            }
        ]
        block = build_rag_context_block(chunks)
        assert "RETRIEVED KNOWLEDGE CONTEXT" in block
        assert 'Source 1: "Magic Rules"' in block
        assert "Spells require verbal incantations." in block
        assert 'Source 2: "Geography"' in block
        assert "The Whispering Mountains lie north." in block

    def test_build_story_prompt_includes_rag_context(self):
        rag_block = "=== RETRIEVED KNOWLEDGE CONTEXT ===\nCanon: Dragons are immortal."
        params = {
            "topic": "A knight meets a dragon",
            "genre": "Fantasy",
            "language": "English",
            "rag_context": rag_block
        }
        prompt = build_story_prompt(params)
        assert "=== RETRIEVED KNOWLEDGE CONTEXT ===" in prompt
        assert "Canon: Dragons are immortal." in prompt
        assert "A knight meets a dragon" in prompt

    def test_build_script_prompt_includes_rag_context(self):
        rag_block = "=== RETRIEVED KNOWLEDGE CONTEXT ===\nCyberpunk Rule: Rain is acid."
        params = {
            "topic": "Detective investigates neon alley",
            "genre": "Sci-Fi",
            "language": "English",
            "rag_context": rag_block
        }
        prompt = build_script_prompt(params)
        assert "=== RETRIEVED KNOWLEDGE CONTEXT ===" in prompt
        assert "Cyberpunk Rule: Rain is acid." in prompt


# ============================================================
# 5. RAG REST API Route Tests
# ============================================================

class TestRAGRoutes:
    """Verifies all /api/rag/* HTTP endpoints."""

    @pytest.fixture(autouse=True)
    def isolate_global_rag(self, tmp_path):
        from services.rag_service import rag_service

        rag_service.persist_directory = str(tmp_path / "chroma")
        rag_service._client = None
        rag_service._collection = None

    def test_rag_status_route(self, client):
        res = client.get("/api/rag/status")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["embedding_dimension"] == 384
        assert data["data"]["distance_metric"] == "cosine"

    def test_rag_disabled_returns_explicit_unavailable_response(self, client, monkeypatch):
        from services.rag_service import rag_service

        monkeypatch.setattr(rag_service, "enabled", False)

        res = client.post("/api/rag/query", json={"query": "story lore"})

        assert res.status_code == 503
        assert res.get_json()["success"] is False
        assert "disabled" in res.get_json()["message"]

    def test_generation_reports_rag_retrieval_failure(self, client, monkeypatch):
        from services.rag_service import rag_service

        def fail_retrieval(**kwargs):
            raise RAGUnavailableError("RAG retrieval is unavailable.")

        monkeypatch.setattr(rag_service, "retrieve_context", fail_retrieval)

        res = client.post("/api/generate-story", json={
            "topic": "A story using established lore",
            "genre": "Fantasy",
            "language": "English",
            "use_rag": True
        })

        assert res.status_code == 503
        assert res.get_json()["success"] is False
        assert res.get_json()["errors"]["rag"] == "Semantic retrieval is unavailable."

    def test_rag_ingest_route_valid(self, client):
        payload = {
            "title": "API Ingest Test Document",
            "content": "This is test lore ingested via the REST API endpoint.",
            "doc_type": "worldbuilding",
            "genre": "fantasy",
            "language": "English"
        }
        res = client.post("/api/rag/ingest", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert "document_id" in data["data"]
        assert data["data"]["title"] == "API Ingest Test Document"

    def test_rag_ingest_route_validation_error(self, client):
        # Missing required fields
        res = client.post("/api/rag/ingest", json={"title": "No content provided"})
        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "errors" in data
        assert "content" in data["errors"]

    def test_rag_documents_list_and_get(self, client):
        # Ingest first
        ingest_res = client.post("/api/rag/ingest", json={
            "title": "Document to Retrieve",
            "content": "Specific content for retrieval testing.",
            "doc_type": "lore"
        })
        doc_id = ingest_res.get_json()["data"]["document_id"]

        # List
        list_res = client.get("/api/rag/documents")
        assert list_res.status_code == 200
        docs = list_res.get_json()["data"]["documents"]
        assert any(d["document_id"] == doc_id for d in docs)

        # Get single
        get_res = client.get(f"/api/rag/documents/{doc_id}")
        assert get_res.status_code == 200
        single = get_res.get_json()["data"]
        assert single["document_id"] == doc_id
        assert single["title"] == "Document to Retrieve"

        # Delete
        del_res = client.delete(f"/api/rag/documents/{doc_id}")
        assert del_res.status_code == 200

        # Get after delete -> 404
        get_res_after = client.get(f"/api/rag/documents/{doc_id}")
        assert get_res_after.status_code == 404

    def test_rag_query_route(self, client):
        client.post("/api/rag/ingest", json={
            "title": "Moonlit Tower",
            "content": "The Moonlit Tower shines with silver radiance when the tides rise.",
            "doc_type": "worldbuilding"
        })
        query_res = client.post("/api/rag/query", json={
            "query": "silver radiance moonlit tower",
            "n_results": 2
        })
        assert query_res.status_code == 200
        data = query_res.get_json()["data"]
        assert data["count"] >= 1
        assert "silver radiance" in data["retrieved_chunks"][0]["text"]


# ============================================================
# 6. CRITICAL MANDATORY TEST: RETRIEVED LORE IN PROMPT
# ============================================================

class TestRAGGenerativeGrounding:
    """
    CRITICAL PROOF OF RAG:
    Demonstrates with automated assertions that retrieved document content
    from ChromaDB is ACTUALLY injected into the exact prompt string sent
    to the AI generation provider (Mock / Gemini).
    """

    def test_story_generation_actually_includes_retrieved_lore_in_ai_prompt(self, client):
        """
        1. Ingest a distinctive, uniquely phrased lore fact into RAG.
        2. Call /api/generate-story with use_rag=True and a topic referencing the lore.
        3. Assert the unique fact is PRESENT in the prompt sent to the AI provider.
        """
        mock_provider = MockAIProvider()
        ai_service.set_provider(mock_provider)

        from services.rag_service import rag_service
        unique_lore_phrase = "The sacred chronocrystal of Valoria shatters only under midnight lunar eclipse"
        ingest_res = rag_service.ingest_document(
            title="Valoria Chronocrystal Canon",
            content=f"Ancient canon states: {unique_lore_phrase}. It cannot be harmed by mortal steel.",
            doc_type="lore",
            genre="fantasy",
            language="English"
        )
        doc_id = ingest_res["document_id"]

        try:
            # Request story generation with RAG enabled
            payload = {
                "topic": "A thief attempts to break the Valoria chronocrystal",
                "genre": "Fantasy",
                "language": "English",
                "tone": "Suspenseful",
                "length": "Medium",
                "use_rag": True
            }

            res = client.post("/api/generate-story", json=payload)
            assert res.status_code == 200
            data = res.get_json()["data"]

            # 1. Assert response metadata indicates RAG was applied
            assert data["metadata"]["rag_applied"] is True
            assert len(data["retrieved_context"]) >= 1

            # 2. PROOF OF GROUNDING: Inspect the exact prompt received by the AI model
            ai_received_prompt = mock_provider.last_prompt
            assert ai_received_prompt is not None, "AI provider did not receive a prompt"

            # Check for RAG context block header
            assert "RETRIEVED KNOWLEDGE CONTEXT" in ai_received_prompt
            # Check for source title
            assert "Valoria Chronocrystal Canon" in ai_received_prompt
            # Check for exact unique lore text
            assert unique_lore_phrase in ai_received_prompt

            print(f"\n[VERIFIED] RAG Grounding confirmed: '{unique_lore_phrase}' was verified in AI prompt.")

        finally:
            # Clean up test document
            rag_service.delete_document(doc_id)

    def test_script_generation_actually_includes_retrieved_lore_in_ai_prompt(self, client):
        """
        Confirms Script Generator also retrieves and injects knowledge chunks
        into the screenplay generation prompt.
        """
        mock_provider = MockAIProvider()
        ai_service.set_provider(mock_provider)

        from services.rag_service import rag_service
        unique_script_lore = "Agent Vesper carries a modified Walther PPK with subsonic cryo-rounds"
        ingest_res = rag_service.ingest_document(
            title="Agent Vesper Dossier",
            content=f"Operative details: {unique_script_lore}. Code designation: Shadow Falcon.",
            doc_type="character",
            genre="action",
            language="English"
        )
        doc_id = ingest_res["document_id"]

        try:
            payload = {
                "topic": "Agent Vesper confronts the syndicate boss on a rooftop",
                "genre": "Action",
                "language": "English",
                "tone": "Tense",
                "num_scenes": 2,
                "use_rag": True
            }

            res = client.post("/api/generate-script", json=payload)
            assert res.status_code == 200
            data = res.get_json()["data"]

            assert data["metadata"]["rag_applied"] is True
            assert len(data["retrieved_context"]) >= 1

            ai_received_prompt = mock_provider.last_prompt
            assert ai_received_prompt is not None

            # Assert prompt contains RAG header and exact character dossier detail
            assert "RETRIEVED KNOWLEDGE CONTEXT" in ai_received_prompt
            assert unique_script_lore in ai_received_prompt

            print(f"\n[VERIFIED] Script RAG Grounding confirmed: '{unique_script_lore}' was verified in AI prompt.")

        finally:
            rag_service.delete_document(doc_id)

    def test_character_generation_actually_includes_retrieved_lore_in_ai_prompt(self, client):
        """
        Confirms Character Generator retrieves and injects knowledge chunks
        into the character bible prompt.
        """
        mock_provider = MockAIProvider()
        ai_service.set_provider(mock_provider)

        from services.rag_service import rag_service
        unique_char_fact = "Kaelen bears a crescent-shaped burn mark from the Siege of Solitude"
        ingest_res = rag_service.ingest_document(
            title="Kaelen Lore",
            content=f"Historical record: {unique_char_fact}. His weapon is the Silver Halberd.",
            doc_type="character",
            genre="fantasy",
            language="English"
        )
        doc_id = ingest_res["document_id"]

        try:
            payload = {
                "character_name": "Kaelen",
                "genre": "Fantasy",
                "character_role": "Protagonist",
                "language": "English",
                "tone": "Emotional",
                "description": "A battle-hardened veteran who survived the Siege of Solitude",
                "use_rag": True
            }

            res = client.post("/api/generate-character", json=payload)
            assert res.status_code == 200
            data = res.get_json()["data"]

            assert data["metadata"]["rag_applied"] is True
            assert len(data["retrieved_context"]) >= 1

            ai_received_prompt = mock_provider.last_prompt
            assert ai_received_prompt is not None

            assert "RETRIEVED KNOWLEDGE CONTEXT" in ai_received_prompt
            assert unique_char_fact in ai_received_prompt

            print(f"\n[VERIFIED] Character RAG Grounding confirmed: '{unique_char_fact}' was verified in AI prompt.")

        finally:
            rag_service.delete_document(doc_id)

    def test_character_variations_actually_includes_retrieved_lore_in_ai_prompt(self, client):
        """
        Confirms Character Variations generation retrieves and injects knowledge chunks
        into the ensemble concept prompt.
        """
        mock_provider = MockAIProvider()
        ai_service.set_provider(mock_provider)

        from services.rag_service import rag_service
        unique_faction_lore = "The Obsidian Hand guild requires all initiates to wear a cobalt mask"
        ingest_res = rag_service.ingest_document(
            title="Obsidian Hand Guild Canon",
            content=f"Faction rules: {unique_faction_lore}.",
            doc_type="rules",
            genre="fantasy",
            language="English"
        )
        doc_id = ingest_res["document_id"]

        try:
            payload = {
                "premise": "Rivals inside the Obsidian Hand guild competing for leadership",
                "genre": "Fantasy",
                "count": 3,
                "language": "English",
                "character_role": "Antagonist",
                "use_rag": True
            }

            res = client.post("/api/generate-character-variations", json=payload)
            assert res.status_code == 200
            data = res.get_json()["data"]

            assert data["metadata"]["rag_applied"] is True

            ai_received_prompt = mock_provider.last_prompt
            assert ai_received_prompt is not None
            assert "RETRIEVED KNOWLEDGE CONTEXT" in ai_received_prompt
            assert unique_faction_lore in ai_received_prompt

            print(f"\n[VERIFIED] Variations RAG Grounding confirmed: '{unique_faction_lore}' was verified in AI prompt.")

        finally:
            rag_service.delete_document(doc_id)

    def test_writing_assistant_continue_writing_actually_includes_retrieved_lore_in_ai_prompt(self, client):
        """
        Confirms Writing Assistant 'continue' operation retrieves and injects knowledge chunks
        into the continuation prompt.
        """
        mock_provider = MockAIProvider()
        ai_service.set_provider(mock_provider)

        from services.rag_service import rag_service
        unique_secret = "The cipher to disarm the neutron core is Delta-Niner-Seven"
        ingest_res = rag_service.ingest_document(
            title="Facility Protocol",
            content=f"Emergency manual: {unique_secret}.",
            doc_type="lore",
            language="English"
        )
        doc_id = ingest_res["document_id"]

        try:
            payload = {
                "content": "Dr. Aris rushed to the terminal to disarm the neutron core.",
                "direction": "He enters the emergency cipher code",
                "use_rag": True
            }

            res = client.post("/api/continue-writing", json=payload)
            assert res.status_code == 200
            data = res.get_json()["data"]

            assert data["metadata"]["rag_applied"] is True

            ai_received_prompt = mock_provider.last_prompt
            assert ai_received_prompt is not None
            assert "RETRIEVED KNOWLEDGE CONTEXT" in ai_received_prompt
            assert unique_secret in ai_received_prompt

            print(f"\n[VERIFIED] Assistant Continue RAG Grounding confirmed: '{unique_secret}' in AI prompt.")

        finally:
            rag_service.delete_document(doc_id)

    def test_writing_assistant_dialogue_actually_includes_retrieved_lore_in_ai_prompt(self, client):
        """
        Confirms Writing Assistant dialogue generation retrieves and injects knowledge chunks
        into the dialogue prompt.
        """
        mock_provider = MockAIProvider()
        ai_service.set_provider(mock_provider)

        from services.rag_service import rag_service
        unique_feud = "The blood feud between Clan Moros and Clan Vane began at the Red Wedding of 1492"
        ingest_res = rag_service.ingest_document(
            title="Clan Feud History",
            content=f"Historical chronicle: {unique_feud}.",
            doc_type="lore",
            language="English"
        )
        doc_id = ingest_res["document_id"]

        try:
            payload = {
                "characters": "Lord Moros and Lady Vane",
                "context": "Meeting at dusk to discuss the ancestral blood feud",
                "use_rag": True
            }

            res = client.post("/api/generate-dialogue", json=payload)
            assert res.status_code == 200
            data = res.get_json()["data"]

            assert data["metadata"]["rag_applied"] is True

            ai_received_prompt = mock_provider.last_prompt
            assert ai_received_prompt is not None
            assert "RETRIEVED KNOWLEDGE CONTEXT" in ai_received_prompt
            assert unique_feud in ai_received_prompt

            print(f"\n[VERIFIED] Assistant Dialogue RAG Grounding confirmed: '{unique_feud}' in AI prompt.")

        finally:
            rag_service.delete_document(doc_id)

    def test_rag_disabled_does_not_inject_context_across_all_four_modules(self, client):
        """
        Confirms that when use_rag is False, no RAG context is retrieved or injected
        into the AI prompt across all four creative modules.
        """
        mock_provider = MockAIProvider()
        ai_service.set_provider(mock_provider)

        # 1. Story Generator with RAG disabled
        res_story = client.post("/api/generate-story", json={
            "topic": "The forgotten astral fortress",
            "genre": "Fantasy",
            "language": "English",
            "use_rag": False
        })
        assert res_story.status_code == 200
        assert res_story.get_json()["data"]["metadata"]["rag_applied"] is False
        assert "RETRIEVED KNOWLEDGE CONTEXT" not in mock_provider.last_prompt

        # 2. Script Generator with RAG disabled
        res_script = client.post("/api/generate-script", json={
            "topic": "Heist at the central bank",
            "genre": "Thriller",
            "language": "English",
            "num_scenes": 2,
            "use_rag": False
        })
        assert res_script.status_code == 200
        assert res_script.get_json()["data"]["metadata"]["rag_applied"] is False
        assert "RETRIEVED KNOWLEDGE CONTEXT" not in mock_provider.last_prompt

        # 3. Character Generator with RAG disabled
        res_char = client.post("/api/generate-character", json={
            "description": "A rogue chronomancer seeking lost timelines",
            "genre": "Fantasy",
            "language": "English",
            "use_rag": False
        })
        assert res_char.status_code == 200
        assert res_char.get_json()["data"]["metadata"]["rag_applied"] is False
        assert "RETRIEVED KNOWLEDGE CONTEXT" not in mock_provider.last_prompt

        # 4. Writing Assistant Dialogue with RAG disabled
        res_dialogue = client.post("/api/generate-dialogue", json={
            "characters": "Elena and Marcus",
            "context": "Debating whether to trigger the reactor meltdown",
            "language": "English",
            "use_rag": False
        })
        assert res_dialogue.status_code == 200
        assert res_dialogue.get_json()["data"]["metadata"]["rag_applied"] is False
        assert "RETRIEVED KNOWLEDGE CONTEXT" not in mock_provider.last_prompt

    def test_multilingual_rag_generation_preserves_target_languages(self, client):
        """
        Confirms that when RAG is enabled, the retrieved knowledge context does NOT
        override or alter the user's requested output language (Telugu, Tamil, Hindi, English).
        """
        mock_provider = MockAIProvider()
        ai_service.set_provider(mock_provider)

        from services.rag_service import rag_service
        doc_res = rag_service.ingest_document(
            title="Ancient Chrono Nexus Canon",
            content="The Chrono Nexus was built in 1400 BC by the high mystics.",
            doc_type="lore",
            language="English"
        )
        doc_id = doc_res["document_id"]

        try:
            # 1. Telugu Story with RAG
            res_telugu = client.post("/api/generate-story", json={
                "topic": "Chrono Nexus అన్వేషణ",
                "genre": "Fantasy",
                "language": "Telugu",
                "use_rag": True,
                "rag_query": "Chrono Nexus"
            })
            assert res_telugu.status_code == 200
            prompt_telugu = mock_provider.last_prompt
            assert "RETRIEVED KNOWLEDGE CONTEXT" in prompt_telugu
            assert "- Language: Telugu" in prompt_telugu
            assert "Write exclusively in Telugu." in prompt_telugu

            # 2. Tamil Script with RAG
            res_tamil = client.post("/api/generate-script", json={
                "topic": "Chrono Nexus பாதுகாப்பு",
                "genre": "Mystery",
                "language": "Tamil",
                "num_scenes": 1,
                "use_rag": True,
                "rag_query": "Chrono Nexus"
            })
            assert res_tamil.status_code == 200
            prompt_tamil = mock_provider.last_prompt
            assert "RETRIEVED KNOWLEDGE CONTEXT" in prompt_tamil
            assert "- Language: Tamil" in prompt_tamil
            assert "MULTILINGUAL SCREENPLAY DIRECTIVES (TAMIL)" in prompt_tamil
            assert "Write strictly in Tamil." in prompt_tamil

            # 3. Hindi Character with RAG
            res_hindi = client.post("/api/generate-character", json={
                "description": "Chrono Nexus का मुख्य रक्षक",
                "genre": "Fantasy",
                "language": "Hindi",
                "use_rag": True,
                "rag_query": "Chrono Nexus"
            })
            assert res_hindi.status_code == 200
            prompt_hindi = mock_provider.last_prompt
            assert "RETRIEVED KNOWLEDGE CONTEXT" in prompt_hindi
            assert "- Language: Hindi" in prompt_hindi
            assert "Write strictly in Hindi." in prompt_hindi

        finally:
            rag_service.delete_document(doc_id)
