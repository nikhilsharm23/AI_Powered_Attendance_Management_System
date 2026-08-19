import streamlit as st
import time

from PIL import Image
import numpy as np

from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout
)

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard

from src.pipelines.face_pipeline import (
    predict_attendance,
    get_face_embeddings,
    train_classifier
)

from src.pipelines.voice_pipeline import get_voice_embedding

from src.Database.db import (
    get_all_students,
    create_student,  
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject
)


from src.components.dialog_enroll import enroll_dialog 
from src.components.subject_card import subject_card





# =========================================================
# STUDENT DASHBOARD
# =========================================================

def student_dashboard():

    student_data = st.session_state.student_data
    student_id = student_data['student_id']
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
                f"Welcome, {student_data['name']}"
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
                st.session_state["current_teacher_tab"] = "take_attendance"
                del st.session_state.student_data

    
                st.rerun()
    
    st.space()


    c1 , c2 = st.columns(2)

    with c1:
        st.header("Your Enrolled Subjects")
    with c2:
        if st.button("Enroll in Subject" , type = "primary" , width='stretch'):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)        

    stats_map = {}

    for log in logs:
            sid = log['subject_id']

            if sid not in stats_map:
                stats_map[sid] = {"total":0, "attended": 0}

            stats_map[sid]['total'] +=1

            if logs.get('is_present'):
                stats_map[sid]['attended'] += 1

    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
            sub = sub_node['subjects']
            sid = sub['subject_id']

            stats = stats_map.get(sid,{"total":0, "attended": 0} )
            def unenroll_btn():
                if st.button("Unenroll from this course", type="tertiary", width="stretch" , icon=":material/delete_forever:"):
                    unenroll_student_to_subject(student_id , sid)
                    st.toast(f"Unenrolled from {sub['name']} sucessfully")
                    st.rerun()
            with cols[i % 2]:
                subject_card(
                    name = sub['name'],
                    code = sub['subject_code'],
                    section = sub['section'],
                    stats = [
                        ('📅', 'Total', stats['total']),
                        ('✅', 'Attended', stats['attended'])],
                        footer_callback=unenroll_btn
                )


    footer_dashboard()


# =========================================================
# STUDENT SCREEN
# =========================================================

def student_screen():

    # -----------------------------------------------------
    # Styling
    # -----------------------------------------------------

    style_background_dashboard()
    style_base_layout()

    # -----------------------------------------------------
    # Already Logged In
    # -----------------------------------------------------

    if "student_data" in st.session_state:

        student_dashboard()

        return

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    with c1:
        header_dashboard()

    with c2:

        if st.button(
            "Go back to Home",
            type="secondary",
            key="student_login_back_btn",
            shortcut="control+backspace"
        ):

            st.session_state.pop("student_data", None)
            st.session_state.pop("is_logged_in", None)
            st.session_state.pop("user_role", None)

            st.session_state["login_type"] = None

            st.rerun()

    st.space()

    # =====================================================
    # REGISTRATION STATE
    # =====================================================

    if "show_student_registration" not in st.session_state:
        st.session_state.show_student_registration = False

    # =====================================================
    # FACE LOGIN
    # =====================================================

    if not st.session_state.show_student_registration:

        st.subheader("Login using Face Recognition")

        photo_source = st.camera_input(
            "Position Your Face in Center",
            key="student_face_camera"
        )

        if photo_source:

            try:

                img = np.array(
                    Image.open(photo_source)
                )

                with st.spinner("AI is Scanning..."):

                    detected, all_ids, num_faces = predict_attendance(
                        img
                    )

                # -----------------------------------------
                # No Face
                # -----------------------------------------

                if num_faces == 0:

                    st.warning(
                        "Face not Found! "
                        "Please position your face properly."
                    )

                # -----------------------------------------
                # Multiple Faces
                # -----------------------------------------

                elif num_faces > 1:

                    st.warning(
                        "Multiple Faces Found! "
                        "Please make sure only one person is visible."
                    )

                # -----------------------------------------
                # One Face
                # -----------------------------------------

                else:

                    # -------------------------------------
                    # Face Recognized
                    # -------------------------------------

                    if detected:

                        student_id = list(
                            detected.keys()
                        )[0]

                        all_students = get_all_students()

                        student = next(
                            (
                                s
                                for s in all_students
                                if s.get("student_id") == student_id
                            ),
                            None
                        )

                        if student:

                            st.session_state.is_logged_in = True

                            st.session_state.user_role = "student"

                            st.session_state.student_data = student

                            st.toast(
                                f"Welcome Back {student['name']}"
                            )

                            time.sleep(1)

                            st.rerun()

                        else:

                            st.warning(
                                "Student record not found in database."
                            )

                    # -------------------------------------
                    # Face Not Recognized
                    # -------------------------------------

                    else:

                        st.info(
                            "Face Not Recognized. "
                            "You can register as a new student."
                        )

                        st.session_state.show_student_registration = True

                        st.session_state.student_registration_image = img

                        st.rerun()

            except Exception as e:

                st.error(
                    f"Face scanning failed: {e}"
                )

    # =====================================================
    # STUDENT REGISTRATION
    # =====================================================

    if st.session_state.show_student_registration:

        with st.container(border=True):

            st.header("Register Your Profile")

            st.write(
                "Your face was not found in our database. "
                "Create a new student profile."
            )

            # ---------------------------------------------
            # Student Name
            # ---------------------------------------------

            new_name = st.text_input(
                "Enter Your Name",
                placeholder="E.g. Nikhil Sharma",
                key="student_registration_name"
            )

            # ---------------------------------------------
            # Voice Enrollment
            # ---------------------------------------------

            st.subheader(
                "Optional: Voice Enrollment"
            )

            st.info(
                "Enroll your voice if you want to use "
                "voice-based attendance."
            )

            audio_data = None

            try:

                audio_data = st.audio_input(
                    "Record a short phrase "
                    "like: I am present, My name is Nikhil",
                    key="student_voice_input"
                )

            except Exception as e:

                st.warning(
                    f"Audio recording is not available: {e}"
                )

            # ---------------------------------------------
            # Create Account
            # ---------------------------------------------

            if st.button(
                "Create Account",
                type="primary",
                key="create_student_account_btn"
            ):

                # -----------------------------------------
                # Validate Name
                # -----------------------------------------

                if not new_name.strip():

                    st.warning(
                        "Please enter your name."
                    )

                else:

                    with st.spinner(
                        "Creating Student Profile..."
                    ):

                        try:

                            # ---------------------------------
                            # Get Captured Face
                            # ---------------------------------

                            img = st.session_state.get(
                                "student_registration_image"
                            )

                            if img is None:

                                st.error(
                                    "Registration image not found. "
                                    "Please capture your face again."
                                )

                                return

                            # ---------------------------------
                            # Generate Face Embedding
                            # ---------------------------------

                            encodings = get_face_embeddings(
                                img
                            )

                            if not encodings:

                                st.error(
                                    "Couldn't capture your facial "
                                    "features. Please try again."
                                )

                                return

                            face_emb = encodings[0].tolist()

                            # ---------------------------------
                            # Generate Voice Embedding
                            # ---------------------------------

                            voice_emb = None

                            if audio_data:

                                try:

                                    audio_bytes = audio_data.read()

                                    if audio_bytes:

                                        voice_emb = get_voice_embedding(
                                            audio_bytes
                                        )

                                except Exception as e:

                                    st.warning(
                                        f"Voice enrollment failed: {e}"
                                    )

                                    voice_emb = None

                            # ---------------------------------
                            # Create Student
                            # ---------------------------------

                            response_data = create_student(
                                new_name.strip(),
                                face_embedding=face_emb,
                                voice_embedding=voice_emb
                            )

                            # ---------------------------------
                            # Success
                            # ---------------------------------

                            if response_data:

                                train_classifier()

                                st.session_state.is_logged_in = True

                                st.session_state.user_role = "student"

                                st.session_state.student_data = (
                                    response_data[0]
                                )

                                st.session_state.show_student_registration = False

                                st.session_state.pop(
                                    "student_registration_image",
                                    None
                                )

                                st.toast(
                                    f"Profile Created! "
                                    f"Hi {new_name.strip()}"
                                )

                                time.sleep(1)

                                st.rerun()

                            else:

                                st.error(
                                    "Student profile could not be created."
                                )

                        except Exception as e:

                            st.error(
                                f"Registration failed: {e}"
                            )

            # ---------------------------------------------
            # Cancel Registration
            # ---------------------------------------------

            if st.button(
                "Cancel Registration",
                key="cancel_student_registration_btn"
            ):

                st.session_state.show_student_registration = False

                st.session_state.pop(
                    "student_registration_image",
                    None
                )

                st.rerun()

    st.space()

    # -----------------------------------------------------
    # Footer
    # -----------------------------------------------------

    footer_dashboard()