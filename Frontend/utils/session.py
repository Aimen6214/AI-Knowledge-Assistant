import streamlit as st


# -------------------------
# Save Login Session
# -------------------------

def login_user(token):
    st.session_state.token = token
    # Store token in URL query params so F5 reloads don't log you out
    st.query_params["token"] = token


# -------------------------
# Alias
# -------------------------

def set_session(token):
    login_user(token)


# -------------------------
# Get Current Token
# -------------------------

def get_token():
    # 1. Check in-memory session state first
    if st.session_state.get("token"):
        return st.session_state.token

    # 2. Recover from browser query params if user pressed F5
    token_param = st.query_params.get("token")
    if token_param:
        st.session_state.token = token_param
        return token_param

    return None


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
    # Auto-recover token on browser reload
    token_from_url = st.query_params.get("token")

    if "token" not in st.session_state or st.session_state.token is None:
        st.session_state.token = token_from_url

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

    # Remove token from URL on explicit logout
    if "token" in st.query_params:
        del st.query_params["token"]