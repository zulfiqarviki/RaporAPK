from typing import Any

from src.api.client import api_request


def list_components(
    token: str,
    grade_table_id: int,
) -> list[dict[str, Any]]:
    return api_request(
        "GET",
        f"/grade-tables/{grade_table_id}/components",
        token=token,
    )


def get_component(
    token: str,
    component_id: int,
) -> dict[str, Any]:
    return api_request(
        "GET",
        f"/grade-components/{component_id}",
        token=token,
    )


def create_component(
    token: str,
    grade_table_id: int,
    *,
    name: str,
    weight: float,
    order_index: int,
) -> dict[str, Any]:
    return api_request(
        "POST",
        f"/grade-tables/{grade_table_id}/components",
        token=token,
        json={
            "name": name,
            "weight": weight,
            "order_index": order_index,
        },
    )


def update_component(
    token: str,
    component_id: int,
    *,
    name: str | None = None,
    weight: float | None = None,
    order_index: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    if name is not None:
        payload["name"] = name

    if weight is not None:
        payload["weight"] = weight

    if order_index is not None:
        payload["order_index"] = order_index

    return api_request(
        "PATCH",
        f"/grade-components/{component_id}",
        token=token,
        json=payload,
    )


def delete_component(
    token: str,
    component_id: int,
) -> None:
    api_request(
        "DELETE",
        f"/grade-components/{component_id}",
        token=token,
    )