import json

import pytest
import requests

from src.utils import get_currency_rates, get_stock_prices, read_transactions, read_user_settings


class MockResponse:
    def __init__(
        self,
        json_data: dict,
        status_code: int = 200,
    ) -> None:
        self.json_data = json_data
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.RequestException("API error")

    def json(self) -> dict:
        return self.json_data


def test_read_user_settings(tmp_path) -> None:
    settings_path = tmp_path / "settings.json"

    settings = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL"],
    }

    settings_path.write_text(
        json.dumps(settings),
        encoding="utf-8",
    )

    result = read_user_settings(settings_path)

    assert result == settings


def test_read_user_settings_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        read_user_settings("missing_settings.json")


def test_read_user_settings_invalid_json(tmp_path) -> None:
    settings_path = tmp_path / "settings.json"

    settings_path.write_text(
        "{invalid json}",
        encoding="utf-8",
    )

    with pytest.raises(json.JSONDecodeError):
        read_user_settings(settings_path)


def test_read_transactions(tmp_path) -> None:
    import xlwt

    file_path = tmp_path / "operations.xls"

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Sheet1")

    sheet.write(0, 0, "Дата операции")
    sheet.write(0, 1, "Категория")

    sheet.write(1, 0, "01.12.2021")
    sheet.write(1, 1, "Супермаркеты")

    sheet.write(2, 0, "02.12.2021")
    sheet.write(2, 1, "Транспорт")

    workbook.save(str(file_path))

    result = read_transactions(file_path)

    assert len(result) == 2
    assert result.columns.tolist() == [
        "Дата операции",
        "Категория",
    ]


def test_get_currency_rates(monkeypatch) -> None:
    def mock_get(*args, **kwargs) -> MockResponse:
        return MockResponse(
            {
                "rub": {
                    "rate": 80.5,
                }
            }
        )

    monkeypatch.setattr(
        "src.utils.requests.get",
        mock_get,
    )

    result = get_currency_rates(
        ["USD", "EUR"],
    )

    assert result == [
        {
            "currency": "USD",
            "rate": 80.5,
        },
        {
            "currency": "EUR",
            "rate": 80.5,
        },
    ]


def test_get_currency_rates_api_error(monkeypatch) -> None:
    def mock_get(*args, **kwargs) -> MockResponse:
        return MockResponse(
            {},
            status_code=500,
        )

    monkeypatch.setattr(
        "src.utils.requests.get",
        mock_get,
    )

    result = get_currency_rates(["USD"])

    assert result == []


def test_get_stock_prices(monkeypatch) -> None:
    def mock_get(*args, **kwargs) -> MockResponse:
        return MockResponse(
            {
                "chart": {
                    "result": [
                        {
                            "meta": {
                                "regularMarketPrice": 250.75,
                            }
                        }
                    ]
                }
            }
        )

    monkeypatch.setattr(
        "src.utils.requests.get",
        mock_get,
    )

    result = get_stock_prices(
        ["AAPL", "MSFT"],
    )

    assert result == [
        {
            "stock": "AAPL",
            "price": 250.75,
        },
        {
            "stock": "MSFT",
            "price": 250.75,
        },
    ]


def test_get_stock_prices_api_error(monkeypatch) -> None:
    def mock_get(*args, **kwargs) -> MockResponse:
        return MockResponse(
            {},
            status_code=500,
        )

    monkeypatch.setattr(
        "src.utils.requests.get",
        mock_get,
    )

    result = get_stock_prices(["AAPL"])

    assert result == []
