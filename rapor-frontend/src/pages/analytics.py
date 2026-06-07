import pandas as pd
import streamlit as st

from src.api import analytics as analytics_api
from src.api import grade_components as components_api
from src.api import students as students_api
from src.api.client import ApiError


DEFAULT_RANGES = [
    {"label": "0-60", "min": 0, "max": 60},
    {"label": "60-70", "min": 60, "max": 70},
    {"label": "70-80", "min": 70, "max": 80},
    {"label": "80-90", "min": 80, "max": 90},
    {"label": "90-100", "min": 90, "max": 100},
]


def _build_student_label(student: dict) -> str:
    student_number = student.get("student_number") or "-"
    return f"{student['id']} - {student_number} - {student['name']}"


def _build_component_label(component: dict) -> str:
    return f"{component['id']} - {component['name']}"


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


def _render_summary_tab(
    token: str,
    grade_table_id: int,
) -> None:
    st.subheader("Analytics Summary")

    try:
        summary = analytics_api.get_summary(
            token=token,
            grade_table_id=grade_table_id,
        )
    except ApiError as error:
        st.error(error.detail)
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Students", summary["total_students"])

    with col2:
        st.metric("Components", summary["total_components"])

    with col3:
        st.metric("Average Final Grade", summary["final_grade_average"])

    with col4:
        st.metric("Subject", summary["subject_name"])

    st.markdown("#### Highest / Lowest Final Grade")

    highest = summary.get("highest_final_grade")
    lowest = summary.get("lowest_final_grade")

    col_highest, col_lowest = st.columns(2)

    with col_highest:
        if highest:
            st.success(
                f"Highest: {highest['student_name']} — {highest['final_grade']}"
            )
        else:
            st.info("Belum ada highest final grade.")

    with col_lowest:
        if lowest:
            st.warning(
                f"Lowest: {lowest['student_name']} — {lowest['final_grade']}"
            )
        else:
            st.info("Belum ada lowest final grade.")

    st.markdown("#### Component Summary")

    component_summaries = summary.get("component_summaries", [])

    if not component_summaries:
        st.info("Belum ada component summary.")
        return

    rows: list[dict] = []

    for item in component_summaries:
        highest_score = item.get("highest_score")
        lowest_score = item.get("lowest_score")

        rows.append(
            {
                "component_id": item["component_id"],
                "component_name": item["component_name"],
                "weight": item["weight"],
                "order_index": item["order_index"],
                "average_score": item["average_score"],
                "highest_score": highest_score["score"] if highest_score else None,
                "highest_student": highest_score["student_name"] if highest_score else None,
                "lowest_score": lowest_score["score"] if lowest_score else None,
                "lowest_student": lowest_score["student_name"] if lowest_score else None,
                "total_students": item["total_students"],
                "filled_scores": item["filled_scores"],
                "missing_scores": item["missing_scores"],
            }
        )

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Average Score per Component")
    chart_df = df[["component_name", "average_score"]].set_index("component_name")
    st.bar_chart(chart_df)


def _render_distribution_tab(
    token: str,
    grade_table_id: int,
    components: list[dict],
) -> None:
    st.subheader("Distribution")

    target_label = st.radio(
        "Target distribusi",
        options=[
            "Final Grade",
            "Component",
        ],
        horizontal=True,
    )

    target = "final_grade" if target_label == "Final Grade" else "component"

    selected_component_id: int | None = None

    if target == "component":
        if not components:
            st.info("Belum ada component untuk distribution.")
            return

        component_options = {
            _build_component_label(component): component["id"]
            for component in components
        }

        selected_component_label = st.selectbox(
            "Pilih component",
            options=list(component_options.keys()),
            key="distribution_component_selectbox",
        )
        selected_component_id = component_options[selected_component_label]

    st.caption(
        "Untuk tahap ini, frontend memakai range default: "
        "0-60, 60-70, 70-80, 80-90, 90-100."
    )

    if st.button("Generate Distribution"):
        try:
            distribution = analytics_api.get_distribution(
                token=token,
                grade_table_id=grade_table_id,
                target=target,
                component_id=selected_component_id,
                ranges=DEFAULT_RANGES,
            )
        except ApiError as error:
            st.error(error.detail)
            return

        st.markdown("#### Distribution Result")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Target", distribution["target"])

        with col2:
            st.metric("Total Counted", distribution["total_counted"])

        with col3:
            st.metric("Missing Count", distribution["missing_count"])

        if distribution.get("component_name"):
            st.caption(f"Component: {distribution['component_name']}")

        df = pd.DataFrame(distribution["distribution"])

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        chart_df = df[["label", "count"]].set_index("label")
        st.bar_chart(chart_df)


def _render_student_progress_tab(
    token: str,
    grade_table_id: int,
    students: list[dict],
) -> None:
    st.subheader("Student Progress")

    if not students:
        st.info("Belum ada student untuk progress.")
        return

    student_options = {
        _build_student_label(student): student["id"]
        for student in students
    }

    selected_student_label = st.selectbox(
        "Pilih student",
        options=list(student_options.keys()),
        key="progress_student_selectbox",
    )

    selected_student_id = student_options[selected_student_label]

    if st.button("Load Student Progress"):
        try:
            progress = analytics_api.get_student_progress(
                token=token,
                grade_table_id=grade_table_id,
                student_id=selected_student_id,
            )
        except ApiError as error:
            st.error(error.detail)
            return

        st.markdown(f"#### Progress: {progress['student_name']}")

        col1, col2 = st.columns(2)

        with col1:
            status = "Complete" if progress["is_complete"] else "Incomplete"
            st.metric("Status", status)

        with col2:
            missing_components = progress.get("missing_components", [])
            st.metric("Missing Components", len(missing_components))

        if missing_components:
            st.warning("Missing: " + ", ".join(missing_components))

        df = pd.DataFrame(progress["progress"])

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        chart_df = df[["component_name", "score"]].set_index("component_name")
        st.bar_chart(chart_df)


def _render_student_comparison_tab(
    token: str,
    grade_table_id: int,
    students: list[dict],
    components: list[dict],
) -> None:
    st.subheader("Student Comparison")

    if len(students) < 2:
        st.info("Minimal perlu 2 students untuk comparison.")
        return

    student_options = {
        _build_student_label(student): student["id"]
        for student in students
    }

    selected_student_labels = st.multiselect(
        "Pilih 2 sampai 5 students",
        options=list(student_options.keys()),
        max_selections=5,
    )

    comparison_target = st.radio(
        "Target comparison",
        options=[
            "Final Grade",
            "Component",
        ],
        horizontal=True,
    )

    selected_component_id: int | None = None

    if comparison_target == "Component":
        if not components:
            st.info("Belum ada component untuk comparison.")
            return

        component_options = {
            _build_component_label(component): component["id"]
            for component in components
        }

        selected_component_label = st.selectbox(
            "Pilih component",
            options=list(component_options.keys()),
            key="comparison_component_selectbox",
        )
        selected_component_id = component_options[selected_component_label]

    if st.button("Compare Students"):
        selected_student_ids = [
            student_options[label]
            for label in selected_student_labels
        ]

        if len(selected_student_ids) < 2:
            st.error("Pilih minimal 2 students.")
            return

        try:
            comparison = analytics_api.compare_students(
                token=token,
                grade_table_id=grade_table_id,
                student_ids=selected_student_ids,
                component_id=selected_component_id,
            )
        except ApiError as error:
            st.error(error.detail)
            return

        st.markdown("#### Comparison Result")

        if comparison.get("component_name"):
            st.caption(f"Component: {comparison['component_name']}")
        else:
            st.caption("Comparison type: Final Grade")

        df = pd.DataFrame(comparison["students"])

        if "missing_components" in df.columns:
            df["missing_components"] = df["missing_components"].apply(
                lambda value: ", ".join(value) if isinstance(value, list) else value
            )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        chart_df = df[["student_name", "value"]].set_index("student_name")
        st.bar_chart(chart_df)


def render_analytics_page(
    token: str,
    grade_table: dict,
) -> None:
    grade_table_id = grade_table["id"]

    st.subheader("Analytics")
    st.caption(
        "Analytics dihitung oleh backend. Missing score dihitung sebagai 0, "
        "tetapi status kelengkapan tetap ditampilkan."
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
    except ApiError as error:
        st.error(error.detail)
        return

    tab_summary, tab_distribution, tab_progress, tab_comparison = st.tabs(
        [
            "Summary",
            "Distribution",
            "Student Progress",
            "Student Comparison",
        ]
    )

    with tab_summary:
        _render_summary_tab(
            token=token,
            grade_table_id=grade_table_id,
        )

    with tab_distribution:
        _render_distribution_tab(
            token=token,
            grade_table_id=grade_table_id,
            components=components,
        )

    with tab_progress:
        _render_student_progress_tab(
            token=token,
            grade_table_id=grade_table_id,
            students=students,
        )

    with tab_comparison:
        _render_student_comparison_tab(
            token=token,
            grade_table_id=grade_table_id,
            students=students,
            components=components,
        )