from typing import Any

from src.api.client import api_request


def list_students(
    token: str,
    grade_table_id: int,
) -> list[dict[str, Any]]:
    return api_request(
        "GET",
        f"/grade-tables/{grade_table_id}/students",
        token=token,
    )


def get_student(
    token: str,
    student_id: int,
) -> dict[str, Any]:
    return api_request(
        "GET",
        f"/students/{student_id}",
        token=token,
    )


def create_student(
    token: str,
    grade_table_id: int,
    *,
    name: str,
    student_number: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": name,
        "student_number": student_number,
    }

    return api_request(
        "POST",
        f"/grade-tables/{grade_table_id}/students",
        token=token,
        json=payload,
    )


def update_student(
    token: str,
    student_id: int,
    *,
    name: str | None = None,
    student_number: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    if name is not None:
        payload["name"] = name

    if student_number is not None:
        payload["student_number"] = student_number

    return api_request(
        "PATCH",
        f"/students/{student_id}",
        token=token,
        json=payload,
    )


def clear_student_number(
    token: str,
    student_id: int,
) -> dict[str, Any]:
    return api_request(
        "PATCH",
        f"/students/{student_id}",
        token=token,
        json={
            "student_number": None,
        },
    )


def delete_student(
    token: str,
    student_id: int,
) -> None:
    api_request(
        "DELETE",
        f"/students/{student_id}",
        token=token,
    )