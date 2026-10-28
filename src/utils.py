import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import xlrd

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "operations.xls"
SETTINGS_PATH = BASE_DIR / "user_settings.json"

logger = logging.getLogger(__name__)


def read_transactions(file_path: str | Path = DATA_PATH) -> pd.DataFrame:
    """Читает Excel-файл с транзакциями и возвращает DataFrame."""
    try:
        workbook = xlrd.open_workbook(str(file_path))
        sheet = workbook.sheet_by_index(0)

        headers = [str(header) for header in sheet.row_values(0)]
        rows = [list(sheet.row_values(row_index)) for row_index in range(1, sheet.nrows)]

        transactions: pd.DataFrame = pd.DataFrame(
            data=rows,
            columns=headers,
        )

        logger.info("Файл с транзакциями успешно прочитан: %s", file_path)
        return transactions

    except FileNotFoundError:
        logger.error("Файл с транзакциями не найден: %s", file_path)
        raise
    except Exception as error:
        logger.error("Ошибка при чтении файла с транзакциями: %s", error)
        raise


def read_user_settings(file_path: str | Path = SETTINGS_PATH) -> dict[str, Any]:
    """Читает пользовательские настройки из JSON-файла."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            settings: dict[str, Any] = json.load(file)

        logger.info("Файл пользовательских настроек успешно прочитан: %s", file_path)
        return settings

    except FileNotFoundError:
        logger.error("Файл пользовательских настроек не найден: %s", file_path)
        raise
    except json.JSONDecodeError:
        logger.error("Ошибка декодирования JSON-файла: %s", file_path)
        raise


def get_currency_rates(currencies: list[str]) -> list[dict[str, Any]]:
    """Получает курсы валют к рублю."""
    result: list[dict[str, Any]] = []

    for currency in currencies:
        try:
            url = f"https://www.floatrates.com/daily/{currency.lower()}.json"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            rate = float(data["rub"]["rate"])

            result.append(
                {
                    "currency": currency,
                    "rate": rate,
                }
            )

        except (requests.RequestException, KeyError, TypeError, ValueError) as error:
            logger.error("Не удалось получить курс %s: %s", currency, error)

    return result


def get_stock_prices(stocks: list[str]) -> list[dict[str, Any]]:
    """Получает текущие цены акций."""
    result: list[dict[str, Any]] = []

    for stock in stocks:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}"

            response = requests.get(
                url,
                params={
                    "interval": "1d",
                    "range": "1d",
                },
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            price = float(data["chart"]["result"][0]["meta"]["regularMarketPrice"])

            result.append(
                {
                    "stock": stock,
                    "price": price,
                }
            )

        except (
            requests.RequestException,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ) as error:
            logger.error(
                "Не удалось получить стоимость акции %s: %s",
                stock,
                error,
            )

    return result
