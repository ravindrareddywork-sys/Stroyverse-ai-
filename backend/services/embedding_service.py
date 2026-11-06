"""
StoryVerse AI — Multilingual Embedding Service
=================================================
Provides text embeddings using Sentence Transformers for semantic retrieval in RAG.
Supports multilingual encoding (English, Telugu, Tamil, Hindi, and 50+ languages).

Architecture:
  - SentenceTransformer model: defaults to 'all-MiniLM-L6-v2' (or multilingual MiniLM)
  - Lazy loading: Model is initialized on first encode call to preserve fast app startup
  - Deterministic Mock Mode: Explicitly enabled for unit testing only
"""

import os
import re
import math
import hashlib
import logging
from typing import List, Optional

from .rag_errors import RAGUnavailableError

logger = logging.getLogger(__name__)

# Default embedding model (multilingual-e5-small: high-performance 384-d dense vectors across 100+ languages including Telugu, Tamil, Hindi)
DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-small"
EMBEDDING_DIMENSION = 384


class EmbeddingService:
    """
    Manages text and query vector embeddings for semantic similarity search.
    Supports multilingual encoding with E5 models (intfloat/multilingual-e5-small).
    """

    def __init__(self, model_name: Optional[str] = None, mock_mode: Optional[bool] = None, force_mock: Optional[bool] = None):
        self.model_name = model_name or os.environ.get("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
        self._model = None
        self._mock_mode = force_mock if force_mock is not None else mock_mode

    @property
    def is_mock_mode(self) -> bool:
        """Determines if mock embedding mode should be used."""
        if self._mock_mode is not None:
            return self._mock_mode
        # Inherit from global AI_MOCK_MODE if not explicitly set
        env_val = os.environ.get("AI_MOCK_MODE", "false").lower()
        return env_val in ("true", "1", "yes")

    def _get_model(self):
        """Lazy loader for the SentenceTransformer neural model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info("SentenceTransformer model loaded successfully.")
            except Exception as err:
                logger.exception("Could not load SentenceTransformer model '%s'.", self.model_name)
                raise RAGUnavailableError(
                    f"The configured RAG embedding model '{self.model_name}' is unavailable. "
                    "Check backend logs and model download/runtime configuration."
                ) from err
        return self._model

    def _format_text(self, text: str, is_query: bool = False) -> str:
        """Applies required 'query: ' or 'passage: ' prefix for E5 models."""
        text = (text or "").strip()
        if not text:
            return ""
        if "e5" in self.model_name.lower():
            if is_query:
                if not text.startswith("query:"):
                    return f"query: {text}"
            else:
                if not text.startswith("passage:"):
                    return f"passage: {text}"
        return text

    def encode(self, texts: List[str]) -> List[List[float]]:
        """
        Generates dense vector embeddings for a list of text strings.

        Args:
            texts: List of text passages/chunks.

        Returns:
            List of 384-dimensional float embedding vectors.
        """
        if not texts:
            return []

        if self.is_mock_mode:
            return [self._generate_mock_vector(t) for t in texts]

        try:
            model = self._get_model()
            if model is not None and not self.is_mock_mode:
                embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
                return embeddings.tolist()
        except Exception as err:
            if isinstance(err, RAGUnavailableError):
                raise
            logger.exception("SentenceTransformer encoding failed for model '%s'.", self.model_name)
            raise RAGUnavailableError(
                f"The configured RAG embedding model '{self.model_name}' failed to encode text."
            ) from err

        raise RAGUnavailableError(
            f"The configured RAG embedding model '{self.model_name}' is unavailable."
        )

    def encode_passages(self, texts: List[str]) -> List[List[float]]:
        """Encodes passages/documents for vector indexing with 'passage: ' prefix for E5."""
        formatted = [self._format_text(t, is_query=False) for t in texts]
        return self.encode(formatted)

    def encode_queries(self, queries: List[str]) -> List[List[float]]:
        """Encodes search queries with 'query: ' prefix for E5."""
        formatted = [self._format_text(q, is_query=True) for q in queries]
        return self.encode(formatted)

    def encode_query(self, query: str) -> List[float]:
        """
        Generates dense vector embedding for a single search query.

        Args:
            query: User search query or premise text.

        Returns:
            384-dimensional float vector.
        """
        vectors = self.encode_queries([query])
        return vectors[0] if vectors else [0.0] * EMBEDDING_DIMENSION

    def get_embedding(self, text: str) -> List[float]:
        """Convenience alias for encode_query()."""
        return self.encode_query(text)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Convenience alias for encode()."""
        return self.encode_passages(texts)

    def _generate_mock_vector(self, text: str) -> List[float]:
        """
        Generates a deterministic, normalized 384-dimensional pseudo-embedding vector.
        Semantic similarity is preserved for identical or overlapping terms using character-trigram hashing.
        Strips 'query: ' and 'passage: ' prefixes so matching terms align symmetrically.
        """
        if not text:
            return [0.0] * EMBEDDING_DIMENSION

        # Strip prefixes for symmetric mock matching
        clean_text = re.sub(r"^(query|passage):\s*", "", text.strip(), flags=re.IGNORECASE)

        vec = [0.0] * EMBEDDING_DIMENSION
        text_lower = clean_text.lower()

        # Seed vector using word and character trigram hashes
        words = text_lower.split()
        for w in words:
            h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16)
            idx = h % EMBEDDING_DIMENSION
            vec[idx] += 1.0

        # Add trigrams for sub-word semantic overlap
        for i in range(len(text_lower) - 2):
            tri = text_lower[i:i+3]
            h = int(hashlib.sha256(tri.encode("utf-8")).hexdigest(), 16)
            idx = h % EMBEDDING_DIMENSION
            vec[idx] += 0.5

        # L2-normalize the vector
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        else:
            vec[0] = 1.0

        return vec


# Singleton instance
embedding_service = EmbeddingService()
