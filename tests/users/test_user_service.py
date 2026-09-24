import pytest

from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.core.security import verify_password
from app.models import Tag
from app.modules.users.models import Role
from app.modules.users.schemas import UserCreate, UserUpdate
from app.modules.users.service import UserService
from app.shared.pagination import PageParams


@pytest.fixture
def service(session) -> UserService:
    return UserService(session)


def _create_payload(**overrides) -> UserCreate:
    data = {"email": "New@Example.com", "full_name": "New User", "password": "long-password"}
    return UserCreate(**(data | overrides))


def test_create_user_hashes_password_and_normalizes_email(service):
    user = service.create(_create_payload())

    assert user.email == "new@example.com"
    assert user.role == Role.CLIENT
    assert user.is_active
    assert user.ticket_count == 0
    assert verify_password("long-password", user.password_hash)


def test_admin_can_create_another_admin(service):
    user = service.create(_create_payload(role=Role.ADMIN))

    assert user.is_admin


def test_create_user_rejects_duplicate_email(service, client_user):
    with pytest.raises(ConflictError):
        service.create(_create_payload(email=client_user.email.upper()))


def test_update_user_changes_profile(service, client_user):
    data = UserUpdate(email="renamed@example.com", full_name="Renamed", role=Role.ADMIN)

    user = service.update(client_user.id, data)

    assert (user.email, user.full_name, user.role) == ("renamed@example.com", "Renamed", Role.ADMIN)


def test_update_user_rejects_email_of_another_user(service, client_user, admin):
    data = UserUpdate(email=admin.email, full_name="X", role=Role.CLIENT)

    with pytest.raises(ConflictError):
        service.update(client_user.id, data)


def test_set_password_replaces_hash(service, client_user):
    service.set_password(client_user.id, "brand-new-password")

    assert verify_password("brand-new-password", client_user.password_hash)


def test_admin_can_deactivate_and_reactivate_user(service, admin, client_user):
    service.set_active(admin, client_user.id, is_active=False)
    assert not client_user.is_active

    service.set_active(admin, client_user.id, is_active=True)
    assert client_user.is_active


def test_admin_cannot_deactivate_themselves(service, admin):
    with pytest.raises(ValidationError):
        service.set_active(admin, admin.id, is_active=False)


def test_set_tags_replaces_user_tags(service, session, client_user):
    pro, basic = Tag(name="Pro"), Tag(name="Basic")
    session.add_all([pro, basic])
    session.commit()

    service.set_tags(client_user.id, [pro.id])
    service.set_tags(client_user.id, [basic.id, pro.id])

    assert {tag.name for tag in client_user.tags} == {"Pro", "Basic"}


def test_set_tags_rejects_unknown_tag(service, client_user):
    with pytest.raises(NotFoundError):
        service.set_tags(client_user.id, [999])


def test_get_missing_user_raises(service):
    with pytest.raises(NotFoundError):
        service.get(999)


def test_list_filters_by_role_and_search(service, make_user):
    make_user(full_name="Ana Client")
    make_user(full_name="Bob Client")
    make_user(role=Role.ADMIN, full_name="Ana Admin")

    page = service.search(PageParams(), role=Role.CLIENT, search="ana")

    assert [user.full_name for user in page.items] == ["Ana Client"]
    assert page.total == 1


def test_create_and_update_assign_tags(service, session):
    pro, basic = Tag(name="Pro"), Tag(name="Basic")
    session.add_all([pro, basic])
    session.commit()

    user = service.create(_create_payload(tag_ids=[pro.id]))
    assert [tag.name for tag in user.tags] == ["Pro"]

    data = UserUpdate(email=user.email, full_name="X", role=Role.CLIENT, tag_ids=[basic.id])
    assert [tag.name for tag in service.update(user.id, data).tags] == ["Basic"]
