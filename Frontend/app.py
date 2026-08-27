import streamlit as st

from utils.session import initialize_session, is_logged_in
from views.login import login_page
from views.register import register_page
from views.chat import chat_page
from views.documents import documents_page


st.set_page_config(
    page_title="SAFE AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL CSS
# ============================================================

with open("static/style.css", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True,
    )


# ============================================================
# RECOVER SESSION
# ============================================================

initialize_session()


# ============================================================
# INITIAL SESSION STATE
# ============================================================

if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "login"


# Page to display after login
if "page" not in st.session_state:
    st.session_state["page"] = "chat"


# ============================================================
# AUTHENTICATION
# ============================================================

if not is_logged_in():

    # --------------------------------------------------------
    # User is NOT logged in
    # --------------------------------------------------------

    if st.session_state["auth_mode"] == "register":
        register_page()

    else:
        login_page()


else:

    # --------------------------------------------------------
    # User IS logged in
    # --------------------------------------------------------

    if st.session_state.get("page") == "documents":

        documents_page()

    else:

        chat_page()


# ============================================================
# RUN
# ============================================================

# Activate venv:
# .\venv\Scripts\Activate.ps1

# Run app:
# streamlit run app.py