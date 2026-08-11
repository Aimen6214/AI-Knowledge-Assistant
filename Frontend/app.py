import streamlit as st
from utils.session import initialize_session, is_logged_in
from views.login import login_page
from views.register import register_page
from views.chat import chat_page

st.set_page_config(page_title="SAFE AI", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

with open("static/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 1. Recover token from URL if F5 was pressed
initialize_session()

# 2. Set initial state ONCE
if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"

# 3. Check authentication status using helper
if not is_logged_in():
    if st.session_state["auth_mode"] == "register":
        register_page()
    else:
        login_page()
else:
    chat_page()