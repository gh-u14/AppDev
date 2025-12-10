from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.cache import CacheService
from app.schemas import ProductCreate, ProductRead, ProductUpdate
from models import Product


class ProductRepository:
    def __init__(self) -> None:
        self.model = Product
        self.cache_service = CacheService()

    async def create(self, session: Session, product_data: ProductCreate) -> Product:
        product = self.model(
            name=product_data.name,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity or 0,
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        # Инвалидируем кэш списков продуктов при создании нового продукта
        self.cache_service.invalidate_products_list()
        return product

    async def get_by_id(self, session: Session, product_id: UUID) -> Optional[Product]:
        # Проверяем кэш
        cached_data = self.cache_service.get_cached_product(product_id)
        if cached_data:
            # Восстанавливаем объект Product из кэша
            product = Product(
                id=UUID(cached_data["id"]),
                name=cached_data["name"],
                price=cached_data["price"],
                stock_quantity=cached_data["stock_quantity"],
                created_at=datetime.fromisoformat(cached_data["created_at"]) if isinstance(cached_data["created_at"], str) else cached_data["created_at"],
            )
            return product

        # Если нет в кэше, получаем из БД
        product = session.query(self.model).filter(self.model.id == product_id).first()
        if product:
            # Кэшируем данные продукта на 10 минут
            product_data = ProductRead.model_validate(product).model_dump()
            self.cache_service.cache_product(product_id, product_data)

        return product

    async def list(
        self,
        session: Session,
        count: int = 10,
        page: int = 1,
    ) -> List[Product]:
        # Проверяем кэш
        cached_data = self.cache_service.get_cached_products_list(page, count)
        if cached_data:
            # Восстанавливаем список продуктов из кэша
            products = []
            for product_data in cached_data["products"]:
                product = Product(
                    id=UUID(product_data["id"]),
                    name=product_data["name"],
                    price=product_data["price"],
                    stock_quantity=product_data["stock_quantity"],
                    created_at=datetime.fromisoformat(product_data["created_at"]) if isinstance(product_data["created_at"], str) else product_data["created_at"],
                )
                products.append(product)
            return products

        # Если нет в кэше, получаем из БД
        query = session.query(self.model)
        products = query.offset((page - 1) * count).limit(count).all()
        
        if products:
            # Кэшируем список продуктов на 10 минут
            total_count = session.query(self.model).count()
            products_data = [ProductRead.model_validate(p).model_dump() for p in products]
            self.cache_service.cache_products_list(page, count, products_data, total_count)

        return products

    async def update(
        self,
        session: Session,
        product_id: UUID,
        product_data: ProductUpdate,
    ) -> Optional[Product]:
        # Получаем продукт из БД (без кэша, чтобы получить актуальные данные)
        product = session.query(self.model).filter(self.model.id == product_id).first()
        if not product:
            return None
        data = product_data.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(product, key, value)
        session.commit()
        session.refresh(product)
        
        # Обновляем данные в кэше
        if product:
            product_data_dict = ProductRead.model_validate(product).model_dump()
            self.cache_service.update_cached_product(product_id, product_data_dict)
            # Инвалидируем кэш списков продуктов
            self.cache_service.invalidate_products_list()
        
        return product

    async def delete(self, session: Session, product_id: UUID) -> None:
        product = await self.get_by_id(session, product_id)
        if product:
            session.delete(product)
            session.commit()
            # Удаляем продукт из кэша и инвалидируем кэш списков
            self.cache_service.delete(f"product:{product_id}")
            self.cache_service.invalidate_products_list()
