import asyncio
import pytest

from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas import ProductCreate
from models import User


def test_create_order_with_multiple_items(
    db_session,
    order_repository: OrderRepository,
    product_repository: ProductRepository,
):
    async def _run():
        user = User(username="order_user", email="order_user@example.com")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        product_one = await product_repository.create(
            db_session,
            ProductCreate(name="Product A", price=10.0, stock_quantity=10),
        )
        product_two = await product_repository.create(
            db_session,
            ProductCreate(name="Product B", price=20.0, stock_quantity=5),
        )

        order = await order_repository.create(
            db_session,
            user_id=user.id,
            address_id=None,
            status="pending",
            items=[
                {"product_id": product_one.id, "quantity": 2, "price": 10.0},
                {"product_id": product_two.id, "quantity": 1, "price": 20.0},
            ],
        )

        assert order.total_amount == pytest.approx(40.0)
        assert len(order.items) == 2

    asyncio.run(_run())


def test_list_and_delete_orders(
    db_session,
    order_repository: OrderRepository,
    product_repository: ProductRepository,
):
    async def _run():
        user = User(username="list_user", email="list_user@example.com")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        product = await product_repository.create(
            db_session,
            ProductCreate(name="Product C", price=5.0, stock_quantity=10),
        )

        created_order = await order_repository.create(
            db_session,
            user_id=user.id,
            address_id=None,
            status="pending",
            items=[{"product_id": product.id, "quantity": 2, "price": 5.0}],
        )

        orders = await order_repository.list(db_session, count=10, page=1)
        assert any(order.id == created_order.id for order in orders)

        fetched = await order_repository.get_by_id(db_session, created_order.id)
        assert fetched is not None
        assert fetched.total_amount == pytest.approx(10.0)

        updated = await order_repository.update_status(db_session, created_order.id, "shipped")
        assert updated is not None
        assert updated.status == "shipped"

        await order_repository.delete(db_session, created_order.id)
        deleted = await order_repository.get_by_id(db_session, created_order.id)
        assert deleted is None

    asyncio.run(_run())

