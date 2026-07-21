"""
Central place for all st.session_state reads/writes related to auth.
Nothing outside this file should touch session_state keys directly.
"""

import streamlit as st

_DEFAULTS = {
    "logged_in": False,
    "username": None,
    "access_token": None,
    "id_token": None,
    "refresh_token": None,
    "shared_file_ids": set(),
}


def init_session():
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def start_session(username: str, tokens: dict):
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.access_token = tokens.get("access_token")
    st.session_state.id_token = tokens.get("id_token")
    st.session_state.refresh_token = tokens.get("refresh_token")


def end_session():
    for key in _DEFAULTS:
        if key in st.session_state:
            del st.session_state[key]


def get_access_token() -> str:
    return st.session_state.get("access_token", "")


def get_username() -> str:
    return st.session_state.get("username", "User")


def mark_file_shared(file_id: str):
    st.session_state.shared_file_ids.add(file_id)


def shared_count() -> int:
    return len(st.session_state.get("shared_file_ids", set()))
