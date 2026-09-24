from sqlalchemy.orm import Session

from app.core.errors import AuthenticationError
from app.core.security import hash_password, verify_password
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

# Verifying against a dummy hash when the email is unknown keeps response times
# similar, so attackers cannot discover which emails exist.
_DUMMY_HASH = hash_password("dummy-password-for-timing")


class AuthService:
    def __init__(self, session: Session) -> None:
        self._users = UserRepository(session)

    def authenticate(self, email: str, password: str) -> User:
        user = self._users.get_by_email(email.strip())
        password_ok = verify_password(password, user.password_hash if user else _DUMMY_HASH)
        if user is None or not password_ok:
            raise AuthenticationError("Email o contraseña incorrectos.")
        if not user.is_active:
            raise AuthenticationError("Tu cuenta está inactiva. Comunícate con un administrador.")
        return user
