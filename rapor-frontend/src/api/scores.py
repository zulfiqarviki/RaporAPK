from typing import Any

from src.api.client import api_request


def list_scores(
    token: str,
    grade_table_id: int,
) -> list[dict[str, Any]]:
    return api_request(
        "GET",
        f"/grade-tables/{grade_table_id}/scores",
        token=token,
    )


def get_score(
    token: str,
    score_id: int,
) -> dict[str, Any]:
    return api_request(
        "GET",
        f"/scores/{score_id}",
        token=token,
    )


def create_score(
    token: str,
    grade_table_id: int,
    *,
    student_id: int,
    component_id: int,
    score: float,
) -> dict[str, Any]:
    return api_request(
        "POST",
        f"/grade-tables/{grade_table_id}/scores",
        token=token,
        json={
            "student_id": student_id,
            "component_id": component_id,
            "score": score,
        },
    )


def update_score(
    token: str,
    score_id: int,
    *,
    score: float,
) -> dict[str, Any]:
    return api_request(
        "PATCH",
        f"/scores/{score_id}",
        token=token,
        json={
            "score": score,
        },
    )


def delete_score(
    token: str,
    score_id: int,
) -> None:
    api_request(
        "DELETE",
        f"/scores/{score_id}",
        token=token,
    )