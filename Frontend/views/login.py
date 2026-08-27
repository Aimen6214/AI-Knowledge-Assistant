import streamlit as st
from api.auth import login
from utils.helpers import handle_response
from utils.session import login_user


def login_page():

    # Header & Branding
    st.markdown(
        """
        <div style="text-align: center;">
            <div style="font-size: 1.6rem; font-weight: 700;">
                🛡️ SAFE AI
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<h2 style='text-align:center;'>Welcome back</h2>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center; color:#64748B;'>"
        "Sign in to continue securely."
        "</p>",
        unsafe_allow_html=True
    )

    # Continue Button Styling (Streamlit 1.61.1 uses stBaseButton-primary)
    st.markdown(
        """
        <style>
        div[data-testid="stForm"] button[data-testid="stBaseButton-primary"][data-testid="stBaseButton-primary"] {
            background-color: #2563EB !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.6rem 1rem !important;
            transition: background-color 0.15s ease-in-out;
        }

        div[data-testid="stForm"] button[data-testid="stBaseButton-primary"][data-testid="stBaseButton-primary"] div,
        div[data-testid="stForm"] button[data-testid="stBaseButton-primary"][data-testid="stBaseButton-primary"] span,
        div[data-testid="stForm"] button[data-testid="stBaseButton-primary"][data-testid="stBaseButton-primary"] p {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: 600 !important;
            opacity: 1 !important;
        }

        div[data-testid="stForm"] button[data-testid="stBaseButton-primary"][data-testid="stBaseButton-primary"]:hover {
            background-color: #1D4ED8 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Login Form
    with st.form("login_form", border=False):

        email = st.text_input(
            "Email address",
            placeholder="name@example.com"
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••"
        )

        submit = st.form_submit_button(
            "Continue",
            use_container_width=True,
            type="primary"
        )

        if submit:

            if not email or not password:
                st.error("Please fill in all fields.")

            else:
                response = login(email, password)
                data = handle_response(response)

                if data:
                    token = data.get("access_token")

                    if token:
                        login_user(token)
                        st.rerun()
                    else:
                        st.error(
                            "Login failed: access token not received."
                        )

    # Handle register navigation
    if st.query_params.get("nav") == "register":

        st.session_state.auth_mode = "register"

        if "nav" in st.query_params:
            del st.query_params["nav"]

        st.rerun()

    # Sign-up link
    st.markdown(
        """
        <div style="text-align:center; margin-top:1.2rem;">
            Don't have an account?
            <a href="?nav=register" target="_self">
                Sign up
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )
