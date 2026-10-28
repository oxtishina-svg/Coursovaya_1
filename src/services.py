import json
import logging
from typing import Any, cast

import pandas as pd

logger = logging.getLogger(__name__)


def simple_search(
    transactions: pd.DataFrame,
    search_string: str,
) -> str:
    """Ищет транзакции по подстроке в категории или описании."""
    if not search_string.strip():
        return json.dumps([], ensure_ascii=False, indent=4)

    search_text = search_string.strip()

    category_matches = (
        transactions["Категория"]
        .fillna("")
        .astype(str)
        .str.contains(
            search_text,
            case=False,
            regex=False,
        )
    )

    description_matches = (
        transactions["Описание"]
        .fillna("")
        .astype(str)
        .str.contains(
            search_text,
            case=False,
            regex=False,
        )
    )

    result = transactions[category_matches | description_matches]

    records = cast(
        list[dict[str, Any]],
        result.to_dict(orient="records"),
    )

    logger.info(
        "По запросу '%s' найдено транзакций: %s",
        search_string,
        len(records),
    )

    return json.dumps(
        records,
        ensure_ascii=False,
        indent=4,
        default=str,
    )
