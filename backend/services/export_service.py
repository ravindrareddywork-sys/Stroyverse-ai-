"""
StoryVerse AI — Document Export Service Layer
================================================
Generates professional exports in three formats:
  1. Plain Text (.txt): Clean UTF-8 formatted text with structural headings.
  2. Microsoft Word (.docx): Styled document with typography, headers, and metadata.
  3. Portable Document Format (.pdf): ReportLab layout with running headers,
     page numbers, clean margins, and Unicode font support (English, Telugu, Tamil, Hindi).
"""

import os
import io
import re
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional

# ReportLab PDF imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# python-docx imports
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from utils.validators import sanitize_filename
from services.project_service import project_service

logger = logging.getLogger(__name__)

# Track registered fonts
_UNICODE_FONT_NAME: Optional[str] = None
_SCRIPT_FONTS: Dict[str, str] = {}
_FONT_INIT_ATTEMPTED = False


def _init_unicode_fonts() -> Optional[str]:
    """
    Detects and registers TrueType/OpenType fonts capable of rendering Unicode
    (including Indic scripts: Hindi, Telugu, Tamil) in ReportLab.
    Maintains script-specific mappings in _SCRIPT_FONTS and primary font in _UNICODE_FONT_NAME.
    """
    global _UNICODE_FONT_NAME, _SCRIPT_FONTS, _FONT_INIT_ATTEMPTED
    if _FONT_INIT_ATTEMPTED:
        return _UNICODE_FONT_NAME
    _FONT_INIT_ATTEMPTED = True

    windir = os.environ.get("WINDIR", "C:\\Windows")
    win_fonts = os.path.join(windir, "Fonts")

    # Script-specific font candidates: (file_path, subfontIndex, font_name, scripts)
    script_candidates = []

    if os.path.isdir(win_fonts):
        script_candidates.extend([
            # Nirmala covers Devanagari, Telugu, Tamil, Bengali, Gujarati, Gurmukhi, Kannada, Malayalam, Odia
            (os.path.join(win_fonts, "Nirmala.ttc"), 0, "NirmalaUI", ["tamil", "telugu", "hindi", "english"]),
            (os.path.join(win_fonts, "mangal.ttf"), None, "Mangal", ["hindi"]),
            (os.path.join(win_fonts, "gautami.ttf"), None, "Gautami", ["telugu"]),
            (os.path.join(win_fonts, "latha.ttf"), None, "Latha", ["tamil"]),
            (os.path.join(win_fonts, "arial.ttf"), None, "ArialUnicode", ["english"]),
        ])

    # Linux / Container Fonts directory
    linux_font_dirs = [
        "/usr/share/fonts/truetype",
        "/usr/share/fonts/opentype",
        "/usr/local/share/fonts",
    ]
    linux_specific = [
        # Tamil
        ("/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf", None, "NotoSansTamil", ["tamil"]),
        ("/usr/share/fonts/truetype/lohit-tamil/Lohit-Tamil.ttf", None, "LohitTamil", ["tamil"]),
        # Telugu
        ("/usr/share/fonts/truetype/noto/NotoSansTelugu-Regular.ttf", None, "NotoSansTelugu", ["telugu"]),
        ("/usr/share/fonts/truetype/lohit-telugu/Lohit-Telugu.ttf", None, "LohitTelugu", ["telugu"]),
        # Devanagari / Hindi
        ("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf", None, "NotoSansDevanagari", ["hindi"]),
        ("/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf", None, "LohitHindi", ["hindi"]),
        # Multilingual / English
        ("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", None, "NotoSans", ["english"]),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", None, "DejaVuSans", ["english"]),
    ]
    script_candidates.extend(linux_specific)

    for font_path, sub_idx, font_name, scripts in script_candidates:
        if os.path.isfile(font_path):
            try:
                if font_name not in pdfmetrics.getRegisteredFontNames():
                    if sub_idx is not None:
                        pdfmetrics.registerFont(TTFont(font_name, font_path, subfontIndex=sub_idx))
                    else:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                for s in scripts:
                    if s not in _SCRIPT_FONTS:
                        _SCRIPT_FONTS[s] = font_name
                if not _UNICODE_FONT_NAME:
                    _UNICODE_FONT_NAME = font_name
                logger.info("Registered ReportLab font: %s for %s (%s)", font_name, scripts, font_path)
            except Exception as err:
                logger.debug("Could not register font %s: %s", font_path, err)

    if not _UNICODE_FONT_NAME:
        logger.warning("No TrueType Unicode font registered. Standard Type 1 fonts will be used for English.")
    return _UNICODE_FONT_NAME


def get_font_for_language(lang: Optional[str]) -> str:
    """
    Returns an appropriate registered font for the given language.
    For Indic scripts (Tamil, Telugu, Hindi), ensures an Indic-capable Unicode font is used;
    raises ValueError if none is available rather than silently corrupting glyphs with Helvetica.
    """
    _init_unicode_fonts()
    norm_lang = (lang or "English").strip().lower()
    is_indic = norm_lang in ("tamil", "telugu", "hindi")

    # 1. Script-specific registered font
    if norm_lang in _SCRIPT_FONTS:
        return _SCRIPT_FONTS[norm_lang]

    # 2. General registered Unicode font
    if _UNICODE_FONT_NAME:
        return _UNICODE_FONT_NAME

    # 3. For Indic languages, do NOT silently fall back to Helvetica
    if is_indic:
        raise ValueError(
            f"PDF export for {lang} requires an Indic Unicode TrueType font (e.g., Nirmala UI on Windows, "
            f"or Noto Sans {lang} on Linux). No suitable font was found on this system. "
            f"Please install the required font or export in DOCX or TXT format."
        )

    # 4. Default Latin fallback for English
    return "Helvetica"


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass ReportLab Canvas that dynamically computes total page count
    and prints 'Page X of Y' in the running footer alongside document title.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "StoryVerse AI — Creative Manuscript")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)

        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_str)
        self.drawString(54, 36, "Generated with StoryVerse AI")
        self.restoreState()


class ExportService:
    """
    Handles file synthesis for plain text, Microsoft Word, and PDF downloads.
    """

    MIME_TXT = "text/plain; charset=utf-8"
    MIME_PDF = "application/pdf"
    MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def __init__(self):
        _init_unicode_fonts()

    def resolve_export_payload(self, data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Dict[str, Any], Optional[str]]:
        """
        Extracts title, content, and metadata from explicit payload or database project.

        Returns:
            Tuple of (title, content, metadata, error_message)
        """
        project_id = data.get("project_id")
        title = (data.get("title") or "").strip()
        content = (
            data.get("content")
            if "content" in data
            else data.get("generated_content")
        )
        if content:
            content = content.strip()

        metadata = {
            "project_type": data.get("project_type") or data.get("content_type") or "Story",
            "genre": data.get("genre") or "General",
            "language": data.get("language") or "English",
            "tone": data.get("tone") or "",
        }

        # If project_id is provided, retrieve database project to supplement fields
        if project_id:
            try:
                pid = int(project_id)
            except (ValueError, TypeError):
                return None, None, {}, f"Invalid project_id '{project_id}'."

            proj = project_service.get_project_by_id(pid)
            if not proj:
                return None, None, {}, f"Project #{pid} not found."

            if not title:
                title = proj.get("title") or "Untitled Project"
            if not content:
                content = proj.get("generated_content") or ""

            metadata["project_type"] = proj.get("content_type") or metadata["project_type"]
            metadata["genre"] = proj.get("genre") or metadata["genre"]
            metadata["language"] = proj.get("language") or metadata["language"]
            metadata["tone"] = proj.get("tone") or metadata["tone"]

        if not title:
            title = "StoryVerse Creative Manuscript"
        if not content:
            return None, None, {}, "Content cannot be empty for export."

        return title, content, metadata, None

    # ==========================================
    # 1. Plain Text (.txt) Export
    # ==========================================
    def export_txt(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[io.BytesIO, str]:
        """
        Creates a clean plain-text manuscript document encoded in UTF-8.
        """
        metadata = metadata or {}
        p_type = (metadata.get("project_type") or "Story").capitalize()
        genre = metadata.get("genre") or "Creative"
        lang = metadata.get("language") or "English"
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        header_banner = [
            "=" * 72,
            f"TITLE: {title.upper()}",
            f"TYPE: {p_type} | GENRE: {genre} | LANGUAGE: {lang}",
            f"EXPORTED: {now_str} via StoryVerse AI",
            "=" * 72,
            "",
            content.strip(),
            "",
            "=" * 72,
            "StoryVerse AI — Final Year College Project",
            "=" * 72,
        ]

        full_text = "\n".join(header_banner)
        buffer = io.BytesIO(full_text.encode("utf-8"))
        buffer.seek(0)

        filename = f"{sanitize_filename(title)}.txt"
        return buffer, filename

    # ==========================================
    # 2. Microsoft Word (.docx) Export
    # ==========================================
    def export_docx(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[io.BytesIO, str]:
        """
        Creates a Microsoft Word document (.docx) using python-docx.
        """
        metadata = metadata or {}
        doc = docx.Document()

        # Set 1-inch margins
        for section in doc.sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

        # Title
        title_para = doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_para.add_run(title)
        title_run.font.name = "Georgia"
        title_run.font.size = Pt(22)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(30, 27, 75)  # Navy

        # Subtitle / Metadata
        meta_para = doc.add_paragraph()
        meta_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_type = (metadata.get("project_type") or "Story").capitalize()
        genre = metadata.get("genre") or "General"
        lang = metadata.get("language") or "English"

        meta_text = f"{p_type} • {genre} • {lang} • StoryVerse AI"
        meta_run = meta_para.add_run(meta_text)
        meta_run.font.name = "Arial"
        meta_run.font.size = Pt(9.5)
        meta_run.font.italic = True
        meta_run.font.color.rgb = RGBColor(100, 116, 139)  # Slate

        # Spacing divider
        doc.add_paragraph().paragraph_format.space_after = Pt(12)

        # Body Content
        paragraphs = content.strip().split("\n\n")
        is_script = p_type.lower() == "script"

        for raw_para in paragraphs:
            para_text = raw_para.strip()
            if not para_text:
                continue

            # Detect headings (e.g. # Heading, ACT 1, SCENE 1, INT., EXT.)
            is_heading = (
                para_text.startswith("#")
                or re.match(r"^(ACT\s+\d+|SCENE\s+\d+|INT\.|EXT\.|CHAPTER\s+\d+|EPILOGUE|PROLOGUE)", para_text, re.IGNORECASE)
            )

            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(8)
            p.paragraph_format.line_spacing = 1.25

            if is_heading:
                clean_heading = re.sub(r"^#+\s*", "", para_text)
                run = p.add_run(clean_heading)
                run.font.name = "Arial" if is_script else "Georgia"
                run.font.size = Pt(13)
                run.font.bold = True
                run.font.color.rgb = RGBColor(124, 58, 237)  # Violet
                p.paragraph_format.space_before = Pt(12)
            else:
                run = p.add_run(para_text)
                if is_script:
                    run.font.name = "Courier New"
                    run.font.size = Pt(10.5)
                else:
                    run.font.name = "Georgia"
                    run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(15, 23, 42)

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        filename = f"{sanitize_filename(title)}.docx"
        return buffer, filename

    # ==========================================
    # 3. Portable Document Format (.pdf) Export
    # ==========================================
    def export_pdf(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[io.BytesIO, str]:
        """
        Creates a PDF document using ReportLab with custom styling and Unicode font support.
        """
        metadata = metadata or {}
        buffer = io.BytesIO()

        # Document setup with 0.75-inch margins
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54,
        )

        lang = metadata.get("language") or "English"
        is_indic = lang.strip().lower() in ("tamil", "telugu", "hindi")
        font_name = get_font_for_language(lang)

        # Stylesheet setup
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#1E1B4B"),
            alignment=1,  # Center
            spaceAfter=6,
        )

        meta_style = ParagraphStyle(
            "DocMeta",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#64748B"),
            alignment=1,  # Center
            spaceAfter=14,
        )

        heading_style = ParagraphStyle(
            "DocHeading",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#7C3AED"),  # Violet
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True,
        )

        p_type = (metadata.get("project_type") or "Story").capitalize()
        is_script = p_type.lower() == "script"

        # Screenplay scripts in English can use Courier if font is Helvetica;
        # Indic scripts always use the Unicode TrueType font to preserve script characters
        script_font = font_name if is_indic else ("Courier" if (is_script and font_name == "Helvetica") else font_name)

        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName=script_font if is_script else font_name,
            fontSize=10 if is_script else 10.5,
            leading=15 if is_script else 16.5,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=8,
        )

        elements = []

        # Document Title
        elements.append(Paragraph(self._escape_xml(title), title_style))

        # Subtitle
        genre = metadata.get("genre") or "General"
        lang = metadata.get("language") or "English"
        meta_text = f"{p_type} • {genre} • {lang} • StoryVerse AI"
        elements.append(Paragraph(self._escape_xml(meta_text), meta_style))

        # Horizontal Rule Divider
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#E2E8F0"),
            spaceBefore=4,
            spaceAfter=14
        ))

        # Body Paragraphs
        paragraphs = content.strip().split("\n\n")

        for raw_para in paragraphs:
            para_text = raw_para.strip()
            if not para_text:
                continue

            # Detect headings
            is_heading = (
                para_text.startswith("#")
                or re.match(r"^(ACT\s+\d+|SCENE\s+\d+|INT\.|EXT\.|CHAPTER\s+\d+|EPILOGUE|PROLOGUE)", para_text, re.IGNORECASE)
            )

            # Preserve line breaks within paragraphs
            escaped_text = self._escape_xml(para_text).replace("\n", "<br/>")

            if is_heading:
                clean_heading = re.sub(r"^#+\s*", "", escaped_text)
                elements.append(Paragraph(clean_heading, heading_style))
            else:
                elements.append(Paragraph(escaped_text, body_style))

        # Build document with NumberedCanvas for professional running page numbers
        doc.build(elements, canvasmaker=NumberedCanvas)
        buffer.seek(0)

        filename = f"{sanitize_filename(title)}.pdf"
        return buffer, filename

    def _escape_xml(self, text: str) -> str:
        """
        Escapes XML special characters for ReportLab Paragraph rendering.
        """
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )


# Global default instance
export_service = ExportService()
