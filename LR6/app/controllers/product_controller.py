"""Контроллер для работы с продуктами через Litestar API"""

from typing import Any, Dict
from uuid import UUID

from litestar import Controller, get
from litestar.exceptions import NotFoundException
from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.schemas import ProductRead


class ProductController(Controller):
    path = "/products"

    @get("/{product_id:uuid}")
    async def get_product_by_id(
        self,
        session: Session,
        product_id: UUID,
    ) -> ProductRead:
        product_repo = ProductRepository()
        product = await product_repo.get_by_id(session, product_id)
        if not product:
            raise NotFoundException(detail=f"Product with ID {product_id} not found")
        return ProductRead.model_validate(product)

    @get()
    async def get_all_products(
        self,
        session: Session,
        count: int = 10,
        page: int = 1,
    ) -> Dict[str, Any]:
        product_repo = ProductRepository()
        products = await product_repo.list(session, count=count, page=page)
        total_count = session.query(product_repo.model).count()
        return {
            "total": total_count,
            "page": page,
            "count": count,
            "products": [ProductRead.model_validate(p) for p in products],
        }

