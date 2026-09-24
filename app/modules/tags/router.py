from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request

from app.core.templates import templates
from app.modules.auth.dependencies import AdminUser, DbSession
from app.modules.tags.schemas import TagInput
from app.modules.tags.service import TagService
from app.shared.web import redirect

router = APIRouter(prefix="/admin/tags", tags=["tags"])


def get_tag_service(db: DbSession) -> TagService:
    return TagService(db)


Tags = Annotated[TagService, Depends(get_tag_service)]


@router.get("")
def list_tags(request: Request, _: AdminUser, tags: Tags):
    return templates.TemplateResponse(request, "tags/list.html", {"tags": tags.list_all()})


@router.post("")
def create_tag(request: Request, _: AdminUser, tags: Tags, data: Annotated[TagInput, Form()]):
    tag = tags.create(data)
    return redirect(request, "/admin/tags", f"Etiqueta {tag.name} creada.")


@router.get("/{tag_id}")
def edit_tag_form(request: Request, _: AdminUser, tags: Tags, tag_id: int):
    return templates.TemplateResponse(request, "tags/edit.html", {"tag": tags.get(tag_id)})


@router.post("/{tag_id}")
def update_tag(
    request: Request, _: AdminUser, tags: Tags, tag_id: int, data: Annotated[TagInput, Form()]
):
    tags.update(tag_id, data)
    return redirect(request, "/admin/tags", "Etiqueta actualizada.")


@router.post("/{tag_id}/delete")
def delete_tag(request: Request, _: AdminUser, tags: Tags, tag_id: int):
    tags.delete(tag_id)
    return redirect(request, "/admin/tags", "Etiqueta eliminada.")
