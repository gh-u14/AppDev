import asyncio

from app.repositories.product_repository import ProductRepository
from app.schemas import ProductCreate


def test_product_pagination(db_session, product_repository: ProductRepository):
    async def _run():
        for i in range(1, 6):
            await product_repository.create(
                db_session,
                ProductCreate(name=f"Product {i}", price=float(10 * i), stock_quantity=i),
            )

        first_page = await product_repository.list(db_session, count=2, page=1)
        second_page = await product_repository.list(db_session, count=2, page=2)
        third_page = await product_repository.list(db_session, count=2, page=3)

        assert [product.name for product in first_page] == ["Product 1", "Product 2"]
        assert [product.name for product in second_page] == ["Product 3", "Product 4"]
        assert [product.name for product in third_page] == ["Product 5"]
        assert len(third_page) == 1

    asyncio.run(_run())
