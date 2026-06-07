import streamlit as st

from src.auth.session import get_current_user, init_auth_state, is_authenticated
from src.pages.dashboard import render_dashboard_page
from src.pages.login import render_login_page
from src.ui.layout import render_sidebar
from src.pages.admin_teachers import render_admin_teachers_page
from src.pages.grade_tables import render_grade_tables_page


st.set_page_config(
    page_title="Rapor App",
    page_icon="📘",
    layout="wide",
)


def main() -> None:
    init_auth_state()

    if not is_authenticated():
        render_login_page()
        st.stop()

    user = get_current_user()

    if user is None:
        render_login_page()
        st.stop()

    page = render_sidebar(user)

    if page == "Dashboard":
        render_dashboard_page(user)

    elif page == "Teacher Accounts":
        render_admin_teachers_page()

    elif page == "Grade Tables":
        render_grade_tables_page()

    elif page == "My Grade Tables":
        render_grade_tables_page()


if __name__ == "__main__":
    main()