import pandas as pd
import streamlit as st

from src.api import grade_components as components_api
from src.api import scores as scores_api
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


def _load_components(
    token: str,
    grade_table_id: int,
) -> list[dict]:
    components = components_api.list_components(
        token=token,
        grade_table_id=grade_table_id,
    )

    return sorted(
        components,
        key=lambda component: component.get("order_index", 0),
    )


def _load_scores(
    token: str,
    grade_table_id: int,
) -> list[dict]:
    return scores_api.list_scores(
        token=token,
        grade_table_id=grade_table_id,
    )


def _build_student_label(student: dict) -> str:
    student_number = student.get("student_number") or "-"
    return f"{student['id']} - {student_number} - {student['name']}"


def _build_component_label(component: dict) -> str:
    return f"{component['id']} - {component['name']}"


def _render_score_table(
    scores: list[dict],
    students: list[dict],
    components: list[dict],
) -> None:
    if not scores:
        st.info("Belum ada score yang diinput.")
        return

    student_map = {
        student["id"]: _build_student_label(student)
        for student in students
    }
    component_map = {
        component["id"]: component["name"]
        for component in components
    }

    df = pd.DataFrame(scores)

    if "student_id" in df.columns:
        df["student"] = df["student_id"].map(student_map).fillna(df["student_id"])

    if "component_id" in df.columns:
        df["component"] = df["component_id"].map(component_map).fillna(df["component_id"])

    ordered_columns = [
        "id",
        "student_id",
        "student",
        "component_id",
        "component",
        "score",
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


def _render_score_matrix(
    scores: list[dict],
    students: list[dict],
    components: list[dict],
) -> None:
    st.markdown("#### Matrix Score")

    if not students:
        st.info("Belum ada student.")
        return

    if not components:
        st.info("Belum ada component.")
        return

    score_lookup = {
        (score["student_id"], score["component_id"]): score["score"]
        for score in scores
    }

    rows: list[dict] = []

    for student in students:
        row = {
            "student_id": student["id"],
            "student_number": student.get("student_number"),
            "student_name": student["name"],
        }

        for component in components:
            row[component["name"]] = score_lookup.get(
                (student["id"], component["id"]),
                None,
            )

        rows.append(row)

    df = pd.DataFrame(rows)

    st.caption(
        "Sel kosong berarti missing score. Missing score tidak dibuat sebagai record score."
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


def _render_create_score_form(
    token: str,
    grade_table_id: int,
    students: list[dict],
    components: list[dict],
) -> None:
    st.subheader("Tambah Score")

    if not students:
        st.info("Tambahkan student terlebih dahulu sebelum menginput score.")
        return

    if not components:
        st.info("Tambahkan component terlebih dahulu sebelum menginput score.")
        return

    student_options = {
        _build_student_label(student): student["id"]
        for student in students
    }
    component_options = {
        _build_component_label(component): component["id"]
        for component in components
    }

    with st.form(
        f"create_score_form_{grade_table_id}",
        clear_on_submit=True,
    ):
        selected_student_label = st.selectbox(
            "Student",
            options=list(student_options.keys()),
            key=f"create_score_student_{grade_table_id}",
        )
        selected_component_label = st.selectbox(
            "Component",
            options=list(component_options.keys()),
            key=f"create_score_component_{grade_table_id}",
        )
        score = st.number_input(
            "Score",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
        )

        submitted = st.form_submit_button("Tambah Score")

    if submitted:
        try:
            scores_api.create_score(
                token=token,
                grade_table_id=grade_table_id,
                student_id=student_options[selected_student_label],
                component_id=component_options[selected_component_label],
                score=float(score),
            )
            st.success("Score berhasil dibuat.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def _render_update_score_form(
    token: str,
    scores: list[dict],
    students: list[dict],
    components: list[dict],
) -> None:
    st.subheader("Edit Score")

    if not scores:
        st.info("Belum ada score yang bisa diedit.")
        return

    student_map = {
        student["id"]: _build_student_label(student)
        for student in students
    }
    component_map = {
        component["id"]: component["name"]
        for component in components
    }

    score_options = {
        (
            f"{score['id']} - "
            f"{student_map.get(score['student_id'], score['student_id'])} - "
            f"{component_map.get(score['component_id'], score['component_id'])}"
        ): score
        for score in scores
    }

    selected_label = st.selectbox(
        "Pilih score",
        options=list(score_options.keys()),
        key="update_score_selectbox",
    )

    selected_score = score_options[selected_label]

    with st.form(f"update_score_form_{selected_score['id']}"):
        score_value = st.number_input(
            "Score",
            min_value=0.0,
            max_value=100.0,
            value=float(selected_score["score"]),
            step=1.0,
        )

        submitted = st.form_submit_button("Simpan Perubahan")

    if submitted:
        try:
            scores_api.update_score(
                token=token,
                score_id=selected_score["id"],
                score=float(score_value),
            )
            st.success("Score berhasil diperbarui.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def _render_delete_score_form(
    token: str,
    scores: list[dict],
    students: list[dict],
    components: list[dict],
) -> None:
    st.subheader("Hapus Score")

    if not scores:
        st.info("Belum ada score yang bisa dihapus.")
        return

    student_map = {
        student["id"]: _build_student_label(student)
        for student in students
    }
    component_map = {
        component["id"]: component["name"]
        for component in components
    }

    score_options = {
        (
            f"{score['id']} - "
            f"{student_map.get(score['student_id'], score['student_id'])} - "
            f"{component_map.get(score['component_id'], score['component_id'])}"
        ): score
        for score in scores
    }

    selected_label = st.selectbox(
        "Pilih score yang akan dihapus",
        options=list(score_options.keys()),
        key="delete_score_selectbox",
    )

    selected_score = score_options[selected_label]

    st.warning(
        "Menghapus score akan membuat nilai student-component tersebut menjadi missing score. "
        "Pada results dan analytics, missing score akan dihitung sebagai 0 oleh backend."
    )

    confirm = st.checkbox(
        f"Saya yakin ingin menghapus score ID {selected_score['id']}",
        key="delete_score_confirm",
    )

    if st.button("Hapus Score", type="primary", disabled=not confirm):
        try:
            scores_api.delete_score(
                token=token,
                score_id=selected_score["id"],
            )
            st.success("Score berhasil dihapus.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def render_scores_page(
    token: str,
    grade_table: dict,
) -> None:
    grade_table_id = grade_table["id"]

    st.subheader("Scores")
    st.caption(
        "Score diinput per kombinasi student dan component. "
        "Jika belum ada score, maka dianggap missing score."
    )

    try:
        students = _load_students(
            token=token,
            grade_table_id=grade_table_id,
        )
        components = _load_components(
            token=token,
            grade_table_id=grade_table_id,
        )
        scores = _load_scores(
            token=token,
            grade_table_id=grade_table_id,
        )
    except ApiError as error:
        st.error(error.detail)
        return

    _render_score_matrix(
        scores=scores,
        students=students,
        components=components,
    )

    st.markdown("#### Daftar Score Record")
    _render_score_table(
        scores=scores,
        students=students,
        components=components,
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
        _render_create_score_form(
            token=token,
            grade_table_id=grade_table_id,
            students=students,
            components=components,
        )

    with tab_update:
        _render_update_score_form(
            token=token,
            scores=scores,
            students=students,
            components=components,
        )

    with tab_delete:
        _render_delete_score_form(
            token=token,
            scores=scores,
            students=students,
            components=components,
        )