from typing import Any

from src.api.client import api_request


EXCEL_MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def export_grade_table(
    token: str,
    grade_table_id: int,
) -> bytes:
    return api_request(
        "GET",
        f"/grade-tables/{grade_table_id}/export/excel",
        token=token,
        timeout=60,
    )


def import_grade_table(
    token: str,
    *,
    file_name: str,
    file_bytes: bytes,
    teacher_id: int | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    if teacher_id is not None:
        params["teacher_id"] = teacher_id

    return api_request(
        "POST",
        "/grade-tables/import/excel",
        token=token,
        params=params,
        files={
            "file": (
                file_name,
                file_bytes,
                EXCEL_MIME_TYPE,
            )
        },
        timeout=60,
    )