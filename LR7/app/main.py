import os
from typing import Any, Generator

from dotenv import load_dotenv
from litestar import Litestar
from litestar.di import Provide
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.controllers.order_controller import OrderController
from app.controllers.product_controller import ProductController
from app.controllers.user_controller import UserController
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from models import Base

# Загружаем переменные окружения
load_dotenv()

# === Настройка SQLAlchemy ===
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:pass@localhost:5432/labdb"
)
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Создание всех таблиц
Base.metadata.create_all(engine)


# === DI функции ===
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_user_repository(session: Any = Provide(get_session)) -> UserRepository:
    return UserRepository()


def get_user_service(
    user_repository: Any = Provide(get_user_repository),
) -> UserService:
    return UserService(user_repository)


# === Создаем приложение Litestar ===
app = Litestar(
    route_handlers=[UserController, ProductController, OrderController],
    dependencies={
        "session": Provide(get_session),
        "user_repository": Provide(get_user_repository),
        "user_service": Provide(get_user_service),
    },
)
