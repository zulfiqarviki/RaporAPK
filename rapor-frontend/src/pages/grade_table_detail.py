import streamlit as st

from src.api import grade_tables as grade_table_api
from src.api.client import ApiError
from src.pages.students import render_students_page
from src.pages.grade_components import render_grade_components_page
from src.pages.scores import render_scores_page
from src.pages.analytics import render_analytics_page
from src.pages.results import render_results_page


def _render_grade_table_header(grade_table: dict) -> None:
    st.subheader(grade_table["subject_name"])

    description = grade_table.get("description")

    if description:
        st.caption(description)
    else:
        st.caption("Tidak ada deskripsi.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Grade Table ID", grade_table["id"])

    with col2:
        st.metric("Teacher ID", grade_table["teacher_id"])

    with col3:
        st.metric("Subject", grade_table["subject_name"])


def _render_students_tab(
    token: str,
    grade_table: dict,
) -> None:
    render_students_page(
        token=token,
        grade_table=grade_table,
    )


def _render_components_tab(
    token: str,
    grade_table: dict,
) -> None:
    render_grade_components_page(
        token=token,
        grade_table=grade_table,
    )


def _render_scores_tab(
    token: str,
    grade_table: dict,
) -> None:
    render_scores_page(
        token=token,
        grade_table=grade_table,
    )


def _render_results_tab(
    token: str,
    grade_table: dict,
) -> None:
    render_results_page(
        token=token,
        grade_table=grade_table,
    )


def _render_analytics_tab(
    token: str,
    grade_table: dict,
) -> None:
    render_analytics_page(
        token=token,
        grade_table=grade_table,
    )


def _render_excel_tab(grade_table: dict) -> None:
    st.info(
        "Tab Excel akan menangani export dan import Excel. "
        "Validasi strict format Excel tetap dilakukan oleh backend."
    )


def render_grade_table_detail_shell(
    token: str,
    grade_table_id: int,
) -> None:
    try:
        grade_table = grade_table_api.get_grade_table(
            token,
            grade_table_id,
        )
    except ApiError as error:
        st.error(error.detail)
        return

    _render_grade_table_header(grade_table)

    st.divider()

    tab_students, tab_components, tab_scores, tab_results, tab_analytics, tab_excel = st.tabs(
        [
            "Students",
            "Components",
            "Scores",
            "Results",
            "Analytics",
            "Excel",
        ]
    )

    with tab_students:
        _render_students_tab(
            token=token,
            grade_table=grade_table,
    )

    with tab_components:
        _render_components_tab(
            token=token,
            grade_table=grade_table,
    )

    with tab_scores:
        _render_scores_tab(
            token=token,
            grade_table=grade_table,
    )

    with tab_results:
        _render_results_tab(
            token=token,
            grade_table=grade_table,
    )

    with tab_analytics:
        _render_analytics_tab(
            token=token,
            grade_table=grade_table,
    )

    with tab_excel:
        _render_excel_tab(grade_table)