from typing import Any

from src.api.client import api_request


def list_teachers(token: str) -> list[dict[str, Any]]:
    return api_request(
        "GET",
        "/admin/teachers",
        token=token,
    )


def create_teacher(
    token: str,
    *,
    nip: str,
    name: str,
    password: str,
) -> dict[str, Any]:
    return api_request(
        "POST",
        "/admin/teachers",
        token=token,
        json={
            "nip": nip,
            "name": name,
            "password": password,
        },
    )


def update_teacher(
    token: str,
    teacher_id: int,
    *,
    nip: str | None = None,
    name: str | None = None,
    password: str | None = None,
    is_active: bool | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    if nip is not None:
        payload["nip"] = nip

    if name is not None:
        payload["name"] = name

    if password is not None:
        payload["password"] = password

    if is_active is not None:
        payload["is_active"] = is_active

    return api_request(
        "PATCH",
        f"/admin/teachers/{teacher_id}",
        token=token,
        json=payload,
    )


def delete_teacher(token: str, teacher_id: int) -> None:
    api_request(
        "DELETE",
        f"/admin/teachers/{teacher_id}",
        token=token,
    )