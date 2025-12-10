import asyncio
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from app.services.order_service import OrderService
from app.schemas import OrderCreate, OrderItemCreate


def test_create_order_success():
    async def _run():
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=UUID(int=1))

        product = Mock(id=UUID(int=2), price=100.0, stock_quantity=5)
        mock_product_repo.get_by_id.return_value = product

        mock_order_repo.create.return_value = Mock(total_amount=200.0)

        service = OrderService(mock_order_repo, mock_product_repo, mock_user_repo)

        order_data = OrderCreate(
            user_id=UUID(int=1),
            address_id=None,
            items=[OrderItemCreate(product_id=UUID(int=2), quantity=2)],
        )

        result = await service.create_order(Mock(), order_data)
        assert result.total_amount == 200.0
        assert product.stock_quantity == 3
        mock_order_repo.create.assert_awaited_once()

    asyncio.run(_run())


def test_create_order_insufficient_stock():
    async def _run():
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=UUID(int=1))
        mock_product_repo.get_by_id.return_value = Mock(
            id=UUID(int=2),
            price=100.0,
            stock_quantity=1,
        )

        service = OrderService(mock_order_repo, mock_product_repo, mock_user_repo)

        order_data = OrderCreate(
            user_id=UUID(int=1),
            address_id=None,
            items=[OrderItemCreate(product_id=UUID(int=2), quantity=5)],
        )

        with pytest.raises(ValueError, match="Insufficient stock"):
            await service.create_order(Mock(), order_data)

    asyncio.run(_run())


def test_create_order_without_items():
    async def _run():
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        mock_user_repo.get_by_id.return_value = Mock(id=UUID(int=1))

        service = OrderService(mock_order_repo, mock_product_repo, mock_user_repo)

        order_data = OrderCreate(
            user_id=UUID(int=1),
            address_id=None,
            items=[],
        )

        with pytest.raises(ValueError, match="Order items cannot be empty"):
            await service.create_order(Mock(), order_data)

    asyncio.run(_run())

