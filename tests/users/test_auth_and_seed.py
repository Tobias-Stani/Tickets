import pytest

from app.core.errors import AuthenticationError
from app.core.security import verify_password
from app.modules.auth.service import AuthService
from app.modules.users.models import Role, User
from app.modules.users.seed import ensure_admin
from tests.conftest import TEST_PASSWORD


def test_authenticate_returns_user_with_valid_credentials(session, client_user):
    user = AuthService(session).authenticate("CLIENT@example.com", TEST_PASSWORD)

    assert user.id == client_user.id


@pytest.mark.parametrize(
    ("email", "password"),
    [("client@example.com", "wrong-password"), ("nobody@example.com", TEST_PASSWORD)],
)
def test_authenticate_rejects_invalid_credentials(session, client_user, email, password):
    with pytest.raises(AuthenticationError):
        AuthService(session).authenticate(email, password)


def test_authenticate_rejects_inactive_user(session, make_user):
    make_user(email="off@example.com", is_active=False)

    with pytest.raises(AuthenticationError, match="inactiva"):
        AuthService(session).authenticate("off@example.com", TEST_PASSWORD)


def test_ensure_admin_creates_admin_once(session):
    assert ensure_admin(session, "root@example.com", "root-password", "Root")
    assert not ensure_admin(session, "root@example.com", "other-password", "Root")

    admins = session.query(User).filter_by(role=Role.ADMIN).all()
    assert len(admins) == 1
    assert verify_password("root-password", admins[0].password_hash)
