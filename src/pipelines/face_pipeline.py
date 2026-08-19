import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.Database.db import get_all_students


# =========================================================
# LOAD DLIB MODELS
# =========================================================

@st.cache_resource
def load_dlib_models():

    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


# =========================================================
# GET FACE EMBEDDINGS
# =========================================================

def get_face_embeddings(image_np):

    detector, sp, facerec = load_dlib_models()

    faces = detector(image_np, 1)

    encodings = []

    for face in faces:

        shape = sp(image_np, face)

        face_descriptor = facerec.compute_face_descriptor(
            image_np,
            shape
        )

        encoding = np.array(
            face_descriptor,
            dtype=np.float64
        )

        encodings.append(encoding)

    return encodings


# =========================================================
# TRAIN MODEL
# =========================================================

@st.cache_resource
def get_trained_model():

    X = []
    y = []

    student_db = get_all_students()

    if not student_db:
        return None

    # -----------------------------------------------------
    # Get face embeddings from database
    # -----------------------------------------------------

    for student in student_db:

        embedding = student.get("face_embedding")
        student_id = student.get("student_id")

        if embedding and student_id is not None:

            try:

                embedding_array = np.array(
                    embedding,
                    dtype=np.float64
                )

                # Make sure embedding has 128 values
                if embedding_array.shape[0] != 128:
                    continue

                X.append(embedding_array)
                y.append(student_id)

            except Exception:
                continue

    # -----------------------------------------------------
    # No face embeddings
    # -----------------------------------------------------

    if len(X) == 0:

        return None

    # -----------------------------------------------------
    # Train SVC only if there are 2+ students
    # -----------------------------------------------------

    clf = None

    unique_students = list(set(y))

    if len(unique_students) >= 2:

        clf = SVC(
            kernel="linear",
            probability=True,
            class_weight="balanced"
        )

        try:

            clf.fit(X, y)

        except ValueError as e:

            st.error(
                f"Model training failed: {e}"
            )

            clf = None

    # -----------------------------------------------------
    # Return model data
    # -----------------------------------------------------

    return {
        "clf": clf,
        "X": X,
        "y": y
    }


# =========================================================
# RETRAIN CLASSIFIER
# =========================================================

def train_classifier():

    # Clear cached trained model
    get_trained_model.clear()

    model_data = get_trained_model()

    return model_data is not None


# =========================================================
# FACE PREDICTION
# =========================================================

def predict_attendance(class_image_np):

    # -----------------------------------------------------
    # Detect faces
    # -----------------------------------------------------

    encodings = get_face_embeddings(
        class_image_np
    )

    detected_student = {}

    num_faces = len(encodings)

    # -----------------------------------------------------
    # Load trained data
    # -----------------------------------------------------

    model_data = get_trained_model()

    if not model_data:

        return (
            detected_student,
            [],
            num_faces
        )

    clf = model_data["clf"]

    X_train = model_data["X"]

    y_train = model_data["y"]

    all_students = list(
        set(y_train)
    )

    if not all_students:

        return (
            detected_student,
            [],
            num_faces
        )

    # =====================================================
    # CHECK EACH FACE
    # =====================================================

    for encoding in encodings:

        predicted_id = None

        # -------------------------------------------------
        # CASE 1: Multiple students
        # -------------------------------------------------

        if clf is not None:

            predicted_id = clf.predict(
                [encoding]
            )[0]

        # -------------------------------------------------
        # CASE 2: Only one student
        # -------------------------------------------------

        else:

            predicted_id = all_students[0]

        # -------------------------------------------------
        # Find best embedding for predicted student
        # -------------------------------------------------

        best_match_score = float("inf")

        for i, student_id in enumerate(y_train):

            if student_id != predicted_id:
                continue

            stored_embedding = X_train[i]

            distance = np.linalg.norm(
                stored_embedding - encoding
            )

            if distance < best_match_score:

                best_match_score = distance

        # -------------------------------------------------
        # FACE MATCH THRESHOLD
        # -------------------------------------------------

        resemblance_threshold = 0.60

        if best_match_score <= resemblance_threshold:

            detected_student[predicted_id] = True

    return (
        detected_student,
        all_students,
        num_faces
    )