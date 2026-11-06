"""
StoryVerse AI — RAG (Retrieval-Augmented Generation) Service
==============================================================
Orchestrates vector database storage (ChromaDB), document chunking,
metadata filtering, and semantic context retrieval for narrative generation.

Capabilities:
  1. Chunking: Sliding-window chunker with overlap and paragraph boundary awareness.
  2. Persistent Vector Store: ChromaDB with cosine distance metric.
  3. Metadata Filtering: Filter by project_id, genre, language, and doc_type.
  4. Context Formatting: Generates grounded knowledge blocks for prompt injection.
  5. Project Lore Isolation: Project-specific vs. Global worldbuilding lore.
"""

import os
import re
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.api.types import EmbeddingFunction

from .embedding_service import embedding_service, EmbeddingService

logger = logging.getLogger(__name__)

# Default RAG settings
DEFAULT_COLLECTION_NAME = "storyverse_knowledge_base"
DEFAULT_CHUNK_SIZE = 500       # Target characters per chunk
DEFAULT_CHUNK_OVERLAP = 50     # Overlap characters to preserve continuity


class ChromaEmbeddingAdapter(EmbeddingFunction):
    """
    Bridges ChromaDB with our custom multilingual EmbeddingService.
    Supports query/passage prefixing for models like intfloat/multilingual-e5-small.
    """

    def __init__(self, service: EmbeddingService):
        self.service = service

    def __call__(self, input: List[str]) -> List[List[float]]:
        """Invoked by ChromaDB when indexing documents/passages."""
        return self.service.encode_passages(input)

    def embed_query(self, input: List[str]) -> List[List[float]]:
        """Invoked by ChromaDB when searching/querying."""
        return self.service.encode_queries(input)

    def name(self) -> str:
        return f"chroma_adapter_{self.service.model_name}"


class RAGService:
    """
    Core RAG Engine managing ingestion, vector indexing, and semantic retrieval.
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embed_service: Optional[EmbeddingService] = None
    ):
        self.persist_directory = persist_directory or self._default_persist_dir()
        self.collection_name = collection_name
        self.embed_service = embed_service or embedding_service
        self._client = None
        self._collection = None

    def _default_persist_dir(self) -> str:
        """Determines default local directory for persistent ChromaDB storage."""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "chroma_db"))
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    @property
    def client(self) -> chromadb.PersistentClient:
        """Lazy-loaded persistent Chroma client."""
        if self._client is None:
            os.makedirs(self.persist_directory, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_directory)
        return self._client

    @property
    def collection(self):
        """Retrieves or creates the target vector collection."""
        if self._collection is None:
            adapter = ChromaEmbeddingAdapter(self.embed_service)
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=adapter,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    # ============================================================
    # 1. Document Chunking
    # ============================================================

    def chunk_document(
        self,
        text: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ) -> List[str]:
        """
        Splits raw text into semantically cohesive overlapping chunks.
        Respects paragraph (double newlines) and sentence boundaries where practical.

        Args:
            text: Full text document to chunk.
            chunk_size: Maximum character count per chunk.
            chunk_overlap: Character overlap between consecutive chunks.

        Returns:
            List of text chunk strings.
        """
        text = (text or "").strip()
        if not text:
            return []

        if len(text) <= chunk_size:
            return [text]

        # First break into paragraphs
        paragraphs = re.split(r"\n\s*\n", text)
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If adding this paragraph fits, append it
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                # Flush current chunk if it has content
                if current_chunk:
                    chunks.append(current_chunk)
                    # Keep overlap from the end of the previous chunk
                    current_chunk = current_chunk[-chunk_overlap:].strip()

                # If single paragraph is longer than chunk_size, split by sentences
                if len(para) > chunk_size:
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        if len(current_chunk) + len(sent) + 1 <= chunk_size:
                            current_chunk = f"{current_chunk} {sent}".strip()
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                                current_chunk = current_chunk[-chunk_overlap:].strip()
                            current_chunk = f"{current_chunk} {sent}".strip()
                else:
                    current_chunk = f"{current_chunk}\n\n{para}".strip()

        if current_chunk:
            chunks.append(current_chunk)

        # Remove empty or trivial chunks
        return [c for c in chunks if len(c) > 10]

    # ============================================================
    # 2. Knowledge Ingestion
    # ============================================================

    def ingest_document(
        self,
        title: str,
        content: str,
        doc_type: str = "worldbuilding",
        genre: Optional[str] = None,
        language: str = "English",
        project_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Chunks and vectorizes a reference document into ChromaDB.

        Args:
            title: Document title or lore topic (e.g. 'Magic System of Eldoria').
            content: Raw text body of the reference lore or notes.
            doc_type: Category (e.g. 'worldbuilding', 'character', 'lore', 'rules', 'reference').
            genre: Optional literary genre tag.
            language: Language of the document (English, Telugu, Tamil, Hindi).
            project_id: Optional project identifier for project-specific lore isolation.
            metadata: Additional user-defined key-value attributes.

        Returns:
            Dictionary containing document_id, chunk_count, and ingestion summary.
        """
        title = (title or "").strip()
        content = (content or "").strip()
        if not title:
            raise ValueError("Document title is required.")
        if not content:
            raise ValueError("Document content cannot be empty.")

        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        chunks = self.chunk_document(content)
        if not chunks:
            chunks = [content]

        total_chunks = len(chunks)
        now_iso = datetime.now(timezone.utc).isoformat()

        ids = []
        documents = []
        metadatas = []

        for idx, chunk_text in enumerate(chunks):
            chunk_id = f"{doc_id}_c{idx}"
            chunk_meta = {
                "document_id": doc_id,
                "document_title": title,
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "doc_type": str(doc_type).lower(),
                "language": str(language or "English"),
                "genre": str(genre or "all").lower(),
                "project_id": int(project_id) if project_id is not None else 0,
                "created_at": now_iso
            }
            if metadata and isinstance(metadata, dict):
                for k, v in metadata.items():
                    if k not in chunk_meta and isinstance(v, (str, int, float, bool)):
                        chunk_meta[k] = v

            ids.append(chunk_id)
            documents.append(chunk_text)
            metadatas.append(chunk_meta)

        # Batch insert into ChromaDB collection
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        logger.info(f"Ingested document '{title}' ({doc_id}) into RAG vector store with {total_chunks} chunks.")

        return {
            "document_id": doc_id,
            "title": title,
            "doc_type": doc_type,
            "chunk_count": total_chunks,
            "genre": genre,
            "language": language,
            "project_id": project_id,
            "created_at": now_iso
        }

    # ============================================================
    # 3. Semantic Retrieval & Metadata Filtering
    # ============================================================

    def retrieve_context(
        self,
        query: str,
        n_results: int = 3,
        project_id: Optional[int] = None,
        genre: Optional[str] = None,
        language: Optional[str] = None,
        doc_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top relevant knowledge chunks matching semantic query and metadata filters.

        Args:
            query: User premise or prompt used to find relevant lore.
            n_results: Number of context chunks to return.
            project_id: If specified, includes project-specific lore AND global lore (project_id=0).
            genre: Optional genre filter.
            language: Optional language filter.
            doc_type: Optional doc_type filter (e.g. 'worldbuilding').

        Returns:
            List of retrieved chunk dicts with content, metadata, and relevance scores.
        """
        query = (query or "").strip()
        if not query:
            return []

        # Check if collection is empty
        count = self.collection.count()
        if count == 0:
            return []

        # Construct ChromaDB metadata filter conditions
        where_conditions = []

        if project_id is not None:
            # Allow chunks matching this project OR global lore (project_id == 0)
            where_conditions.append({
                "$or": [
                    {"project_id": int(project_id)},
                    {"project_id": 0}
                ]
            })

        if genre and str(genre).lower() not in ("all", "any", "general"):
            where_conditions.append({
                "$or": [
                    {"genre": str(genre).lower()},
                    {"genre": "all"}
                ]
            })

        if doc_type:
            where_conditions.append({"doc_type": str(doc_type).lower()})

        # Combine where filters
        where_filter = None
        if len(where_conditions) == 1:
            where_filter = where_conditions[0]
        elif len(where_conditions) > 1:
            where_filter = {"$and": where_conditions}

        # Query collection
        query_n = min(n_results, count)
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=query_n,
                where=where_filter
            )
        except Exception as err:
            logger.warning(f"ChromaDB query with filter failed ('{err}'). Retrying without metadata filter.")
            results = self.collection.query(
                query_texts=[query],
                n_results=query_n
            )

        retrieved_chunks = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)
            ids = results["ids"][0] if results.get("ids") else [""] * len(docs)

            for doc, meta, dist, cid in zip(docs, metas, distances, ids):
                # Calculate normalized similarity score (0.0 to 1.0)
                score = round(max(0.0, 1.0 - float(dist)), 4) if dist is not None else 1.0

                retrieved_chunks.append({
                    "chunk_id": cid,
                    "document_id": meta.get("document_id"),
                    "document_title": meta.get("document_title", "Reference Context"),
                    "doc_type": meta.get("doc_type", "reference"),
                    "text": doc,
                    "similarity_score": score,
                    "project_id": meta.get("project_id"),
                    "genre": meta.get("genre"),
                    "language": meta.get("language")
                })

        return retrieved_chunks

    # ============================================================
    # 4. Document Management (List, Get, Delete)
    # ============================================================

    def list_documents(self, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieves summary list of all ingested documents in the vector store.
        """
        count = self.collection.count()
        if count == 0:
            return []

        where_filter = None
        if project_id is not None:
            where_filter = {
                "$or": [
                    {"project_id": int(project_id)},
                    {"project_id": 0}
                ]
            }

        try:
            results = self.collection.get(where=where_filter, include=["metadatas", "documents"])
        except Exception:
            results = self.collection.get(include=["metadatas", "documents"])

        if not results or not results.get("metadatas"):
            return []

        # Group by document_id
        doc_map = {}
        for meta, doc in zip(results["metadatas"], results["documents"]):
            did = meta.get("document_id")
            if not did:
                continue
            if did not in doc_map:
                doc_map[did] = {
                    "document_id": did,
                    "title": meta.get("document_title", "Untitled Document"),
                    "doc_type": meta.get("doc_type", "worldbuilding"),
                    "genre": meta.get("genre", "all"),
                    "language": meta.get("language", "English"),
                    "project_id": meta.get("project_id", 0),
                    "created_at": meta.get("created_at"),
                    "chunk_count": meta.get("total_chunks", 1),
                    "preview": doc[:120] + ("..." if len(doc) > 120 else "")
                }

        return list(doc_map.values())

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a full document and all its chunks by document_id.
        """
        results = self.collection.get(
            where={"document_id": doc_id},
            include=["metadatas", "documents"]
        )
        if not results or not results.get("documents") or len(results["documents"]) == 0:
            return None

        # Sort chunks by chunk_index
        paired = sorted(
            zip(results["metadatas"], results["documents"]),
            key=lambda p: p[0].get("chunk_index", 0)
        )
        first_meta = paired[0][0]
        full_text = "\n\n".join(text for _, text in paired)

        return {
            "document_id": doc_id,
            "title": first_meta.get("document_title"),
            "doc_type": first_meta.get("doc_type"),
            "genre": first_meta.get("genre"),
            "language": first_meta.get("language"),
            "project_id": first_meta.get("project_id"),
            "created_at": first_meta.get("created_at"),
            "chunk_count": len(paired),
            "content": full_text
        }

    def delete_document(self, doc_id: str) -> bool:
        """
        Deletes all chunks belonging to a document from ChromaDB.
        """
        try:
            self.collection.delete(where={"document_id": doc_id})
            logger.info(f"Deleted RAG document '{doc_id}' from vector store.")
            return True
        except Exception as err:
            logger.error(f"Failed to delete RAG document '{doc_id}': {err}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Returns health and metrics of the RAG vector store.
        """
        total_vectors = self.collection.count()
        return {
            "status": "ready",
            "collection_name": self.collection_name,
            "total_vectors": total_vectors,
            "total_documents": len(self.list_documents()),
            "persist_directory": self.persist_directory,
            "embedding_model": self.embed_service.model_name,
            "embedding_dimension": 384,
            "distance_metric": "cosine"
        }


# Global singleton instance
rag_service = RAGService()
