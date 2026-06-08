import pandas as pd
import streamlit as st

from src.api import results as results_api
from src.api.client import ApiError


def _build_results_dataframe(results_data: dict) -> pd.DataFrame:
    rows: list[dict] = []

    for student_result in results_data["results"]:
        row = {
            "student_id": student_result["student_id"],
            "student_number": student_result.get("student_number"),
            "student_name": student_result["student_name"],
            "final_grade": student_result["final_grade"],
            "is_complete": student_result["is_complete"],
            "missing_components": ", ".join(student_result.get("missing_components", [])),
        }

        for component_score in student_result["component_scores"]:
            component_name = component_score["component_name"]
            score = component_score.get("score")

            row[component_name] = "Missing" if score is None else score

        rows.append(row)

    return pd.DataFrame(rows)


def _render_results_summary(results_data: dict) -> None:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Subject", results_data["subject_name"])

    with col2:
        st.metric("Teacher", results_data["teacher_name"])

    with col3:
        st.metric("Total Weight", results_data["total_weight"])


def render_results_page(
    token: str,
    grade_table: dict,
) -> None:
    grade_table_id = grade_table["id"]

    st.subheader("Results")
    st.caption(
        "Final grade dihitung oleh backend. "
        "Missing score dihitung sebagai 0, tetapi tetap ditandai di is_complete dan missing_components."
    )

    try:
        results_data = results_api.get_results(
            token=token,
            grade_table_id=grade_table_id,
        )
    except ApiError as error:
        st.error(error.detail)
        return

    _render_results_summary(results_data)

    st.divider()

    if not results_data["results"]:
        st.info("Belum ada result yang bisa ditampilkan.")
        return

    df = _build_results_dataframe(results_data)

    st.markdown("#### Final Results")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    incomplete_df = df[df["is_complete"] == False]  # noqa: E712

    if not incomplete_df.empty:
        st.warning(
            f"Ada {len(incomplete_df)} student dengan missing score. "
            "Cek kolom missing_components untuk detailnya."
        )