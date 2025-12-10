from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cache import CacheService
from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserRead, UserUpdate
from models import User


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.cache_service = CacheService()

    async def get_by_id(self, session: Session, user_id: UUID) -> Optional[User]:
        # Проверяем кэш
        cached_data = self.cache_service.get_cached_user(user_id)
        if cached_data:
            # Восстанавливаем объект User из кэша
            user = User(
                id=UUID(cached_data["id"]),
                username=cached_data["username"],
                email=cached_data["email"],
                description=cached_data.get("description", ""),
                created_at=datetime.fromisoformat(cached_data["created_at"]) if isinstance(cached_data["created_at"], str) else cached_data["created_at"],
                updated_at=datetime.fromisoformat(cached_data["updated_at"]) if isinstance(cached_data["updated_at"], str) else cached_data["updated_at"],
            )
            return user

        # Если нет в кэше, получаем из БД
        user = await self.user_repository.get_by_id(session, user_id)
        if user:
            # Кэшируем данные пользователя на 1 час
            user_data = UserRead.model_validate(user).model_dump()
            self.cache_service.cache_user(user_id, user_data)

        return user

    async def get_by_filter(
        self, session: Session, count: int = 10, page: int = 1, **kwargs
    ) -> List[User]:
        return await self.user_repository.get_by_filter(session, count, page, **kwargs)

    async def create(self, session: Session, user_data: UserCreate) -> User:
        return await self.user_repository.create(session, user_data)

    async def update(
        self, session: Session, user_id: UUID, user_data: UserUpdate
    ) -> Optional[User]:
        # Обновляем пользователя в БД
        user = await self.user_repository.update(session, user_id, user_data)
        if user:
            # Удаляем данные из кэша при обновлении
            self.cache_service.delete_cached_user(user_id)
        return user

    async def delete(self, session: Session, user_id: UUID) -> None:
        await self.user_repository.delete(session, user_id)
