from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import PermissionDeniedError
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

SESSION_USER_KEY = "user_id"


class NotAuthenticatedError(Exception):
    """Raised when there is no valid, active user in the session."""


def get_current_user(request: Request, db: Annotated[Session, Depends(get_db)]) -> User:
    """`is_active` is checked on every request, so deactivation is immediate."""
    user_id = request.session.get(SESSION_USER_KEY)
    user = UserRepository(db).get(user_id) if user_id else None
    if user is None or not user.is_active:
        request.session.clear()
        raise NotAuthenticatedError
    request.state.user = user  # available to layouts (menu, header)
    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_admin:
        raise PermissionDeniedError("Acceso solo para administradores.")
    return user


def require_client(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.is_admin:
        raise PermissionDeniedError("Acceso solo para clientes.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
ClientUser = Annotated[User, Depends(require_client)]
DbSession = Annotated[Session, Depends(get_db)]
