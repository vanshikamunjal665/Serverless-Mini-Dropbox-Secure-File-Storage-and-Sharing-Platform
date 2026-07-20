import streamlit as st
from datetime import datetime
from utils.api import list_files

# -----------------------------------------
# Page Configuration
# -----------------------------------------
st.set_page_config(
    page_title="Mini Dropbox",
    page_icon="☁️",
    layout="wide"
)

# -----------------------------------------
# Header
# -----------------------------------------
st.title("☁️ Mini Dropbox")
st.caption("Secure Serverless File Storage & Sharing Platform")

st.divider()

# -----------------------------------------
# Get Files
# -----------------------------------------
try:
    files = list_files(st.session_state["access_token"])
except:
    files = []

# -----------------------------------------
# Dashboard Metrics
# -----------------------------------------
total_files = len(files)
storage_used = "N/A"
shared_files = "-"

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📁 Total Files", total_files)

with col2:
    st.metric("☁️ Storage Used", storage_used)

with col3:
    st.metric("🔗 Shared Files", shared_files)

st.divider()

# -----------------------------------------
# Upload Section
# -----------------------------------------
st.subheader("☁️ Upload File")

uploaded_file = st.file_uploader(
    "Choose a file",
    label_visibility="collapsed"
)

if uploaded_file:

    st.success(f"Selected: {uploaded_file.name}")

    if st.button("Upload", use_container_width=True):
        st.info("Upload API will be connected here.")

st.divider()

# -----------------------------------------
# File List
# -----------------------------------------
st.subheader("📂 My Files")

if not files:
    st.info("No files uploaded yet.")

else:

    for file in files:

        upload_time = datetime.fromisoformat(file["UploadTime"])

        formatted_time = upload_time.strftime("%d %b %Y, %I:%M %p")

        with st.container(border=True):

            st.markdown(f"### 📄 {file['FileName']}")

            st.caption(f"Uploaded: {formatted_time}")

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button(
                    "⬇ Download",
                    key=f"download_{file['FileID']}"
                ):
                    st.info("Download feature coming next.")

            with c2:
                if st.button(
                    "🔗 Share",
                    key=f"share_{file['FileID']}"
                ):
                    st.info("Share feature coming next.")

            with c3:
                if st.button(
                    "🗑 Delete",
                    key=f"delete_{file['FileID']}"
                ):
                    st.info("Delete feature coming next.")

st.divider()

# -----------------------------------------
# Logout
# -----------------------------------------
if st.button("🚪 Logout"):

    st.session_state.clear()

    st.switch_page("pages/login.py")

st.divider()

st.caption("© 2026 Mini Dropbox | AWS Serverless Platform")
