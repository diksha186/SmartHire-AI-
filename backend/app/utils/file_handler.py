"""
Secure resume upload handling: extension check, MIME check, size check,
random filename, and storage inside the uploads directory.
"""
import os
import uuid

from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _extension(filename: str) -> str:
    return os.path.splitext(filename or "")[1].lower()


def save_resume(file: UploadFile, user_id: int) -> tuple[str, str]:
    """
    Validate and store an uploaded resume.

    Returns (stored_filename, absolute_path).
    """
    ext = _extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only .pdf and .docx resumes are allowed")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unsupported file type: {file.content_type}")

    contents = file.file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB",
        )
    if not contents:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Uploaded file is empty")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    # Random name -> the user cannot control the path, and files are never executed.
    stored_name = f"user{user_id}_{uuid.uuid4().hex}{ext}"
    path = os.path.join(settings.UPLOAD_DIR, stored_name)
    with open(path, "wb") as f:
        f.write(contents)
    return stored_name, path


def resume_path(stored_name: str) -> str:
    return os.path.join(settings.UPLOAD_DIR, stored_name)
