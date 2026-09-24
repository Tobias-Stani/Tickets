from dataclasses import dataclass

import filetype

from app.core.errors import ValidationError

MAX_IMAGES = 3
MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


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


def validate_images(files: list[ImageFile]) -> list[ValidatedImage]:
    uploads = [file for file in files if file.content]
    if len(uploads) > MAX_IMAGES:
        raise ValidationError(f"Puedes adjuntar hasta {MAX_IMAGES} imágenes.")
    return [_validate(file) for file in uploads]


def _validate(file: ImageFile) -> ValidatedImage:
    if len(file.content) > MAX_IMAGE_BYTES:
        raise ValidationError(f"'{file.filename}' supera el límite de 5 MB.")
    content_type = _detect_type(file.content)
    if content_type not in ALLOWED_TYPES:
        raise ValidationError(f"'{file.filename}' debe ser una imagen JPG, PNG o WEBP.")
    return ValidatedImage(file.content, content_type, ALLOWED_TYPES[content_type])


def _detect_type(content: bytes) -> str | None:
    kind = filetype.guess(content)
    return kind.mime if kind else None
