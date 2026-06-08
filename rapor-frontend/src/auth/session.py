import streamlit as st

from src.api import auth as auth_api


def init_auth_state() -> None:
    st.session_state.setdefault("access_token", None)
    st.session_state.setdefault("token_type", None)
    st.session_state.setdefault("current_user", None)


def is_authenticated() -> bool:
    return (
        st.session_state.get("access_token") is not None
        and st.session_state.get("current_user") is not None
    )


def get_access_token() -> str | None:
    return st.session_state.get("access_token")


def get_current_user() -> dict | None:
    return st.session_state.get("current_user")


def login_user(nip: str, password: str) -> None:
    token_data = auth_api.login(nip=nip, password=password)

    access_token = token_data["access_token"]
    user_data = auth_api.get_current_user(token=access_token)

    st.session_state["access_token"] = access_token
    st.session_state["token_type"] = token_data.get("token_type", "bearer")
    st.session_state["current_user"] = user_data


def logout_user() -> None:
    st.session_state["access_token"] = None
    st.session_state["token_type"] = None
    st.session_state["current_user"] = None
    st.rerun()


def require_auth() -> dict:
    user = get_current_user()

    if not is_authenticated() or user is None:
        st.warning("Silakan login terlebih dahulu.")
        st.stop()

    return user


def require_role(*allowed_roles: str) -> dict:
    user = require_auth()

    if user["role"] not in allowed_roles:
        st.error("Anda tidak memiliki akses ke halaman ini.")
        st.stop()

    return user