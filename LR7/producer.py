"""Продюсер данных для отправки сообщений в RabbitMQ очереди"""

import json
import os
from uuid import UUID

import pika
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import User, Product

load_dotenv()

# Настройка подключения к RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "local")

# Настройка подключения к БД для получения пользователей
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://postgres:pass@localhost:{POSTGRES_PORT}/labdb",
)


def send_message_to_queue(
    connection: pika.BlockingConnection,
    queue_name: str,
    message: dict,
) -> None:
    """Отправка сообщения в очередь"""
    channel = connection.channel()
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(message, default=str),
    )
    print(f"Отправлено сообщение в очередь '{queue_name}': {message}")
    channel.close()


def create_products(connection: pika.BlockingConnection) -> list[dict]:
    """Создание 5 продуктов через очередь"""
    products = [
        {"name": "Ноутбук Gaming Pro", "price": 129990.0, "stock_quantity": 10},
        {"name": "Смартфон Ultra Max", "price": 89990.0, "stock_quantity": 20},
        {"name": "Планшет Tablet X", "price": 45990.0, "stock_quantity": 15},
        {"name": "Клавиатура Mechanical", "price": 12990.0, "stock_quantity": 30},
        {"name": "Мышь Wireless Pro", "price": 5990.0, "stock_quantity": 25},
    ]

    created_products = []
    for product in products:
        send_message_to_queue(connection, "product", product)
        created_products.append(product)

    return created_products


def create_orders(connection: pika.BlockingConnection) -> None:
    """Создание 3 заказов через очередь"""
    # Получаем пользователей из БД
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        users = session.query(User).limit(3).all()
        if len(users) < 3:
            print("Внимание: В базе данных меньше 3 пользователей. Создайте пользователей через fill_full_db.py")
            return

        # Получаем продукты из БД для создания заказов
        products = session.query(Product).all()
        if len(products) < 2:
            print("Внимание: В базе данных недостаточно продуктов. Сначала создайте продукты.")
            return

        # Заказ 1: пользователь 1, несколько товаров
        order1_items = [
            {"product_id": str(products[0].id), "quantity": 1},
        ]
        # Добавляем второй товар, если есть минимум 3 продукта
        if len(products) >= 3:
            order1_items.append({"product_id": str(products[2].id), "quantity": 2})
        
        order1 = {
            "user_id": str(users[0].id),
            "address_id": str(users[0].addresses[0].id) if users[0].addresses else None,
            "status": "pending",
            "items": order1_items,
        }
        send_message_to_queue(connection, "order", order1)

        # Заказ 2: пользователь 2, один товар
        product_idx_2 = 1 if len(products) > 1 else 0
        order2 = {
            "user_id": str(users[1].id),
            "address_id": str(users[1].addresses[0].id) if users[1].addresses else None,
            "status": "pending",
            "items": [
                {"product_id": str(products[product_idx_2].id), "quantity": 1},
            ],
        }
        send_message_to_queue(connection, "order", order2)

        # Заказ 3: пользователь 3, несколько товаров
        # Используем последние доступные продукты
        order3_items = []
        if len(products) >= 4:
            # Если есть 4+ продукта, используем 3-й и 2-й
            order3_items = [
                {"product_id": str(products[3].id), "quantity": 1},
                {"product_id": str(products[2].id), "quantity": 1},
            ]
        elif len(products) >= 2:
            # Если есть 2-3 продукта, используем последний и предпоследний
            order3_items = [
                {"product_id": str(products[-1].id), "quantity": 1},
                {"product_id": str(products[-2].id), "quantity": 1},
            ]
        elif len(products) == 1:
            # Если только один продукт, используем его
            order3_items = [
                {"product_id": str(products[0].id), "quantity": 1},
            ]
        
        if order3_items:
            order3 = {
                "user_id": str(users[2].id),
                "address_id": str(users[2].addresses[0].id) if users[2].addresses else None,
                "status": "pending",
                "items": order3_items,
            }
            send_message_to_queue(connection, "order", order3)

    finally:
        session.close()
        engine.dispose()


def main() -> None:
    """Основная функция для отправки сообщений"""
    # Создание подключения к RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VHOST,
        )
    )

    try:
        print("=== Создание продуктов ===")
        products = create_products(connection)
        print(f"Создано {len(products)} продуктов\n")

        print("=== Создание заказов ===")
        create_orders(connection)
        print("Создано 3 заказа\n")

        print("Все сообщения успешно отправлены в очереди RabbitMQ")
    finally:
        connection.close()


if __name__ == "__main__":
    main()

