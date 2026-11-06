"""
StoryVerse AI — Project Service Layer
========================================
Business logic and persistence operations for user creative projects:
  - Project creation, retrieval, updates, and deletion
  - Filtering, searching, sorting, and pagination
  - Snapshot version history and restore capabilities
  - Cascade management and transactional integrity
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from sqlalchemy import or_, desc, asc
from extensions import db
from models.project import Project
from models.generation_history import GenerationHistory

logger = logging.getLogger(__name__)


class ProjectService:
    """
    Coordinates database persistence, versioning, and retrieval of creative writing projects.
    """

    def create_project(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates and persists a new Project.

        Args:
            data: Validated project payload.

        Returns:
            dict: The newly created project as a dictionary.
        """
        content_type = (
            data.get("content_type")
            or data.get("project_type")
            or "story"
        ).strip().lower()

        content = (
            data.get("generated_content")
            if "generated_content" in data
            else data.get("content")
        )
        if content:
            content = content.strip()

        desc_val = (
            data.get("description")
            or data.get("topic")
            or ""
        ).strip() or None

        project = Project(
            title=data["title"].strip(),
            content_type=content_type,
            genre=(data.get("genre") or "").strip() or None,
            language=(data.get("language") or "English").strip(),
            tone=(data.get("tone") or "").strip() or None,
            topic=desc_val,
            description=desc_val,
            generated_content=content,
        )

        try:
            db.session.add(project)
            db.session.flush()  # Assigns primary key id

            # If initial content is provided, create the initial version record
            if content:
                history_entry = GenerationHistory(
                    project_id=project.id,
                    operation="initial_save",
                    content_type=content_type,
                    content_snapshot=content,
                    input_summary=f"Initial {content_type} creation",
                    ai_model=data.get("ai_model") or "Manual / System",
                )
                db.session.add(history_entry)

            db.session.commit()
            logger.info("Created project #%d ('%s')", project.id, project.title)
            return project.to_dict()

        except Exception as err:
            db.session.rollback()
            logger.error("Failed to create project: %s", err, exc_info=True)
            raise

    def get_projects(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieves projects with filtering, searching, sorting, and pagination.

        Supported params:
          - search: Case-insensitive substring match on title or description
          - project_type / content_type: Filter by 'story', 'script', 'character', 'other'
          - genre: Filter by genre
          - page: 1-indexed page number (default: 1)
          - per_page: Items per page (default: 10, max: 100)
          - sort_by: 'updated_at' (default), 'created_at', or 'title'
          - order: 'desc' (default) or 'asc'

        Returns:
            dict containing:
              - 'projects': list of project dicts
              - 'pagination': page metadata
              - 'stats': counts per project type
        """
        params = params or {}

        # Parse pagination parameters
        try:
            page = max(1, int(params.get("page", 1)))
        except (ValueError, TypeError):
            page = 1

        try:
            per_page = max(1, min(100, int(params.get("per_page", 10))))
        except (ValueError, TypeError):
            per_page = 10

        query = Project.query

        # Compute global statistics for dashboard badges
        stats = {
            "total": Project.query.count(),
            "story": Project.query.filter_by(content_type="story").count(),
            "script": Project.query.filter_by(content_type="script").count(),
            "character": Project.query.filter_by(content_type="character").count(),
            "other": Project.query.filter_by(content_type="other").count(),
        }

        # Filtering by content_type / project_type
        target_type = (params.get("project_type") or params.get("content_type") or "").strip().lower()
        if target_type and target_type != "all":
            query = query.filter(Project.content_type == target_type)

        # Filtering by genre
        target_genre = (params.get("genre") or "").strip()
        if target_genre and target_genre.lower() != "all":
            query = query.filter(Project.genre.ilike(f"%{target_genre}%"))

        # Searching by query string
        search = (params.get("search") or params.get("q") or "").strip()
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Project.title.ilike(search_pattern),
                    Project.topic.ilike(search_pattern),
                    Project.description.ilike(search_pattern),
                )
            )

        # Sorting
        sort_by = (params.get("sort_by") or "updated_at").strip().lower()
        order = (params.get("order") or "desc").strip().lower()

        sort_col = Project.updated_at
        if sort_by == "created_at":
            sort_col = Project.created_at
        elif sort_by == "title":
            sort_col = Project.title

        query = query.order_by(desc(sort_col) if order == "desc" else asc(sort_col))

        # Paginate results
        total = query.count()
        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        items = query.offset(offset).limit(per_page).all()

        return {
            "projects": [p.to_dict() for p in items],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": pages,
                "has_next": page < pages,
                "has_prev": page > 1,
            },
            "stats": stats,
        }

    def get_project_by_id(self, project_id: int, include_history: bool = False) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single project by its primary key ID.
        """
        project = Project.query.get(project_id)
        if not project:
            return None
        return project.to_dict(include_history=include_history)

    def update_project(self, project_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates an existing project and snapshots changes into history if content changed.
        """
        project = Project.query.get(project_id)
        if not project:
            return None

        # Check if content changed
        new_content = data.get("generated_content") if "generated_content" in data else data.get("content")
        has_new_content = new_content is not None and new_content.strip() != (project.generated_content or "").strip()

        project.update_from_dict(data)

        try:
            if has_new_content:
                history_entry = GenerationHistory(
                    project_id=project.id,
                    operation="update",
                    content_type=project.content_type,
                    content_snapshot=project.generated_content,
                    input_summary=data.get("summary") or f"Manual update to '{project.title}'",
                )
                db.session.add(history_entry)

            db.session.commit()
            logger.info("Updated project #%d ('%s')", project.id, project.title)
            return project.to_dict()

        except Exception as err:
            db.session.rollback()
            logger.error("Failed to update project #%d: %s", project_id, err, exc_info=True)
            raise

    def delete_project(self, project_id: int) -> bool:
        """
        Safely deletes a project and cascades deletion of its history records.
        """
        project = Project.query.get(project_id)
        if not project:
            return False

        try:
            db.session.delete(project)
            db.session.commit()
            logger.info("Deleted project #%d", project_id)
            return True
        except Exception as err:
            db.session.rollback()
            logger.error("Failed to delete project #%d: %s", project_id, err, exc_info=True)
            raise

    def save_version(self, project_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Creates an explicit version snapshot in GenerationHistory.
        """
        project = Project.query.get(project_id)
        if not project:
            return None

        content = data.get("content") if "content" in data else data.get("generated_content")
        if content is None:
            content = project.generated_content or ""

        summary = (
            data.get("summary")
            or data.get("version_note")
            or data.get("input_summary")
            or f"Version snapshot at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
        )

        history_entry = GenerationHistory(
            project_id=project.id,
            operation=data.get("operation") or "version_save",
            content_type=project.content_type,
            content_snapshot=content,
            input_summary=summary,
            ai_model=data.get("ai_model") or "User Snapshot",
            tokens_used=data.get("tokens_used"),
        )

        # Update project's current content and timestamp if content was provided
        if content:
            project.generated_content = content
            project.updated_at = datetime.now(timezone.utc)

        try:
            db.session.add(history_entry)
            db.session.commit()
            logger.info("Saved version #%d for project #%d", history_entry.id, project.id)
            return history_entry.to_dict()
        except Exception as err:
            db.session.rollback()
            logger.error("Failed to save version for project #%d: %s", project_id, err, exc_info=True)
            raise

    def get_versions(self, project_id: int, order: str = "asc") -> Optional[List[Dict[str, Any]]]:
        """
        Retrieves all version snapshots for a project in chronological (or reverse) order.
        """
        project = Project.query.get(project_id)
        if not project:
            return None

        query = GenerationHistory.query.filter_by(project_id=project_id)
        if order.lower() == "desc":
            query = query.order_by(desc(GenerationHistory.created_at), desc(GenerationHistory.id))
        else:
            query = query.order_by(asc(GenerationHistory.created_at), asc(GenerationHistory.id))

        records = query.all()
        return [r.to_dict() for r in records]

    def get_version(self, project_id: int, version_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single version snapshot and verifies it belongs to the given project.
        """
        version = GenerationHistory.query.filter_by(id=version_id, project_id=project_id).first()
        if not version:
            return None
        return version.to_dict()

    def restore_version(self, project_id: int, version_id: int) -> Optional[Dict[str, Any]]:
        """
        Restores a project's content to a designated previous version snapshot.
        """
        project = Project.query.get(project_id)
        if not project:
            return None

        version = GenerationHistory.query.filter_by(id=version_id, project_id=project_id).first()
        if not version:
            return None

        try:
            project.generated_content = version.content_snapshot
            project.updated_at = datetime.now(timezone.utc)

            # Record a new history snapshot documenting the restoration
            restore_entry = GenerationHistory(
                project_id=project.id,
                operation="restore_version",
                content_type=project.content_type,
                content_snapshot=project.generated_content,
                input_summary=f"Restored to version #{version_id}",
            )
            db.session.add(restore_entry)
            db.session.commit()

            logger.info("Restored project #%d to version #%d", project.id, version_id)
            return project.to_dict()

        except Exception as err:
            db.session.rollback()
            logger.error("Failed to restore version #%d for project #%d: %s", version_id, project_id, err, exc_info=True)
            raise


# Global default instance
project_service = ProjectService()
