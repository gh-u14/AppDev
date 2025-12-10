"""Контроллер для работы с заказами через Litestar API"""

from typing import Any, Dict
from uuid import UUID

from litestar import Controller, get
from litestar.exceptions import NotFoundException
from sqlalchemy.orm import Session

from app.repositories.order_repository import OrderRepository
from app.schemas import OrderRead


class OrderController(Controller):
    path = "/orders"

    @get("/{order_id:uuid}")
    async def get_order_by_id(
        self,
        session: Session,
        order_id: UUID,
    ) -> OrderRead:
        order_repo = OrderRepository()
        order = await order_repo.get_by_id(session, order_id)
        if not order:
            raise NotFoundException(detail=f"Order with ID {order_id} not found")
        return OrderRead.model_validate(order)

    @get()
    async def get_all_orders(
        self,
        session: Session,
        count: int = 10,
        page: int = 1,
    ) -> Dict[str, Any]:
        order_repo = OrderRepository()
        orders = await order_repo.list(session, count=count, page=page)
        total_count = session.query(order_repo.model).count()
        return {
            "total": total_count,
            "page": page,
            "count": count,
            "orders": [OrderRead.model_validate(o) for o in orders],
        }

