"""Планировщик задач TaskIQ для формирования отчетов по заказам"""

import os
from datetime import datetime

from dotenv import load_dotenv
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_aio_pika import AioPikaBroker

# Загружаем переменные окружения
load_dotenv()

# Настройка брокера RabbitMQ
# Используем виртуальный хост "local" (как настроено в docker-compose)
RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL", "amqp://guest:guest@localhost:5672/local"
)

broker = AioPikaBroker(
    RABBITMQ_URL,
    exchange_name="report",  # обменник
    queue_name="cmd_order",  # очередь для отправки
)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)


@broker.task(
    schedule=[
        {
            "cron": "*/1 * * * *",  # Выражение cron: каждую минуту
            "args": [],  # Аргументы для функции
            "schedule_id": "generate_order_report",  # Уникальный ID расписания
        }
    ]
)
async def my_scheduled_task() -> str:
    """Задача, выполняемая по расписанию. Формирует отчет по заказам."""
    from app.main import SessionLocal
    from app.repositories.report_repository import ReportRepository
    from app.repositories.order_repository import OrderRepository
    from app.services.report_service import ReportService

    session = SessionLocal()
    try:
        # Создаем репозитории и сервис
        report_repo = ReportRepository()
        order_repo = OrderRepository()
        report_service = ReportService(report_repo, order_repo)

        # Генерируем отчет за текущий день
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        await report_service.generate_report(session, current_date)

        message = f"Отчет по заказам сформирован за {current_date.date()}!"
        print(message)
        return message
    except Exception as e:
        error_message = f"Ошибка при формировании отчета: {e}"
        print(error_message)
        return error_message
    finally:
        session.close()

