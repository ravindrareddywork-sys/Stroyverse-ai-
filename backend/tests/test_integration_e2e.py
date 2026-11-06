"""
StoryVerse AI — Phase 11 Integration & End-to-End Workflow Tests
==================================================================
Comprehensive integration and end-to-end regression tests verifying:
- Complete Workflow A: Story Generation -> Expansion -> Save -> Dashboard -> Edit -> Version -> Export (TXT, PDF, DOCX)
- Complete Workflow B: Screenplay Generation -> Scene Addition -> Save -> Dashboard -> Edit -> Export
- Complete Workflow C: Character Generation -> Variations -> Save -> Dashboard -> Edit -> Export
- Complete Workflow D: Writing Assistant (Rewrite, Translate, Summarize, Dialogue, Plot Twist, Continue) -> Save -> Export
- Complete Workflow E: Project Management (Multi-type create, Search, Filter, Sort, Paginate, Versions, Restore, Delete)
- All 21 API Endpoints Integration and HTTP Status / Schema Verification
- Security checks: XSS prevention, SQL injection safety, Filename path traversal sanitization
"""

import io
import json
import pytest
from models.project import Project
from models.generation_history import GenerationHistory


class TestWorkflowAStoryE2E:
    """Workflow A: Story Generator complete end-to-end user journey."""

    def test_workflow_a_story_full_cycle(self, client, db_session):
        # 1. Generate Story
        story_payload = {
            "topic": "An apprentice clockmaker finds a pocket watch that can rewind time by seven minutes.",
            "genre": "Fantasy",
            "language": "English",
            "tone": "Emotional",
            "length": "Medium",
            "audience": "Teenagers"
        }
        res_gen = client.post("/api/generate-story", json=story_payload)
        assert res_gen.status_code == 200
        data_gen = res_gen.get_json()
        assert data_gen["success"] is True
        story_content = data_gen["data"]["full_text"]
        story_title = data_gen["data"].get("title", "The Clockmaker's Gift")
        assert len(story_content) > 0

        # 2. Expand Story
        res_exp = client.post("/api/expand", json={
            "content": story_content,
            "genre": "Fantasy",
            "language": "English",
            "instructions": "Add vivid sensory details of ticking gears."
        })
        assert res_exp.status_code == 200
        data_exp = res_exp.get_json()
        assert data_exp["success"] is True
        expanded_content = data_exp["data"]["full_text"]
        assert len(expanded_content) > 0

        # 3. Save Story as a Project
        res_save = client.post("/api/projects", json={
            "title": story_title,
            "project_type": "story",
            "genre": "Fantasy",
            "language": "English",
            "content": expanded_content,
            "description": "Story about time manipulation clock."
        })
        assert res_save.status_code == 201
        project = res_save.get_json()["data"]
        project_id = project["id"]
        assert project["title"] == story_title
        assert project["project_type"] == "story"

        # 4. Open Dashboard & Find Saved Story
        res_list = client.get("/api/projects?project_type=story")
        assert res_list.status_code == 200
        projects_list = res_list.get_json()["data"]["projects"]
        assert any(p["id"] == project_id for p in projects_list)

        # 5. Open Project in Editor
        res_get = client.get(f"/api/projects/{project_id}")
        assert res_get.status_code == 200
        p_data = res_get.get_json()["data"]
        assert p_data["id"] == project_id
        assert p_data["content"] == expanded_content

        # 6. Edit & Save Updated Project
        edited_content = expanded_content + "\n\nEPILOGUE: The clock was finally returned to the mantle."
        res_update = client.put(f"/api/projects/{project_id}", json={
            "title": story_title + " (Revised)",
            "content": edited_content
        })
        assert res_update.status_code == 200
        updated_data = res_update.get_json()["data"]
        assert updated_data["title"] == story_title + " (Revised)"
        assert updated_data["content"] == edited_content

        # 7. Verify Version History
        res_versions = client.get(f"/api/projects/{project_id}/versions")
        assert res_versions.status_code == 200
        versions = res_versions.get_json()["data"]
        assert len(versions) >= 2  # initial create + update revision

        # 8. Export All Three Formats (TXT, PDF, DOCX) via project_id
        res_txt = client.post("/api/export/txt", json={"project_id": project_id})
        assert res_txt.status_code == 200
        assert "text/plain" in res_txt.content_type
        assert len(res_txt.data) > 0

        res_pdf = client.post("/api/export/pdf", json={"project_id": project_id})
        assert res_pdf.status_code == 200
        assert "application/pdf" in res_pdf.content_type
        assert res_pdf.data.startswith(b"%PDF-")

        res_docx = client.post("/api/export/docx", json={"project_id": project_id})
        assert res_docx.status_code == 200
        assert "application/vnd.openxmlformats-officedocument" in res_docx.content_type
        assert res_docx.data.startswith(b"PK")


class TestWorkflowBScreenplayE2E:
    """Workflow B: Screenplay Generator complete end-to-end user journey."""

    def test_workflow_b_screenplay_full_cycle(self, client, db_session):
        # 1. Generate Screenplay
        script_payload = {
            "topic": "A detective and a forensic specialist trap an art thief in a locked gallery.",
            "genre": "Thriller",
            "language": "English",
            "num_scenes": 2,
            "tone": "Suspenseful"
        }
        res_gen = client.post("/api/generate-script", json=script_payload)
        assert res_gen.status_code == 200
        data_gen = res_gen.get_json()["data"]
        script_title = data_gen.get("title", "Midnight Heist")
        full_script = data_gen.get("full_script", "")
        assert len(full_script) > 0

        # 2. Generate Individual Scene
        res_scene = client.post("/api/generate-scene", json={
            "scene_number": 3,
            "scene_goal": "The detective confronts the thief near the emergency exit.",
            "genre": "Thriller",
            "language": "English"
        })
        assert res_scene.status_code == 200
        scene_text = res_scene.get_json()["data"]["full_text"]
        assert len(scene_text) > 0

        # 3. Append Scene and Save Screenplay Project
        combined_script = f"{full_script}\n\nSCENE 3\n{scene_text}"
        res_save = client.post("/api/projects", json={
            "title": script_title,
            "project_type": "script",
            "genre": "Thriller",
            "language": "English",
            "content": combined_script,
            "description": "3-scene thriller screenplay in a gallery."
        })
        assert res_save.status_code == 201
        project_id = res_save.get_json()["data"]["id"]

        # 4. Open from Dashboard
        res_get = client.get(f"/api/projects/{project_id}")
        assert res_get.status_code == 200
        assert res_get.get_json()["data"]["project_type"] == "script"

        # 5. Edit Screenplay
        edited_script = combined_script + "\n\nFADE OUT."
        res_put = client.put(f"/api/projects/{project_id}", json={"content": edited_script})
        assert res_put.status_code == 200

        # 6. Export TXT, PDF, and DOCX
        for fmt in ["txt", "pdf", "docx"]:
            res_exp = client.post(f"/api/export/{fmt}", json={"project_id": project_id})
            assert res_exp.status_code == 200
            assert len(res_exp.data) > 0


class TestWorkflowCCharacterE2E:
    """Workflow C: Character Studio complete end-to-end user journey."""

    def test_workflow_c_character_full_cycle(self, client, db_session):
        # 1. Generate Character Profile
        char_payload = {
            "character_name": "Kaelen Voss",
            "description": "A rogue chronomancer haunted by a temporal paradox he caused.",
            "genre": "Science Fiction",
            "character_role": "protagonist",
            "personality_type": "Guarded, intensely analytical, deeply remorseful",
            "language": "English"
        }
        res_char = client.post("/api/generate-character", json=char_payload)
        assert res_char.status_code == 200
        char_data = res_char.get_json()["data"]
        full_profile = char_data.get("full_profile", "")
        assert len(full_profile) > 0

        # 2. Generate Ensemble Variations
        res_var = client.post("/api/generate-character-variations", json={
            "premise": "A rebellion against a temporal empire",
            "genre": "Science Fiction",
            "count": 3,
            "language": "English"
        })
        assert res_var.status_code == 200
        var_data = res_var.get_json()["data"]
        assert var_data["count"] >= 1

        # 3. Save Character Profile as Project
        res_save = client.post("/api/projects", json={
            "title": "Kaelen Voss — Character Bible",
            "project_type": "character",
            "genre": "Science Fiction",
            "language": "English",
            "content": full_profile,
            "description": "Protagonist character bible for temporal sci-fi novel."
        })
        assert res_save.status_code == 201
        project_id = res_save.get_json()["data"]["id"]

        # 4. Open from Dashboard
        res_get = client.get(f"/api/projects/{project_id}")
        assert res_get.status_code == 200
        assert res_get.get_json()["data"]["title"] == "Kaelen Voss — Character Bible"

        # 5. Edit Character Notes
        updated_notes = full_profile + "\n\nAdditional Arc Note: Kaelen must sacrifice his time-device."
        res_put = client.put(f"/api/projects/{project_id}", json={"content": updated_notes})
        assert res_put.status_code == 200

        # 6. Export all three formats
        for fmt in ["txt", "pdf", "docx"]:
            res_exp = client.post(f"/api/export/{fmt}", json={"project_id": project_id})
            assert res_exp.status_code == 200
            assert len(res_exp.data) > 0


class TestWorkflowDWritingAssistantE2E:
    """Workflow D: Writing Assistant complete tool suite end-to-end journey."""

    def test_workflow_d_assistant_tools_cycle(self, client, db_session):
        sample_text = (
            "The ancient door groaned as Marcus pushed it inward. Darkness swallowed the hall, "
            "punctuated only by the faint glow of emerald moss clinging to the stone pillars."
        )

        # 1. Rewrite Text
        res_rw = client.post("/api/rewrite", json={
            "content": sample_text,
            "style": "make it engaging"
        })
        assert res_rw.status_code == 200
        rewritten = res_rw.get_json()["data"]["rewritten"]
        assert len(rewritten) > 0

        # 2. Translate Text (to Telugu)
        res_tr = client.post("/api/translate", json={
            "content": sample_text,
            "target_language": "Telugu"
        })
        assert res_tr.status_code == 200
        translated = res_tr.get_json()["data"]["translation"]
        assert len(translated) > 0

        # 3. Summarize Text
        res_sum = client.post("/api/summarize", json={
            "content": sample_text,
            "length": "short"
        })
        assert res_sum.status_code == 200
        summary = res_sum.get_json()["data"]["summary"]
        assert len(summary) > 0

        # 4. Generate Dialogue
        res_dia = client.post("/api/generate-dialogue", json={
            "characters": "Marcus, Elena",
            "context": "Exploring the forbidden sanctuary while hearing footsteps behind them.",
            "genre": "Fantasy",
            "tone": "Suspenseful"
        })
        assert res_dia.status_code == 200
        dialogue = res_dia.get_json()["data"]["dialogue"]
        assert len(dialogue) > 0

        # 5. Generate Plot Twist
        res_tw = client.post("/api/generate-plot-twist", json={
            "premise": "A team of researchers exploring an abandoned subterranean temple.",
            "genre": "Mystery",
            "tone": "Dark"
        })
        assert res_tw.status_code == 200
        twists = res_tw.get_json()["data"]["plot_twists"]
        assert len(twists) > 0

        # 6. Continue Writing
        res_cw = client.post("/api/continue-writing", json={
            "content": sample_text,
            "genre": "Fantasy",
            "tone": "Suspenseful"
        })
        assert res_cw.status_code == 200
        continuation = res_cw.get_json()["data"]["continuation"]
        assert len(continuation) > 0

        # 7. Assemble Manuscript and Save as Project
        combined_draft = f"{rewritten}\n\n[DIALOGUE]\n{dialogue}\n\n[CONTINUATION]\n{continuation}"
        res_save = client.post("/api/projects", json={
            "title": "The Sanctuary of Emerald Moss",
            "project_type": "story",
            "genre": "Fantasy",
            "language": "English",
            "content": combined_draft,
            "description": "Collaborative draft created with StoryVerse AI writing assistant."
        })
        assert res_save.status_code == 201
        project_id = res_save.get_json()["data"]["id"]

        # 8. Export All Formats
        for fmt in ["txt", "pdf", "docx"]:
            res_exp = client.post(f"/api/export/{fmt}", json={"project_id": project_id})
            assert res_exp.status_code == 200
            assert len(res_exp.data) > 0


class TestWorkflowEProjectManagementE2E:
    """Workflow E: Project persistence, versions, search, filters, restore, and delete."""

    def test_workflow_e_project_lifecycle(self, client, db_session):
        # 1. Create Projects across multiple types & genres
        types = [
            ("Epic Chronicles", "story", "Fantasy"),
            ("City of Neon", "script", "Science Fiction"),
            ("Shadow Detective", "character", "Mystery"),
            ("General Draft", "other", "Drama")
        ]
        created_ids = []
        for title, p_type, genre in types:
            res = client.post("/api/projects", json={
                "title": title,
                "project_type": p_type,
                "genre": genre,
                "language": "English",
                "content": f"Initial content for {title}"
            })
            assert res.status_code == 201
            created_ids.append(res.get_json()["data"]["id"])

        target_id = created_ids[0]

        # 2. Search by Keyword
        res_search = client.get("/api/projects?search=Neon")
        assert res_search.status_code == 200
        search_results = res_search.get_json()["data"]["projects"]
        assert len(search_results) == 1
        assert search_results[0]["title"] == "City of Neon"

        # 3. Filter by Type and Genre
        res_filter = client.get("/api/projects?project_type=story&genre=Fantasy")
        assert res_filter.status_code == 200
        filtered = res_filter.get_json()["data"]["projects"]
        assert all(p["project_type"] == "story" and p["genre"] == "Fantasy" for p in filtered)

        # 4. Sorting and Pagination
        res_sort = client.get("/api/projects?sort=title&order=asc&page=1&per_page=2")
        assert res_sort.status_code == 200
        page_data = res_sort.get_json()["data"]
        assert len(page_data["projects"]) == 2
        assert page_data["pagination"]["total"] >= 4

        # 5. Create Explicit Version Snapshot
        res_ver = client.post(f"/api/projects/{target_id}/versions", json={
            "content": "Snapshot Version 2: Major structural overhaul.",
            "change_summary": "Added second act revelation"
        })
        assert res_ver.status_code == 201
        snapshot_id = res_ver.get_json()["data"]["id"]

        # 6. Update Project Content further
        client.put(f"/api/projects/{target_id}", json={
            "content": "Current Working Draft (v3): Final polishing."
        })

        # 7. Restore Previous Snapshot
        res_restore = client.post(f"/api/projects/{target_id}/versions/{snapshot_id}/restore")
        assert res_restore.status_code == 200
        restored_proj = res_restore.get_json()["data"]
        assert restored_proj["content"] == "Snapshot Version 2: Major structural overhaul."

        # 8. Delete Project Safely
        res_del = client.delete(f"/api/projects/{target_id}")
        assert res_del.status_code == 200

        # 9. Verify Deleted Project Returns 404
        res_verify = client.get(f"/api/projects/{target_id}")
        assert res_verify.status_code == 404


class TestAllEndpointsDirectIntegration:
    """Direct verification of all 21 endpoints for status codes and response schemas."""

    def test_health_check_endpoint(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert data["data"]["database"] == "connected"

    def test_story_endpoints(self, client):
        # /api/generate-story
        r1 = client.post("/api/generate-story", json={"topic": "Test story premise", "genre": "Drama", "language": "English"})
        assert r1.status_code == 200
        # /api/regenerate
        r2 = client.post("/api/regenerate", json={"topic": "Test story premise", "genre": "Drama", "language": "English"})
        assert r2.status_code == 200
        # /api/expand
        r3 = client.post("/api/expand", json={"content": "Short story base", "genre": "Drama", "language": "English"})
        assert r3.status_code == 200
        # /api/shorten
        r4 = client.post("/api/shorten", json={"content": "Long story text to condense", "genre": "Drama", "language": "English"})
        assert r4.status_code == 200
        # /api/continue
        r5 = client.post("/api/continue", json={"content": "Story cliffhanger", "genre": "Drama", "language": "English"})
        assert r5.status_code == 200

    def test_script_endpoints(self, client):
        # /api/generate-script
        r1 = client.post("/api/generate-script", json={"topic": "Heist screenplay", "genre": "Action", "language": "English"})
        assert r1.status_code == 200
        # /api/generate-scene
        r2 = client.post("/api/generate-scene", json={"scene_number": 1, "scene_goal": "Establish setting", "genre": "Action", "language": "English"})
        assert r2.status_code == 200

    def test_character_endpoints(self, client):
        # /api/generate-character
        r1 = client.post("/api/generate-character", json={"description": "Mysterious scholar", "genre": "Mystery", "language": "English"})
        assert r1.status_code == 200
        # /api/generate-character-variations
        r2 = client.post("/api/generate-character-variations", json={"premise": "Stolen relic", "genre": "Mystery", "count": 2, "language": "English"})
        assert r2.status_code == 200

    def test_writing_assistant_endpoints(self, client):
        # /api/rewrite
        r1 = client.post("/api/rewrite", json={"content": "Sample prose", "style": "improve clarity"})
        assert r1.status_code == 200
        # /api/translate
        r2 = client.post("/api/translate", json={"content": "Hello world", "target_language": "Hindi"})
        assert r2.status_code == 200
        # /api/summarize
        r3 = client.post("/api/summarize", json={"content": "Paragraph of text to summarize", "length": "short"})
        assert r3.status_code == 200
        # /api/generate-dialogue
        r4 = client.post("/api/generate-dialogue", json={"characters": "A, B", "context": "Meeting in diner"})
        assert r4.status_code == 200
        # /api/generate-plot-twist
        r5 = client.post("/api/generate-plot-twist", json={"premise": "Murder in mansion", "genre": "Mystery"})
        assert r5.status_code == 200
        # /api/continue-writing
        r6 = client.post("/api/continue-writing", json={"content": "They arrived at midnight."})
        assert r6.status_code == 200

    def test_export_endpoints(self, client):
        payload = {"title": "Integration Doc", "content": "Sample export text content"}
        r1 = client.post("/api/export/txt", json=payload)
        assert r1.status_code == 200
        r2 = client.post("/api/export/pdf", json=payload)
        assert r2.status_code == 200
        r3 = client.post("/api/export/docx", json=payload)
        assert r3.status_code == 200


class TestSecurityAndInputSanitization:
    """Security checks: SQL injection, XSS escaping, Path traversal."""

    def test_sql_injection_resilience(self, client):
        malicious_search = "' OR 1=1 --"
        res = client.get(f"/api/projects?search={malicious_search}")
        assert res.status_code == 200
        # Should not crash or return unescaped database dump
        data = res.get_json()["data"]
        assert isinstance(data["projects"], list)

    def test_path_traversal_in_export_filename(self, client):
        malicious_title = "../../../../etc/passwd"
        res = client.post("/api/export/txt", json={
            "title": malicious_title,
            "content": "Safe content"
        })
        assert res.status_code == 200
        disposition = res.headers.get("Content-Disposition", "")
        assert ".." not in disposition
        assert "/" not in disposition
        assert "\\" not in disposition

    def test_xss_content_in_export_safety(self, client):
        xss_payload = "<script>alert('xss')</script><b>Bold Text</b>"
        res = client.post("/api/export/pdf", json={
            "title": "XSS Test",
            "content": xss_payload
        })
        assert res.status_code == 200
        assert res.data.startswith(b"%PDF-")
