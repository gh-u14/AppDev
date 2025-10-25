from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserUpdate
from models import User
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, session: Session, user_id: UUID) -> Optional[User]:
        return await self.user_repository.get_by_id(session, user_id)

    async def get_by_filter(self, session: Session, count: int = 10, page: int = 1, **kwargs) -> List[User]:
        return await self.user_repository.get_by_filter(session, count, page, **kwargs)

    async def create(self, session: Session, user_data: UserCreate) -> User:
        return await self.user_repository.create(session, user_data)

    async def update(self, session: Session, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        return await self.user_repository.update(session, user_id, user_data)

    async def delete(self, session: Session, user_id: UUID) -> None:
        await self.user_repository.delete(session, user_id)
