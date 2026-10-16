"""Attachment validation for tickets and replies: images and a few document types.

Module and class names predate documents; "image" here means any allowed attachment."""

from dataclasses import dataclass

import filetype

from app.core.errors import ValidationError

MAX_IMAGES = 3
MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
}
ACCEPT = ",".join(ALLOWED_TYPES)  # for <input accept>


@dataclass(frozen=True)
class ImageFile:
    """Raw upload, decoupled from the web framework."""

    filename: str
    content: bytes


@dataclass(frozen=True)
class ValidatedImage:
    content: bytes
    content_type: str
    extension: str
    filename: str


def validate_images(files: list[ImageFile]) -> list[ValidatedImage]:
    uploads = [file for file in files if file.content]
    if len(uploads) > MAX_IMAGES:
        raise ValidationError(f"Puedes adjuntar hasta {MAX_IMAGES} archivos.")
    return [_validate(file) for file in uploads]


def _validate(file: ImageFile) -> ValidatedImage:
    if len(file.content) > MAX_IMAGE_BYTES:
        raise ValidationError(f"'{file.filename}' supera el límite de 5 MB.")
    content_type = _detect_type(file.content)
    if content_type not in ALLOWED_TYPES:
        raise ValidationError(
            f"'{file.filename}' debe ser una imagen (JPG, PNG, WEBP), un PDF, Word o Excel."
        )
    extension = ALLOWED_TYPES[content_type]
    return ValidatedImage(file.content, content_type, extension, _display_name(file, extension))


def _display_name(file: ImageFile, extension: str) -> str:
    """Base name only (browsers may send full paths); used for the download name."""
    name = file.filename.replace("\\", "/").rsplit("/", 1)[-1].strip()[:200]
    return name or f"archivo.{extension}"


def _detect_type(content: bytes) -> str | None:
    kind = filetype.guess(content)
    return kind.mime if kind else None
