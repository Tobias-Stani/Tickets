import pytest

from app.core.errors import ConflictError
from app.modules.topics.schemas import TopicInput
from app.modules.topics.service import TopicService


@pytest.fixture
def service(session) -> TopicService:
    return TopicService(session)


def test_create_topic_is_active_by_default(service):
    topic = service.create(TopicInput(name="  Billing  "))

    assert topic.name == "Billing"
    assert topic.is_active


def test_create_rejects_duplicate_name(service):
    service.create(TopicInput(name="Billing"))

    with pytest.raises(ConflictError):
        service.create(TopicInput(name="BILLING"))


def test_rename_topic(service):
    topic = service.create(TopicInput(name="Billing"))

    assert service.update(topic.id, TopicInput(name="Payments")).name == "Payments"


def test_deactivated_topics_are_hidden_from_active_list(service):
    billing = service.create(TopicInput(name="Billing"))
    service.create(TopicInput(name="Support"))

    service.set_active(billing.id, is_active=False)

    assert [topic.name for topic in service.list_active()] == ["Support"]
    assert len(service.list_all()) == 2
