"""
StoryVerse AI — Document Export Tests
========================================
Tests for Phase 10:
  - TXT, DOCX, and PDF document exports
  - Database project retrieval vs direct content exports
  - Multilingual Unicode content (English, Telugu, Tamil, Hindi)
  - Screenplay and story formatting
  - MIME types and Content-Disposition headers
  - Filename sanitization and path traversal prevention
  - Error handling (empty content, missing project, invalid JSON)
  - Large document export handling
"""

import io
import pytest
import docx

from extensions import db as _db
from models import Project


class TestTxtExport:
    """Tests for POST /api/export/txt."""

    def test_export_txt_direct_content(self, client):
        """Exporting direct content to TXT returns a valid UTF-8 plain-text attachment."""
        payload = {
            "title": "Cosmic Voyage",
            "content": "The starship accelerated into hyperspace.",
            "project_type": "story",
            "genre": "Science Fiction",
            "language": "English",
        }
        res = client.post("/api/export/txt", json=payload)
        assert res.status_code == 200
        assert "text/plain" in res.headers.get("Content-Type", "")
        disposition = res.headers.get("Content-Disposition", "")
        assert "attachment" in disposition
        assert "Cosmic_Voyage.txt" in disposition

        text_content = res.data.decode("utf-8")
        assert "TITLE: COSMIC VOYAGE" in text_content
        assert "The starship accelerated into hyperspace." in text_content
        assert "StoryVerse AI" in text_content

    def test_export_txt_with_project_id(self, client):
        """Exporting by project_id fetches content from the database."""
        create_res = client.post("/api/projects", json={
            "title": "Saved Database Story",
            "content_type": "story",
            "genre": "Fantasy",
            "language": "English",
            "content": "Once upon a time in an enchanted grove.",
        })
        p_id = create_res.get_json()["data"]["id"]

        res = client.post("/api/export/txt", json={"project_id": p_id})
        assert res.status_code == 200
        text_content = res.data.decode("utf-8")
        assert "SAVED DATABASE STORY" in text_content
        assert "Once upon a time in an enchanted grove." in text_content

    def test_export_txt_multilingual_unicode(self, client):
        """Exporting TXT with Telugu, Tamil, and Hindi Unicode strings preserves full fidelity."""
        indic_content = (
            "Hindi: एक नई शुरुआत।\n\n"
            "Telugu: ఒక కొత్త ప్రయాణం మొదలైంది.\n\n"
            "Tamil: ஒரு புதிய பயணம் தொடங்கியது."
        )
        payload = {
            "title": "Indic Chronicles",
            "content": indic_content,
            "language": "Telugu",
        }
        res = client.post("/api/export/txt", json=payload)
        assert res.status_code == 200
        decoded = res.data.decode("utf-8")
        assert "ఒక కొత్త ప్రయాణం" in decoded
        assert "एक नई शुरुआत" in decoded
        assert "ஒரு புதிய பயணம்" in decoded


class TestDocxExport:
    """Tests for POST /api/export/docx."""

    def test_export_docx_direct_content(self, client):
        """Exporting direct content to DOCX returns a valid OpenXML Word document."""
        payload = {
            "title": "The Whispering Observatory",
            "content": "ACT 1: THE SIGNAL\n\nDr. Evelyn Ross adjusted the receiver.",
            "project_type": "script",
            "genre": "Mystery",
            "language": "English",
        }
        res = client.post("/api/export/docx", json=payload)
        assert res.status_code == 200
        assert "wordprocessingml.document" in res.headers.get("Content-Type", "")
        disposition = res.headers.get("Content-Disposition", "")
        assert "attachment" in disposition
        assert "The_Whispering_Observatory.docx" in disposition

        # Verify binary stream is a readable docx document
        doc_stream = io.BytesIO(res.data)
        doc = docx.Document(doc_stream)
        full_text = "\n".join(p.text for p in doc.paragraphs)
        assert "The Whispering Observatory" in full_text
        assert "THE SIGNAL" in full_text
        assert "Dr. Evelyn Ross" in full_text

    def test_export_docx_with_project_id(self, client):
        """Exporting DOCX via project_id retrieves database project."""
        create_res = client.post("/api/projects", json={
            "title": "Database Screenplay",
            "content_type": "script",
            "genre": "Thriller",
            "content": "EXT. HIGHWAY - NIGHT\nRain beats against the windshield.",
        })
        p_id = create_res.get_json()["data"]["id"]

        res = client.post("/api/export/docx", json={"project_id": p_id})
        assert res.status_code == 200
        doc = docx.Document(io.BytesIO(res.data))
        full_text = "\n".join(p.text for p in doc.paragraphs)
        assert "Database Screenplay" in full_text
        assert "EXT. HIGHWAY - NIGHT" in full_text

    def test_export_docx_multilingual(self, client):
        """Exporting DOCX with Telugu and Hindi characters preserves Unicode text."""
        payload = {
            "title": "మాయాజాలం",
            "content": "ఈ కథ ఒక మంత్రగాడి గురించి.\n\nयह कहानी एक जादूगर की है।",
            "language": "Telugu",
        }
        res = client.post("/api/export/docx", json=payload)
        assert res.status_code == 200
        doc = docx.Document(io.BytesIO(res.data))
        full_text = "\n".join(p.text for p in doc.paragraphs)
        assert "మాయాజాలం" in full_text
        assert "ఈ కథ ఒక మంత్రగాడి గురించి." in full_text
        assert "यह कहानी एक जादूगर की है।" in full_text


class TestPdfExport:
    """Tests for POST /api/export/pdf."""

    def test_export_pdf_direct_content(self, client):
        """Exporting direct content to PDF returns a valid PDF starting with %PDF-."""
        payload = {
            "title": "Chronicles of Olympus",
            "content": "CHAPTER 1: THE SUMMIT\n\nZeus gazed across the clouds.",
            "project_type": "story",
            "genre": "Fantasy",
            "language": "English",
        }
        res = client.post("/api/export/pdf", json=payload)
        assert res.status_code == 200
        assert "application/pdf" in res.headers.get("Content-Type", "")
        disposition = res.headers.get("Content-Disposition", "")
        assert "attachment" in disposition
        assert "Chronicles_of_Olympus.pdf" in disposition
        assert res.data.startswith(b"%PDF-")
        assert len(res.data) > 1000  # Valid PDF size

    def test_export_pdf_with_project_id(self, client):
        """Exporting PDF using project_id retrieves project and compiles document."""
        create_res = client.post("/api/projects", json={
            "title": "PDF Candidate Project",
            "content_type": "story",
            "genre": "Adventure",
            "content": "The expedition embarked at sunrise.",
        })
        p_id = create_res.get_json()["data"]["id"]

        res = client.post("/api/export/pdf", json={"project_id": p_id})
        assert res.status_code == 200
        assert res.data.startswith(b"%PDF-")

    def test_export_pdf_indic_unicode(self, client):
        """PDF generation handles Indic scripts (Hindi, Telugu, Tamil) using registered Unicode font."""
        indic_content = (
            "Hindi: नमस्ते दुनिया। यह एक सुंदर कहानी है।\n\n"
            "Telugu: నమస్కారం. కథలు మానవ భావోద్వేగాలను ప్రతిబింబిస్తాయి.\n\n"
            "Tamil: வணக்கம் உலகம். மனித உணர்வுகளை வெளிப்படுத்தும் கதை."
        )
        payload = {
            "title": "భారతీయ కథలు",
            "content": indic_content,
            "language": "Telugu",
        }
        res = client.post("/api/export/pdf", json=payload)
        assert res.status_code == 200
        assert res.data.startswith(b"%PDF-")
        assert len(res.data) > 2000

    def test_export_pdf_tamil_script(self, client):
        """PDF generation handles Tamil text and embeds appropriate Unicode font."""
        payload = {
            "title": "தமிழ் இலக்கியம்",
            "content": "வணக்கம் உலகம். கதை வசனம் இயக்கம் மற்றும் தயாரிப்பு.",
            "language": "Tamil",
        }
        res = client.post("/api/export/pdf", json=payload)
        assert res.status_code == 200
        assert res.data.startswith(b"%PDF-")
        assert len(res.data) > 2000

    def test_export_pdf_telugu_script(self, client):
        """PDF generation handles Telugu text and embeds appropriate Unicode font."""
        payload = {
            "title": "తెలుగు నాటకం",
            "content": "నమస్కారం. కథ మరియు సంభాషణలు విక్రమ్ రాశారు.",
            "language": "Telugu",
        }
        res = client.post("/api/export/pdf", json=payload)
        assert res.status_code == 200
        assert res.data.startswith(b"%PDF-")
        assert len(res.data) > 2000

    def test_export_pdf_hindi_script(self, client):
        """PDF generation handles Hindi text and embeds appropriate Unicode font."""
        payload = {
            "title": "हिंदी नाटक",
            "content": "नमस्ते दुनिया। कहानी और पटकथा लेखन में आपका स्वागत है।",
            "language": "Hindi",
        }
        res = client.post("/api/export/pdf", json=payload)
        assert res.status_code == 200
        assert res.data.startswith(b"%PDF-")
        assert len(res.data) > 2000

    def test_export_pdf_indic_rejects_silent_helvetica_fallback(self, monkeypatch):
        """When no Unicode Indic font is registered, Indic PDF export raises ValueError rather than silently using Helvetica."""
        import sys
        es_module = sys.modules["services.export_service"]

        # Simulate system with no Indic fonts registered
        monkeypatch.setattr(es_module, "_UNICODE_FONT_NAME", None)
        monkeypatch.setattr(es_module, "_SCRIPT_FONTS", {})
        monkeypatch.setattr(es_module, "_FONT_INIT_ATTEMPTED", True)

        with pytest.raises(ValueError, match="requires an Indic Unicode TrueType font"):
            es_module.export_service.export_pdf("Indic Test", "నమస్కారం", {"language": "Telugu"})


class TestExportValidationAndErrors:
    """Tests input validation and error responses for export endpoints."""

    def test_export_missing_content_and_id_rejected(self, client):
        """Request without project_id or content returns HTTP 400."""
        res = client.post("/api/export/txt", json={"title": "Empty Book"})
        assert res.status_code == 400
        assert res.get_json()["success"] is False

    def test_export_empty_content_rejected(self, client):
        """Empty string content returns HTTP 400."""
        res = client.post("/api/export/docx", json={"title": "Book", "content": "   "})
        assert res.status_code == 400

    def test_export_nonexistent_project_id_returns_404(self, client):
        """Nonexistent project_id returns HTTP 404."""
        res = client.post("/api/export/pdf", json={"project_id": 999999})
        assert res.status_code == 404
        assert res.get_json()["success"] is False

    def test_export_non_json_body_rejected(self, client):
        """Non-JSON body returns HTTP 400."""
        res = client.post("/api/export/txt", data="invalid plain text", content_type="text/plain")
        assert res.status_code == 400

    def test_export_safe_filename_path_traversal(self, client):
        """Malicious filenames with path traversal characters are sanitized in header."""
        payload = {
            "title": "../../../etc/passwd",
            "content": "Secret document contents.",
        }
        res = client.post("/api/export/txt", json=payload)
        assert res.status_code == 200
        disposition = res.headers.get("Content-Disposition", "")
        assert ".." not in disposition
        assert "/" not in disposition
        assert "\\" not in disposition

    def test_export_large_content(self, client):
        """Exporting a large manuscript (20,000+ words) completes successfully across all formats."""
        large_body = "\n\n".join(
            f"CHAPTER {i}: SECTION {i}\n" + ("This is a paragraph of manuscript prose text describing events. " * 30)
            for i in range(1, 15)
        )
        payload = {
            "title": "Epic Multi-Chapter Manuscript",
            "content": large_body,
            "project_type": "story",
        }

        # TXT
        txt_res = client.post("/api/export/txt", json=payload)
        assert txt_res.status_code == 200
        assert len(txt_res.data) > 20000

        # DOCX
        docx_res = client.post("/api/export/docx", json=payload)
        assert docx_res.status_code == 200
        assert len(docx_res.data) > 10000

        # PDF
        pdf_res = client.post("/api/export/pdf", json=payload)
        assert pdf_res.status_code == 200
        assert pdf_res.data.startswith(b"%PDF-")
