from typing import Any, Dict, List
from uuid import UUID

from litestar import Controller, delete, get, post, put
from litestar.exceptions import NotFoundException
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService


class UserController(Controller):
    path = "/users"

    @get("/{user_id:uuid}")
    async def get_user_by_id(
        self,
        user_service: UserService,
        session: Session,
        user_id: UUID,
    ) -> UserRead:
        user = await user_service.get_by_id(session, user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserRead.model_validate(user)

    @get()
    async def get_all_users(
        self,
        user_service: UserService,
        session: Session,
    ) -> Dict[str, Any]:
        users = await user_service.get_by_filter(session, count=100, page=1)
        user_repo = UserRepository()
        total_count = session.query(user_repo.model).count()
        return {
            "total": total_count,
            "users": [UserRead.model_validate(u) for u in users],
        }

    @post()
    async def create_user(
        self,
        user_service: UserService,
        session: Session,
        data: UserCreate,
    ) -> UserRead:
        user = await user_service.create(session, data)
        return UserRead.model_validate(user)

    @put("/{user_id:uuid}")
    async def update_user(
        self,
        user_service: UserService,
        session: Session,
        user_id: UUID,
        data: UserUpdate,
    ) -> UserRead:
        user = await user_service.update(session, user_id, data)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserRead.model_validate(user)

    @delete("/{user_id:uuid}")
    async def delete_user(
        self,
        user_service: UserService,
        session: Session,
        user_id: UUID,
    ) -> None:
        await user_service.delete(session, user_id)
