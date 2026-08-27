import streamlit as st


# -------------------------
# Save Login Session
# -------------------------

def login_user(token):
    st.session_state.token = token


# -------------------------
# Alias
# -------------------------

def set_session(token):
    login_user(token)


# -------------------------
# Get Current Token
# -------------------------

def get_token():
    return st.session_state.get("token")


# -------------------------
# Headers
# -------------------------

def get_headers():
    token = get_token()

    if token:
        return {
            "Authorization": f"Bearer {token}"
        }

    return {}


# -------------------------
# Check Login Status
# -------------------------

def is_logged_in():
    return get_token() is not None


# -------------------------
# Initialize Session
# -------------------------

def initialize_session():

    if "token" not in st.session_state:
        st.session_state.token = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

    if "sources" not in st.session_state:
        st.session_state.sources = []


# -------------------------
# Logout
# -------------------------

def logout():

    keys = [
        "token",
        "messages",
        "conversation_id",
        "sources"
    ]

    for key in keys:
        if key in st.session_state:
            del st.session_state[key]