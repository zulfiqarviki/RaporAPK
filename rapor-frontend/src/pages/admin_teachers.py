import pandas as pd
import streamlit as st

from src.api import admin as admin_api
from src.api.client import ApiError
from src.auth.session import get_access_token, require_role


def _load_teachers(token: str) -> list[dict]:
    return admin_api.list_teachers(token)


def _render_teacher_table(teachers: list[dict]) -> None:
    if not teachers:
        st.info("Belum ada akun teacher.")
        return

    df = pd.DataFrame(teachers)

    ordered_columns = ["id", "nip", "name", "role", "is_active"]
    available_columns = [column for column in ordered_columns if column in df.columns]

    st.dataframe(
        df[available_columns],
        use_container_width=True,
        hide_index=True,
    )


def _render_create_teacher_form(token: str) -> None:
    st.subheader("Tambah Teacher")

    with st.form("create_teacher_form", clear_on_submit=True):
        nip = st.text_input("NIP")
        name = st.text_input("Nama")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Tambah Teacher")

    if submitted:
        if not nip.strip() or not name.strip() or not password:
            st.error("NIP, nama, dan password wajib diisi.")
            return

        try:
            admin_api.create_teacher(
                token,
                nip=nip.strip(),
                name=name.strip(),
                password=password,
            )
            st.success("Teacher berhasil dibuat.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def _render_update_teacher_form(token: str, teachers: list[dict]) -> None:
    st.subheader("Edit Teacher")

    if not teachers:
        st.info("Belum ada teacher yang bisa diedit.")
        return

    teacher_options = {
        f"{teacher['nip']} - {teacher['name']}": teacher
        for teacher in teachers
    }

    selected_label = st.selectbox(
        "Pilih teacher",
        options=list(teacher_options.keys()),
        key="update_teacher_selectbox",
    )

    selected_teacher = teacher_options[selected_label]

    with st.form("update_teacher_form"):
        nip = st.text_input("NIP", value=selected_teacher["nip"])
        name = st.text_input("Nama", value=selected_teacher["name"])
        password = st.text_input(
            "Password baru",
            type="password",
            help="Kosongkan jika tidak ingin mengubah password.",
        )
        is_active = st.checkbox(
            "Aktif",
            value=selected_teacher["is_active"],
        )

        submitted = st.form_submit_button("Simpan Perubahan")

    if submitted:
        if not nip.strip() or not name.strip():
            st.error("NIP dan nama wajib diisi.")
            return

        try:
            admin_api.update_teacher(
                token,
                selected_teacher["id"],
                nip=nip.strip(),
                name=name.strip(),
                password=password if password else None,
                is_active=is_active,
            )
            st.success("Teacher berhasil diperbarui.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def _render_delete_teacher_form(token: str, teachers: list[dict]) -> None:
    st.subheader("Hapus Teacher")

    if not teachers:
        st.info("Belum ada teacher yang bisa dihapus.")
        return

    teacher_options = {
        f"{teacher['nip']} - {teacher['name']}": teacher
        for teacher in teachers
    }

    selected_label = st.selectbox(
        "Pilih teacher yang akan dihapus",
        options=list(teacher_options.keys()),
        key="delete_teacher_selectbox",
    )

    selected_teacher = teacher_options[selected_label]

    st.warning(
        "Delete bersifat permanen. "
        "Menghapus teacher juga akan menghapus grade table milik teacher tersebut."
    )

    confirm = st.checkbox(
        f"Saya yakin ingin menghapus teacher {selected_teacher['nip']} - {selected_teacher['name']}",
        key="delete_teacher_confirm",
    )

    if st.button("Hapus Teacher", type="primary", disabled=not confirm):
        try:
            admin_api.delete_teacher(token, selected_teacher["id"])
            st.success("Teacher berhasil dihapus.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def render_admin_teachers_page() -> None:
    require_role("admin")

    token = get_access_token()

    if token is None:
        st.error("Token tidak ditemukan. Silakan login ulang.")
        st.stop()

    st.title("Teacher Accounts")
    st.caption("Kelola akun teacher. Halaman ini hanya untuk admin.")

    try:
        teachers = _load_teachers(token)
    except ApiError as error:
        st.error(error.detail)
        return

    st.subheader("Daftar Teacher")
    _render_teacher_table(teachers)

    st.divider()

    tab_create, tab_update, tab_delete = st.tabs(
        [
            "Tambah",
            "Edit",
            "Hapus",
        ]
    )

    with tab_create:
        _render_create_teacher_form(token)

    with tab_update:
        _render_update_teacher_form(token, teachers)

    with tab_delete:
        _render_delete_teacher_form(token, teachers)