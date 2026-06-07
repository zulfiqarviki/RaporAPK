from typing import Any

import requests

from src.config import BACKEND_URL


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"{status_code}: {detail}")


def _extract_error_detail(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text or "Unknown API error"

    detail = body.get("detail", "Unknown API error")

    if isinstance(detail, list):
        messages: list[str] = []

        for item in detail:
            loc = " -> ".join(str(part) for part in item.get("loc", []))
            msg = item.get("msg", "")

            if loc:
                messages.append(f"{loc}: {msg}")
            else:
                messages.append(msg)

        return "\n".join(messages)

    return str(detail)


def api_request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
    timeout: int = 20,
) -> Any:
    headers: dict[str, str] = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method=method,
        url=f"{BACKEND_URL}{path}",
        headers=headers,
        params=params,
        json=json,
        data=data,
        files=files,
        timeout=timeout,
    )

    if response.status_code >= 400:
        raise ApiError(
            status_code=response.status_code,
            detail=_extract_error_detail(response),
        )

    if response.status_code == 204:
        return None

    content_type = response.headers.get("content-type", "")

    if "application/json" in content_type:
        return response.json()

    return response.content