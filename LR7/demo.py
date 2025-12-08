"""Скрипт для демонстрации всех функций обработки заказов и продукции через RabbitMQ"""

import json
import os
import sys

import pika
from dotenv import load_dotenv
from sqlalchemy import create_engine, select

from models import Product, User
from sqlalchemy.orm import selectinload, sessionmaker

load_dotenv()

# Настройка подключения к RabbitMQ
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "local")

# Настройка подключения к БД
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5433")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://postgres:pass@localhost:{POSTGRES_PORT}/labdb",
)


def send_message(queue_name: str, message: dict) -> None:
    """Отправка сообщения в очередь"""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            virtual_host=RABBITMQ_VHOST,
        )
    )
    channel = connection.channel()
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(message, default=str),
    )
    print(f"Отправлено в очередь '{queue_name}': {json.dumps(message, ensure_ascii=False, indent=2)}")
    connection.close()


def get_data_from_db():
    """Получение данных из БД для демонстрации"""
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Загружаем пользователей с адресами (eager loading)
        stmt = select(User).options(selectinload(User.addresses)).limit(3)
        users = list(session.execute(stmt).scalars().all())
        products = list(session.execute(select(Product)).scalars().all())
        return users, products
    finally:
        session.close()
        engine.dispose()


def demo_create_products():
    """Демонстрация: Прием продукции (создание)"""
    print("\n" + "=" * 60)
    print("1. ДЕМОНСТРАЦИЯ: Прием продукции (создание)")
    print("=" * 60)

    products = [
        {"name": "Ноутбук Gaming Pro", "price": 129990.0, "stock_quantity": 10},
        {"name": "Смартфон Ultra Max", "price": 89990.0, "stock_quantity": 20},
    ]

    for product in products:
        send_message("product", product)
        print()


def demo_update_product(products):
    """Демонстрация: Обновление продукции"""
    print("\n" + "=" * 60)
    print("2. ДЕМОНСТРАЦИЯ: Обновление продукции")
    print("=" * 60)

    if not products:
        print("⚠ Нет продуктов в базе для обновления")
        return

    product = products[0]
    update_message = {
        "id": str(product.id),
        "price": 99999.0,
        "stock_quantity": 15,
    }
    send_message("product", update_message)
    print()


def demo_mark_product_out_of_stock(products):
    """Демонстрация: Отметка продукции как закончившейся"""
    print("\n" + "=" * 60)
    print("3. ДЕМОНСТРАЦИЯ: Отметка продукции как закончившейся")
    print("=" * 60)

    if not products:
        print("⚠ Нет продуктов в базе")
        return

    product = products[-1]  # Берем последний продукт
    message = {
        "id": str(product.id),
        "out_of_stock": True,
    }
    send_message("product", message)
    print()


def demo_create_order(users, products):
    """Демонстрация: Создание заказа с несколькими позициями"""
    print("\n" + "=" * 60)
    print("4. ДЕМОНСТРАЦИЯ: Создание заказа с несколькими позициями")
    print("=" * 60)

    if len(users) < 1 or len(products) < 2:
        print("⚠ Недостаточно данных в базе (нужно минимум 1 пользователь и 2 продукта)")
        return

    order = {
        "user_id": str(users[0].id),
        "address_id": str(users[0].addresses[0].id) if users[0].addresses else None,
        "status": "pending",
        "items": [
            {"product_id": str(products[0].id), "quantity": 1},
            {"product_id": str(products[1].id), "quantity": 2},
        ],
    }
    send_message("order", order)
    print()


def demo_update_order_status():
    """Демонстрация: Обновление статуса заказа"""
    print("\n" + "=" * 60)
    print("5. ДЕМОНСТРАЦИЯ: Обновление статуса заказа")
    print("=" * 60)
    print("⚠ Для этой демонстрации нужен ID существующего заказа")
    print("   Получите ID заказа через API: curl http://localhost:8000/orders")
    print("   Затем используйте команду:")
    print()
    print('   python -c "')
    print('   import pika, json')
    print('   connection = pika.BlockingConnection(')
    print('       pika.ConnectionParameters(host=\'localhost\', port=5672, virtual_host=\'local\')')
    print('   )')
    print('   channel = connection.channel()')
    print('   message = {\'id\': \'ВАШ_UUID_ЗАКАЗА\', \'status\': \'completed\'}')
    print('   channel.basic_publish(exchange=\'\', routing_key=\'order\', body=json.dumps(message))')
    print('   connection.close()')
    print('   "')
    print()


def demo_reject_order_with_out_of_stock(users, products):
    """Демонстрация: Отказ в создании заказа с закончившейся продукцией"""
    print("\n" + "=" * 60)
    print("6. ДЕМОНСТРАЦИЯ: Отказ в создании заказа с закончившейся продукцией")
    print("=" * 60)

    if len(users) < 1 or len(products) < 1:
        print("⚠ Недостаточно данных в базе")
        return

    # Сначала отметим продукт как закончившийся
    product = products[0]
    out_of_stock_message = {
        "id": str(product.id),
        "out_of_stock": True,
    }
    print("Шаг 1: Отмечаем продукт как закончившийся...")
    send_message("product", out_of_stock_message)
    print()

    # Ждем немного, чтобы consumer обработал сообщение
    print("Шаг 2: Пытаемся создать заказ с закончившимся продуктом...")
    import time
    time.sleep(2)  # Даем время на обработку

    order = {
        "user_id": str(users[0].id),
        "address_id": str(users[0].addresses[0].id) if users[0].addresses else None,
        "status": "pending",
        "items": [
            {"product_id": str(product.id), "quantity": 1},
        ],
    }
    send_message("order", order)
    print("В consumer должно появиться сообщение об отказе в создании заказа")
    print()


def main():
    """Главная функция демонстрации"""
    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ОБРАБОТКИ ЗАКАЗОВ И ПРОДУКЦИИ ЧЕРЕЗ RABBITMQ")
    print("=" * 60)
    print("\nУбедитесь, что:")
    print("  1. RabbitMQ запущен (docker-compose up -d rabbitmq)")
    print("  2. Consumer запущен (./run_consumer.sh)")
    print("  3. База данных заполнена (python fill_full_db.py)")
    print()

    try:
        users, products = get_data_from_db()
        print(f"Найдено в базе: {len(users)} пользователей, {len(products)} продуктов\n")
    except Exception as e:
        print(f"⚠ Ошибка при подключении к БД: {e}")
        print("  Продолжаем демонстрацию без данных из БД...\n")
        users, products = [], []

    # Демонстрации
    demo_create_products()
    demo_update_product(products)
    demo_mark_product_out_of_stock(products)
    demo_create_order(users, products)
    demo_update_order_status()
    demo_reject_order_with_out_of_stock(users, products)

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)
    print("\nПроверьте результаты через API:")
    print("  - Список продуктов: curl http://localhost:8000/products")
    print("  - Список заказов: curl http://localhost:8000/orders")
    print()


if __name__ == "__main__":
    main()

