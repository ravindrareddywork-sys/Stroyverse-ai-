"""
StoryVerse AI — Database Model Tests
=======================================
Tests for:
  - Project model CRUD operations (Create, Read, Update, Delete)
  - GenerationHistory model CRUD operations
  - Foreign-key relationship between Project and GenerationHistory
  - Cascade deletion (deleting a Project removes its history)
  - Invalid data handling

These tests use the in-memory SQLite test database defined in conftest.py.

IMPORTANT: The Project model uses 'content_type' (not 'project_type').
           Allowed values: 'story', 'script', 'character'
"""

import pytest
from extensions import db as _db
from models import Project, GenerationHistory


class TestProjectModel:
    """Tests for the Project database model."""

    def test_create_project(self, db_session, app):
        """A Project can be saved to the database and retrieved."""
        with app.app_context():
            project = Project(
                title="My First Story",
                content_type="story",
                genre="Fantasy",
                language="English",
            )
            _db.session.add(project)
            _db.session.commit()

            retrieved = _db.session.get(Project, project.id)
            assert retrieved is not None
            assert retrieved.title == "My First Story"
            assert retrieved.content_type == "story"

    def test_project_to_dict(self, db_session, app):
        """to_dict() must return a plain dictionary with all required keys."""
        with app.app_context():
            project = Project(
                title="Dict Test",
                content_type="script",
                genre="Drama",
                language="Hindi",
            )
            _db.session.add(project)
            _db.session.commit()

            d = project.to_dict()
            assert isinstance(d, dict)
            # Verify all required keys are present in the serialized output
            for key in ("id", "title", "content_type", "genre", "language",
                        "created_at", "updated_at"):
                assert key in d, f"Missing key in to_dict(): {key}"

    def test_project_requires_title(self, db_session, app):
        """Creating a Project without a title should raise an IntegrityError."""
        with app.app_context():
            project = Project(content_type="story")   # title missing (nullable=False)
            _db.session.add(project)
            with pytest.raises(Exception):   # IntegrityError or similar
                _db.session.commit()
            _db.session.rollback()

    def test_project_requires_content_type(self, db_session, app):
        """Creating a Project without content_type should use the default 'story'."""
        with app.app_context():
            # content_type has default="story", so this should succeed
            project = Project(title="No Explicit Type Project")
            _db.session.add(project)
            _db.session.commit()
            assert project.content_type == "story"   # default applied

    def test_project_update_from_dict(self, db_session, app):
        """update_from_dict() must update only provided fields."""
        with app.app_context():
            project = Project(
                title="Original", content_type="story", genre="Horror", language="English"
            )
            _db.session.add(project)
            _db.session.commit()

            project.update_from_dict({"title": "Updated Title", "genre": "Comedy"})
            _db.session.commit()

            refreshed = _db.session.get(Project, project.id)
            assert refreshed.title == "Updated Title"
            assert refreshed.genre == "Comedy"
            assert refreshed.content_type == "story"   # unchanged

    def test_multiple_projects_unique_ids(self, db_session, app):
        """Multiple projects can coexist with unique IDs."""
        with app.app_context():
            p1 = Project(title="Alpha", content_type="story", genre="Thriller", language="English")
            p2 = Project(title="Beta",  content_type="script", genre="Comedy",   language="Telugu")
            _db.session.add_all([p1, p2])
            _db.session.commit()
            assert p1.id != p2.id

    def test_project_tone_stored(self, db_session, app):
        """Optional fields like tone are persisted correctly."""
        with app.app_context():
            project = Project(
                title="Tone Test", content_type="story",
                genre="Drama", language="Tamil", tone="Emotional"
            )
            _db.session.add(project)
            _db.session.commit()
            retrieved = _db.session.get(Project, project.id)
            assert retrieved.tone == "Emotional"

    def test_timestamps_set_on_creation(self, db_session, app):
        """created_at and updated_at must be set automatically."""
        with app.app_context():
            project = Project(title="Timestamp Test", content_type="story")
            _db.session.add(project)
            _db.session.commit()
            assert project.created_at is not None
            assert project.updated_at is not None


class TestGenerationHistoryModel:
    """Tests for the GenerationHistory database model."""

    def test_create_history_record(self, db_session, app):
        """A GenerationHistory record can be created linked to a Project."""
        with app.app_context():
            project = Project(
                title="History Test Project", content_type="story",
                genre="Mystery", language="English"
            )
            _db.session.add(project)
            _db.session.commit()

            history = GenerationHistory(
                project_id=project.id,
                operation="generate",
                content_type="story",
                content_snapshot="Once upon a time...",
                input_summary="Topic: magic, Genre: Fantasy",
                ai_model="gemini-2.0-flash",
                tokens_used=512,
            )
            _db.session.add(history)
            _db.session.commit()

            retrieved = _db.session.get(GenerationHistory, history.id)
            assert retrieved is not None
            assert retrieved.project_id == project.id
            assert retrieved.operation == "generate"
            assert retrieved.tokens_used == 512

    def test_history_to_dict(self, db_session, app):
        """GenerationHistory.to_dict() must include all required keys."""
        with app.app_context():
            project = Project(
                title="Dict History Project", content_type="script",
                genre="Drama", language="Tamil"
            )
            _db.session.add(project)
            _db.session.commit()

            history = GenerationHistory(
                project_id=project.id,
                operation="regenerate",
                content_type="script",
            )
            _db.session.add(history)
            _db.session.commit()

            d = history.to_dict()
            for key in ("id", "project_id", "operation", "content_type", "created_at"):
                assert key in d, f"Missing key in to_dict(): {key}"

    def test_history_multiple_records_per_project(self, db_session, app):
        """A single project can have multiple history records."""
        with app.app_context():
            project = Project(title="Multi-History", content_type="story", genre="Sci-Fi")
            _db.session.add(project)
            _db.session.commit()

            ops = ["generate", "expand", "shorten"]
            for op in ops:
                h = GenerationHistory(
                    project_id=project.id,
                    operation=op,
                    content_type="story",
                )
                _db.session.add(h)
            _db.session.commit()

            count = _db.session.query(GenerationHistory).filter_by(
                project_id=project.id
            ).count()
            assert count == 3


class TestCascadeDelete:
    """Tests that deleting a Project also deletes its GenerationHistory."""

    def test_cascade_delete(self, db_session, app):
        """
        When a Project is deleted, all linked GenerationHistory rows
        must be automatically deleted too (cascade="all, delete-orphan").
        """
        with app.app_context():
            project = Project(
                title="Cascade Test Project",
                content_type="story",
                genre="Sci-Fi",
                language="English",
            )
            _db.session.add(project)
            _db.session.commit()
            project_id = project.id

            # Add two history records
            for i in range(2):
                h = GenerationHistory(
                    project_id=project_id,
                    operation="generate",
                    content_type="story",
                    content_snapshot=f"Content version {i}",
                )
                _db.session.add(h)
            _db.session.commit()

            # Confirm history exists before deletion
            count_before = _db.session.query(GenerationHistory).filter_by(
                project_id=project_id
            ).count()
            assert count_before == 2, f"Expected 2 history rows, found {count_before}"

            # Delete the project — cascade should remove history automatically
            _db.session.delete(project)
            _db.session.commit()

            # History must also be gone
            count_after = _db.session.query(GenerationHistory).filter_by(
                project_id=project_id
            ).count()
            assert count_after == 0, (
                f"Expected 0 history rows after project deletion, found {count_after}"
            )

            # Project itself must be gone
            assert _db.session.get(Project, project_id) is None

    def test_delete_project_without_history(self, db_session, app):
        """Deleting a project with no history records must still succeed."""
        with app.app_context():
            project = Project(title="Lone Project", content_type="script", genre="Drama")
            _db.session.add(project)
            _db.session.commit()
            pid = project.id

            _db.session.delete(project)
            _db.session.commit()

            assert _db.session.get(Project, pid) is None
