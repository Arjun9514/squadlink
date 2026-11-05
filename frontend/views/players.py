"""Player Directory, 3D Playstyle Visualizer, and Social Network view."""

import streamlit as st
import pandas as pd
from mongo_helper import get_mongo_helper


def render_players_view():
    """Render the Player Profiles and Social Network directory."""
    db_mgr = st.session_state.db_manager
    mongo = get_mongo_helper()
    current_user_id = st.session_state.get("current_user_id", 1)
    users = {u["UserID"]: u for u in db_mgr.get_users()}
    current_user = users.get(current_user_id, {"Username": "player", "Role": "player"})

    st.markdown("""
        <div class="sl-card-title">Player Directory & Profiles</div>
        <div class="sl-card-subtitle">Explore gamer profiles, 3D playstyle vectors, telemetry records, and social connections.</div>
    """, unsafe_allow_html=True)

    tab_profiles, tab_social, tab_editor = st.tabs([
        "🎮 Game Profiles & Playstyles",
        "👥 Social Connections Network",
        "⚙️ Edit My Playstyle Vector",
    ])

    # 1. Profiles & Playstyles
    with tab_profiles:
        games = db_mgr.get_games()
        p_col1, p_col2 = st.columns([5, 5])
        with p_col1:
            game_opts = [{"GameID": 0, "Title": "All Games"}] + games
            sel_game = st.selectbox(
                "Filter by Game:",
                options=game_opts,
                format_func=lambda g: g["Title"],
                key="player_dir_game_filter",
            )
        with p_col2:
            search_query = st.text_input("Search by Username:", placeholder="e.g. rahul, ananya...", key="player_dir_search")

        target_gid = sel_game["GameID"] if sel_game["GameID"] != 0 else None
        profiles = db_mgr.get_profiles(game_id=target_gid)

        if search_query:
            profiles = [p for p in profiles if search_query.lower() in p["Username"].lower()]

        if not profiles:
            st.info("No player profiles found.")
        else:
            for prof in profiles:
                uname = prof["Username"]
                role = prof["Role"]
                gtitle = prof["GameTitle"]
                genre = prof["Genre"]
                rep = float(prof["ReputationScore"])
                vec = prof.get("PlaystyleVector", [0.5, 0.5, 0.5])
                telem = prof.get("Telemetry_Data", {})

                with st.container():
                    st.markdown(f"""
                        <div class="sl-card" style="margin-bottom: 16px; padding: 20px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                <div>
                                    <span style="font-size: 1.25rem; font-weight: 700; color: #1A1B2F;">{uname}</span>
                                    <span class="badge badge-role" style="margin-left: 8px;">{role}</span>
                                    <span style="margin-left: 12px; color: #475569; font-weight: 600;">{gtitle}</span>
                                    <span style="font-size: 0.8rem; color: #64748B; background: #F1F5F9; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">{genre}</span>
                                </div>
                                <span style="background: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 0.9rem;">
                                    ⭐ {rep:.2f}
                                </span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Vector & Telemetry breakdown
                    c1, c2 = st.columns([6, 4])
                    with c1:
                        st.markdown("<strong>3D Playstyle Vector:</strong>", unsafe_allow_html=True)
                        st.progress(float(vec[0]), text=f"Aggression: {vec[0]:.2f}")
                        st.progress(float(vec[1]), text=f"Teamwork: {vec[1]:.2f}")
                        st.progress(float(vec[2]), text=f"Objective Focus: {vec[2]:.2f}")
                    with c2:
                        st.markdown("<strong>Telemetry Metadata:</strong>", unsafe_allow_html=True)
                        if telem:
                            st.json(telem, expanded=False)
                        else:
                            st.write("No telemetry recorded.")

    # 2. Social Connections Network
    with tab_social:
        st.markdown("<strong>Player Social Relationships:</strong>", unsafe_allow_html=True)

        with st.expander("➕ Add New Connection", expanded=False):
            s_col1, s_col2, s_col3 = st.columns([4, 4, 2])
            with s_col1:
                all_u = db_mgr.get_users()
                req_uid = st.selectbox(
                    "Requester:",
                    options=[u["UserID"] for u in all_u],
                    format_func=lambda uid: users[uid]["Username"],
                    index=[u["UserID"] for u in all_u].index(current_user_id) if current_user_id in [u["UserID"] for u in all_u] else 0,
                    key="conn_req_select",
                )
            with s_col2:
                rec_candidates = [u["UserID"] for u in all_u if u["UserID"] != req_uid]
                rec_uid = st.selectbox(
                    "Receiver:",
                    options=rec_candidates,
                    format_func=lambda uid: users[uid]["Username"],
                    key="conn_rec_select",
                )
            with s_col3:
                conn_type = st.selectbox("Type:", options=["friend", "follow", "block"], key="conn_type_select")

            if st.button("Establish Connection", key="btn_add_conn", use_container_width=True):
                try:
                    db_mgr.add_connection(req_uid, rec_uid, conn_type)
                    st.success(f"Connection created: {users[req_uid]['Username']} -> {conn_type} -> {users[rec_uid]['Username']}")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Cannot create connection: {ex}")

        connections = db_mgr.get_connections()
        if connections:
            conn_table = []
            for c in connections:
                badge_type = c["Connection_Type"]
                icon = "🤝 Friend" if badge_type == "friend" else ("👀 Following" if badge_type == "follow" else "🚫 Blocked")
                conn_table.append({
                    "Requester": c["RequesterName"],
                    "Relationship": icon,
                    "Receiver": c["ReceiverName"],
                })
            st.dataframe(pd.DataFrame(conn_table), hide_index=True, use_container_width=True)
        else:
            st.info("No connections found.")

    # 3. Edit My Playstyle Vector
    with tab_editor:
        st.markdown(f"<strong>Adjust Playstyle Vector for {current_user['Username']}:</strong>", unsafe_allow_html=True)
        games = db_mgr.get_games()
        edit_game = st.selectbox(
            "Select Game to Tune Vector:",
            options=games,
            format_func=lambda g: f"{g['Title']} ({g['Genre']})",
            key="edit_vec_game",
        )

        existing_prof = db_mgr.get_profiles(game_id=edit_game["GameID"], user_id=current_user_id)
        current_v = existing_prof[0]["PlaystyleVector"] if existing_prof else [0.5, 0.5, 0.5]

        e_col1, e_col2, e_col3 = st.columns(3)
        with e_col1:
            new_agg = st.slider("Aggression (0.0 - 1.0)", 0.0, 1.0, float(current_v[0]), 0.05, key="edit_agg")
        with e_col2:
            new_team = st.slider("Teamwork (0.0 - 1.0)", 0.0, 1.0, float(current_v[1]), 0.05, key="edit_team")
        with e_col3:
            new_obj = st.slider("Objective Focus (0.0 - 1.0)", 0.0, 1.0, float(current_v[2]), 0.05, key="edit_obj")

        if st.button("Save Playstyle Vector", key="btn_save_vec", use_container_width=True):
            updated_v = [round(new_agg, 2), round(new_team, 2), round(new_obj, 2)]
            db_mgr.save_profile(
                user_id=current_user_id,
                game_id=edit_game["GameID"],
                playstyle_vector=updated_v,
            )
            mongo.log_activity(
                user_id=current_user_id,
                username=current_user["Username"],
                action="PROFILE_UPDATED",
                description=f"Updated 3D playstyle vector for {edit_game['Title']} to {updated_v}.",
                metadata={"game_id": edit_game["GameID"], "playstyle_vector": updated_v},
            )
            st.success(f"Playstyle vector for {edit_game['Title']} updated to {updated_v}!")
            st.rerun()
