from typing import Any

from src.api.client import api_request


def get_summary(
    token: str,
    grade_table_id: int,
) -> dict[str, Any]:
    return api_request(
        "GET",
        f"/grade-tables/{grade_table_id}/analytics/summary",
        token=token,
    )


def get_distribution(
    token: str,
    grade_table_id: int,
    *,
    target: str,
    ranges: list[dict[str, float | str]],
    component_id: int | None = None,
) -> dict[str, Any]:
    return api_request(
        "POST",
        f"/grade-tables/{grade_table_id}/analytics/distribution",
        token=token,
        json={
            "target": target,
            "component_id": component_id,
            "ranges": ranges,
        },
    )


def get_student_progress(
    token: str,
    grade_table_id: int,
    student_id: int,
) -> dict[str, Any]:
    return api_request(
        "GET",
        f"/grade-tables/{grade_table_id}/analytics/students/{student_id}/progress",
        token=token,
    )


def compare_students(
    token: str,
    grade_table_id: int,
    *,
    student_ids: list[int],
    component_id: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "student_ids": student_ids,
    }

    if component_id is not None:
        payload["component_id"] = component_id

    return api_request(
        "POST",
        f"/grade-tables/{grade_table_id}/analytics/student-comparison",
        token=token,
        json=payload,
    )