"""SquadLink Main Application.

Vector-Driven Matchmaking & Telemetry Platform.
"""

import os
import sys
from pathlib import Path

# Add repo root and nosql dir to python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.extend([
    str(ROOT_DIR),
    str(ROOT_DIR / "nosql"),
    str(Path(__file__).resolve().parent),
])

import streamlit as st
from config import APP_TITLE, APP_ICON, NAVIGATION_TABS
from styles import CUSTOM_CSS, render_brand_header
from auth import init_session_state, get_current_user, render_login_screen

# Set Streamlit Page Configuration
st.set_page_config(
    page_title=f"{APP_TITLE} – Matchmaking & Telemetry",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session State
init_session_state()

# Connection / Auth check
if not st.session_state.is_authenticated:
    render_login_screen()
    st.stop()

# Header: Logo, App Title, and Connection Badge + Log out
db_mgr = st.session_state.db_manager
current_user = get_current_user()
user_badge = f"{db_mgr.connection_info}"

header_cols = st.columns([8, 2])
with header_cols[0]:
    st.markdown(render_brand_header(user_info=user_badge), unsafe_allow_html=True)
with header_cols[1]:
    sub_col1, sub_col2 = st.columns([1, 1])
    with sub_col2:
        if st.button("Log out", key="btn_logout", use_container_width=True):
            st.session_state.is_authenticated = False
            st.rerun()

# User Context Bar (simulate current logged-in gamer or admin)
users = db_mgr.get_users()
user_options = {u["UserID"]: f"{u['Username']} ({u['Role']})" for u in users}

with st.expander("👤 User Profile & Role Switcher", expanded=False):
    sel_user_id = st.selectbox(
        "Active Gamer Account:",
        options=list(user_options.keys()),
        format_func=lambda uid: user_options[uid],
        index=list(user_options.keys()).index(st.session_state.current_user_id) if st.session_state.current_user_id in user_options else 0,
        key="active_user_switcher",
    )
    if sel_user_id != st.session_state.current_user_id:
        st.session_state.current_user_id = sel_user_id
        st.rerun()

from views.lobbies import render_lobbies_view, render_join_lobby_view
from views.matchmaking import render_matchmaking_view
from views.ratings import render_ratings_view
from views.players import render_players_view

# Navigation Tabs matching screenshot:
# Lobbies | Join a lobby | Find a match | Ratings | Players | Gameplay Telemetry | Activity Feed | Admin
tabs = st.tabs(NAVIGATION_TABS)

with tabs[0]:
    render_lobbies_view()

with tabs[1]:
    render_join_lobby_view()

with tabs[2]:
    render_matchmaking_view()

with tabs[3]:
    render_ratings_view()

with tabs[4]:
    render_players_view()

with tabs[5]:
    st.markdown("### Gameplay Telemetry Tab")
    st.info("Telemetry view loading...")

with tabs[6]:
    st.markdown("### Activity Feed Tab")
    st.info("Activity feed loading...")

with tabs[7]:
    st.markdown("### Admin Tab")
    st.info("Admin view loading...")
