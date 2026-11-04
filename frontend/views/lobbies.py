"""Lobbies view: browse, inspect rosters, create lobbies, and join via stored procedures."""

import streamlit as st
from config import SQUAD_ROLES
from mongo_helper import get_mongo_helper


def render_lobbies_view():
    """Render the main Lobbies browsing and management interface."""
    db_mgr = st.session_state.db_manager
    mongo = get_mongo_helper()
    current_user_id = st.session_state.get("current_user_id", 1)
    users = {u["UserID"]: u for u in db_mgr.get_users()}
    current_user = users.get(current_user_id, {"Username": "player", "Role": "player"})

    st.markdown("""
        <div class="sl-card-title">Matchmaking Lobbies</div>
        <div class="sl-card-subtitle">Browse active lobbies, manage participant rosters, and create custom squad sessions.</div>
    """, unsafe_allow_html=True)

    # Top Action Bar: Create Lobby Expander
    with st.expander("➕ Create New Matchmaking Lobby", expanded=False):
        games = db_mgr.get_games()
        col1, col2 = st.columns(2)
        with col1:
            sel_game = st.selectbox(
                "Select Game:",
                options=games,
                format_func=lambda g: f"{g['Title']} ({g['Genre']})",
                key="create_lobby_game",
            )
        with col2:
            sel_role = st.selectbox(
                "Your Squad Role (as Host):",
                options=SQUAD_ROLES,
                key="create_lobby_role",
            )

        if st.button("Create Lobby", key="btn_create_lobby", use_container_width=True):
            try:
                new_lobby_id = db_mgr.create_lobby(
                    host_id=current_user_id,
                    game_id=sel_game["GameID"],
                    host_role=sel_role,
                )
                mongo.log_activity(
                    user_id=current_user_id,
                    username=current_user["Username"],
                    action="LOBBY_CREATED",
                    description=f"Created a new {sel_game['Title']} lobby (#{new_lobby_id}) as {sel_role}.",
                    metadata={"lobby_id": new_lobby_id, "game_id": sel_game["GameID"]},
                )
                st.success(f"Lobby #{new_lobby_id} created successfully for {sel_game['Title']}!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create lobby: {e}")

    # Filters row
    f_col1, f_col2, f_col3 = st.columns([4, 4, 2])
    with f_col1:
        game_filter_options = [{"GameID": 0, "Title": "All Games"}] + db_mgr.get_games()
        sel_filter_game = st.selectbox(
            "Filter by Game",
            options=game_filter_options,
            format_func=lambda g: g["Title"],
            key="lobbies_filter_game",
        )
    with f_col2:
        sel_filter_status = st.selectbox(
            "Filter by Status",
            options=["All", "open", "full", "in_progress", "completed"],
            key="lobbies_filter_status",
        )
    with f_col3:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # Query Lobbies
    target_game_id = sel_filter_game["GameID"] if sel_filter_game["GameID"] != 0 else None
    lobbies = db_mgr.get_lobbies(game_id=target_game_id, status=sel_filter_status)

    if not lobbies:
        st.info("No matchmaking lobbies found matching your filter.")
        return

    # Render Lobby Cards
    for lobby in lobbies:
        lobby_id = lobby["LobbyID"]
        status = lobby["Status"]
        game_title = lobby["GameTitle"]
        genre = lobby["Genre"]
        host_name = lobby["HostName"]
        host_id = lobby["HostID"]
        count = lobby["ParticipantCount"]

        # Status badge classes
        badge_class = f"badge badge-{status}"

        with st.container():
            st.markdown(f"""
                <div class="sl-card" style="margin-bottom: 16px; padding: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div>
                            <span style="font-size: 1.25rem; font-weight: 700; color: #1A1B2F;">Lobby #{lobby_id}</span>
                            <span style="margin-left: 10px; font-weight: 600; color: #4B5563;">{game_title}</span>
                            <span style="margin-left: 8px; font-size: 0.8rem; background: #EEF2F6; padding: 2px 8px; border-radius: 4px; color: #64748B;">{genre}</span>
                        </div>
                        <span class="{badge_class}">{status.replace('_', ' ')}</span>
                    </div>
                    <div style="display: flex; gap: 32px; font-size: 0.95rem; color: #4B5563; margin-bottom: 14px;">
                        <div><strong>Host:</strong> {host_name}</div>
                        <div><strong>Capacity:</strong> {count} / 5 Players</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Roster Expander
            participants = db_mgr.get_lobby_participants(lobby_id)
            user_in_lobby = next((p for p in participants if p["UserID"] == current_user_id), None)
            is_host = (host_id == current_user_id) or (current_user.get("Role") in ["moderator", "admin"])

            with st.expander(f"📋 View Roster ({len(participants)} / 5) & Actions for Lobby #{lobby_id}", expanded=False):
                # Roster Table
                if participants:
                    roster_data = []
                    for p in participants:
                        ready_icon = "✅ Ready" if p["Ready_Status"] else "⏳ Waiting"
                        roster_data.append({
                            "Player": p["Username"],
                            "Squad Role": p["Squad_Role"] or "Unassigned",
                            "Status": ready_icon,
                        })
                    st.table(roster_data)
                else:
                    st.write("No participants currently in lobby.")

                # Interactive Action Buttons
                btn_cols = st.columns(3)

                # 1. Toggle My Ready Status
                if user_in_lobby:
                    with btn_cols[0]:
                        cur_ready = user_in_lobby["Ready_Status"]
                        toggle_label = "Mark as Not Ready" if cur_ready else "Mark as Ready"
                        if st.button(toggle_label, key=f"ready_{lobby_id}_{user_in_lobby['ParticipantID']}"):
                            db_mgr.update_participant_ready(user_in_lobby["ParticipantID"], 0 if cur_ready else 1)
                            st.rerun()

                # 2. Host Start Match
                if is_host and status in ["open", "full"]:
                    with btn_cols[1]:
                        if st.button("🚀 Start Match", key=f"start_{lobby_id}"):
                            db_mgr.update_lobby_status(lobby_id, "in_progress")
                            mongo.log_activity(
                                user_id=current_user_id,
                                username=current_user["Username"],
                                action="MATCH_STARTED",
                                description=f"Started match in Lobby #{lobby_id} ({game_title}).",
                                metadata={"lobby_id": lobby_id},
                            )
                            st.success(f"Lobby #{lobby_id} is now In Progress!")
                            st.rerun()

                # 3. Host / Admin Close Lobby (sp_close_lobby)
                if is_host and status != "completed":
                    with btn_cols[2]:
                        if st.button("🏁 Close Lobby (sp_close_lobby)", key=f"close_{lobby_id}"):
                            try:
                                db_mgr.close_lobby(lobby_id)
                                mongo.log_activity(
                                    user_id=current_user_id,
                                    username=current_user["Username"],
                                    action="LOBBY_COMPLETED",
                                    description=f"Closed and completed Lobby #{lobby_id}.",
                                    metadata={"lobby_id": lobby_id},
                                )
                                st.success(f"Lobby #{lobby_id} successfully closed via sp_close_lobby!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to close lobby: {e}")


def render_join_lobby_view():
    """Render the transactional Lobby Joining interface using sp_join_lobby."""
    db_mgr = st.session_state.db_manager
    mongo = get_mongo_helper()
    current_user_id = st.session_state.get("current_user_id", 1)
    users = {u["UserID"]: u for u in db_mgr.get_users()}
    current_user = users.get(current_user_id, {"Username": "player", "Role": "player"})

    st.markdown("""
        <div class="sl-card-title">Join a Matchmaking Lobby</div>
        <div class="sl-card-subtitle">Transactionally enter an active matchmaking lobby using stored procedure <code>sp_join_lobby</code>.</div>
    """, unsafe_allow_html=True)

    st.info(
        "💡 **Database Integrity & Trigger Guarantees:** Joining is handled transactionally by `sp_join_lobby`. "
        "The trigger `trg_part_bi` ensures the lobby is `open` and prevents joining if size >= 5. "
        "The trigger `trg_part_ai` automatically updates the status to `full` when the 5th player enters."
    )

    # Get open lobbies
    all_lobbies = db_mgr.get_lobbies()
    open_lobbies = [l for l in all_lobbies if l["Status"] == "open"]

    if not open_lobbies:
        st.warning("There are currently no lobbies in 'open' status to join. Please create a new lobby in the Lobbies tab!")
        return

    with st.container():
        st.markdown('<div class="sl-card">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            sel_lobby = st.selectbox(
                "Choose Lobby to Join:",
                options=open_lobbies,
                format_func=lambda l: f"Lobby #{l['LobbyID']} – {l['GameTitle']} (Host: {l['HostName']}, {l['ParticipantCount']}/5)",
                key="join_lobby_select",
            )
        with col2:
            # Squad Role
            sel_role = st.selectbox(
                "Select Your Squad Role:",
                options=SQUAD_ROLES,
                key="join_role_select",
            )

        # Inspect Selected Lobby
        lobby_id = sel_lobby["LobbyID"]
        participants = db_mgr.get_lobby_participants(lobby_id)
        current_slots = len(participants)

        st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 16px; margin: 16px 0;">
                <div style="font-weight: 700; color: #1E293B; margin-bottom: 8px;">Lobby #{lobby_id} Overview:</div>
                <div style="display: flex; gap: 24px; color: #475569; font-size: 0.9rem;">
                    <div><strong>Game:</strong> {sel_lobby['GameTitle']} ({sel_lobby['Genre']})</div>
                    <div><strong>Host:</strong> {sel_lobby['HostName']}</div>
                    <div><strong>Capacity:</strong> {current_slots} / 5 slots filled</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Show Current Roster
        st.markdown("<strong>Current Lobby Participants:</strong>", unsafe_allow_html=True)
        if participants:
            st.table([{"Player": p["Username"], "Role": p["Squad_Role"]} for p in participants])
        else:
            st.write("No participants currently in lobby.")

        # Join button
        if st.button("🚀 Join Lobby (CALL sp_join_lobby)", key="btn_confirm_join", use_container_width=True):
            try:
                msg = db_mgr.join_lobby(
                    lobby_id=lobby_id,
                    user_id=current_user_id,
                    squad_role=sel_role,
                )
                mongo.log_activity(
                    user_id=current_user_id,
                    username=current_user["Username"],
                    action="LOBBY_JOINED",
                    description=f"Joined Lobby #{lobby_id} ({sel_lobby['GameTitle']}) as {sel_role}.",
                    metadata={"lobby_id": lobby_id, "squad_role": sel_role},
                )
                st.success(f"🎉 Success! {msg}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Join Rejected by Database Constraint: {e}")

        st.markdown('</div>', unsafe_allow_html=True)
