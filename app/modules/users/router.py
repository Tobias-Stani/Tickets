from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request

from app.core.templates import templates
from app.modules.auth.dependencies import AdminUser, DbSession
from app.modules.tags.service import TagService
from app.modules.users.models import Role
from app.modules.users.schemas import PasswordReset, UserCreate, UserUpdate
from app.modules.users.service import UserService
from app.shared.web import Pagination, redirect

router = APIRouter(prefix="/admin/users", tags=["users"])


def get_user_service(db: DbSession) -> UserService:
    return UserService(db)


Users = Annotated[UserService, Depends(get_user_service)]


def _form(request: Request, db: DbSession, user=None):
    context = {"user_obj": user, "tags": TagService(db).list_all()}
    return templates.TemplateResponse(request, "users/form.html", context)


@router.get("")
def list_users(
    request: Request,
    _: AdminUser,
    users: Users,
    params: Pagination,
    search: Annotated[str, Query()] = "",
    role: Annotated[str, Query()] = "",
):
    selected_role = Role(role) if role in Role else None
    page = users.search(params, role=selected_role, search=search.strip() or None)
    context = {"page": page, "search": search, "role": role}
    return templates.TemplateResponse(request, "users/list.html", context)


@router.get("/new")
def new_user_form(request: Request, _: AdminUser, db: DbSession):
    return _form(request, db)


@router.post("")
def create_user(request: Request, _: AdminUser, users: Users, data: Annotated[UserCreate, Form()]):
    user = users.create(data)
    return redirect(request, "/admin/users", f"Usuario {user.full_name} creado.")


@router.get("/{user_id}")
def edit_user_form(request: Request, _: AdminUser, users: Users, db: DbSession, user_id: int):
    return _form(request, db, users.get(user_id))


@router.post("/{user_id}")
def update_user(
    request: Request, _: AdminUser, users: Users, user_id: int, data: Annotated[UserUpdate, Form()]
):
    users.update(user_id, data)
    return redirect(request, "/admin/users", "Usuario actualizado.")


@router.post("/{user_id}/password")
def reset_password(
    request: Request,
    _: AdminUser,
    users: Users,
    user_id: int,
    data: Annotated[PasswordReset, Form()],
):
    users.set_password(user_id, data.password)
    return redirect(request, f"/admin/users/{user_id}", "Contraseña actualizada.")


@router.post("/{user_id}/active")
def set_active(
    request: Request,
    admin: AdminUser,
    users: Users,
    user_id: int,
    is_active: Annotated[bool, Form()],
):
    user = users.set_active(admin, user_id, is_active)
    state = "activado" if user.is_active else "desactivado"
    return redirect(request, "/admin/users", f"Usuario {user.full_name} {state}.")
