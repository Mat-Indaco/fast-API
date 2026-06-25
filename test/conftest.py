import pytest

from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from main import app
from limiter import limiter
from db import get_session


@pytest.fixture(autouse=True)
def disable_rate_limit():
    limiter.reset()
    original = limiter.enabled
    limiter.enabled = False
    yield
    limiter.enabled = original


sqlite_url = "sqlite://"

engine = create_engine(
    sqlite_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session")
def session_fixture():

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):

    def override_get_session():
        return session

    app.dependency_overrides[get_session] = override_get_session

    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()
