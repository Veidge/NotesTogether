import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import make_url

from app.database import DATABASE_URL, get_db
from app.models import Base
from app.main import app

# Подмена БД.
database_url = make_url(DATABASE_URL)
TEST_DATABASE_NAME = "notes_together_test"
TEST_DATABASE_URL = database_url.set(database=TEST_DATABASE_NAME)

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    admin_url = database_url.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    try:
        with admin_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": TEST_DATABASE_NAME}
            ).scalar()

            if not exists:
                connection.execute(
                    text(f'CREATE DATABASE "{TEST_DATABASE_NAME}"')
                )
    finally:
        admin_engine.dispose()

    yield


# Отдельное подключение к тестовой БД.
test_engine = create_engine(TEST_DATABASE_URL, echo=False)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

# Работа с тестовой БД напрямую.
@pytest.fixture
def db_session():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Отправка HTTP запросов (FastAPI).
@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()