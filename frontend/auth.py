"""Authentication and Session State Management for SquadLink Frontend."""

import streamlit as st
from db import DatabaseManager


def init_session_state():
    """Initialize session state keys."""
    if "db_manager" not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    if "is_authenticated" not in st.session_state:
        # Default to authenticated in demo mode for instant seamless use
        st.session_state.is_authenticated = True
    if "current_user_id" not in st.session_state:
        # Default to Rahul (UserID 1, Player)
        st.session_state.current_user_id = 1
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Lobbies"


def get_current_user():
    """Retrieve current logged in user details."""
    db_mgr: DatabaseManager = st.session_state.db_manager
    users = db_mgr.get_users()
    current_uid = st.session_state.get("current_user_id", 1)
    user = next((u for u in users if u["UserID"] == current_uid), None)
    if not user and users:
        user = users[0]
        st.session_state.current_user_id = user["UserID"]
    return user


def render_login_screen():
    """Render MySQL connection and login modal/page if needed."""
    st.markdown("""
        <div style="max-width: 480px; margin: 3rem auto; background: white; padding: 2rem; border-radius: 16px; border: 1px solid #E5E7EB; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <h2 style="margin-bottom: 0.5rem; color: #1A1B2F;">Connect to SquadLink</h2>
            <p style="color: #6B7280; margin-bottom: 1.5rem;">Connect to your MySQL database or launch in instant Demo Mode.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("db_login_form"):
        col1, col2 = st.columns(2)
        with col1:
            host = st.text_input("MySQL Host", value="localhost")
            user = st.text_input("MySQL User", value="root")
        with col2:
            port = st.number_input("Port", value=3306, step=1)
            database = st.text_input("Database", value="squadlink")
        password = st.text_input("Password", type="password", value="")

        submitted = st.form_submit_button("Connect to MySQL", use_container_width=True)
        if submitted:
            success, msg = st.session_state.db_manager.connect(
                host=host, port=int(port), user=user, password=password, database=database
            )
            if success:
                st.session_state.is_authenticated = True
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)

    st.write("---")
    if st.button("🚀 Launch in Demo Mode (Standalone In-Memory)", use_container_width=True):
        st.session_state.db_manager.enable_demo_mode()
        st.session_state.is_authenticated = True
        st.rerun()
