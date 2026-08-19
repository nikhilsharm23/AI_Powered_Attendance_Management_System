import streamlit as st 

from supabase import create_client  , Client

supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)



# SUPABASE_URL = "https://hvtyebrlxscxpymndpuc.supabase.co"



# SUPABASE_KEY = "sb_secret_MPq4thBP9q3LmF50OmIQ9A_FOV08P3W"