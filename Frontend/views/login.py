import streamlit as st
from api.auth import login
from utils.helpers import handle_response

def login_page():
    # Header & Branding (Centered, no anchor links)
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 1.8rem;'>
            <div style='font-size: 1.6rem; font-weight: 700; color: #1E293B;'>🛡️ SAFE AI</div>
            <h2 style='margin-top: 0.8rem; margin-bottom: 0.2rem; font-size: 1.4rem; font-weight: 600; color: #0F172A;'>Welcome back</h2>
            <p style='color: #64748B; font-size: 0.875rem; margin: 0;'>Sign in to continue securely.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Clean Auth Form
    with st.form("login_form", border=False):
        email = st.text_input("Email address", placeholder="name@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        
        submit = st.form_submit_button("Continue", use_container_width=True, type="primary")

        if submit:
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                response = login(email, password)
                data = handle_response(response)
                if data:
                    st.session_state.token = data.get("access_token")
                    st.rerun()

    # Handle inline query navigation (No extra full-width button!)
    if st.query_params.get("nav") == "register":
        st.session_state.auth_mode = "register"
        st.query_params.clear()
        st.rerun()

    # Clean bottom link
    st.markdown(
        """
        <div style='text-align: center; margin-top: 1.2rem; font-size: 0.875rem; color: #64748B;'>
            Don't have an account? <a href='?nav=register' target='_self' class='auth-link'>Sign up</a>
        </div>
        """,
        unsafe_allow_html=True
    )