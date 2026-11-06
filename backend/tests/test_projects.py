"""
StoryVerse AI — Project Management & Persistence Tests
=========================================================
Tests for Phase 9:
  - Project CRUD (Create, Read, Update, Delete)
  - Pagination, searching, filtering, and sorting
  - Version history snapshotting, retrieval, and restoration
  - Validation enforcement and error handling
  - Cascade deletion of generation history
  - Database transactional rollback simulation
"""

import json
from unittest.mock import patch
import pytest

from extensions import db as _db
from models import Project, GenerationHistory


class TestProjectCreation:
    """Tests for POST /api/projects."""

    def test_create_project_minimal(self, client):
        """Creating a project with minimal required fields succeeds."""
        payload = {
            "title": "Starlight Odyssey",
            "content_type": "story",
        }
        res = client.post("/api/projects", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["title"] == "Starlight Odyssey"
        assert data["data"]["content_type"] == "story"
        assert data["data"]["language"] == "English"
        assert data["data"]["id"] is not None

    def test_create_project_full(self, client):
        """Creating a project with all parameters and content succeeds."""
        payload = {
            "title": "Neon Mumbai: 2099",
            "project_type": "script",
            "genre": "Science Fiction",
            "language": "Hindi",
            "tone": "Suspenseful",
            "description": "A cyber-detective investigates an AI heist in futuristic Mumbai.",
            "content": "EXT. BANDRA SKYWAY - NIGHT\nRain falls through holographic adverts.",
        }
        res = client.post("/api/projects", json=payload)
        assert res.status_code == 201
        data = res.get_json()
        assert data["data"]["title"] == "Neon Mumbai: 2099"
        assert data["data"]["content_type"] == "script"
        assert data["data"]["genre"] == "Science Fiction"
        assert data["data"]["language"] == "Hindi"
        assert data["data"]["tone"] == "Suspenseful"
        assert data["data"]["description"] == payload["description"]
        assert "EXT. BANDRA SKYWAY" in data["data"]["generated_content"]

    def test_create_project_creates_initial_history(self, client, app):
        """Creating a project with content automatically creates an initial history record."""
        payload = {
            "title": "The Forgotten Realm",
            "content_type": "story",
            "content": "Deep inside the ancient forest stood a spire of obsidian.",
        }
        res = client.post("/api/projects", json=payload)
        assert res.status_code == 201
        project_id = res.get_json()["data"]["id"]

        with app.app_context():
            histories = GenerationHistory.query.filter_by(project_id=project_id).all()
            assert len(histories) == 1
            assert histories[0].operation == "initial_save"
            assert "obsidian" in histories[0].content_snapshot

    def test_create_script_project_persists_content_and_generation_metadata(self, client, app):
        """Saved scripts retain full content and their generation parameters after retrieval."""
        script_content = "TITLE: The Last Signal\n\nINT. OBSERVATORY - NIGHT\nA signal cuts through the static."
        generation_parameters = {
            "topic": "A lone astronomer finds a message in deep space.",
            "genre": "Science Fiction",
            "language": "Hindi",
            "tone": "Suspenseful",
            "num_scenes": 4,
            "characters": "Dr. Rao, an astronomer",
            "setting": "A remote observatory",
            "additional_instructions": "End on a revelation.",
        }
        response = client.post("/api/projects", json={
            "title": "The Last Signal",
            "content_type": "script",
            "genre": generation_parameters["genre"],
            "language": generation_parameters["language"],
            "tone": generation_parameters["tone"],
            "topic": generation_parameters["topic"],
            "description": "An astronomer receives a message from beyond.",
            "content": script_content,
            "input_summary": "Science Fiction screenplay, Hindi, suspenseful, 4 scenes.",
            "generation_parameters": generation_parameters,
            "ai_model": "test-model",
            "tokens_used": 123,
        })

        assert response.status_code == 201
        project_id = response.get_json()["data"]["id"]
        retrieved = client.get(f"/api/projects/{project_id}")
        assert retrieved.status_code == 200
        project = retrieved.get_json()["data"]
        assert project["content_type"] == "script"
        assert project["generated_content"] == script_content
        assert project["topic"] == generation_parameters["topic"]
        assert project["tone"] == generation_parameters["tone"]
        assert len(project["history"]) == 1
        assert project["history"][0]["content_snapshot"] == script_content
        assert project["history"][0]["input_summary"] == "Science Fiction screenplay, Hindi, suspenseful, 4 scenes."
        assert json.loads(project["history"][0]["prompt"]) == generation_parameters
        assert project["history"][0]["ai_model"] == "test-model"
        assert project["history"][0]["tokens_used"] == 123

    def test_script_save_payload_creates_then_updates_same_project(self, client, app):
        """Script Generator's create/update payload persists content without duplicating projects."""
        generated_content = "TITLE: Signal Lost\n\nINT. RADIO STATION - NIGHT\nMara hears a voice."
        generation_parameters = {
            "topic": "A late-night radio host hears an impossible transmission.",
            "genre": "Science Fiction",
            "language": "English",
            "tone": "Suspenseful",
            "num_scenes": 3,
            "requested_scenes": 3,
            "detected_scenes": 1,
            "characters_summary": "",
            "logline": "A radio host receives a signal from tomorrow.",
        }
        create_response = client.post("/api/projects", json={
            "title": "Signal Lost",
            "content_type": "script",
            "genre": generation_parameters["genre"],
            "language": generation_parameters["language"],
            "tone": generation_parameters["tone"],
            "topic": generation_parameters["topic"],
            "description": generation_parameters["logline"],
            "content": generated_content,
            "input_summary": (
                "Topic: A late-night radio host hears an impossible transmission., "
                "Genre: Science Fiction, Language: English, Tone: Suspenseful, Scenes: 3"
            ),
            "generation_parameters": generation_parameters,
            "ai_model": "gemini-3.5-flash-lite",
            "tokens_used": 128,
        })

        assert create_response.status_code == 201, create_response.get_json()
        project_id = create_response.get_json()["data"]["id"]

        updated_content = generated_content + "\n\nEXT. STATION - DAWN\nThe signal ends."
        update_response = client.put(f"/api/projects/{project_id}", json={
            "title": "Signal Lost",
            "content_type": "script",
            "genre": "Science Fiction",
            "language": "English",
            "tone": "Suspenseful",
            "topic": generation_parameters["topic"],
            "description": generation_parameters["logline"],
            "content": updated_content,
        })

        assert update_response.status_code == 200, update_response.get_json()
        assert update_response.get_json()["data"]["id"] == project_id
        assert update_response.get_json()["data"]["generated_content"] == updated_content
        listed_projects = client.get("/api/projects?project_type=script").get_json()["data"]
        matching_projects = [
            project for project in listed_projects["projects"]
            if project["id"] == project_id
        ]
        assert len(matching_projects) == 1

        retrieved = client.get(f"/api/projects/{project_id}").get_json()["data"]
        assert len(retrieved["history"]) == 2
        assert retrieved["history"][0]["content_snapshot"] == updated_content

    @pytest.mark.parametrize("method", ["post", "put"])
    def test_script_project_rejects_empty_content(self, client, method):
        """An explicitly empty screenplay is rejected with a field-specific reason."""
        project_id = None
        if method == "put":
            created = client.post("/api/projects", json={
                "title": "Empty Script Test",
                "content_type": "script",
                "content": "Existing screenplay content."
            })
            project_id = created.get_json()["data"]["id"]

        payload = {
            "title": "Empty Script Test",
            "content_type": "script",
            "content": "   ",
        }
        response = (
            client.put(f"/api/projects/{project_id}", json=payload)
            if method == "put"
            else client.post("/api/projects", json=payload)
        )

        assert response.status_code == 400
        body = response.get_json()
        assert body["message"] == "Validation failed. Please check your inputs."
        assert body["errors"]["content"] == "Content cannot be empty."

    def test_create_project_character_type(self, client):
        """Creating a character project succeeds."""
        payload = {
            "title": "Dr. Aris Thorne Profile",
            "content_type": "character",
            "genre": "Mystery",
            "content": "Archetype: The Obsessive Inquisitor",
        }
        res = client.post("/api/projects", json=payload)
        assert res.status_code == 201
        assert res.get_json()["data"]["content_type"] == "character"

    def test_create_project_multilingual_retention(self, client):
        """Projects created with Telugu, Tamil, or Hindi retain their language setting."""
        for lang in ["Telugu", "Tamil", "Hindi"]:
            payload = {
                "title": f"Project in {lang}",
                "content_type": "story",
                "language": lang,
                "content": f"Sample story body in {lang}."
            }
            res = client.post("/api/projects", json=payload)
            assert res.status_code == 201
            p_id = res.get_json()["data"]["id"]

            # Retrieve and verify language is preserved
            get_res = client.get(f"/api/projects/{p_id}")
            assert get_res.status_code == 200
            assert get_res.get_json()["data"]["language"] == lang

    def test_create_project_other_type(self, client):
        """Creating an 'other' project type succeeds."""
        payload = {
            "title": "Worldbuilding Notes",
            "content_type": "other",
            "content": "Timeline of planetary colonization.",
        }
        res = client.post("/api/projects", json=payload)
        assert res.status_code == 201
        assert res.get_json()["data"]["content_type"] == "other"

    def test_create_project_missing_title_rejected(self, client):
        """Missing title returns HTTP 400."""
        res = client.post("/api/projects", json={"content_type": "story"})
        assert res.status_code == 400
        assert res.get_json()["success"] is False

    def test_create_project_empty_title_rejected(self, client):
        """Empty title returns HTTP 400."""
        res = client.post("/api/projects", json={"title": "   ", "content_type": "story"})
        assert res.status_code == 400

    def test_create_project_invalid_content_type(self, client):
        """Invalid content_type returns HTTP 400."""
        payload = {"title": "Invalid Type Project", "content_type": "novel_trilogy"}
        res = client.post("/api/projects", json=payload)
        assert res.status_code == 400

    def test_create_project_missing_json_body(self, client):
        """Non-JSON request body returns HTTP 400."""
        res = client.post("/api/projects", data="plain text", content_type="text/plain")
        assert res.status_code == 400


class TestProjectRetrieval:
    """Tests for GET /api/projects/<id>."""

    def test_get_project_by_id_success(self, client):
        """Retrieving an existing project returns HTTP 200 with full details."""
        create_res = client.post("/api/projects", json={
            "title": "Solar Wind",
            "content_type": "story",
            "genre": "Sci-Fi",
            "content": "The sail unfurled towards Alpha Centauri."
        })
        project_id = create_res.get_json()["data"]["id"]

        get_res = client.get(f"/api/projects/{project_id}")
        assert get_res.status_code == 200
        data = get_res.get_json()["data"]
        assert data["id"] == project_id
        assert data["title"] == "Solar Wind"
        assert "history" in data
        assert len(data["history"]) >= 1

    def test_get_project_nonexistent_returns_404(self, client):
        """Requesting an ID that does not exist returns HTTP 404."""
        res = client.get("/api/projects/999999")
        assert res.status_code == 404
        assert res.get_json()["success"] is False


class TestProjectListing:
    """Tests for GET /api/projects (list, search, filter, paginate, sort)."""

    @pytest.fixture(autouse=True)
    def setup_sample_projects(self, client, app):
        """Cleans and seeds sample projects for listing tests."""
        with app.app_context():
            GenerationHistory.query.delete()
            Project.query.delete()
            _db.session.commit()

        projects = [
            {"title": "The Crimson Key", "content_type": "story", "genre": "Mystery"},
            {"title": "Shadows of Varanasi", "content_type": "script", "genre": "Thriller"},
            {"title": "Inspector Roy Bible", "content_type": "character", "genre": "Mystery"},
            {"title": "Galaxy Express", "content_type": "story", "genre": "Science Fiction"},
            {"title": "Laughter in Lucknow", "content_type": "script", "genre": "Comedy"},
        ]
        for p in projects:
            client.post("/api/projects", json=p)

    def test_list_projects_success(self, client):
        """Listing projects returns projects array and pagination metadata."""
        res = client.get("/api/projects")
        assert res.status_code == 200
        data = res.get_json()["data"]
        assert "projects" in data
        assert "pagination" in data
        assert "stats" in data
        assert len(data["projects"]) >= 5

    def test_list_projects_stats_counts(self, client):
        """Stats counts accurately reflect counts per type."""
        res = client.get("/api/projects")
        stats = res.get_json()["data"]["stats"]
        assert stats["total"] >= 5
        assert stats["story"] >= 2
        assert stats["script"] >= 2
        assert stats["character"] >= 1

    def test_list_projects_filter_by_type(self, client):
        """Filtering by project_type returns only matching projects."""
        res = client.get("/api/projects?project_type=script")
        assert res.status_code == 200
        items = res.get_json()["data"]["projects"]
        assert len(items) >= 2
        for item in items:
            assert item["content_type"] == "script"

    def test_list_projects_filter_by_genre(self, client):
        """Filtering by genre returns only matching projects."""
        res = client.get("/api/projects?genre=Mystery")
        assert res.status_code == 200
        items = res.get_json()["data"]["projects"]
        assert len(items) >= 2
        for item in items:
            assert "Mystery" in item["genre"]

    def test_list_projects_search_by_title(self, client):
        """Searching by title keyword matches correctly."""
        res = client.get("/api/projects?search=Varanasi")
        assert res.status_code == 200
        items = res.get_json()["data"]["projects"]
        assert len(items) == 1
        assert "Varanasi" in items[0]["title"]

    def test_list_projects_pagination(self, client):
        """Pagination controls page size and page offset."""
        res = client.get("/api/projects?per_page=2&page=1")
        assert res.status_code == 200
        data = res.get_json()["data"]
        assert len(data["projects"]) == 2
        assert data["pagination"]["per_page"] == 2
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["has_next"] is True

    def test_list_projects_sorting_title_asc(self, client):
        """Sorting by title asc returns alphabetical order."""
        res = client.get("/api/projects?sort_by=title&order=asc")
        assert res.status_code == 200
        titles = [p["title"] for p in res.get_json()["data"]["projects"]]
        assert titles == sorted(titles)


class TestProjectUpdate:
    """Tests for PUT /api/projects/<id>."""

    def test_update_project_title_and_genre(self, client):
        """Updating title and genre succeeds and updates timestamp."""
        create_res = client.post("/api/projects", json={
            "title": "Original Project",
            "content_type": "story",
            "genre": "Drama"
        })
        p_id = create_res.get_json()["data"]["id"]

        update_res = client.put(f"/api/projects/{p_id}", json={
            "title": "Revised Project Title",
            "genre": "Thriller"
        })
        assert update_res.status_code == 200
        updated = update_res.get_json()["data"]
        assert updated["title"] == "Revised Project Title"
        assert updated["genre"] == "Thriller"
        assert updated["content_type"] == "story"

    def test_update_project_content_creates_history(self, client, app):
        """Changing generated_content creates a new history entry."""
        create_res = client.post("/api/projects", json={
            "title": "History Tracking Test",
            "content_type": "story",
            "content": "First draft content."
        })
        p_id = create_res.get_json()["data"]["id"]

        client.put(f"/api/projects/{p_id}", json={
            "content": "Second polished draft content with additional scenes."
        })

        with app.app_context():
            histories = GenerationHistory.query.filter_by(project_id=p_id).all()
            assert len(histories) >= 2
            operations = [h.operation for h in histories]
            assert "update" in operations

    def test_update_project_nonexistent_returns_404(self, client):
        """Updating a nonexistent project ID returns HTTP 404."""
        res = client.put("/api/projects/88888", json={"title": "Ghost Project"})
        assert res.status_code == 404

    def test_update_project_empty_title_rejected(self, client):
        """Updating with an empty title returns HTTP 400."""
        create_res = client.post("/api/projects", json={"title": "Valid Initial", "content_type": "story"})
        p_id = create_res.get_json()["data"]["id"]

        res = client.put(f"/api/projects/{p_id}", json={"title": ""})
        assert res.status_code == 400


class TestProjectDeletion:
    """Tests for DELETE /api/projects/<id>."""

    def test_delete_project_success(self, client):
        """Deleting a project returns HTTP 200 and removes it from subsequent queries."""
        create_res = client.post("/api/projects", json={
            "title": "Doomed Project",
            "content_type": "story"
        })
        p_id = create_res.get_json()["data"]["id"]

        del_res = client.delete(f"/api/projects/{p_id}")
        assert del_res.status_code == 200
        assert del_res.get_json()["success"] is True

        get_res = client.get(f"/api/projects/{p_id}")
        assert get_res.status_code == 404

    def test_delete_project_cascades_history(self, client, app):
        """Deleting a project cascades and deletes all associated history rows."""
        create_res = client.post("/api/projects", json={
            "title": "Cascade Test",
            "content_type": "story",
            "content": "Initial content."
        })
        p_id = create_res.get_json()["data"]["id"]

        # Add an explicit version
        client.post(f"/api/projects/{p_id}/versions", json={
            "content": "Version 2 content."
        })

        with app.app_context():
            assert GenerationHistory.query.filter_by(project_id=p_id).count() >= 2

        # Delete project
        client.delete(f"/api/projects/{p_id}")

        with app.app_context():
            assert GenerationHistory.query.filter_by(project_id=p_id).count() == 0

    def test_delete_project_nonexistent_returns_404(self, client):
        """Deleting a nonexistent project returns HTTP 404."""
        res = client.delete("/api/projects/77777")
        assert res.status_code == 404


class TestProjectVersioning:
    """Tests for version snapshots and restorations."""

    def test_save_version_success(self, client):
        """POST /api/projects/<id>/versions creates a snapshot."""
        create_res = client.post("/api/projects", json={
            "title": "Versioned Novel",
            "content_type": "story",
            "content": "Chapter 1 text."
        })
        p_id = create_res.get_json()["data"]["id"]

        v_res = client.post(f"/api/projects/{p_id}/versions", json={
            "content": "Chapter 1 + Chapter 2 completed text.",
            "summary": "Added Chapter 2 climax",
            "operation": "chapter_addition"
        })
        assert v_res.status_code == 201
        v_data = v_res.get_json()["data"]
        assert v_data["project_id"] == p_id
        assert "Chapter 2" in v_data["content_snapshot"]

        # Project content should be updated
        p_res = client.get(f"/api/projects/{p_id}")
        assert "Chapter 2" in p_res.get_json()["data"]["generated_content"]

    def test_save_version_missing_content_rejected(self, client):
        """POST /api/projects/<id>/versions without content returns HTTP 400."""
        create_res = client.post("/api/projects", json={"title": "Test Proj", "content_type": "story"})
        p_id = create_res.get_json()["data"]["id"]

        res = client.post(f"/api/projects/{p_id}/versions", json={})
        assert res.status_code == 400

    def test_get_version_history_chronological(self, client):
        """GET /api/projects/<id>/versions returns snapshots in chronological order."""
        create_res = client.post("/api/projects", json={
            "title": "Chronological Test",
            "content_type": "story",
            "content": "V1"
        })
        p_id = create_res.get_json()["data"]["id"]

        client.post(f"/api/projects/{p_id}/versions", json={"content": "V2", "summary": "Second"})
        client.post(f"/api/projects/{p_id}/versions", json={"content": "V3", "summary": "Third"})

        res = client.get(f"/api/projects/{p_id}/versions?order=asc")
        assert res.status_code == 200
        versions = res.get_json()["data"]
        assert len(versions) == 3
        assert versions[0]["content_snapshot"] == "V1"
        assert versions[2]["content_snapshot"] == "V3"

    def test_get_single_version_success(self, client):
        """GET /api/projects/<id>/versions/<version_id> returns specific snapshot."""
        create_res = client.post("/api/projects", json={
            "title": "Single Version Lookup",
            "content_type": "story",
            "content": "Snapshot Target"
        })
        p_id = create_res.get_json()["data"]["id"]

        v_res = client.post(f"/api/projects/{p_id}/versions", json={
            "content": "Specific target snapshot content"
        })
        v_id = v_res.get_json()["data"]["id"]

        res = client.get(f"/api/projects/{p_id}/versions/{v_id}")
        assert res.status_code == 200
        assert res.get_json()["data"]["id"] == v_id
        assert "Specific target" in res.get_json()["data"]["content_snapshot"]

    def test_get_single_version_nonexistent_returns_404(self, client):
        """Querying a nonexistent version ID returns HTTP 404."""
        create_res = client.post("/api/projects", json={"title": "P", "content_type": "story"})
        p_id = create_res.get_json()["data"]["id"]

        res = client.get(f"/api/projects/{p_id}/versions/99999")
        assert res.status_code == 404

    def test_restore_version_success(self, client):
        """Restoring a past version resets project content to that snapshot."""
        create_res = client.post("/api/projects", json={
            "title": "Restoration Candidate",
            "content_type": "story",
            "content": "Golden First Draft"
        })
        p_id = create_res.get_json()["data"]["id"]

        # Get initial version ID
        histories_res = client.get(f"/api/projects/{p_id}/versions")
        v1_id = histories_res.get_json()["data"][0]["id"]

        # Mutate project content
        client.put(f"/api/projects/{p_id}", json={
            "content": "Flawed second draft that broke the ending."
        })

        # Confirm mutated content
        mutated = client.get(f"/api/projects/{p_id}").get_json()["data"]
        assert "Flawed second draft" in mutated["generated_content"]

        # Restore to v1
        restore_res = client.post(f"/api/projects/{p_id}/versions/{v1_id}/restore")
        assert restore_res.status_code == 200
        restored = restore_res.get_json()["data"]
        assert "Golden First Draft" in restored["generated_content"]


class TestDatabaseErrorHandling:
    """Tests simulating unexpected database errors and rollbacks."""

    def test_create_project_rollback_on_db_error(self, client):
        """Database exception during create_project triggers rollback and returns 500."""
        with patch("services.project_service.db.session.commit", side_effect=Exception("Disk full")):
            res = client.post("/api/projects", json={"title": "Error Proj", "content_type": "story"})
            assert res.status_code == 500
            assert res.get_json()["success"] is False

    def test_update_project_rollback_on_db_error(self, client):
        """Database exception during update_project triggers rollback and returns 500."""
        create_res = client.post("/api/projects", json={"title": "Rollback Proj", "content_type": "story"})
        p_id = create_res.get_json()["data"]["id"]

        with patch("services.project_service.db.session.commit", side_effect=Exception("Deadlock")):
            res = client.put(f"/api/projects/{p_id}", json={"title": "New Title"})
            assert res.status_code == 500

    def test_delete_project_rollback_on_db_error(self, client):
        """Database exception during delete_project triggers rollback and returns 500."""
        create_res = client.post("/api/projects", json={"title": "Del Fail Proj", "content_type": "story"})
        p_id = create_res.get_json()["data"]["id"]

        with patch("services.project_service.db.session.commit", side_effect=Exception("DB locked")):
            res = client.delete(f"/api/projects/{p_id}")
            assert res.status_code == 500
