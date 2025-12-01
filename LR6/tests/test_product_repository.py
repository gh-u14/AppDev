import asyncio

from app.repositories.product_repository import ProductRepository
from app.schemas import ProductCreate, ProductUpdate


class TestProductRepository:
    def test_create_product(self, db_session, product_repository: ProductRepository):
        async def _run():
            product = await product_repository.create(
                db_session,
                ProductCreate(name="Test product", price=10.0, stock_quantity=5),
            )
            assert product.name == "Test product"
            assert product.stock_quantity == 5

        asyncio.run(_run())

    def test_list_products(self, db_session, product_repository: ProductRepository):
        async def _run():
            await product_repository.create(
                db_session,
                ProductCreate(name="Product 1", price=5.0, stock_quantity=2),
            )
            await product_repository.create(
                db_session,
                ProductCreate(name="Product 2", price=15.0, stock_quantity=4),
            )
            products = await product_repository.list(db_session, count=10, page=1)
            assert len(products) == 2

        asyncio.run(_run())

    def test_update_product(self, db_session, product_repository: ProductRepository):
        async def _run():
            product = await product_repository.create(
                db_session,
                ProductCreate(name="Product update", price=20.0, stock_quantity=1),
            )

            updated = await product_repository.update(
                db_session,
                product.id,
                ProductUpdate(price=25.0, stock_quantity=3),
            )
            assert updated is not None
            assert updated.price == 25.0
            assert updated.stock_quantity == 3

        asyncio.run(_run())

    def test_delete_product(self, db_session, product_repository: ProductRepository):
        async def _run():
            product = await product_repository.create(
                db_session,
                ProductCreate(name="Product delete", price=30.0, stock_quantity=1),
            )

            await product_repository.delete(db_session, product.id)
            found = await product_repository.get_by_id(db_session, product.id)
            assert found is None

        asyncio.run(_run())

