import asyncio
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas import UserCreate, UserUpdate

# Настраиваем соединение
engine = create_engine("postgresql+psycopg2://postgres:pass@localhost:5432/labdb")
Session = sessionmaker(bind=engine)
session = Session()

repo = UserRepository()
service = UserService(repo)

async def main():
    print("=== Создание пользователя ===")
    user_data = UserCreate(username="ServiceUser", email="service@example.com", description="через сервис")
    user = await service.create(session, user_data)
    print("Создан:", user.id, user.username, user.email)

    print("\n=== Получение всех пользователей ===")
    users = await service.get_by_filter(session)
    for u in users:
        print("-", u.username)

    print("\n=== Обновление пользователя ===")
    update_data = UserUpdate(description="обновлено через сервис")
    updated_user = await service.update(session, user.id, update_data) # type: ignore
    if updated_user:
        print("Новый description:", updated_user.description)
    else:
        print("Обновление не выполнено, пользователь не найден")

    print("\n=== Удаление пользователя ===")
    await service.delete(session, user.id) # type: ignore
    print("Пользователь удалён")

    session.close()

asyncio.run(main())
