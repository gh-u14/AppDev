import asyncio

from app.schemas import UserCreate, UserUpdate
from app.services.user_service import UserService


class TestUserService:
    def test_create_user(self, db_session, user_service: UserService):
        async def _run():
            user = await user_service.create(
                db_session,
                UserCreate(username="service_user", email="service@example.com"),
            )
            assert user.username == "service_user"

        asyncio.run(_run())

    def test_get_users(self, db_session, user_service: UserService):
        async def _run():
            await user_service.create(
                db_session,
                UserCreate(username="service_user_1", email="service1@example.com"),
            )
            await user_service.create(
                db_session,
                UserCreate(username="service_user_2", email="service2@example.com"),
            )

            users = await user_service.get_by_filter(db_session, count=10, page=1)
            assert len(users) == 2

        asyncio.run(_run())

    def test_update_user(self, db_session, user_service: UserService):
        async def _run():
            created = await user_service.create(
                db_session,
                UserCreate(username="to_update_service", email="update_service@example.com"),
            )

            updated = await user_service.update(
                db_session,
                created.id,
                UserUpdate(description="updated via service"),
            )
            assert updated is not None
            assert updated.description == "updated via service"

        asyncio.run(_run())

    def test_delete_user(self, db_session, user_service: UserService):
        async def _run():
            created = await user_service.create(
                db_session,
                UserCreate(username="to_delete_service", email="delete_service@example.com"),
            )

            await user_service.delete(db_session, created.id)
            found = await user_service.get_by_id(db_session, created.id)
            assert found is None

        asyncio.run(_run())

