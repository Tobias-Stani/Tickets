"""Creates the initial admin from settings. Safe to run on every startup.

Usage: python -m app.modules.users.seed
"""

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_session_factory
from app.core.security import hash_password
from app.modules.users.models import Role, User
from app.modules.users.repository import UserRepository


def ensure_admin(session: Session, email: str, password: str, full_name: str) -> bool:
    """Returns True when the admin was created, False when it already existed."""
    users = UserRepository(session)
    if users.get_by_email(email):
        return False
    users.add(
        User(
            email=email.lower(),
            full_name=full_name,
            password_hash=hash_password(password),
            role=Role.ADMIN,
        )
    )
    session.commit()
    return True


def main() -> None:
    settings = get_settings()
    with get_session_factory()() as session:
        created = ensure_admin(
            session, settings.admin_email, settings.admin_password, settings.admin_full_name
        )
    print("Admin created." if created else "Admin already exists.")


if __name__ == "__main__":
    main()
