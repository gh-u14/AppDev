from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Address, Product, Order, OrderItem

load_dotenv()

POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://postgres:pass@localhost:{POSTGRES_PORT}/labdb",
)

def main() -> None:
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(bind=engine)

    # Полностью пересоздаём структуру — подходит для локального тестирования
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session = SessionLocal()

    try:
        users = seed_users(session)
        products = seed_products(session)
        seed_orders(session, users, products)
        session.commit()
        print("База успешно заполнена тестовыми данными")
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        raise exc
    finally:
        session.close()
        engine.dispose()


def seed_users(session) -> list[User]:
    users: list[User] = []

    alice = User(
        username="alice",
        email="alice@example.com",
        description="Активный покупатель",
    )
    alice.addresses = [
        Address(
            street="Ленина, 12",
            city="Екатеринбург",
            state="Свердловская область",
            country="Россия",
            zip_code="620000",
            is_primary=True,
        ),
        Address(
            street="Мира, 5",
            city="Челябинск",
            state="Челябинская область",
            country="Россия",
            zip_code="454000",
            is_primary=False,
        ),
    ]
    users.append(alice)

    bob = User(
        username="bob",
        email="bob@example.com",
        description="Любит технику",
    )
    bob.addresses = [
        Address(
            street="Невский проспект, 25",
            city="Санкт-Петербург",
            state="Ленинградская область",
            country="Россия",
            zip_code="190000",
            is_primary=True,
        )
    ]
    users.append(bob)

    carol = User(
        username="carol",
        email="carol@example.com",
        description="Тестовый пользователь",
    )
    carol.addresses = [
        Address(
            street="Тверская, 8",
            city="Москва",
            state="Москва",
            country="Россия",
            zip_code="101000",
            is_primary=True,
        )
    ]
    users.append(carol)

    session.add_all(users)
    session.flush()

    print(f"Создано пользователей: {len(users)}")
    return users


def seed_products(session) -> list[Product]:
    products = [
        Product(name="Ноутбук Aurora 15", price=79900.0, stock_quantity=8),
        Product(name="Смартфон Vega X", price=45990.0, stock_quantity=15),
        Product(name="Наушники Pulse", price=8990.0, stock_quantity=25),
        Product(name="Монитор LightView", price=25990.0, stock_quantity=5),
    ]

    session.add_all(products)
    session.flush()
    print(f"Создано товаров: {len(products)}")
    return products


def seed_orders(session, users: list[User], products: list[Product]) -> None:
    def create_order(user: User, address: Address | None, items: list[tuple[Product, int]], status: str) -> None:
        order = Order(
            user_id=user.id,
            address_id=address.id if address else None,
            status=status,
        )
        session.add(order)
        session.flush()

        total = 0.0
        for product, quantity in items:
            session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price_at_purchase=product.price,
                )
            )
            product.stock_quantity = max(product.stock_quantity - quantity, 0)
            total += product.price * quantity

        order.total_amount = total
        session.add(order)

    create_order(
        users[0],
        next((addr for addr in users[0].addresses if addr.is_primary), None),
        [(products[0], 1), (products[2], 2)],
        status="processing",
    )

    create_order(
        users[1],
        next((addr for addr in users[1].addresses if addr.is_primary), None),
        [(products[1], 1)],
        status="pending",
    )

    create_order(
        users[2],
        next((addr for addr in users[2].addresses if addr.is_primary), None),
        [(products[3], 1), (products[2], 1)],
        status="shipped",
    )

    print("Созданы тестовые заказы")


if __name__ == "__main__":
    main()
