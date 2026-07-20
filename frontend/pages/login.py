import streamlit as st
from utils.auth import login

st.set_page_config(page_title="Mini Dropbox")

st.title("☁ Mini Dropbox")

st.subheader("Secure Serverless File Storage")

st.write("")

email = st.text_input("Email")

password = st.text_input(
    "Password",
    type="password"
)

if st.button("Login", use_container_width=True):

    with st.spinner("Logging in..."):

        result = login(email, password)

        if result["success"]:

            st.session_state["access_token"] = result["access_token"]
            st.session_state["logged_in"] = True

            st.success("Login Successful!")

            st.rerun()

        else:

            st.error(result["message"])
