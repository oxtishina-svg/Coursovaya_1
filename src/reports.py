import logging
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"


def save_report(
    filename: Optional[str] = None,
) -> Callable[[Callable[..., pd.DataFrame]], Callable[..., pd.DataFrame]]:
    """Сохраняет результат функции-отчета в Excel-файл."""

    def decorator(
        function: Callable[..., pd.DataFrame],
    ) -> Callable[..., pd.DataFrame]:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            result = function(*args, **kwargs)

            REPORTS_DIR.mkdir(exist_ok=True)

            report_filename = filename or f"{function.__name__}_report.xlsx"
            report_path = REPORTS_DIR / report_filename

            result.to_excel(
                report_path,
                index=False,
            )

            logger.info("Отчет сохранен: %s", report_path)

            return result

        return wrapper

    return decorator


@save_report()
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: Optional[str] = None,
) -> pd.DataFrame:
    """Возвращает траты по категории за последние три месяца."""
    data = transactions.copy()

    data["Дата операции"] = pd.to_datetime(
        data["Дата операции"],
        dayfirst=True,
        errors="coerce",
    )

    data["Сумма платежа"] = pd.to_numeric(
        data["Сумма платежа"],
        errors="coerce",
    )

    if date is None:
        end_date = pd.Timestamp(datetime.now())
    else:
        end_date = pd.to_datetime(date)

    start_date = end_date - pd.DateOffset(months=3)

    result = data[
        (data["Дата операции"] >= start_date)
        & (data["Дата операции"] <= end_date)
        & (data["Категория"] == category)
        & (data["Сумма платежа"] < 0)
    ].copy()

    logger.info(
        "Сформирован отчет по категории '%s'. Найдено транзакций: %s",
        category,
        len(result),
    )

    return result
