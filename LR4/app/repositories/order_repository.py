from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Order, OrderItem


class OrderRepository:
    def __init__(self) -> None:
        self.model = Order

    async def create(
        self,
        session: Session,
        *,
        user_id: UUID,
        address_id: Optional[UUID],
        status: str,
        items: Sequence[dict],
    ) -> Order:
        order = self.model(
            user_id=user_id,
            address_id=address_id,
            status=status,
        )
        session.add(order)
        session.flush()

        total_amount = 0.0
        for item in items:
            quantity = item["quantity"]
            price = item["price"]
            total_amount += price * quantity
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=quantity,
                price_at_purchase=price,
            )
            session.add(order_item)

        order.total_amount = total_amount
        session.commit()
        session.refresh(order)
        session.refresh(order, attribute_names=["items"])
        return order

    async def get_by_id(self, session: Session, order_id: UUID) -> Optional[Order]:
        return session.execute(
            select(self.model)
            .options(selectinload(self.model.items).selectinload(OrderItem.product))
            .filter(self.model.id == order_id)
        ).scalar_one_or_none()

    async def list(self, session: Session, count: int = 10, page: int = 1) -> List[Order]:
        stmt = (
            select(self.model)
            .options(selectinload(self.model.items).selectinload(OrderItem.product))
            .offset((page - 1) * count)
            .limit(count)
        )
        return list(session.execute(stmt).scalars().all())

    async def update_status(
        self,
        session: Session,
        order_id: UUID,
        status: str,
    ) -> Optional[Order]:
        order = session.query(self.model).filter(self.model.id == order_id).first()
        if not order:
            return None
        order.status = status
        session.commit()
        session.refresh(order)
        return order

    async def delete(self, session: Session, order_id: UUID) -> None:
        order = session.query(self.model).filter(self.model.id == order_id).first()
        if order:
            session.delete(order)
            session.commit()

