from src.logging_config import setup_logging
from src.reports import spending_by_category
from src.services import simple_search
from src.utils import read_transactions
from src.views import main_page


def main() -> None:
    setup_logging()

    transactions = read_transactions()

    print("=== ГЛАВНАЯ ===")
    print(main_page("2021-12-31 23:59:59"))

    print("\n=== ПОИСК ===")
    print(simple_search(transactions, "супермаркет"))

    print("\n=== ОТЧЕТ ===")
    report = spending_by_category(
        transactions,
        "Супермаркеты",
        "2021-12-31",
    )
    print(report)


if __name__ == "__main__":
    main()
