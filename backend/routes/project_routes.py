"""
StoryVerse AI — Project Management Routes
============================================
Flask Blueprint providing REST API endpoints for:
  - POST /api/projects                             : Create a new project
  - GET  /api/projects                             : List and search projects with pagination
  - GET  /api/projects/<id>                        : Retrieve single project by ID
  - PUT  /api/projects/<id>                        : Update an existing project
  - DELETE /api/projects/<id>                      : Delete project safely
  - POST /api/projects/<id>/versions               : Save project version snapshot
  - GET  /api/projects/<id>/versions               : Retrieve version history
  - GET  /api/projects/<id>/versions/<version_id>  : Retrieve single version snapshot
  - POST /api/projects/<id>/versions/<version_id>/restore : Restore project to version
"""

import logging
from flask import Blueprint, request

from extensions import limiter
from services.project_service import project_service
from utils.validators import validate_project_input, validate_version_input
from utils.response import (
    success_response,
    created_response,
    error_response,
    not_found_response,
    server_error_response,
)

logger = logging.getLogger(__name__)

project_bp = Blueprint("projects", __name__)


@project_bp.route("/projects", methods=["POST"])
@limiter.limit("60 per minute")
def create_project():
    """
    POST /api/projects
    Creates a new creative project with title, type, content, genre, and metadata.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_project_input(data, is_update=False)
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        result = project_service.create_project(data)
        return created_response("Project created successfully.", data=result)

    except Exception as err:
        logger.error("Error creating project: %s", err, exc_info=True)
        return server_error_response("Failed to create project due to an internal error.")


@project_bp.route("/projects", methods=["GET"])
@limiter.limit("120 per minute")
def get_projects():
    """
    GET /api/projects
    Lists saved projects with filtering, searching, sorting, and pagination.
    """
    try:
        params = {
            "search": request.args.get("search") or request.args.get("q"),
            "project_type": request.args.get("project_type") or request.args.get("content_type"),
            "genre": request.args.get("genre"),
            "page": request.args.get("page", 1),
            "per_page": request.args.get("per_page", 10),
            "sort_by": request.args.get("sort_by", "updated_at"),
            "order": request.args.get("order", "desc"),
        }

        result = project_service.get_projects(params)
        return success_response("Projects retrieved successfully.", data=result, status_code=200)

    except Exception as err:
        logger.error("Error retrieving projects: %s", err, exc_info=True)
        return server_error_response("Failed to retrieve projects.")


@project_bp.route("/projects/<int:project_id>", methods=["GET"])
@limiter.limit("120 per minute")
def get_project(project_id):
    """
    GET /api/projects/<id>
    Retrieves a single project by ID including its generation history trail.
    """
    try:
        project = project_service.get_project_by_id(project_id, include_history=True)
        if not project:
            return not_found_response(f"Project with ID #{project_id} not found.")

        return success_response("Project retrieved successfully.", data=project, status_code=200)

    except Exception as err:
        logger.error("Error retrieving project #%d: %s", project_id, err, exc_info=True)
        return server_error_response("Failed to retrieve project.")


@project_bp.route("/projects/<int:project_id>", methods=["PUT"])
@limiter.limit("60 per minute")
def update_project(project_id):
    """
    PUT /api/projects/<id>
    Updates an existing project's title, content, genre, or parameters.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_project_input(data, is_update=True)
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        result = project_service.update_project(project_id, data)
        if not result:
            return not_found_response(f"Project with ID #{project_id} not found.")

        return success_response("Project updated successfully.", data=result, status_code=200)

    except Exception as err:
        logger.error("Error updating project #%d: %s", project_id, err, exc_info=True)
        return server_error_response("Failed to update project.")


@project_bp.route("/projects/<int:project_id>", methods=["DELETE"])
@limiter.limit("30 per minute")
def delete_project(project_id):
    """
    DELETE /api/projects/<id>
    Safely deletes a project and cascades history records.
    """
    try:
        deleted = project_service.delete_project(project_id)
        if not deleted:
            return not_found_response(f"Project with ID #{project_id} not found.")

        return success_response("Project deleted successfully.", data={"id": project_id}, status_code=200)

    except Exception as err:
        logger.error("Error deleting project #%d: %s", project_id, err, exc_info=True)
        return server_error_response("Failed to delete project.")


@project_bp.route("/projects/<int:project_id>/versions", methods=["POST"])
@limiter.limit("60 per minute")
def save_project_version(project_id):
    """
    POST /api/projects/<id>/versions
    Saves an explicit content version snapshot in generation history.
    """
    try:
        data = request.get_json(silent=True) or {}
        errors = validate_version_input(data)
        if errors:
            return error_response("Validation failed. Please check your inputs.", errors=errors, status_code=400)

        version = project_service.save_version(project_id, data)
        if not version:
            return not_found_response(f"Project with ID #{project_id} not found.")

        return created_response("Project version saved successfully.", data=version)

    except Exception as err:
        logger.error("Error saving version for project #%d: %s", project_id, err, exc_info=True)
        return server_error_response("Failed to save project version.")


@project_bp.route("/projects/<int:project_id>/versions", methods=["GET"])
@limiter.limit("120 per minute")
def get_project_versions(project_id):
    """
    GET /api/projects/<id>/versions
    Retrieves all version snapshots in chronological order.
    """
    try:
        order = request.args.get("order", "asc")
        versions = project_service.get_versions(project_id, order=order)
        if versions is None:
            return not_found_response(f"Project with ID #{project_id} not found.")

        return success_response("Version history retrieved successfully.", data=versions, status_code=200)

    except Exception as err:
        logger.error("Error retrieving versions for project #%d: %s", project_id, err, exc_info=True)
        return server_error_response("Failed to retrieve version history.")


@project_bp.route("/projects/<int:project_id>/versions/<int:version_id>", methods=["GET"])
@limiter.limit("120 per minute")
def get_project_version(project_id, version_id):
    """
    GET /api/projects/<id>/versions/<version_id>
    Retrieves a single version snapshot by ID.
    """
    try:
        version = project_service.get_version(project_id, version_id)
        if not version:
            return not_found_response(
                f"Version #{version_id} not found for project #{project_id}."
            )

        return success_response("Version snapshot retrieved successfully.", data=version, status_code=200)

    except Exception as err:
        logger.error("Error retrieving version #%d for project #%d: %s", version_id, project_id, err, exc_info=True)
        return server_error_response("Failed to retrieve version snapshot.")


@project_bp.route("/projects/<int:project_id>/versions/<int:version_id>/restore", methods=["POST"])
@limiter.limit("30 per minute")
def restore_project_version(project_id, version_id):
    """
    POST /api/projects/<id>/versions/<version_id>/restore
    Restores the project's content to the specified past snapshot.
    """
    try:
        restored = project_service.restore_version(project_id, version_id)
        if not restored:
            return not_found_response(
                f"Version #{version_id} not found for project #{project_id}."
            )

        return success_response("Project successfully restored to version snapshot.", data=restored, status_code=200)

    except Exception as err:
        logger.error("Error restoring version #%d for project #%d: %s", version_id, project_id, err, exc_info=True)
        return server_error_response("Failed to restore project version.")
