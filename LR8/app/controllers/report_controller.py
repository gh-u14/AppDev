"""Контроллер для работы с отчетами через Litestar API"""

from datetime import datetime
from typing import Any, Dict, Optional

from litestar import Controller, get
from litestar.exceptions import HTTPException
from sqlalchemy.orm import Session

from app.repositories.report_repository import ReportRepository
from app.schemas import ReportRead


class ReportController(Controller):
    path = "/report"

    @get()
    async def get_report_by_date(
        self,
        session: Session,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Получить отчет по заказам за конкретную дату.
        
        Параметры:
        - date: Дата отчета в формате YYYY-MM-DD (по умолчанию - сегодня)
        """
        # Если дата не указана, используем сегодняшнюю дату
        if date is None:
            report_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            try:
                # Парсим строку даты
                report_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Неверный формат даты. Используйте формат YYYY-MM-DD"
                )
        
        report_repo = ReportRepository()
        reports = await report_repo.get_by_date(session, report_date)
        
        return {
            "date": report_date.date().isoformat(),
            "count": len(reports),
            "reports": [ReportRead.model_validate(r) for r in reports],
        }

