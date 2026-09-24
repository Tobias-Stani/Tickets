import pytest

from app.core.errors import ValidationError
from app.modules.tickets.images import MAX_IMAGE_BYTES, ImageFile, validate_images
from tests.tickets.images import JPEG, PDF, PNG, WEBP


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
        validate_images([ImageFile("doc.png", PDF)])


def test_rejects_oversized_image():
    big = PNG + b"\x00" * MAX_IMAGE_BYTES

    with pytest.raises(ValidationError, match="5 MB"):
        validate_images([ImageFile("big.png", big)])
