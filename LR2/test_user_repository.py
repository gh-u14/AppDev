import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
from models import User
from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate

# Настраиваем соединение
engine = create_engine("postgresql+psycopg2://postgres:pass@localhost:5432/labdb")
Session = sessionmaker(bind=engine)
session = Session()

repo = UserRepository()

async def main():
    print("=== Создание пользователя ===")
    user_data = UserCreate(username="RepoTestUser", email="repo_test@example.com")
    user = await repo.create(session, user_data)
    print("Создан:", user.id, user.username, user.email)

    print("\n=== Получение всех пользователей ===")
    users = await repo.get_by_filter(session)
    for u in users:
        print(f"- {u.username} ({u.email})")

    print("\n=== Получение пользователя по ID ===")
    found = await repo.get_by_id(session, user.id)  # type: ignore
    print("Найден:", found.username if found else "не найден")

    print("\n=== Удаление пользователя ===")
    await repo.delete(session, user.id)  # type: ignore
    print("Удалён:", user.id)

    session.close()

asyncio.run(main())
