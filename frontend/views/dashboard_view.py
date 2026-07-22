import streamlit as st
from datetime import datetime
from core.formatters import format_bytes
import time

from services import storage_service
from core.session import get_username, end_session, mark_file_shared, shared_count


def _format_time(raw: str) -> str:
    try:
        return datetime.fromisoformat(raw).strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return raw


def render():
    _header()
    st.divider()

    success, files = storage_service.list_files()
    if not success:
        st.error(f"Could not load files: {files}")
        files = []

    _metrics(files)
    st.divider()

    _upload_section()
    st.divider()

    _file_list(files)
    st.divider()
    st.caption("Mini Dropbox — Serverless File Storage & Sharing Platform")


def _header():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(
            f"<h1 style='margin-bottom:0;'>📦 Mini Dropbox</h1>"
            f"<p style='color:#9aa0a6;margin-top:0;'>Welcome, {get_username()}</p>",
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("Logout", use_container_width=True):
            end_session()
            st.rerun()


def _metrics(files):
    total_size = sum(item.get("FileSize", 0) for item in files)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Files", len(files))
    with col2:
        st.metric("Storage Used", format_bytes(total_size))
    with col3:
        st.metric("Shared This Session", shared_count())

def _upload_section():
    st.subheader("Upload File")
    uploaded_file = st.file_uploader("Choose a file", label_visibility="collapsed")

    if st.button("Upload", type="primary", disabled=uploaded_file is None):
        with st.spinner("Uploading..."):
            success, message = storage_service.upload_file(
                uploaded_file.name, uploaded_file.getvalue()
            )

        if not success:
            st.error(message)
            return

        # S3's ObjectCreated trigger writes DynamoDB metadata asynchronously,
        # so poll briefly until the new file actually shows up before refreshing.
        with st.spinner("Processing upload..."):
            found = _wait_for_file(uploaded_file.name)

        if not found:
            st.warning("Upload succeeded, but it's taking longer than usual to appear. Refresh in a few seconds.")

        st.success(message)
        st.rerun()


def _wait_for_file(file_name: str, attempts: int = 8, delay_seconds: float = 1.0) -> bool:
    for _ in range(attempts):
        ok, files = storage_service.list_files()
        if ok and any(f.get("FileName") == file_name for f in files):
            return True
        time.sleep(delay_seconds)
    return False

def _file_list(files):
    st.subheader("My Files")

    if not files:
        st.info("No files uploaded yet.")
        return

    for item in files:
        file_id = item.get("FileID")
        file_name = item.get("FileName", "Unknown")
        upload_time = item.get("UploadTime", "")

        with st.container(border=True):
            name_col, time_col, action_col = st.columns([3, 2, 3])

            with name_col:
                st.markdown(f"**{file_name}**")
            with time_col:
                st.caption(_format_time(upload_time))

            with action_col:
                dl_col, share_col, del_col = st.columns(3)

                with dl_col:
                    if st.button("⬇️", key=f"dl_{file_id}", help="Download", use_container_width=True):
                        with st.spinner("Preparing link..."):
                            ok, result = storage_service.download_file(file_id)
                        if ok:
                            st.link_button("Download", result, use_container_width=True)
                        else:
                            st.error(result)

                with share_col:
                    if st.button("🔗", key=f"sh_{file_id}", help="Share", use_container_width=True):
                        with st.spinner("Generating link..."):
                            ok, result = storage_service.share_file(file_id)
                        if ok:
                            mark_file_shared(file_id)
                            st.code(result, language=None)
                        else:
                            st.error(result)

                with del_col:
                    if st.button("🗑️", key=f"del_{file_id}", help="Delete", use_container_width=True):
                        with st.spinner("Deleting..."):
                            ok, result = storage_service.delete_file(file_id)
                        (st.success if ok else st.error)(result)
                        if ok:
                            st.rerun()
