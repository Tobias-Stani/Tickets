import os
from collections.abc import Callable, Iterator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.update(
    SECRET_KEY="test-secret",
    DATABASE_URL="sqlite://",
    ADMIN_EMAIL="admin@example.com",
    ADMIN_PASSWORD="admin-password",
    HTTPS_ONLY_COOKIES="false",
)

from app.core.security import hash_password  # noqa: E402
from app.models import Base, Topic, User  # noqa: E402
from app.modules.users.models import Role  # noqa: E402
from tests.fakes import InMemoryStorage  # noqa: E402

TEST_PASSWORD = "secret-password"
_TEST_PASSWORD_HASH = hash_password(TEST_PASSWORD)


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture
def session(session_factory) -> Iterator[Session]:
    with session_factory() as session:
        yield session


@pytest.fixture
def storage() -> InMemoryStorage:
    return InMemoryStorage()


@pytest.fixture
def make_user(session) -> Callable[..., User]:
    counter = iter(range(1, 10_000))

    def factory(role: Role = Role.CLIENT, is_active: bool = True, **fields) -> User:
        number = next(counter)
        user = User(
            email=fields.pop("email", f"user{number}@example.com"),
            full_name=fields.pop("full_name", f"User {number}"),
            password_hash=_TEST_PASSWORD_HASH,
            role=role,
            is_active=is_active,
            **fields,
        )
        session.add(user)
        session.commit()
        return user

    return factory


@pytest.fixture
def admin(make_user) -> User:
    return make_user(role=Role.ADMIN, email="boss@example.com")


@pytest.fixture
def client_user(make_user) -> User:
    return make_user(role=Role.CLIENT, email="client@example.com")


@pytest.fixture
def make_topic(session) -> Callable[..., Topic]:
    def factory(name: str = "Billing", is_active: bool = True) -> Topic:
        topic = Topic(name=name, is_active=is_active)
        session.add(topic)
        session.commit()
        return topic

    return factory
