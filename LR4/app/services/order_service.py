from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas import OrderCreate, OrderRead
from models import Order


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
    ) -> None:
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.user_repository = user_repository

    async def create_order(self, session: Session, order_data: OrderCreate) -> Order:
        user = await self.user_repository.get_by_id(session, order_data.user_id)
        if not user:
            raise ValueError("User not found")

        if not order_data.items:
            raise ValueError("Order items cannot be empty")

        prepared_items = []
        for item in order_data.items:
            product = await self.product_repository.get_by_id(session, item.product_id)
            if not product:
                raise ValueError("Product not found")
            if product.stock_quantity < item.quantity:
                raise ValueError("Insufficient stock")

            product.stock_quantity -= item.quantity
            prepared_items.append(
                {
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "price": product.price,
                }
            )

        order = await self.order_repository.create(
            session,
            user_id=order_data.user_id,
            address_id=order_data.address_id,
            status=order_data.status or "pending",
            items=prepared_items,
        )
        return order

    async def get_order(self, session: Session, order_id: UUID) -> Optional[Order]:
        return await self.order_repository.get_by_id(session, order_id)

    async def list_orders(self, session: Session, count: int = 10, page: int = 1) -> List[Order]:
        return await self.order_repository.list(session, count=count, page=page)

    async def update_status(self, session: Session, order_id: UUID, status: str) -> Optional[Order]:
        return await self.order_repository.update_status(session, order_id, status)

    async def delete_order(self, session: Session, order_id: UUID) -> None:
        await self.order_repository.delete(session, order_id)

