"""Отдельное приложение для запуска FastStream consumer"""

import asyncio
import os

from dotenv import load_dotenv
from faststream import FastStream
from faststream.rabbit import RabbitBroker

from app.consumers import subscribe_order, subscribe_product

load_dotenv()

# === Настройка RabbitMQ ===
RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL", "amqp://guest:guest@localhost:5672/local"
)
broker = RabbitBroker(RABBITMQ_URL)
app = FastStream(broker)

# Регистрируем подписчиков
broker.subscriber("order")(subscribe_order)
broker.subscriber("product")(subscribe_product)


async def main() -> None:
    """Запуск FastStream приложения"""
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())

