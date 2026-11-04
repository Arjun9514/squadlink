"""Player Activity Feed view matching Player_activity_feed.png."""

import streamlit as st
import pandas as pd
from mongo_helper import get_mongo_helper


def render_activity_feed_view():
    """Render MongoDB Player Activity Feed view."""
    db_mgr = st.session_state.db_manager
    mongo = get_mongo_helper()
    users = db_mgr.get_users()

    st.markdown("""
        <div class="sl-card-title">Player activity feed</div>
        <div class="sl-card-subtitle">A MongoDB-backed timeline of important actions across SquadLink.</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        p_opts = [{"UserID": None, "Username": "Everyone"}] + users
        sel_feed_player = st.selectbox(
            "Player",
            options=p_opts,
            format_func=lambda u: u["Username"],
            key="feed_player_select",
        )
    with col2:
        action_types = [
            "All actions",
            "MATCH_RECORDED",
            "LOBBY_CREATED",
            "LOBBY_JOINED",
            "LOBBY_COMPLETED",
            "MATCH_STARTED",
            "FEEDBACK_SUBMITTED",
            "ROLE_CHANGED",
            "PROFILE_UPDATED",
        ]
        sel_action_type = st.selectbox(
            "Activity type",
            options=action_types,
            key="feed_action_select",
        )

    # Fetch activities from MongoDB or fallback
    activities = mongo.get_activities(
        user_id=sel_feed_player["UserID"],
        action=sel_action_type,
        limit=100,
    )

    if not activities:
        st.info("No matching activities found.")
        return

    table_rows = []
    for a in activities:
        c_time = a.get("created_at")
        if hasattr(c_time, "strftime"):
            time_str = c_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = str(c_time)[:19]

        table_rows.append({
            "Time": time_str,
            "Player": a.get("username", "Unknown"),
            "Action": a.get("action", "-"),
            "Description": a.get("description", "-"),
        })

    df_act = pd.DataFrame(table_rows)
    st.dataframe(df_act, hide_index=True, use_container_width=True)

    st.markdown(f"""
        <div style="color: #64748B; font-size: 0.85rem; margin-top: 12px;">
            Showing {len(table_rows)} most recent matching activities (maximum 100).
        </div>
    """, unsafe_allow_html=True)
