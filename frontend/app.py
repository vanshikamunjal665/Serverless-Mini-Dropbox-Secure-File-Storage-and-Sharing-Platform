import streamlit as st

from core.config import APP_TITLE, APP_ICON
from core.session import init_session, is_logged_in
from views import login_view, dashboard_view

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")
init_session()

if is_logged_in():
    dashboard_view.render()
else:
    login_view.render()
