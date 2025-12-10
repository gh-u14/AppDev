from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models import Report, Order, OrderItem


class ReportRepository:
    def __init__(self) -> None:
        self.model = Report

    async def create(
        self,
        session: Session,
        *,
        report_at: datetime,
        order_id: UUID,
        count_product: int,
    ) -> Report:
        """Создать новый отчет."""
        report = self.model(
            report_at=report_at,
            order_id=order_id,
            count_product=count_product,
        )
        session.add(report)
        session.commit()
        session.refresh(report)
        return report

    async def get_by_date(
        self, session: Session, report_date: datetime
    ) -> List[Report]:
        """Получить все отчеты за конкретную дату."""
        # Нормализуем дату (убираем время, оставляем только дату)
        date_start = report_date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        stmt = (
            select(self.model)
            .filter(
                self.model.report_at >= date_start,
                self.model.report_at <= date_end,
            )
        )
        return list(session.execute(stmt).scalars().all())

    async def get_all(self, session: Session) -> List[Report]:
        """Получить все отчеты."""
        stmt = select(self.model)
        return list(session.execute(stmt).scalars().all())

