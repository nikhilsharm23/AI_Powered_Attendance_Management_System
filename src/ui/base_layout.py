import streamlit as st 

def style_background_home():
    st.markdown(""" 
        <style>
            .stApp {
                background: #5865F2 !important;
            }
            .stApp div[data-testid="stColumn"]{
                background-color:#E0E3FF !important;
                padding: 1.5rem !important; /* Yahan 2.5rem se 1.5rem kar diya hai boxes ko chota karne ke liye */
                border-radius: 2rem !important; /* 5rem se 2rem kiya taaki chote box ke sath shape sahi lage */
            }
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown(""" 
        <style>
            .stApp {
                background: #E0E3FF !important;
            }
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    st.markdown(""" 
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');

            /* Hide top bar of streamlit */

            
            #MainMenu, footer , header {
                visibility: hidden;
            }

            .block-container {
                max-width: 700px !important; /* Pura app chota aur center ho jayega */
                padding-top: 1rem !important;
            }

            h1{
                font-family: 'Climate Crisis' , sans-serif !important;
                font-size: 3.5rem !important;
                line-height: 1.1 !important;
                margin-bottom: 0rem !important;
            }
            h2{
                font-family: 'Climate Crisis' , sans-serif !important;
                font-size: 2rem !important;
                line-height: 0.9 !important;
                margin-bottom: 0rem !important;
            }
            h3,h4,p{
                 font-family: 'Outfit' , sans-serif;
            }

            button{
                background:#5865F2 !important;
                border-radius: 1rem !important; /* 1.5rem se kam kiya */
                color: white !important;
                padding: 5px 15px !important; /* Button ko chota karne ke liye padding kam ki */
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
            }
            button[kind="secondary"]{
                background:#EB459E !important;
                border-radius: 1rem !important;
                color: white !important;
                padding: 5px 15px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
            }
            button[kind="tertiary"]{
                background: black !important;
                border-radius: 1rem !important;
                color: white !important;
                padding: 5px 15px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
            }
            button:hover{
                transform: scale(1.05)
            }
        </style>
    """, unsafe_allow_html=True)