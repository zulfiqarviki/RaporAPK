import streamlit as st

from src.auth.session import logout_user


def render_sidebar(user: dict) -> str:
    st.sidebar.title("Rapor App")

    st.sidebar.write(f"**{user['name']}**")
    st.sidebar.caption(f"NIP: {user['nip']}")
    st.sidebar.caption(f"Role: {user['role']}")

    st.sidebar.divider()

    if user["role"] == "admin":
        page = st.sidebar.radio(
            "Menu",
            [
                "Dashboard",
                "Teacher Accounts",
                "Grade Tables",
            ],
        )
    else:
        page = st.sidebar.radio(
            "Menu",
            [
                "Dashboard",
                "My Grade Tables",
            ],
        )

    st.sidebar.divider()

    if st.sidebar.button("Logout"):
        logout_user()

    return page