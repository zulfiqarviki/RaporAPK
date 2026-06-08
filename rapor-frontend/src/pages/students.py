import pandas as pd
import streamlit as st

from src.api import students as students_api
from src.api.client import ApiError


def _load_students(
    token: str,
    grade_table_id: int,
) -> list[dict]:
    return students_api.list_students(
        token=token,
        grade_table_id=grade_table_id,
    )


def _render_student_table(students: list[dict]) -> None:
    if not students:
        st.info("Belum ada student di grade table ini.")
        return

    df = pd.DataFrame(students)

    ordered_columns = [
        "id",
        "student_number",
        "name",
        "grade_table_id",
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


def _render_create_student_form(
    token: str,
    grade_table_id: int,
) -> None:
    st.subheader("Tambah Student")

    with st.form(
        f"create_student_form_{grade_table_id}",
        clear_on_submit=True,
    ):
        student_number = st.text_input(
            "Nomor Student",
            placeholder="Optional, contoh: 001",
        )
        name = st.text_input(
            "Nama Student",
            placeholder="Contoh: Andi",
        )

        submitted = st.form_submit_button("Tambah Student")

    if submitted:
        if not name.strip():
            st.error("Nama student wajib diisi.")
            return

        try:
            students_api.create_student(
                token=token,
                grade_table_id=grade_table_id,
                name=name.strip(),
                student_number=student_number.strip() if student_number.strip() else None,
            )
            st.success("Student berhasil dibuat.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def _render_update_student_form(
    token: str,
    students: list[dict],
) -> None:
    st.subheader("Edit Student")

    if not students:
        st.info("Belum ada student yang bisa diedit.")
        return

    student_options = {
        f"{student['id']} - {student.get('student_number') or '-'} - {student['name']}": student
        for student in students
    }

    selected_label = st.selectbox(
        "Pilih student",
        options=list(student_options.keys()),
        key="update_student_selectbox",
    )

    selected_student = student_options[selected_label]

    with st.form(f"update_student_form_{selected_student['id']}"):
        student_number = st.text_input(
            "Nomor Student",
            value=selected_student.get("student_number") or "",
            help="Kosongkan lalu centang opsi di bawah jika ingin menghapus nomor student.",
        )
        name = st.text_input(
            "Nama Student",
            value=selected_student["name"],
        )
        clear_number = st.checkbox(
            "Kosongkan nomor student",
            value=False,
        )

        submitted = st.form_submit_button("Simpan Perubahan")

    if submitted:
        if not name.strip():
            st.error("Nama student wajib diisi.")
            return

        try:
            if clear_number:
                students_api.update_student(
                    token=token,
                    student_id=selected_student["id"],
                    name=name.strip(),
                )
                students_api.clear_student_number(
                    token=token,
                    student_id=selected_student["id"],
                )
            else:
                students_api.update_student(
                    token=token,
                    student_id=selected_student["id"],
                    name=name.strip(),
                    student_number=student_number.strip() if student_number.strip() else selected_student.get("student_number"),
                )

            st.success("Student berhasil diperbarui.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def _render_delete_student_form(
    token: str,
    students: list[dict],
) -> None:
    st.subheader("Hapus Student")

    if not students:
        st.info("Belum ada student yang bisa dihapus.")
        return

    student_options = {
        f"{student['id']} - {student.get('student_number') or '-'} - {student['name']}": student
        for student in students
    }

    selected_label = st.selectbox(
        "Pilih student yang akan dihapus",
        options=list(student_options.keys()),
        key="delete_student_selectbox",
    )

    selected_student = student_options[selected_label]

    st.warning(
        "Delete bersifat permanen. "
        "Menghapus student juga akan menghapus scores milik student tersebut."
    )

    confirm = st.checkbox(
        f"Saya yakin ingin menghapus student '{selected_student['name']}'",
        key="delete_student_confirm",
    )

    if st.button("Hapus Student", type="primary", disabled=not confirm):
        try:
            students_api.delete_student(
                token=token,
                student_id=selected_student["id"],
            )
            st.success("Student berhasil dihapus.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def render_students_page(
    token: str,
    grade_table: dict,
) -> None:
    grade_table_id = grade_table["id"]

    st.subheader("Students")
    st.caption(
        "Student pada aplikasi ini tersimpan hanya di dalam satu grade table."
    )

    try:
        students = _load_students(
            token=token,
            grade_table_id=grade_table_id,
        )
    except ApiError as error:
        st.error(error.detail)
        return

    st.markdown("#### Daftar Student")
    _render_student_table(students)

    st.divider()

    tab_create, tab_update, tab_delete = st.tabs(
        [
            "Tambah",
            "Edit",
            "Hapus",
        ]
    )

    with tab_create:
        _render_create_student_form(
            token=token,
            grade_table_id=grade_table_id,
        )

    with tab_update:
        _render_update_student_form(
            token=token,
            students=students,
        )

    with tab_delete:
        _render_delete_student_form(
            token=token,
            students=students,
        )