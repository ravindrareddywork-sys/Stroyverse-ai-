"""
StoryVerse AI — RAG (Retrieval-Augmented Generation) Routes
============================================================
Flask Blueprint providing REST API endpoints for:
  - POST   /api/rag/ingest            : Ingests documents/lore into vector storage
  - GET    /api/rag/documents         : Lists ingested knowledge base documents
  - GET    /api/rag/documents/<doc_id>: Retrieves document details and full text
  - DELETE /api/rag/documents/<doc_id>: Deletes document from vector storage
  - POST   /api/rag/query             : Performs semantic vector similarity search
  - GET    /api/rag/status            : Vector database status and metrics
"""

import logging
from flask import Blueprint, request

from services.rag_service import rag_service
from services.rag_errors import RAGUnavailableError
from utils.validators import validate_rag_ingest_input, validate_rag_query_input
from utils.response import (
    success_response,
    created_response,
    error_response,
    not_found_response,
    server_error_response,
)

logger = logging.getLogger(__name__)

rag_bp = Blueprint("rag", __name__)


@rag_bp.route("/rag/ingest", methods=["POST"])
def ingest_document():
    """
    POST /api/rag/ingest
    Ingests reference lore, character notes, or worldbuilding documents
    into ChromaDB with sentence-transformers embeddings.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_rag_ingest_input(data)
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        p_id = data.get("project_id")
        project_id = int(p_id) if p_id is not None and str(p_id).strip() != "" else None

        result = rag_service.ingest_document(
            title=data.get("title"),
            content=data.get("content"),
            doc_type=data.get("doc_type", "worldbuilding"),
            genre=data.get("genre"),
            language=data.get("language", "English"),
            project_id=project_id,
            metadata=data.get("metadata")
        )
        return created_response("Document ingested into vector knowledge base successfully.", data=result)

    except RAGUnavailableError as err:
        return error_response(
            str(err),
            errors={"rag": "Semantic retrieval is unavailable."},
            status_code=503
        )
    except ValueError as val_err:
        return error_response(str(val_err), status_code=400)
    except Exception as err:
        logger.error(f"Error in /api/rag/ingest: {err}", exc_info=True)
        return server_error_response("Failed to ingest document into vector knowledge base.")


@rag_bp.route("/rag/documents", methods=["GET"])
def list_documents():
    """
    GET /api/rag/documents
    Lists all documents stored in the vector knowledge base, optionally
    filtered by project_id.
    """
    try:
        p_id_param = request.args.get("project_id")
        project_id = None
        if p_id_param is not None and p_id_param.strip() != "":
            try:
                project_id = int(p_id_param)
            except ValueError:
                return error_response("project_id query parameter must be an integer.", status_code=400)

        docs = rag_service.list_documents(project_id=project_id)
        return success_response(
            "Documents retrieved successfully.",
            data={"documents": docs, "total": len(docs)}
        )

    except RAGUnavailableError as err:
        return error_response(
            str(err),
            errors={"rag": "Semantic retrieval is unavailable."},
            status_code=503
        )
    except Exception as err:
        logger.error(f"Error in /api/rag/documents: {err}", exc_info=True)
        return server_error_response("Failed to retrieve documents.")


@rag_bp.route("/rag/documents/<doc_id>", methods=["GET"])
def get_document(doc_id):
    """
    GET /api/rag/documents/<doc_id>
    Retrieves full details and chunked contents for a specific document.
    """
    try:
        doc = rag_service.get_document(doc_id)
        if not doc:
            return not_found_response("Document not found in vector database.")

        return success_response("Document details retrieved successfully.", data=doc)

    except RAGUnavailableError as err:
        return error_response(
            str(err),
            errors={"rag": "Semantic retrieval is unavailable."},
            status_code=503
        )
    except Exception as err:
        logger.error(f"Error in /api/rag/documents/{doc_id}: {err}", exc_info=True)
        return server_error_response("Failed to retrieve document details.")


@rag_bp.route("/rag/documents/<doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    """
    DELETE /api/rag/documents/<doc_id>
    Removes document and all associated embeddings from ChromaDB.
    """
    try:
        doc = rag_service.get_document(doc_id)
        if not doc:
            return not_found_response("Document not found in vector database.")

        success = rag_service.delete_document(doc_id)
        if not success:
            return server_error_response("Failed to delete document from vector store.")

        return success_response(
            "Document removed from vector knowledge base successfully.",
            data={"document_id": doc_id}
        )

    except RAGUnavailableError as err:
        return error_response(
            str(err),
            errors={"rag": "Semantic retrieval is unavailable."},
            status_code=503
        )
    except Exception as err:
        logger.error(f"Error in DELETE /api/rag/documents/{doc_id}: {err}", exc_info=True)
        return server_error_response("Failed to delete document.")


@rag_bp.route("/rag/query", methods=["POST"])
def query_rag():
    """
    POST /api/rag/query
    Performs semantic vector retrieval against the knowledge base.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_rag_query_input(data)
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        query = data.get("query")
        n_results = int(data.get("n_results", rag_service.default_top_k))
        p_id = data.get("project_id")
        project_id = int(p_id) if p_id is not None and str(p_id).strip() != "" else None
        genre = data.get("genre")
        language = data.get("language")
        doc_type = data.get("doc_type")

        results = rag_service.retrieve_context(
            query=query,
            n_results=n_results,
            project_id=project_id,
            genre=genre,
            language=language,
            doc_type=doc_type
        )

        return success_response(
            "Semantic context retrieved successfully.",
            data={
                "query": query,
                "retrieved_chunks": results,
                "count": len(results),
                "embedding_mode": (
                    "deterministic_mock"
                    if rag_service.embed_service.is_mock_mode
                    else "sentence_transformers"
                )
            }
        )

    except RAGUnavailableError as err:
        return error_response(
            str(err),
            errors={"rag": "Semantic retrieval is unavailable."},
            status_code=503
        )
    except Exception as err:
        logger.error(f"Error in /api/rag/query: {err}", exc_info=True)
        return server_error_response("Failed to perform semantic retrieval.")


@rag_bp.route("/rag/status", methods=["GET"])
def get_status():
    """
    GET /api/rag/status
    Returns health status and metrics of the ChromaDB vector database.
    """
    try:
        status_data = rag_service.get_status()
        return success_response("RAG vector store status retrieved.", data=status_data)

    except RAGUnavailableError as err:
        return error_response(
            str(err),
            errors={"rag": "Semantic retrieval is unavailable."},
            status_code=503
        )
    except Exception as err:
        logger.error(f"Error in /api/rag/status: {err}", exc_info=True)
        return server_error_response("Failed to retrieve vector store status.")
