import re

import streamlit as st

from src.api import admin as admin_api
from src.api import excel as excel_api
from src.api.client import ApiError
from src.auth.session import get_current_user


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip())
    cleaned = cleaned.strip("_")

    return cleaned or "grade_table"


def _render_export_section(
    token: str,
    grade_table: dict,
) -> None:
    grade_table_id = grade_table["id"]
    subject_name = grade_table["subject_name"]

    st.subheader("Export Excel")

    export_state_key = f"excel_export_bytes_{grade_table_id}"
    filename_state_key = f"excel_export_filename_{grade_table_id}"

    if st.button(
        "Generate Excel Export",
        key=f"generate_excel_export_{grade_table_id}",
    ):
        try:
            file_bytes = excel_api.export_grade_table(
                token=token,
                grade_table_id=grade_table_id,
            )

            filename = (
                f"grade_table_{grade_table_id}_"
                f"{_safe_filename(subject_name)}.xlsx"
            )

            st.session_state[export_state_key] = file_bytes
            st.session_state[filename_state_key] = filename

            st.success("Excel export berhasil dibuat.")
        except ApiError as error:
            st.error(error.detail)

    if export_state_key in st.session_state:
        st.download_button(
            "Download Excel",
            data=st.session_state[export_state_key],
            file_name=st.session_state[filename_state_key],
            mime=excel_api.EXCEL_MIME_TYPE,
            key=f"download_excel_export_{grade_table_id}",
        )


def _load_teacher_options(token: str) -> dict[str, int]:
    teachers = admin_api.list_teachers(token)

    return {
        f"{teacher['nip']} - {teacher['name']}": teacher["id"]
        for teacher in teachers
    }


def _render_import_section(
    token: str,
    grade_table: dict,
) -> None:
    user = get_current_user()

    st.subheader("Import Excel")
    st.warning(
        "Import Excel selalu membuat grade table baru. "
        "Import tidak mengubah grade table yang sedang dibuka."
    )

    selected_teacher_id: int | None = None

    if user is not None and user["role"] == "admin":
        try:
            teacher_options = _load_teacher_options(token)
        except ApiError as error:
            st.error(error.detail)
            return

        if not teacher_options:
            st.info("Belum ada teacher. Buat teacher terlebih dahulu sebelum import.")
            return

        labels = list(teacher_options.keys())

        default_index = 0
        current_teacher_id = grade_table.get("teacher_id")

        for index, label in enumerate(labels):
            if teacher_options[label] == current_teacher_id:
                default_index = index
                break

        selected_teacher_label = st.selectbox(
            "Teacher pemilik grade table hasil import",
            options=labels,
            index=default_index,
            key=f"excel_import_teacher_{grade_table['id']}",
        )

        selected_teacher_id = teacher_options[selected_teacher_label]

        st.caption(
            "Admin wajib memilih teacher. Nilai teacher_id akan dikirim sebagai query parameter."
        )

    else:
        st.caption(
            "Sebagai teacher, hasil import akan menjadi grade table baru milik akun Anda."
        )

    uploaded_file = st.file_uploader(
        "Upload file Excel",
        type=["xlsx"],
        key=f"excel_import_file_{grade_table['id']}",
    )

    confirm = st.checkbox(
        "Saya paham bahwa import akan membuat grade table baru.",
        key=f"excel_import_confirm_{grade_table['id']}",
    )

    if st.button(
        "Import Excel",
        type="primary",
        disabled=uploaded_file is None or not confirm,
        key=f"excel_import_button_{grade_table['id']}",
    ):
        if uploaded_file is None:
            st.error("File Excel wajib diupload.")
            return

        try:
            result = excel_api.import_grade_table(
                token=token,
                file_name=uploaded_file.name,
                file_bytes=uploaded_file.getvalue(),
                teacher_id=selected_teacher_id,
            )

            st.success("Excel berhasil diimport. Grade table baru telah dibuat.")

            st.json(result)

            st.info(
                "Buka kembali menu Grade Tables / My Grade Tables untuk melihat grade table hasil import."
            )
        except ApiError as error:
            st.error(error.detail)


def render_excel_page(
    token: str,
    grade_table: dict,
) -> None:

    _render_export_section(
        token=token,
        grade_table=grade_table,
    )

    st.divider()

    _render_import_section(
        token=token,
        grade_table=grade_table,
    )