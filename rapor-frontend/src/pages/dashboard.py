import streamlit as st


def render_dashboard_page(user: dict) -> None:
    st.title("Dashboard")

    st.write(f"Selamat datang, **{user['name']}**.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("NIP", user["nip"])

    with col2:
        st.metric("Role", user["role"])

    with col3:
        status = "Aktif" if user["is_active"] else "Tidak Aktif"
        st.metric("Status", status)

    st.divider()

    if user["role"] == "admin":
        st.info(
            "Anda login sebagai admin. "
            "Admin dapat mengelola akun teacher dan mengakses semua grade table."
        )
    else:
        st.info(
            "Anda login sebagai teacher. "
            "Teacher hanya dapat mengakses grade table miliknya sendiri."
        )