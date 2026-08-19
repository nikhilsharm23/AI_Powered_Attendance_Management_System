import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog


def main():
    st.set_page_config(
        page_title='SnapClass - Making Attendence faster using AI',
        page_icon="https://i.ibb.co/YTYGn5qV/logo.png"
    )
    

    # =====================================================
    # LOGIN TYPE
    # =====================================================

    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None

    # =====================================================
    # JOIN CODE
    # =====================================================

    join_code = st.query_params.get("join-code")

    # =====================================================
    # IF JOIN CODE EXISTS
    # =====================================================

    if join_code:

        # ---------------------------------------------
        # Store join code
        # ---------------------------------------------

        if st.session_state.get("pending_join_code") != join_code:
            st.session_state["pending_join_code"] = join_code

        # ---------------------------------------------
        # Force student screen
        # ---------------------------------------------

        if st.session_state["login_type"] != "student":

            st.session_state["login_type"] = "student"

            st.rerun()

    # =====================================================
    # SHOW SCREEN
    # =====================================================

    match st.session_state["login_type"]:

        case "teacher":

            teacher_screen()

        case "student":

            student_screen()

        case None:

            home_screen()

    # =====================================================
    # AUTO ENROLL DIALOG
    # =====================================================

    pending_join_code = st.session_state.get(
        "pending_join_code"
    )

    if (
        pending_join_code
        and st.session_state.get("is_logged_in")
        and st.session_state.get("user_role") == "student"
    ):

        # ---------------------------------------------
        # Prevent dialog from opening repeatedly
        # ---------------------------------------------

        if (
            st.session_state.get("auto_enroll_opened_code")
            != pending_join_code
        ):

            st.session_state[
                "auto_enroll_opened_code"
            ] = pending_join_code

            auto_enroll_dialog(
                pending_join_code
            )


if __name__ == "__main__":
    main()