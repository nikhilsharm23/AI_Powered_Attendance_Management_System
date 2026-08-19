from src.Database.config import supabase
import bcrypt


# =========================================================
# PASSWORD FUNCTIONS
# =========================================================

def hash_pass(pwd):
    return bcrypt.hashpw(
        pwd.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def check_pass(pwd, hashed):
    try:
        return bcrypt.checkpw(
            pwd.encode("utf-8"),
            hashed.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


# =========================================================
# TEACHER FUNCTIONS
# =========================================================

def check_teacher_exists(username):
    response = (
        supabase
        .table("teachers")
        .select("username")
        .eq("username", username)
        .execute()
    )

    return len(response.data or []) > 0


def create_teacher(username, password, name):
    data = {
        "username": username,
        "password": hash_pass(password),
        "name": name
    }

    response = (
        supabase
        .table("teachers")
        .insert(data)
        .execute()
    )

    return response.data or []


def teacher_login(username, password):
    response = (
        supabase
        .table("teachers")
        .select("*")
        .eq("username", username)
        .execute()
    )

    if not response.data:
        return None

    teacher = response.data[0]

    if check_pass(
        password,
        teacher.get("password", "")
    ):
        return teacher

    return None


# =========================================================
# STUDENT FUNCTIONS
# =========================================================

def get_all_students():
    response = (
        supabase
        .table("students")
        .select("*")
        .execute()
    )

    return response.data or []


def create_student(
    new_name,
    face_embedding=None,
    voice_embedding=None
):
    data = {
        "name": new_name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }

    response = (
        supabase
        .table("students")
        .insert(data)
        .execute()
    )

    return response.data or []


# =========================================================
# SUBJECT FUNCTIONS
# =========================================================

def create_subject(
    subject_code,
    name,
    section,
    teacher_id
):
    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id
    }

    response = (
        supabase
        .table("subjects")
        .insert(data)
        .execute()
    )

    return response.data or []


def get_teacher_subject(teacher_id):
    response = (
        supabase
        .table("subjects")
        .select("*")
        .eq("teacher_id", teacher_id)
        .execute()
    )

    subjects = response.data or []

    for subject in subjects:

        subject_id = subject.get("id")

        subject["total_students"] = 0
        subject["total_classes"] = 0

        if not subject_id:
            continue

        # -------------------------------------------------
        # TOTAL STUDENTS
        # -------------------------------------------------

        try:
            student_response = (
                supabase
                .table("subject_students")
                .select(
                    "id",
                    count="exact"
                )
                .eq(
                    "subject_id",
                    subject_id
                )
                .execute()
            )

            subject["total_students"] = (
                student_response.count
                if student_response.count is not None
                else 0
            )

        except Exception:
            subject["total_students"] = 0

        # -------------------------------------------------
        # TOTAL CLASSES
        # -------------------------------------------------

        try:
            attendance_response = (
                supabase
                .table("attendance_logs")
                .select("timestamp")
                .eq(
                    "subject_id",
                    subject_id
                )
                .execute()
            )

            attendance_logs = (
                attendance_response.data or []
            )

            unique_sessions = set()

            for log in attendance_logs:

                timestamp = log.get("timestamp")

                if timestamp:
                    unique_sessions.add(timestamp)

            subject["total_classes"] = len(
                unique_sessions
            )

        except Exception:
            subject["total_classes"] = 0

    return subjects


# =========================================================
# ENROLL STUDENT
# =========================================================

def enroll_student_to_subject(
    student_id,
    subject_id
):
    data = {
        "student_id": student_id,
        "subject_id": subject_id
    }

    response = (
        supabase
        .table("subject_students")
        .insert(data)
        .execute()
    )

    return response.data or []


# =========================================================
# UNENROLL STUDENT
# =========================================================

def unenroll_student_to_subject(
    student_id,
    subject_id
):
    response = (
        supabase
        .table("subject_students")
        .delete()
        .eq(
            "student_id",
            student_id
        )
        .eq(
            "subject_id",
            subject_id
        )
        .execute()
    )

    return response.data or []


# =========================================================
# GET STUDENT SUBJECTS
# =========================================================

def get_student_subjects(student_id):
    response = (
        supabase
        .table("subject_students")
        .select(
            "*, subjects(*)"
        )
        .eq(
            "student_id",
            student_id
        )
        .execute()
    )

    return response.data or []


# =========================================================
# GET STUDENT ATTENDANCE
# =========================================================

def get_student_attendance(student_id):
    response = (
        supabase
        .table("attendance_logs")
        .select(
            "*, subjects(*)"
        )
        .eq(
            "student_id",
            student_id
        )
        .execute()
    )

    return response.data or []



def create_attendance(logs):
    response = supabase.table('attendance_logs').insert(logs).execute()
    return response.data



def get_attendance_for_teacher(teacher_id):
    response = (
        supabase
        .table("attendance_logs")
        .select("*, subjects!inner(*)")
        .eq("subjects.teacher_id", teacher_id)
        .execute()
    )

    return response.data or []