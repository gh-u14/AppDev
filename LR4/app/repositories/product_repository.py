from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models import Product
from app.schemas import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self) -> None:
        self.model = Product

    async def create(self, session: Session, product_data: ProductCreate) -> Product:
        product = self.model(
            name=product_data.name,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity or 0,
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        return product

    async def get_by_id(self, session: Session, product_id: UUID) -> Optional[Product]:
        return session.query(self.model).filter(self.model.id == product_id).first()

    async def list(
        self,
        session: Session,
        count: int = 10,
        page: int = 1,
    ) -> List[Product]:
        query = session.query(self.model)
        return query.offset((page - 1) * count).limit(count).all()

    async def update(
        self,
        session: Session,
        product_id: UUID,
        product_data: ProductUpdate,
    ) -> Optional[Product]:
        product = await self.get_by_id(session, product_id)
        if not product:
            return None
        data = product_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(product, key, value)
        session.commit()
        session.refresh(product)
        return product

    async def delete(self, session: Session, product_id: UUID) -> None:
        product = await self.get_by_id(session, product_id)
        if product:
            session.delete(product)
            session.commit()

