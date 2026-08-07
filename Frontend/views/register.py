import streamlit as st
from api.auth import register
from utils.helpers import handle_response

def register_page():
    # Center the register container in "wide" layout mode
    _, center_col, _ = st.columns([1, 1.2, 1])

    with center_col:
        st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>Create an account</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 0.85rem; margin-bottom: 1.5rem;'>Sign up for SAFE AI</p>", unsafe_allow_html=True)

        with st.form("register_form", border=False):
            email = st.text_input("Email", placeholder="name@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Sign up", use_container_width=True, type="primary")

            if submit:
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    response = register(email, password)
                    data = handle_response(response)
                    if data:
                        st.success("Account created! Please log in.")
                        st.session_state.auth_mode = "login"
                        st.rerun()

        st.write("")
        c1, c2 = st.columns([2.3, 1], vertical_alignment="center")
        with c1:
            st.markdown("<p style='text-align: right; margin: 0; color: #666; font-size: 0.9rem;'>Already have an account?</p>", unsafe_allow_html=True)
        with c2:
            if st.button("Log in", key="to_login"):
                st.session_state.auth_mode = "login"
                st.rerun()