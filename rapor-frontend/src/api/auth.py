from src.api.client import api_request


def login(nip: str, password: str) -> dict:
    return api_request(
        "POST",
        "/auth/login",
        data={
            "username": nip,
            "password": password,
        },
    )


def get_current_user(token: str) -> dict:
    return api_request(
        "GET",
        "/auth/me",
        token=token,
    )