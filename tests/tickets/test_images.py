import pytest

from app.core.errors import ValidationError
from app.modules.tickets.images import MAX_IMAGE_BYTES, ImageFile, validate_images
from tests.tickets.images import DOCX, JPEG, PDF, PNG, WEBP, XLSX, ZIP


def test_detects_type_from_content_not_filename():
    [image] = validate_images([ImageFile(filename="photo.pdf", content=PNG)])

    assert (image.content_type, image.extension) == ("image/png", "png")


def test_accepts_jpeg_and_webp():
    images = validate_images([ImageFile("a", JPEG), ImageFile("b", WEBP)])

    assert [image.extension for image in images] == ["jpg", "webp"]


def test_ignores_empty_uploads():
    assert validate_images([ImageFile(filename="", content=b"")]) == []


def test_rejects_more_than_three_images():
    with pytest.raises(ValidationError, match="3"):
        validate_images([ImageFile("x.png", PNG)] * 4)


def test_rejects_unsupported_type():
    with pytest.raises(ValidationError):
        validate_images([ImageFile("archive.pdf", ZIP)])


def test_accepts_pdf_word_and_excel():
    files = validate_images([ImageFile("a.pdf", PDF), ImageFile("b", DOCX), ImageFile("c", XLSX)])

    assert [file.extension for file in files] == ["pdf", "docx", "xlsx"]


def test_keeps_only_base_filename():
    [file] = validate_images([ImageFile(r"C:\Users\ana\informe final.pdf", PDF)])

    assert file.filename == "informe final.pdf"


def test_names_unnamed_uploads_after_their_type():
    [file] = validate_images([ImageFile("", PDF)])

    assert file.filename == "archivo.pdf"


def test_rejects_oversized_image():
    big = PNG + b"\x00" * MAX_IMAGE_BYTES

    with pytest.raises(ValidationError, match="5 MB"):
        validate_images([ImageFile("big.png", big)])
