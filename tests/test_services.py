import json

import pandas as pd

from src.services import simple_search


def test_simple_search_by_category() -> None:
    transactions = pd.DataFrame(
        {
            "Категория": [
                "Супермаркеты",
                "Транспорт",
                "Супермаркеты",
            ],
            "Описание": [
                "Лента",
                "Метро",
                "Перекресток",
            ],
        }
    )

    result = simple_search(
        transactions,
        "супермаркет",
    )

    data = json.loads(result)

    assert len(data) == 2
    assert data[0]["Категория"] == "Супермаркеты"
    assert data[1]["Категория"] == "Супермаркеты"


def test_simple_search_by_description_case_insensitive() -> None:
    transactions = pd.DataFrame(
        {
            "Категория": [
                "Продукты",
                "Транспорт",
            ],
            "Описание": [
                "Ozon.ru",
                "Метро",
            ],
        }
    )

    result = simple_search(
        transactions,
        "OZON",
    )

    data = json.loads(result)

    assert len(data) == 1
    assert data[0]["Описание"] == "Ozon.ru"


def test_simple_search_by_substring() -> None:
    transactions = pd.DataFrame(
        {
            "Категория": [
                "Супермаркеты",
                "Фастфуд",
            ],
            "Описание": [
                "Пятерочка",
                "Burger King",
            ],
        }
    )

    result = simple_search(
        transactions,
        "маркет",
    )

    data = json.loads(result)

    assert len(data) == 1
    assert data[0]["Категория"] == "Супермаркеты"


def test_simple_search_empty_string() -> None:
    transactions = pd.DataFrame(
        {
            "Категория": [
                "Супермаркеты",
            ],
            "Описание": [
                "Лента",
            ],
        }
    )

    result = simple_search(
        transactions,
        "   ",
    )

    assert json.loads(result) == []


def test_simple_search_no_results() -> None:
    transactions = pd.DataFrame(
        {
            "Категория": [
                "Супермаркеты",
            ],
            "Описание": [
                "Лента",
            ],
        }
    )

    result = simple_search(
        transactions,
        "такси",
    )

    assert json.loads(result) == []
