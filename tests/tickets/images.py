"""Minimal valid file headers, enough for content-based type detection."""

import io
import zipfile


def _zip(*parts: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for part in parts:
            archive.writestr(part, "<x/>")
    return buffer.getvalue()


PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 32
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 32
PDF = b"%PDF-1.7" + b"\x00" * 32
DOCX = _zip("[Content_Types].xml", "word/document.xml")
XLSX = _zip("[Content_Types].xml", "xl/workbook.xml")
ZIP = _zip("notes.txt")
