import pandas as pd
import streamlit as st

from src.api import grade_components as components_api
from src.api.client import ApiError


def _load_components(
    token: str,
    grade_table_id: int,
) -> list[dict]:
    return components_api.list_components(
        token=token,
        grade_table_id=grade_table_id,
    )


def _render_component_table(components: list[dict]) -> None:
    if not components:
        st.info("Belum ada component di grade table ini.")
        return

    df = pd.DataFrame(components)

    if "order_index" in df.columns:
        df = df.sort_values("order_index")

    ordered_columns = [
        "id",
        "name",
        "weight",
        "max_score",
        "order_index",
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


def _render_create_component_form(
    token: str,
    grade_table_id: int,
) -> None:
    st.subheader("Tambah Component")

    with st.form(
        f"create_component_form_{grade_table_id}",
        clear_on_submit=True,
    ):
        name = st.text_input(
            "Nama Component",
            placeholder="Contoh: Tugas, UTS, UAS",
        )
        weight = st.number_input(
            "Weight",
            min_value=0.01,
            value=1.0,
            step=0.5,
            help="Bobot component. Harus lebih besar dari 0.",
        )
        order_index = st.number_input(
            "Order Index",
            min_value=0,
            value=0,
            step=1,
            help="Digunakan untuk mengurutkan component.",
        )

        st.caption("Max score selalu 100 dan ditentukan oleh backend.")

        submitted = st.form_submit_button("Tambah Component")

    if submitted:
        if not name.strip():
            st.error("Nama component wajib diisi.")
            return

        try:
            components_api.create_component(
                token=token,
                grade_table_id=grade_table_id,
                name=name.strip(),
                weight=float(weight),
                order_index=int(order_index),
            )
            st.success("Component berhasil dibuat.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def _render_update_component_form(
    token: str,
    components: list[dict],
) -> None:
    st.subheader("Edit Component")

    if not components:
        st.info("Belum ada component yang bisa diedit.")
        return

    component_options = {
        f"{component['id']} - {component['name']}": component
        for component in sorted(
            components,
            key=lambda item: item.get("order_index", 0),
        )
    }

    selected_label = st.selectbox(
        "Pilih component",
        options=list(component_options.keys()),
        key="update_component_selectbox",
    )

    selected_component = component_options[selected_label]

    with st.form(f"update_component_form_{selected_component['id']}"):
        name = st.text_input(
            "Nama Component",
            value=selected_component["name"],
        )
        weight = st.number_input(
            "Weight",
            min_value=0.01,
            value=float(selected_component["weight"]),
            step=0.5,
        )
        order_index = st.number_input(
            "Order Index",
            min_value=0,
            value=int(selected_component["order_index"]),
            step=1,
        )

        st.caption(
            f"Max score saat ini: {selected_component['max_score']}. "
            "Nilai ini tidak diedit dari frontend."
        )

        submitted = st.form_submit_button("Simpan Perubahan")

    if submitted:
        if not name.strip():
            st.error("Nama component wajib diisi.")
            return

        try:
            components_api.update_component(
                token=token,
                component_id=selected_component["id"],
                name=name.strip(),
                weight=float(weight),
                order_index=int(order_index),
            )
            st.success("Component berhasil diperbarui.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def _render_delete_component_form(
    token: str,
    components: list[dict],
) -> None:
    st.subheader("Hapus Component")

    if not components:
        st.info("Belum ada component yang bisa dihapus.")
        return

    component_options = {
        f"{component['id']} - {component['name']}": component
        for component in sorted(
            components,
            key=lambda item: item.get("order_index", 0),
        )
    }

    selected_label = st.selectbox(
        "Pilih component yang akan dihapus",
        options=list(component_options.keys()),
        key="delete_component_selectbox",
    )

    selected_component = component_options[selected_label]

    st.warning(
        "Delete bersifat permanen. "
        "Menghapus component juga akan menghapus scores terkait component tersebut."
    )

    confirm = st.checkbox(
        f"Saya yakin ingin menghapus component '{selected_component['name']}'",
        key="delete_component_confirm",
    )

    if st.button("Hapus Component", type="primary", disabled=not confirm):
        try:
            components_api.delete_component(
                token=token,
                component_id=selected_component["id"],
            )
            st.success("Component berhasil dihapus.")
            st.rerun()
        except ApiError as error:
            st.error(error.detail)


def render_grade_components_page(
    token: str,
    grade_table: dict,
) -> None:
    grade_table_id = grade_table["id"]

    st.subheader("Components")
    st.caption(
        "Component adalah komponen nilai seperti Tugas, UTS, atau UAS. "
        "Max score selalu 100."
    )

    try:
        components = _load_components(
            token=token,
            grade_table_id=grade_table_id,
        )
    except ApiError as error:
        st.error(error.detail)
        return

    st.markdown("#### Daftar Component")
    _render_component_table(components)

    st.divider()

    tab_create, tab_update, tab_delete = st.tabs(
        [
            "Tambah",
            "Edit",
            "Hapus",
        ]
    )

    with tab_create:
        _render_create_component_form(
            token=token,
            grade_table_id=grade_table_id,
        )

    with tab_update:
        _render_update_component_form(
            token=token,
            components=components,
        )

    with tab_delete:
        _render_delete_component_form(
            token=token,
            components=components,
        )