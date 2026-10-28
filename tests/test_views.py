import json

import pandas as pd

from src.views import (
    generate_main_page,
    get_card_last_digits,
    get_cards_info,
    get_greeting,
    get_top_transactions,
    prepare_transactions,
)


def test_get_greeting() -> None:
    assert get_greeting("2021-12-31 06:00:00") == "Доброе утро"
    assert get_greeting("2021-12-31 11:59:59") == "Доброе утро"

    assert get_greeting("2021-12-31 12:00:00") == "Добрый день"
    assert get_greeting("2021-12-31 17:59:59") == "Добрый день"

    assert get_greeting("2021-12-31 18:00:00") == "Добрый вечер"
    assert get_greeting("2021-12-31 22:59:59") == "Добрый вечер"

    assert get_greeting("2021-12-31 23:00:00") == "Доброй ночи"
    assert get_greeting("2021-12-31 05:59:59") == "Доброй ночи"


def test_prepare_transactions() -> None:
    transactions = pd.DataFrame(
        {
            "Дата операции": [
                "30.11.2021 12:00:00",
                "01.12.2021 10:00:00",
                "15.12.2021 15:00:00",
                "31.12.2021 23:00:00",
                "01.01.2022 10:00:00",
            ]
        }
    )

    result = prepare_transactions(
        transactions,
        "2021-12-31 23:59:59",
    )

    assert len(result) == 3
    assert result["Дата операции"].min() == pd.Timestamp("2021-12-01 10:00:00")
    assert result["Дата операции"].max() == pd.Timestamp("2021-12-31 23:00:00")


def test_get_card_last_digits() -> None:
    assert get_card_last_digits("*4556") == "4556"
    assert get_card_last_digits("1234 5678 9012 7197") == "7197"
    assert get_card_last_digits("****5091") == "5091"


def test_get_cards_info() -> None:
    transactions = pd.DataFrame(
        {
            "Номер карты": [
                "*4556",
                "*4556",
                "*5091",
                "",
                None,
            ],
            "Сумма платежа": [
                -1000.0,
                -500.0,
                -250.0,
                -10000.0,
                -20000.0,
            ],
        }
    )

    result = get_cards_info(transactions)

    assert len(result) == 2

    cards = {card["last_digits"]: card for card in result}

    assert cards["4556"]["total_spent"] == 1500.0
    assert cards["4556"]["cashback"] == 15.0

    assert cards["5091"]["total_spent"] == 250.0
    assert cards["5091"]["cashback"] == 2.5


def test_get_top_transactions() -> None:
    transactions = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                [
                    "2021-12-01",
                    "2021-12-02",
                    "2021-12-03",
                    "2021-12-04",
                    "2021-12-05",
                    "2021-12-06",
                ]
            ),
            "Сумма платежа": [
                100.0,
                500.0,
                300.0,
                700.0,
                200.0,
                600.0,
            ],
            "Категория": [
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
            ],
            "Описание": [
                "Операция 1",
                "Операция 2",
                "Операция 3",
                "Операция 4",
                "Операция 5",
                "Операция 6",
            ],
        }
    )

    result = get_top_transactions(transactions)

    assert len(result) == 5

    amounts = [transaction["amount"] for transaction in result]

    assert amounts == [
        700.0,
        600.0,
        500.0,
        300.0,
        200.0,
    ]

    assert result[0]["date"] == "04.12.2021"
    assert result[0]["category"] == "D"
    assert result[0]["description"] == "Операция 4"


def test_generate_main_page(monkeypatch) -> None:
    transactions = pd.DataFrame(
        {
            "Дата операции": [
                "01.12.2021 10:00:00",
                "10.12.2021 12:00:00",
                "20.12.2021 14:00:00",
                "25.12.2021 15:00:00",
                "27.12.2021 16:00:00",
                "30.12.2021 17:00:00",
            ],
            "Номер карты": [
                "*4556",
                "*4556",
                "*4556",
                "*4556",
                "*4556",
                "*4556",
            ],
            "Сумма платежа": [
                -100.0,
                -200.0,
                -300.0,
                -400.0,
                -500.0,
                -600.0,
            ],
            "Категория": [
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
            ],
            "Описание": [
                "Операция 1",
                "Операция 2",
                "Операция 3",
                "Операция 4",
                "Операция 5",
                "Операция 6",
            ],
        }
    )

    settings = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "MSFT"],
    }

    monkeypatch.setattr(
        "src.views.get_currency_rates",
        lambda currencies: [
            {"currency": "USD", "rate": 80.0},
            {"currency": "EUR", "rate": 90.0},
        ],
    )

    monkeypatch.setattr(
        "src.views.get_stock_prices",
        lambda stocks: [
            {"stock": "AAPL", "price": 200.0},
            {"stock": "MSFT", "price": 500.0},
        ],
    )

    result = generate_main_page(
        "2021-12-31 12:00:00",
        transactions,
        settings,
    )

    data = json.loads(result)

    assert data["greeting"] == "Добрый день"

    assert len(data["cards"]) == 1
    assert data["cards"][0]["last_digits"] == "4556"
    assert data["cards"][0]["total_spent"] == 2100.0
    assert data["cards"][0]["cashback"] == 21.0

    assert len(data["top_transactions"]) == 5

    assert data["currency_rates"] == [
        {"currency": "USD", "rate": 80.0},
        {"currency": "EUR", "rate": 90.0},
    ]

    assert data["stock_prices"] == [
        {"stock": "AAPL", "price": 200.0},
        {"stock": "MSFT", "price": 500.0},
    ]
