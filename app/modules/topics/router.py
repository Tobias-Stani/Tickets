from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request

from app.core.templates import templates
from app.modules.auth.dependencies import AdminUser, DbSession
from app.modules.topics.schemas import TopicInput
from app.modules.topics.service import TopicService
from app.shared.web import redirect

router = APIRouter(prefix="/admin/topics", tags=["topics"])


def get_topic_service(db: DbSession) -> TopicService:
    return TopicService(db)


Topics = Annotated[TopicService, Depends(get_topic_service)]


@router.get("")
def list_topics(request: Request, _: AdminUser, topics: Topics):
    return templates.TemplateResponse(request, "topics/list.html", {"topics": topics.list_all()})


@router.post("")
def create_topic(
    request: Request, _: AdminUser, topics: Topics, data: Annotated[TopicInput, Form()]
):
    topic = topics.create(data)
    return redirect(request, "/admin/topics", f"Tema {topic.name} creado.")


@router.get("/{topic_id}")
def edit_topic_form(request: Request, _: AdminUser, topics: Topics, topic_id: int):
    return templates.TemplateResponse(request, "topics/edit.html", {"topic": topics.get(topic_id)})


@router.post("/{topic_id}")
def update_topic(
    request: Request,
    _: AdminUser,
    topics: Topics,
    topic_id: int,
    data: Annotated[TopicInput, Form()],
):
    topics.update(topic_id, data)
    return redirect(request, "/admin/topics", "Tema actualizado.")


@router.post("/{topic_id}/active")
def set_active(
    request: Request,
    _: AdminUser,
    topics: Topics,
    topic_id: int,
    is_active: Annotated[bool, Form()],
):
    topic = topics.set_active(topic_id, is_active)
    state = "activado" if topic.is_active else "desactivado"
    return redirect(request, "/admin/topics", f"Tema {topic.name} {state}.")
