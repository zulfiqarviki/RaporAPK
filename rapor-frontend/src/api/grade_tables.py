from typing import Any

from src.api.client import api_request


def list_grade_tables(token: str) -> list[dict[str, Any]]:
    return api_request(
        "GET",
        "/grade-tables/",
        token=token,
    )


def get_grade_table(token: str, grade_table_id: int) -> dict[str, Any]:
    return api_request(
        "GET",
        f"/grade-tables/{grade_table_id}",
        token=token,
    )


def create_grade_table(
    token: str,
    *,
    subject_name: str,
    description: str | None = None,
    teacher_id: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "subject_name": subject_name,
        "description": description,
    }

    if teacher_id is not None:
        payload["teacher_id"] = teacher_id

    return api_request(
        "POST",
        "/grade-tables/",
        token=token,
        json=payload,
    )


def update_grade_table(
    token: str,
    grade_table_id: int,
    *,
    subject_name: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    if subject_name is not None:
        payload["subject_name"] = subject_name

    if description is not None:
        payload["description"] = description

    return api_request(
        "PATCH",
        f"/grade-tables/{grade_table_id}",
        token=token,
        json=payload,
    )


def delete_grade_table(token: str, grade_table_id: int) -> None:
    api_request(
        "DELETE",
        f"/grade-tables/{grade_table_id}",
        token=token,
    )