from typing import Generator, Any
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from litestar import Litestar
from litestar.di import Provide
from dotenv import load_dotenv

from models import Base
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.controllers.user_controller import UserController

# Загружаем переменные окружения
load_dotenv()

# === Настройка SQLAlchemy ===
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:pass@localhost:5432/labdb"
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

def get_user_service(user_repository: Any = Provide(get_user_repository)) -> UserService:
    return UserService(user_repository)

# === Создаем приложение Litestar ===
app = Litestar(
    route_handlers=[UserController],
    dependencies={
        "session": Provide(get_session),
        "user_repository": Provide(get_user_repository),
        "user_service": Provide(get_user_service),
    },
)
