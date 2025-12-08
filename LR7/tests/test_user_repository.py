import asyncio

from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserUpdate


class TestUserRepository:
    def test_create_user(self, db_session, user_repository: UserRepository):
        async def _run():
            user = await user_repository.create(
                db_session,
                UserCreate(username="repo_user", email="repo_user@example.com"),
            )
            assert user.id is not None
            assert user.username == "repo_user"
            assert user.email == "repo_user@example.com"

        asyncio.run(_run())

    def test_get_user_by_email(self, db_session, user_repository: UserRepository):
        async def _run():
            created = await user_repository.create(
                db_session,
                UserCreate(username="email_user", email="email@example.com"),
            )

            found = await user_repository.get_by_email(db_session, "email@example.com")
            assert found is not None
            assert found.id == created.id

        asyncio.run(_run())

    def test_get_by_filter_returns_list(self, db_session, user_repository: UserRepository):
        async def _run():
            await user_repository.create(
                db_session,
                UserCreate(username="user1", email="user1@example.com"),
            )
            await user_repository.create(
                db_session,
                UserCreate(username="user2", email="user2@example.com"),
            )

            users = await user_repository.get_by_filter(db_session, count=10, page=1)
            usernames = sorted([user.username for user in users])
            assert usernames == ["user1", "user2"]

        asyncio.run(_run())

    def test_update_user(self, db_session, user_repository: UserRepository):
        async def _run():
            created = await user_repository.create(
                db_session,
                UserCreate(username="to_update", email="update@example.com", description="old"),
            )

            updated = await user_repository.update(
                db_session,
                created.id,
                UserUpdate(description="new description"),
            )
            assert updated is not None
            assert updated.description == "new description"
            assert updated.username == "to_update"

        asyncio.run(_run())

    def test_delete_user(self, db_session, user_repository: UserRepository):
        async def _run():
            created = await user_repository.create(
                db_session,
                UserCreate(username="to_delete", email="delete@example.com"),
            )

            await user_repository.delete(db_session, created.id)
            deleted = await user_repository.get_by_id(db_session, created.id)
            assert deleted is None

        asyncio.run(_run())

