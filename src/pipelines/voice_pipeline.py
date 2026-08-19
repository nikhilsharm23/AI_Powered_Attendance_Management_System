from resemblyzer import VoiceEncoder, preprocess_wav

import numpy as np
import io
import librosa

import streamlit as st


@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()


def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()

        # Load audio at 16 kHz
        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000,
            mono=True
        )

        # Resemblyzer preprocessing
        wav = preprocess_wav(audio, source_sr=sr)

        # Generate 256-dimensional voice embedding
        embedding = encoder.embed_utterance(wav)

        return embedding.tolist()

    except Exception as e:
        st.error(f"Voice recognition error: {e}")
        return None


def identify_speaker(new_embedding, candidates_dict, threshold=0.65):

    if new_embedding is None or not candidates_dict:
        return None, 0.0, 0

    new_embedding = np.array(new_embedding)

    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():

        if stored_embedding is None:
            continue

        stored_embedding = np.array(stored_embedding)

        # Cosine similarity
        similarity = np.dot(
            new_embedding,
            stored_embedding
        ) / (
            np.linalg.norm(new_embedding)
            * np.linalg.norm(stored_embedding)
        )

        if similarity > best_score:
            best_score = similarity
            best_sid = sid

    # Threshold check AFTER checking all candidates
    if best_score >= threshold:
        return best_sid, best_score, 1

    return None, best_score, 0


def process_bulk_audio(
    audio_bytes,
    candidates_dict,
    threshold=0.65
):

    try:

        encoder = load_voice_encoder()

        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000,
            mono=True
        )

        # Detect non-silent portions
        segments = librosa.effects.split(
            audio,
            top_db=30
        )

        identified_results = {}

        for start, end in segments:

            # Ignore very short segments
            if (end - start) < sr * 0.5:
                continue

            segment_audio = audio[start:end]

            # Resemblyzer preprocessing
            wav = preprocess_wav(
                segment_audio,
                source_sr=sr
            )

            # Generate embedding
            embedding = encoder.embed_utterance(wav)

            sid, score, matched = identify_speaker(
                embedding,
                candidates_dict,
                threshold
            )

            if matched and sid is not None:

                if (
                    sid not in identified_results
                    or score > identified_results[sid]
                ):
                    identified_results[sid] = score

        return identified_results

    except Exception as e:

        st.error(f"Bulk process error: {e}")

        return {}