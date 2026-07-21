import streamlit as st

from services import cognito_service
from core.session import start_session


def render():
    st.markdown(
        "<h1 style='margin-bottom:0;'>📦 Mini Dropbox</h1>"
        "<p style='color:#9aa0a6;margin-top:0;'>Serverless File Storage & Sharing Platform</p>",
        unsafe_allow_html=True,
    )

    tab_login, tab_signup, tab_confirm = st.tabs(["Login", "Sign Up", "Confirm Account"])

    # -------------------- LOGIN --------------------
    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("Enter both username and password.")
            else:
                with st.spinner("Logging in..."):
                    success, result = cognito_service.login(username, password)

                if success:
                    start_session(username, result)
                    st.rerun()
                else:
                    st.error(result.get("message", "Login failed."))

    # -------------------- SIGN UP --------------------
    with tab_signup:
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="su_username")
            new_email = st.text_input("Email", key="su_email")
            new_password = st.text_input("Password", type="password", key="su_password")
            signup_submitted = st.form_submit_button("Sign Up", use_container_width=True)

        if signup_submitted:
            if not new_username or not new_email or not new_password:
                st.error("Fill in all fields.")
            else:
                with st.spinner("Creating account..."):
                    success, result = cognito_service.sign_up(new_username, new_password, new_email)
                (st.success if success else st.error)(result["message"])

    # -------------------- CONFIRM --------------------
    with tab_confirm:
        with st.form("confirm_form"):
            confirm_username = st.text_input("Username", key="cf_username")
            confirm_code = st.text_input("Verification Code", key="cf_code")
            confirm_submitted = st.form_submit_button("Confirm", use_container_width=True)

        if confirm_submitted:
            if not confirm_username or not confirm_code:
                st.error("Fill in all fields.")
            else:
                with st.spinner("Verifying..."):
                    success, result = cognito_service.confirm_sign_up(confirm_username, confirm_code)
                (st.success if success else st.error)(result["message"])
