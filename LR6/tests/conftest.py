import os
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.controllers.user_controller import UserController
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.services.order_service import OrderService
from app.services.user_service import UserService
from models import Base

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
    )
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def user_repository():
    return UserRepository()


@pytest.fixture
def product_repository():
    return ProductRepository()


@pytest.fixture
def order_repository():
    return OrderRepository()


@pytest.fixture
def user_service(user_repository):
    return UserService(user_repository)


@pytest.fixture
def order_service(order_repository, product_repository, user_repository):
    return OrderService(order_repository, product_repository, user_repository)


@pytest.fixture
def test_client(db_session, user_repository, user_service):
    def get_session() -> Generator[Session, None, None]:
        yield db_session

    def get_user_repository():
        return user_repository

    def get_user_service():
        return user_service

    app = Litestar(
        route_handlers=[UserController],
        dependencies={
            "session": Provide(get_session),
            "user_repository": Provide(get_user_repository, sync_to_thread=False),
            "user_service": Provide(get_user_service, sync_to_thread=False),
        },
    )

    with TestClient(app=app) as client:
        yield client

