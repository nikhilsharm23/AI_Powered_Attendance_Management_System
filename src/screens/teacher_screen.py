import streamlit as st

from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout
)

import pandas as pd
from datetime import datetime
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
import numpy as np
from src.components.dialog_voice_attendance import voice_attendance_dialog 
from src.pipelines.face_pipeline import predict_attendance
from src.Database.config import supabase

from src.Database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subject,
    get_attendance_for_teacher
)

from src.pipelines.voice_pipeline import (
    get_voice_embedding,
    load_voice_encoder
)

from src.components.dialog_attendance_results import (
    attendance_result_dialog
)

from src.components.dialog_create_subject import (
    create_subject_dialog
)

from src.components.subject_card import (
    subject_card
)

from src.components.dialog_share_subject import (
    share_subject_dialog
)

from src.components.dialog_add_photo import (
    add_photos_dialog
)


# =========================================================
# TEACHER SCREEN
# =========================================================

def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:

        teacher_dashboard()

    elif (
        "teacher_login_type" not in st.session_state
        or st.session_state.teacher_login_type == "login"
    ):

        teacher_screen_login()

    elif st.session_state.teacher_login_type == "register":

        teacher_screen_register()


# =========================================================
# TEACHER DASHBOARD
# =========================================================

def teacher_dashboard():

    teacher_data = st.session_state.teacher_data

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    # -------------------------
    # Header
    # -------------------------

    with c1:

        header_dashboard()

    # -------------------------
    # Welcome + Logout
    # -------------------------

    with c2:

        st.subheader(
            f"Welcome, {teacher_data['name']}"
        )

        if st.button(
            "Logout",
            type="secondary",
            key="teacher_dashboard_logout",
            shortcut="control+backspace"
        ):

            st.session_state.pop(
                "teacher_data",
                None
            )

            st.session_state["is_logged_in"] = False
            st.session_state["user_role"] = None
            st.session_state["current_teacher_tab"] = (
                "take_attendance"
            )

            st.rerun()

    st.space()

    # =====================================================
    # DEFAULT TAB
    # =====================================================

    if "current_teacher_tab" not in st.session_state:

        st.session_state.current_teacher_tab = (
            "take_attendance"
        )

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3 = st.columns(3)

    # -------------------------
    # Take Attendance
    # -------------------------

    with tab1:

        type1 = (
            "primary"
            if st.session_state.current_teacher_tab
            == "take_attendance"
            else "tertiary"
        )

        if st.button(
            "Take Attendance",
            type=type1,
            width="stretch",
            icon=":material/ar_on_you:",
            key="teacher_take_attendance_tab"
        ):

            st.session_state.current_teacher_tab = (
                "take_attendance"
            )

            st.rerun()

    # -------------------------
    # Manage Subjects
    # -------------------------

    with tab2:

        type2 = (
            "primary"
            if st.session_state.current_teacher_tab
            == "manage_subjects"
            else "tertiary"
        )

        if st.button(
            "Manage Subjects",
            type=type2,
            width="stretch",
            icon=":material/book_ribbon:",
            key="teacher_manage_subjects_tab"
        ):

            st.session_state.current_teacher_tab = (
                "manage_subjects"
            )

            st.rerun()

    # -------------------------
    # Attendance Records
    # -------------------------

    with tab3:

        type3 = (
            "primary"
            if st.session_state.current_teacher_tab
            == "attendance_records"
            else "tertiary"
        )

        if st.button(
            "Attendance Records",
            type=type3,
            width="stretch",
            icon=":material/cards_stack:",
            key="teacher_attendance_records_tab"
        ):

            st.session_state.current_teacher_tab = (
                "attendance_records"
            )

            st.rerun()

    st.divider()

    # =====================================================
    # TAB CONTENT
    # =====================================================

    if st.session_state.current_teacher_tab == "take_attendance":

        teacher_tab_take_attendance()

    elif st.session_state.current_teacher_tab == "manage_subjects":

        teacher_tab_manage_subjects()

    elif (
        st.session_state.current_teacher_tab
        == "attendance_records"
    ):

        teacher_tab_attendance_records()

    footer_dashboard()


# =========================================================
# TAKE ATTENDANCE
# =========================================================

def teacher_tab_take_attendance():

    teacher_id = st.session_state.teacher_data["teacher_id"]

    st.header("Take AI Attendance")

    # =====================================================
    # INITIALIZE PHOTOS
    # =====================================================

    if "attendance_images" not in st.session_state:

        st.session_state.attendance_images = []

    # =====================================================
    # GET SUBJECTS
    # =====================================================

    subjects = get_teacher_subject(teacher_id)

    if not subjects:

        st.warning(
            "You haven't created any subjects yet! "
            "Please create one to begin!"
        )

        return

    # =====================================================
    # SUBJECT OPTIONS
    # =====================================================

    subject_options = {
        f"{s['name']} - {s['subject_code']}":
        s["subject_id"]
        for s in subjects
    }

    # =====================================================
    # SUBJECT + ADD PHOTOS
    # =====================================================

    col1, col2 = st.columns(
        [3, 1],
        vertical_alignment="bottom"
    )

    with col1:

        selected_subject_label = st.selectbox(
            "Select Subject",
            options=list(subject_options.keys())
        )

    with col2:

        if st.button(
            "Add Photos",
            type="primary",
            icon=":material/photo_prints:",
            width="stretch"
        ):

            add_photos_dialog()

    selected_subject_id = (
        subject_options[selected_subject_label]
    )

    # =====================================================
    # ADDED PHOTOS
    # =====================================================

    st.divider()

    if st.session_state.attendance_images:

        st.header("Added Photos")

        gallery_cols = st.columns(4)

        for idx, img in enumerate(
            st.session_state.attendance_images
        ):

            with gallery_cols[idx % 4]:

                st.image(
                    img,
                    width="stretch",
                    caption=f"Photo {idx + 1}"
                )

        has_photos = bool(
            st.session_state.attendance_images
        )

        c1, c2, c3 = st.columns(3)

        # =================================================
        # CLEAR PHOTOS
        # =================================================

        with c1:

            if st.button(
                "Clear all photos",
                width="stretch",
                type="tertiary",
                icon=":material/delete:",
                disabled=not has_photos
            ):

                st.session_state.attendance_images = []

                st.rerun()

        # =================================================
        # FACE ANALYSIS
        # =================================================

        with c2:

            if st.button(
                "Run Face Analysis",
                width="stretch",
                type="secondary",
                icon=":material/analytics:",
                disabled=not has_photos
            ):

                all_detected_ids = {}

                # -----------------------------------------
                # SCAN ALL PHOTOS
                # -----------------------------------------

                with st.spinner(
                    "Deep Scanning classroom photos..."
                ):

                    for idx, img in enumerate(
                        st.session_state.attendance_images
                    ):

                        img_np = np.array(
                            img.convert("RGB")
                        )

                        detected, _, _ = predict_attendance(
                            img_np
                        )

                        if detected:

                            for sid in detected.keys():

                                student_id = int(sid)

                                all_detected_ids.setdefault(
                                    student_id,
                                    []
                                ).append(
                                    f"Photo {idx + 1}"
                                )

                    # -----------------------------------------
                    # GET ENROLLED STUDENTS
                    # -----------------------------------------

                    enrolled_res = (
                        supabase
                        .table("subject_students")
                        .select("*,students(*)")
                        .eq(
                            "subject_id",
                            selected_subject_id
                        )
                        .execute()
                    )

                    enrolled_students = (
                        enrolled_res.data
                    )

                    # -----------------------------------------
                    # CHECK STUDENTS
                    # -----------------------------------------

                    if not enrolled_students:

                        st.warning(
                            "No students in this course"
                        )

                    else:

                        results = []

                        attendance_to_log = []

                        current_timestamp = (
                            datetime.now()
                            .strftime(
                                "%Y-%m-%dT%H:%M:%S"
                            )
                        )

                        # -------------------------------------
                        # CREATE ATTENDANCE RESULT
                        # -------------------------------------

                        for node in enrolled_students:

                            student = node["students"]

                            sources = (
                                all_detected_ids.get(
                                    int(
                                        student["student_id"]
                                    ),
                                    []
                                )
                            )

                            is_present = (
                                len(sources) > 0
                            )

                            results.append({
                                "Name": student["name"],

                                "ID": student["student_id"],

                                "Sources": (
                                    ",".join(sources)
                                    if is_present
                                    else "-"
                                ),

                                "Status": (
                                    "✅ Present"
                                    if is_present
                                    else "❌ Absent"
                                )
                            })

                            attendance_to_log.append({
                                "student_id":
                                    student["student_id"],

                                "subject_id":
                                    selected_subject_id,

                                "timestamp":
                                    current_timestamp,

                                "is_present":
                                    bool(is_present)
                            })

                        # -------------------------------------
                        # OPEN RESULT DIALOG
                        # -------------------------------------
                        # IMPORTANT:
                        # This is OUTSIDE the student loop
                        # and photo loop.

                        attendance_result_dialog(
                            pd.DataFrame(results),
                            attendance_to_log
                        )

        # =================================================
        # VOICE ATTENDANCE
        # =================================================

        with c3:

            if st.button(
                "Use Voice Attendance",
                type="primary",
                width="stretch",
                icon=":material/mic:"
            ):

                voice_attendance_dialog(selected_subject_id)


# =========================================================
# MANAGE SUBJECTS
# =========================================================

def teacher_tab_manage_subjects():

    teacher_data = st.session_state.get(
        "teacher_data"
    )

    # -------------------------
    # Check Teacher Session
    # -------------------------

    if not teacher_data:

        st.error(
            "Teacher session not found."
        )

        return

    teacher_id = teacher_data.get(
        "teacher_id"
    )

    if not teacher_id:

        st.error(
            "Teacher ID not found."
        )

        return

    # =====================================================
    # HEADER
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.header(
            "Manage Subjects",
            width="stretch"
        )

    with col2:

        if st.button(
            "Create New Subject",
            width="stretch",
            key="create_new_subject_button"
        ):

            create_subject_dialog(
                teacher_id
            )

    st.divider()

    # =====================================================
    # GET SUBJECTS
    # =====================================================

    try:

        subjects = get_teacher_subject(
            teacher_id
        )

    except Exception as e:

        st.error(
            f"Unable to load subjects: {e}"
        )

        return

    # =====================================================
    # DISPLAY SUBJECTS
    # =====================================================

    if subjects:

        for sub in subjects:

            subject_name = sub.get(
                "name",
                "Unknown Subject"
            )

            subject_code = sub.get(
                "subject_code",
                "N/A"
            )

            section = sub.get(
                "section",
                "N/A"
            )

            total_students = sub.get(
                "total_students",
                0
            )

            total_classes = sub.get(
                "total_classes",
                0
            )

            stats = [
                (
                    "👥",
                    "Students",
                    total_students
                ),
                (
                    "📅",
                    "Classes",
                    total_classes
                )
            ]

            # =================================================
            # SHARE BUTTON
            # =================================================

            def share_btn(
                name=subject_name,
                code=subject_code
            ):

                if st.button(
                    f"Share Code: {name}",
                    key=f"share_subject_{code}",
                    icon=":material/share:"
                ):

                    share_subject_dialog(
                        name,
                        code
                    )

            # =================================================
            # SUBJECT CARD
            # =================================================

            subject_card(
                name=subject_name,
                code=subject_code,
                section=section,
                stats=stats,
                footer_callback=share_btn
            )

    else:

        st.info(
            "NO SUBJECTS FOUND. CREATE ONE ABOVE."
        )


# =========================================================
# ATTENDANCE RECORDS
# =========================================================

def teacher_tab_attendance_records():

    st.header(
        "Attendance Records"
    )


    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)


    if not records:
        return

    data = []

    for r in records:
        ts = r.get('timestamp')

        data.append({
            "ts_group":ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N'A",
            "Subject":r['subjects']['name'],
            "Subject Code":r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present' , False))
        })


        df = pd.DataFrame(data)

        summary = (
            df.groupby(['ts_group' , 'Time' , 'Subject Code' , 'Subject'])
            .agg(
                Present_Count = ('is_present' , 'sum'),
                Total_Count = ('is_present' , 'count')
            ).reset_index()

        )  

        summary['Attendance Stats'] = (
            "✅" + summary['Present_Count'].astype(str)+" /" + summary["Total_Count"].astype(str) + 'Students'
        )      

        display_df = (
            summary
            .sort_values(by='ts_group', ascending=False)
            [['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
        ) 


        st.dataframe(display_df , width='stretch' , hide_index = True)






# =========================================================
# TEACHER LOGIN
# =========================================================

def login_teacher(
    username,
    password
):

    if not username or not password:

        return False

    teacher = teacher_login(
        username,
        password
    )

    if teacher:

        st.session_state["user_role"] = "teacher"

        st.session_state["teacher_data"] = teacher

        st.session_state["is_logged_in"] = True

        st.session_state[
            "current_teacher_tab"
        ] = "take_attendance"

        return True

    return False


# =========================================================
# TEACHER LOGIN SCREEN
# =========================================================

def teacher_screen_login():

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    # -------------------------
    # Header
    # -------------------------

    with c1:

        header_dashboard()

    # -------------------------
    # Back Button
    # -------------------------

    with c2:

        if st.button(
            "Go back to home",
            type="secondary",
            key="teacher_login_back_button",
            shortcut="control+backspace"
        ):

            st.session_state[
                "login_type"
            ] = None

            st.session_state[
                "teacher_login_type"
            ] = "login"

            st.rerun()

    # =====================================================
    # LOGIN FORM
    # =====================================================

    st.header(
        "Login using password",
        text_alignment="center"
    )

    st.space()
    st.space()

    teacher_username = st.text_input(
        "Enter Your Username",
        placeholder="nikhil_sharma",
        key="teacher_login_username"
    )

    teacher_pass = st.text_input(
        "Enter Your Password",
        type="password",
        placeholder="Enter Your Password",
        key="teacher_login_password"
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    # -------------------------
    # Login
    # -------------------------

    with btnc1:

        if st.button(
            "Login",
            icon="🔐",
            shortcut="control+enter",
            width="stretch",
            key="teacher_login_button"
        ):

            if login_teacher(
                teacher_username,
                teacher_pass
            ):

                st.toast(
                    "Welcome back!",
                    icon="👋"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username and password combo"
                )

    # -------------------------
    # Register
    # -------------------------

    with btnc2:

        if st.button(
            "Register Instead",
            type="primary",
            icon="🔐",
            width="stretch",
            key="teacher_register_button"
        ):

            st.session_state[
                "teacher_login_type"
            ] = "register"

            st.rerun()

    footer_dashboard()


# =========================================================
# REGISTER TEACHER
# =========================================================

def register_teacher(
    teacher_username,
    teacher_name,
    teacher_pass,
    teacher_pass_confirm
):

    if (
        not teacher_username
        or not teacher_name
        or not teacher_pass
    ):

        return (
            False,
            "All Fields are Required!"
        )

    # -------------------------
    # Check Existing Username
    # -------------------------

    try:

        if check_teacher_exists(
            teacher_username
        ):

            return (
                False,
                "Username already taken"
            )

    except Exception:

        return (
            False,
            "Unable to check username."
        )

    # -------------------------
    # Confirm Password
    # -------------------------

    if teacher_pass != teacher_pass_confirm:

        return (
            False,
            "Password doesn't match"
        )

    # -------------------------
    # Create Teacher
    # -------------------------

    try:

        create_teacher(
            teacher_username,
            teacher_pass,
            teacher_name
        )

        return (
            True,
            "Successfully Created! Login Now"
        )

    except Exception:

        return (
            False,
            "Unexpected Error while creating account!"
        )


# =========================================================
# TEACHER REGISTER SCREEN
# =========================================================

def teacher_screen_register():

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    # -------------------------
    # Header
    # -------------------------

    with c1:

        header_dashboard()

    # -------------------------
    # Back Button
    # -------------------------

    with c2:

        if st.button(
            "Go back to home",
            type="secondary",
            key="teacher_register_back_button",
            shortcut="control+backspace"
        ):

            st.session_state[
                "login_type"
            ] = None

            st.session_state[
                "teacher_login_type"
            ] = "login"

            st.rerun()

    # =====================================================
    # REGISTER FORM
    # =====================================================

    st.header(
        "Register Your Teacher Profile",
        text_alignment="center"
    )

    st.space()
    st.space()

    teacher_username = st.text_input(
        "Enter Your Username",
        placeholder="@nikhil_sharma",
        key="teacher_register_username"
    )

    teacher_name = st.text_input(
        "Enter Your Name",
        placeholder="Nikhil Sharma",
        key="teacher_register_name"
    )

    teacher_pass = st.text_input(
        "Enter Your Password",
        type="password",
        placeholder="Enter Your Password",
        key="teacher_register_password"
    )

    teacher_pass_confirm = st.text_input(
        "Confirm Your Password",
        type="password",
        placeholder="Enter Your Password",
        key="teacher_register_password_confirm"
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    # -------------------------
    # Register
    # -------------------------

    with btnc1:

        if st.button(
            "Register Now",
            icon="🔐",
            shortcut="control+enter",
            width="stretch",
            key="teacher_register_now_button"
        ):

            success, message = register_teacher(
                teacher_username,
                teacher_name,
                teacher_pass,
                teacher_pass_confirm
            )

            if success:

                st.success(
                    message
                )

                st.session_state[
                    "teacher_login_type"
                ] = "login"

                st.rerun()

            else:

                st.error(
                    message
                )

    # -------------------------
    # Login Instead
    # -------------------------

    with btnc2:

        if st.button(
            "Login Instead",
            type="primary",
            icon="🔐",
            width="stretch",
            key="teacher_login_instead_button"
        ):

            st.session_state[
                "teacher_login_type"
            ] = "login"

            st.rerun()

    footer_dashboard()