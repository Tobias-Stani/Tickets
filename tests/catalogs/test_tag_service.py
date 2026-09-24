import pytest
from pydantic import ValidationError as SchemaError

from app.core.errors import ConflictError, NotFoundError
from app.modules.tags.schemas import TagInput
from app.modules.tags.service import TagService


@pytest.fixture
def service(session) -> TagService:
    return TagService(session)


def test_create_and_list_tags_sorted_by_name(service):
    service.create(TagInput(name="Pro", color="#10b981"))
    service.create(TagInput(name="Basic"))

    assert [tag.name for tag in service.list_all()] == ["Basic", "Pro"]


def test_create_rejects_duplicate_name_case_insensitive(service):
    service.create(TagInput(name="Pro"))

    with pytest.raises(ConflictError):
        service.create(TagInput(name="pro"))


def test_update_tag(service):
    tag = service.create(TagInput(name="Pro"))

    updated = service.update(tag.id, TagInput(name="Premium", color="#f59e0b"))

    assert (updated.name, updated.color) == ("Premium", "#f59e0b")


def test_update_keeping_same_name_is_allowed(service):
    tag = service.create(TagInput(name="Pro"))

    service.update(tag.id, TagInput(name="Pro", color="#000000"))


def test_delete_tag_detaches_it_from_users(service, session, client_user):
    tag = service.create(TagInput(name="Pro"))
    client_user.tags = [tag]
    session.commit()

    service.delete(tag.id)
    session.refresh(client_user)

    assert client_user.tags == []
    with pytest.raises(NotFoundError):
        service.get(tag.id)


def test_color_must_be_hex():
    with pytest.raises(SchemaError):
        TagInput(name="Pro", color="red")
