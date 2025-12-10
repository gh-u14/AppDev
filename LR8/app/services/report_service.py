from datetime import datetime
from typing import List

from sqlalchemy.orm import Session, selectinload

from app.repositories.report_repository import ReportRepository
from app.repositories.order_repository import OrderRepository
from models import Report, Order, OrderItem


class ReportService:
    def __init__(
        self,
        report_repository: ReportRepository,
        order_repository: OrderRepository,
    ) -> None:
        self.report_repository = report_repository
        self.order_repository = order_repository

    async def generate_report(self, session: Session, report_date: datetime) -> None:
        """Сгенерировать отчет по заказам за указанную дату."""
        from sqlalchemy import select
        
        # Получаем все заказы за указанную дату
        date_start = report_date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Получаем все заказы за этот день с загрузкой items
        stmt = (
            select(Order)
            .options(selectinload(Order.items))
            .filter(
                Order.created_at >= date_start,
                Order.created_at <= date_end,
            )
        )
        orders = list(session.execute(stmt).scalars().all())
        
        # Получаем существующие отчеты один раз для всех заказов
        existing_reports = await self.report_repository.get_by_date(session, report_date)
        existing_order_ids = {r.order_id for r in existing_reports}
        
        new_reports_count = 0
        # Для каждого заказа создаем отчет (если его еще нет)
        for order in orders:
            if order.id not in existing_order_ids:
                # Подсчитываем количество продуктов в заказе
                count_product = sum(item.quantity for item in order.items)
                
                # Создаем отчет
                await self.report_repository.create(
                    session,
                    report_at=report_date,
                    order_id=order.id,
                    count_product=count_product,
                )
                new_reports_count += 1
        
        print(f"Обработано заказов: {len(orders)}, создано новых отчетов: {new_reports_count}, существующих отчетов: {len(existing_reports)}")

    async def get_reports_by_date(
        self, session: Session, report_date: datetime
    ) -> List[Report]:
        """Получить отчеты за конкретную дату."""
        return await self.report_repository.get_by_date(session, report_date)

