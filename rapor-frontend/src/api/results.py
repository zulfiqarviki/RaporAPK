from typing import Any

from src.api.client import api_request


def get_results(
    token: str,
    grade_table_id: int,
) -> dict[str, Any]:
    return api_request(
        "GET",
        f"/grade-tables/{grade_table_id}/results",
        token=token,
    )