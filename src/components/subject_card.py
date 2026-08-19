import streamlit as st


def subject_card(
    name,
    code,
    section,
    stats,
    footer_callback=None
):

    st.markdown(
        f"""
        <div style="
            border: 1px solid rgba(128,128,128,0.3);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            background-color: rgba(128,128,128,0.08);
        ">
            <h3 style="margin-bottom: 5px;">{name}</h3>
            <p style="margin: 0;">
                <b>Subject Code:</b> {code}
            </p>
            <p style="margin: 0;">
                <b>Section:</b> {section}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns(len(stats))

    for col, stat in zip(cols, stats):

        icon, label, value = stat

        with col:
            st.metric(
                label=f"{icon} {label}",
                value=value
            )

    if footer_callback:
        footer_callback()

    st.divider()