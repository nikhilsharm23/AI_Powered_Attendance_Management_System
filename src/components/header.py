import streamlit as st

def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    # margin-top aur margin-bottom ko 5px kar diya gaya hai aur <br/> hata diya hai
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:5px; margin-top:5px;">
            <img src='{logo_url}' style='height:80px;' />
            <h2 style='text-align:center; color:#E0E3FF; margin-top:5px; margin-bottom:5px;'>SNAP CLASS</h2>
        </div>
        """, unsafe_allow_html=True)


def header_dashboard():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    # margin-top aur margin-bottom ko 5px kar diya gaya hai aur <br/> hata diya hai
    st.markdown(f"""
        <div style="display:flex;  align-items:center; justify-content:center; gap:10px;">
            <img src='{logo_url}' style='height:90px;' />
            <h3 style='text-align:left; color:#; margin-top:5px; margin-bottom:#5865F2px;'>SNAP</br> CLASS</h3>
        </div>
        """, unsafe_allow_html=True)