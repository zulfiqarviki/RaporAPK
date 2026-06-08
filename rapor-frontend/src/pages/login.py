import streamlit as st

from src.api.client import ApiError
from src.auth.session import login_user


def render_login_page() -> None:
    st.title("Rapor App")
    st.subheader("Login")

    st.caption("Masuk menggunakan NIP dan password.")

    with st.form("login_form"):
        nip = st.text_input("NIP")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

    if submitted:
        if not nip.strip() or not password:
            st.error("NIP dan password wajib diisi.")
            return

        try:
            login_user(nip=nip.strip(), password=password)
            st.rerun()
        except ApiError as error:
            st.error(error.detail)