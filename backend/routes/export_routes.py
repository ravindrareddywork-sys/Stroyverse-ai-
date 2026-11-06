"""
StoryVerse AI — Document Export Routes
=========================================
Flask Blueprint providing document download endpoints for:
  - POST /api/export/txt   : Generates and streams UTF-8 plain-text document
  - POST /api/export/pdf   : Generates and streams PDF document via ReportLab
  - POST /api/export/docx  : Generates and streams Word document via python-docx
"""

import logging
from flask import Blueprint, request, send_file

from services.export_service import export_service
from utils.validators import validate_export_input
from utils.response import error_response, not_found_response, server_error_response

logger = logging.getLogger(__name__)

export_bp = Blueprint("export", __name__)


@export_bp.route("/export/txt", methods=["POST"])
def export_txt():
    """
    POST /api/export/txt
    Streams a plain-text (.txt) file attachment.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_export_input(data)
        if errors:
            return error_response("Validation failed.", errors=errors, status_code=400)

        title, content, metadata, err_msg = export_service.resolve_export_payload(data)
        if err_msg:
            if "not found" in err_msg.lower():
                return not_found_response(err_msg)
            return error_response(err_msg, status_code=400)

        buffer, filename = export_service.export_txt(title, content, metadata)
        return send_file(
            buffer,
            mimetype=export_service.MIME_TXT,
            as_attachment=True,
            download_name=filename,
        )

    except Exception as err:
        logger.error("Error generating TXT export: %s", err, exc_info=True)
        return server_error_response("Failed to generate TXT document.")


@export_bp.route("/export/docx", methods=["POST"])
def export_docx():
    """
    POST /api/export/docx
    Streams a Microsoft Word (.docx) file attachment.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_export_input(data)
        if errors:
            return error_response("Validation failed.", errors=errors, status_code=400)

        title, content, metadata, err_msg = export_service.resolve_export_payload(data)
        if err_msg:
            if "not found" in err_msg.lower():
                return not_found_response(err_msg)
            return error_response(err_msg, status_code=400)

        buffer, filename = export_service.export_docx(title, content, metadata)
        return send_file(
            buffer,
            mimetype=export_service.MIME_DOCX,
            as_attachment=True,
            download_name=filename,
        )

    except Exception as err:
        logger.error("Error generating DOCX export: %s", err, exc_info=True)
        return server_error_response("Failed to generate Word document.")


@export_bp.route("/export/pdf", methods=["POST"])
def export_pdf():
    """
    POST /api/export/pdf
    Streams a Portable Document Format (.pdf) file attachment.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return error_response("Invalid or missing JSON request body.", status_code=400)

        errors = validate_export_input(data)
        if errors:
            return error_response("Validation failed.", errors=errors, status_code=400)

        title, content, metadata, err_msg = export_service.resolve_export_payload(data)
        if err_msg:
            if "not found" in err_msg.lower():
                return not_found_response(err_msg)
            return error_response(err_msg, status_code=400)

        buffer, filename = export_service.export_pdf(title, content, metadata)
        return send_file(
            buffer,
            mimetype=export_service.MIME_PDF,
            as_attachment=True,
            download_name=filename,
        )

    except ValueError as val_err:
        logger.warning("PDF export validation / font requirement failure: %s", val_err)
        return error_response(str(val_err), status_code=400)
    except Exception as err:
        logger.error("Error generating PDF export: %s", err, exc_info=True)
        return server_error_response("Failed to generate PDF document.")
