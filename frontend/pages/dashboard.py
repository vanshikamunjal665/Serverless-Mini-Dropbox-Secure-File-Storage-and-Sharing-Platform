import streamlit as st

st.title("☁ Mini Dropbox")

st.success("Welcome!")

st.write("You are logged in successfully.")

if st.button("Logout"):

    st.session_state.clear()

    st.rerun()
