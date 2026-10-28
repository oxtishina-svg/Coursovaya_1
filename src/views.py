import json
import logging
import re
from datetime import datetime
from typing import Any

import pandas as pd

from src.utils import get_currency_rates, get_stock_prices, read_transactions, read_user_settings

logger = logging.getLogger(__name__)


def get_greeting(date_time: str) -> str:
    """Возвращает приветствие в зависимости от времени."""
    current_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    hour = current_time.hour

    if 6 <= hour < 12:
        return "Доброе утро"

    if 12 <= hour < 18:
        return "Добрый день"

    if 18 <= hour < 23:
        return "Добрый вечер"

    return "Доброй ночи"


def prepare_transactions(transactions: pd.DataFrame, date_time: str) -> pd.DataFrame:
    """Отбирает транзакции с начала месяца до указанной даты."""
    result = transactions.copy()

    result["Дата операции"] = pd.to_datetime(
        result["Дата операции"],
        dayfirst=True,
        errors="coerce",
    )

    end_date = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    start_date = end_date.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    result = result[(result["Дата операции"] >= start_date) & (result["Дата операции"] <= end_date)]

    return result


def get_card_last_digits(card_number: Any) -> str:
    """Возвращает последние четыре цифры номера карты."""
    digits = re.sub(r"\D", "", str(card_number))

    return digits[-4:]


def get_cards_info(transactions: pd.DataFrame) -> list[dict[str, Any]]:
    """Формирует информацию о расходах и кешбэке по картам."""
    data = transactions.copy()

    data["Сумма платежа"] = pd.to_numeric(
        data["Сумма платежа"],
        errors="coerce",
    )

    data = data[
        data["Номер карты"].notna() & data["Номер карты"].astype(str).str.strip().ne("") & (data["Сумма платежа"] < 0)
    ]

    cards = []

    for card_number, card_transactions in data.groupby("Номер карты"):
        total_spent = abs(float(card_transactions["Сумма платежа"].sum()))

        cards.append(
            {
                "last_digits": get_card_last_digits(card_number),
                "total_spent": round(total_spent, 2),
                "cashback": round(total_spent / 100, 2),
            }
        )

    return cards


def get_top_transactions(transactions: pd.DataFrame) -> list[dict[str, Any]]:
    """Возвращает пять транзакций с наибольшей суммой платежа."""
    data = transactions.copy()

    data["Сумма платежа"] = pd.to_numeric(
        data["Сумма платежа"],
        errors="coerce",
    )

    data = data.dropna(subset=["Сумма платежа"])

    data = data.sort_values(
        by="Сумма платежа",
        ascending=False,
    ).head(5)

    result = []

    for _, transaction in data.iterrows():
        result.append(
            {
                "date": transaction["Дата операции"].strftime("%d.%m.%Y"),
                "amount": float(transaction["Сумма платежа"]),
                "category": str(transaction["Категория"]),
                "description": str(transaction["Описание"]),
            }
        )

    return result


def generate_main_page(
    date_time: str,
    transactions: pd.DataFrame,
    settings: dict[str, Any],
) -> str:
    """Формирует JSON-ответ для страницы «Главная»."""
    filtered_transactions = prepare_transactions(
        transactions,
        date_time,
    )

    currencies = settings.get("user_currencies", [])
    stocks = settings.get("user_stocks", [])

    result = {
        "greeting": get_greeting(date_time),
        "cards": get_cards_info(filtered_transactions),
        "top_transactions": get_top_transactions(filtered_transactions),
        "currency_rates": get_currency_rates(currencies),
        "stock_prices": get_stock_prices(stocks),
    }

    return json.dumps(
        result,
        ensure_ascii=False,
        indent=4,
    )


def main_page(date_time: str) -> str:
    """Основная функция страницы «Главная»."""
    transactions = read_transactions()
    settings = read_user_settings()

    return generate_main_page(
        date_time,
        transactions,
        settings,
    )
