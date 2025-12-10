"""Consumer для обработки сообщений из RabbitMQ очередей"""

from uuid import UUID

from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas import (
    OrderCreate,
    OrderStatusUpdate,
    ProductCreate,
    ProductOutOfStock,
    ProductUpdate,
)
from app.services.order_service import OrderService


async def subscribe_product(message: dict) -> None:
    """Обработка сообщений из очереди product"""
    from app.main import SessionLocal

    session = SessionLocal()
    try:
        product_repo = ProductRepository()

        # Определяем тип операции по наличию полей
        if ("id" in message or "product_id" in message) and message.get("out_of_stock", False):
            # Отметка продукции как закончившейся
            product_id_str = message.get("id") or message.get("product_id")
            product_id = UUID(product_id_str) if isinstance(product_id_str, str) else product_id_str
            if product_id:
                product = await product_repo.get_by_id(session, product_id)
                if product:
                    product.stock_quantity = 0
                    session.commit()
                    print(f"Продукт {product_id} отмечен как закончившийся")
                else:
                    print(f"Продукт {product_id} не найден")
        elif "id" in message or "product_id" in message:
            # Обновление продукции
            product_id_str = message.get("id") or message.get("product_id")
            product_id = UUID(product_id_str) if isinstance(product_id_str, str) else product_id_str
            update_data = ProductUpdate(**{k: v for k, v in message.items() if k not in ("id", "product_id")})
            product = await product_repo.update(session, product_id, update_data)
            if product:
                print(f"Продукт {product_id} обновлен: {product.name}")
            else:
                print(f"Продукт {product_id} не найден")
        else:
            # Создание новой продукции
            product_data = ProductCreate(**message)
            product = await product_repo.create(session, product_data)
            print(f"Создан продукт: {product.name}, цена: {product.price}, количество: {product.stock_quantity}")
    except Exception as e:
        print(f"Ошибка при обработке сообщения product: {e}")
    finally:
        session.close()


async def subscribe_order(message: dict) -> None:
    """Обработка сообщений из очереди order"""
    from app.main import SessionLocal

    session = SessionLocal()
    try:
        order_repo = OrderRepository()
        product_repo = ProductRepository()
        user_repo = UserRepository()
        order_service = OrderService(order_repo, product_repo, user_repo)

        # Определяем тип операции
        if ("order_id" in message or "id" in message) and "status" in message:
            # Обновление статуса заказа
            order_id_str = message.get("order_id") or message.get("id")
            order_id = UUID(order_id_str) if isinstance(order_id_str, str) else order_id_str
            status = message.get("status")
            if order_id and status:
                order = await order_repo.update_status(session, order_id, status)
                if order:
                    print(f"Статус заказа {order_id} обновлен на: {status}")
                else:
                    print(f"Заказ {order_id} не найден")
        else:
            # Создание нового заказа
            # Конвертируем строковые UUID в UUID объекты
            order_message = message.copy()
            if "user_id" in order_message and isinstance(order_message["user_id"], str):
                order_message["user_id"] = UUID(order_message["user_id"])
            if "address_id" in order_message and isinstance(order_message["address_id"], str):
                order_message["address_id"] = UUID(order_message["address_id"])
            if "items" in order_message:
                for item in order_message["items"]:
                    if "product_id" in item and isinstance(item["product_id"], str):
                        item["product_id"] = UUID(item["product_id"])
            order_data = OrderCreate(**order_message)
            
            # Проверяем наличие всех продуктов и их количество на складе
            for item in order_data.items:
                product = await product_repo.get_by_id(session, item.product_id)
                if not product:
                    print(f"Продукт {item.product_id} не найден. Заказ не создан.")
                    return
                if product.stock_quantity == 0:
                    print(f"Продукт {item.product_id} закончился на складе. Заказ не создан.")
                    return
                if product.stock_quantity < item.quantity:
                    print(f"Недостаточно товара {item.product_id}. На складе: {product.stock_quantity}, требуется: {item.quantity}. Заказ не создан.")
                    return
            
            # Создаем заказ
            order = await order_service.create_order(session, order_data)
            print(f"Создан заказ {order.id} для пользователя {order.user_id}, сумма: {order.total_amount}")
    except ValueError as e:
        print(f"Ошибка валидации при обработке заказа: {e}")
    except Exception as e:
        print(f"Ошибка при обработке сообщения order: {e}")
    finally:
        session.close()

