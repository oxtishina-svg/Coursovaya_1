import pandas as pd

from src import reports
from src.reports import save_report, spending_by_category


def test_spending_by_category() -> None:
    transactions = pd.DataFrame(
        {
            "Дата операции": [
                "01.09.2021",
                "15.10.2021",
                "01.11.2021",
                "15.12.2021",
                "20.12.2021",
            ],
            "Категория": [
                "Супермаркеты",
                "Супермаркеты",
                "Супермаркеты",
                "Супермаркеты",
                "Транспорт",
            ],
            "Сумма платежа": [
                -100.0,
                -200.0,
                -300.0,
                -400.0,
                -500.0,
            ],
        }
    )

    result = spending_by_category.__wrapped__(
        transactions,
        "Супермаркеты",
        "2021-12-31",
    )

    assert len(result) == 3

    assert result["Категория"].tolist() == [
        "Супермаркеты",
        "Супермаркеты",
        "Супермаркеты",
    ]

    assert result["Сумма платежа"].tolist() == [
        -200.0,
        -300.0,
        -400.0,
    ]


def test_spending_by_category_excludes_income() -> None:
    transactions = pd.DataFrame(
        {
            "Дата операции": [
                "01.12.2021",
                "02.12.2021",
            ],
            "Категория": [
                "Супермаркеты",
                "Супермаркеты",
            ],
            "Сумма платежа": [
                -500.0,
                1000.0,
            ],
        }
    )

    result = spending_by_category.__wrapped__(
        transactions,
        "Супермаркеты",
        "2021-12-31",
    )

    assert len(result) == 1
    assert result.iloc[0]["Сумма платежа"] == -500.0


def test_save_report_default_filename(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        reports,
        "REPORTS_DIR",
        tmp_path,
    )

    @save_report()
    def test_report() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "value": [1, 2, 3],
            }
        )

    result = test_report()

    expected_file = tmp_path / "test_report_report.xlsx"

    assert isinstance(result, pd.DataFrame)
    assert expected_file.exists()


def test_save_report_custom_filename(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        reports,
        "REPORTS_DIR",
        tmp_path,
    )

    @save_report("custom_report.xlsx")
    def test_report() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "value": [1],
            }
        )

    test_report()

    expected_file = tmp_path / "custom_report.xlsx"

    assert expected_file.exists()
