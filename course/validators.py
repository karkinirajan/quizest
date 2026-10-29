"""Validation for files uploaded as course packages (``Store.uploaded_file``)."""

import os

from django.conf import settings
from django.core.exceptions import ValidationError

# Browsers can execute HTML/SVG/JS, so those are deliberately absent from the default list.
DEFAULT_ALLOWED_EXTENSIONS = ["zip", "pdf", "pptx", "docx", "xlsx", "csv", "txt"]
DEFAULT_MAX_UPLOAD_MB = 200

# Container formats must start with the right signature.
SIGNATURES = {
    "zip": b"PK",
    "pptx": b"PK",
    "docx": b"PK",
    "xlsx": b"PK",
    "pdf": b"%PDF",
}


def allowed_extensions():
    return [
        e.lower().lstrip(".")
        for e in getattr(settings, "STORE_ALLOWED_EXTENSIONS", None) or DEFAULT_ALLOWED_EXTENSIONS
    ]


def validate_upload(file):
    """Allow-listed extension, size cap, and a matching file signature."""
    extension = os.path.splitext(file.name)[1].lower().lstrip(".")
    allowed = allowed_extensions()
    if extension not in allowed:
        raise ValidationError(
            "Files of type '.%(ext)s' are not allowed. Allowed types: %(allowed)s.",
            code="invalid_extension",
            params={"ext": extension or "(none)", "allowed": ", ".join(sorted(allowed))},
        )

    max_mb = getattr(settings, "STORE_MAX_UPLOAD_MB", DEFAULT_MAX_UPLOAD_MB)
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(
            "The file is larger than the %(mb)s MB limit.", code="too_large", params={"mb": max_mb}
        )

    signature = SIGNATURES.get(extension)
    if signature:
        position = file.tell() if hasattr(file, "tell") else 0
        head = file.read(len(signature))
        file.seek(position)
        if not head.startswith(signature):
            raise ValidationError(
                "The file content does not match its .%(ext)s extension.",
                code="invalid_content",
                params={"ext": extension},
            )
