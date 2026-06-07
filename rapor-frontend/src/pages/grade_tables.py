import pandas as pd
import streamlit as st

from src.api import admin as admin_api
from src.api import grade_tables as grade_table_api
from src.api.client import ApiError
from src.auth.session import get_access_token, require_auth


def _load_grade_tables(token: str) -> list[dict]:
    return grade_table_api.list_grade_tables(token)


def _load_teachers_for_admin(token: str, user: dict) -> list[dict]:
    if user["role"] != "admin":
        return []

    return admin_api.list_teachers(token)


def _build_teacher_label_map(teachers: list[dict]) -> dict[int, str]:
    return {
        teacher["id"]: f"{teacher['nip']} - {teacher['name']}"
        for teacher in teachers
    }


def _render_grade_table_table(
    grade_tables: list[dict],
    teachers: list[dict],
    user: dict,
) -> None:
    if not grade_tables:
        st.info("Belum ada grade table.")
        return

    df = pd.DataFrame(grade_tables)

    if user["role"] == "admin":
        teacher_label_map = _build_teacher_label_map(teachers)
        df["teacher"] = df["teacher_id"].map(teacher_label_map).fillna(df["teacher_id"])

        ordered_columns = [
            "id",
            "subject_name",
            "description",
            "teacher_id",
            "teacher",
        ]
    else:
        ordered_columns = [
            "id",
            "subject_name",
            "description",
            "teacher_id",
        ]

    available_columns = [
        column for column in ordered_columns
        if column in df.columns
    ]

    st.dataframe(
        df[available_columns],
        use_container_width=True,
        hide_index=True,
    )


def _render_create_grade_table_form(
    token: str,
    teachers: list[dict],
    user: dict,
) -> None:
    st.subheader("Tambah Grade Table")

    with st.form("create_grade_table_form", clear_on_submit=True):
        subject_name = st.text_input("Nama Mata Pelajaran")
        description = st.text_area("Deskripsi", placeholder="Contoh: Kelas 8A")

        selected_teacher_id: int | None = None

        if user["role"] == "admin":
            if not teachers:
                st.warning("Belum ada teacher. Buat akun teacher terlebih dahulu.")
            else:
                teacher_options = {
                    f"{teacher['nip']} - {teacher['name']}": teacher["id"]
                    for teacher in teachers
                }

                selected_teacher_label = st.selectbox(
                    "Teacher pemilik grade table",
                    options=list(teacher_options.keys()),
                )
                selected_teacher_id = teacher_options[selected_teacher_label]

        submitted = st.form_submit_button("Tambah Grade Table")

    if submitted:
        if not subject_name.strip():
            st.error("Nama mata pelajaran wajib diisi.")
            return

        if user["role"] == "admin" and selected_teacher_id is None:
            st.error("Admin wajib memilih teacher.")
            return

        try:
            grade_table_api.create_grade_table(
                token,
                subject_name=subject_name.strip(),
                description=description.strip() if description.strip() else None,
                teacher_id=selected_teacher_id,
            )
            st.success("Grade table berhasil dibuat.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def _render_update_grade_table_form(
    token: str,
    grade_tables: list[dict],
) -> None:
    st.subheader("Edit Grade Table")

    if not grade_tables:
        st.info("Belum ada grade table yang bisa diedit.")
        return

    grade_table_options = {
        f"{grade_table['id']} - {grade_table['subject_name']}": grade_table
        for grade_table in grade_tables
    }

    selected_label = st.selectbox(
        "Pilih grade table",
        options=list(grade_table_options.keys()),
        key="update_grade_table_selectbox",
    )

    selected_grade_table = grade_table_options[selected_label]

    with st.form("update_grade_table_form"):
        subject_name = st.text_input(
            "Nama Mata Pelajaran",
            value=selected_grade_table["subject_name"],
        )
        description = st.text_area(
            "Deskripsi",
            value=selected_grade_table.get("description") or "",
        )

        submitted = st.form_submit_button("Simpan Perubahan")

    if submitted:
        if not subject_name.strip():
            st.error("Nama mata pelajaran wajib diisi.")
            return

        try:
            grade_table_api.update_grade_table(
                token,
                selected_grade_table["id"],
                subject_name=subject_name.strip(),
                description=description.strip(),
            )
            st.success("Grade table berhasil diperbarui.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def _render_delete_grade_table_form(
    token: str,
    grade_tables: list[dict],
) -> None:
    st.subheader("Hapus Grade Table")

    if not grade_tables:
        st.info("Belum ada grade table yang bisa dihapus.")
        return

    grade_table_options = {
        f"{grade_table['id']} - {grade_table['subject_name']}": grade_table
        for grade_table in grade_tables
    }

    selected_label = st.selectbox(
        "Pilih grade table yang akan dihapus",
        options=list(grade_table_options.keys()),
        key="delete_grade_table_selectbox",
    )

    selected_grade_table = grade_table_options[selected_label]

    st.warning(
        "Delete bersifat permanen. "
        "Menghapus grade table juga akan menghapus students, components, dan scores terkait."
    )

    confirm = st.checkbox(
        f"Saya yakin ingin menghapus grade table '{selected_grade_table['subject_name']}'",
        key="delete_grade_table_confirm",
    )

    if st.button("Hapus Grade Table", type="primary", disabled=not confirm):
        try:
            grade_table_api.delete_grade_table(
                token,
                selected_grade_table["id"],
            )
            st.success("Grade table berhasil dihapus.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def render_grade_tables_page() -> None:
    user = require_auth()

    token = get_access_token()

    if token is None:
        st.error("Token tidak ditemukan. Silakan login ulang.")
        st.stop()

    if user["role"] == "admin":
        st.title("Grade Tables")
        st.caption("Admin dapat mengakses semua grade table.")
    else:
        st.title("My Grade Tables")
        st.caption("Teacher hanya dapat mengakses grade table miliknya sendiri.")

    try:
        grade_tables = _load_grade_tables(token)
        teachers = _load_teachers_for_admin(token, user)
    except ApiError as error:
        st.error(error.detail)
        return

    st.subheader("Daftar Grade Table")
    _render_grade_table_table(
        grade_tables=grade_tables,
        teachers=teachers,
        user=user,
    )

    st.divider()

    tab_create, tab_update, tab_delete = st.tabs(
        [
            "Tambah",
            "Edit",
            "Hapus",
        ]
    )

    with tab_create:
        _render_create_grade_table_form(
            token=token,
            teachers=teachers,
            user=user,
        )

    with tab_update:
        _render_update_grade_table_form(
            token=token,
            grade_tables=grade_tables,
        )

    with tab_delete:
        _render_delete_grade_table_form(
            token=token,
            grade_tables=grade_tables,
        )