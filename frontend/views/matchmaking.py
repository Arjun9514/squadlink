"""Vector Matchmaking View: sp_find_match and fn_playstyle_dist implementation."""

import streamlit as st
import pandas as pd
from mongo_helper import get_mongo_helper


def render_matchmaking_view():
    """Render the Vector-Driven Matchmaking view."""
    db_mgr = st.session_state.db_manager
    mongo = get_mongo_helper()
    current_user_id = st.session_state.get("current_user_id", 1)
    users = {u["UserID"]: u for u in db_mgr.get_users()}
    current_user = users.get(current_user_id, {"Username": "player", "Role": "player"})

    st.markdown("""
        <div class="sl-card-title">Vector-Driven Matchmaking</div>
        <div class="sl-card-subtitle">Discover compatible teammates for your lobby using 3D Euclidean playstyle vector distance and reputation scoring.</div>
    """, unsafe_allow_html=True)

    # Mathematical / Architectural Explanation
    with st.expander("📐 How SquadLink Vector Matchmaking Works (`sp_find_match`)", expanded=False):
        st.markdown(r"""
        SquadLink models each player's playstyle as a **3D normalized vector**:
        $$\vec{v} = [\text{Aggression},\ \text{Teamwork},\ \text{Objective Focus}] \in [0.0,\ 1.0]^3$$
        
        When `CALL sp_find_match(p_lobby, p_min_rep)` executes:
        1. It looks up the lobby's **Host** and **Game**.
        2. Retrieves the Host's 3D vector $\vec{v}_{\text{host}}$ for that game.
        3. Invokes the stored function `fn_playstyle_dist` to compute Euclidean distance:
           $$d = \sqrt{(A_{\text{host}} - A_{\text{player}})^2 + (T_{\text{host}} - T_{\text{player}})^2 + (O_{\text{host}} - O_{\text{player}})^2}$$
        4. Filters out players currently in the lobby and players with $\text{ReputationScore} < p_{\text{min\_rep}}$.
        5. Orders candidate players by **Euclidean Distance ASC** (nearest playstyles) and **ReputationScore DESC**, returning the top 5 matches.
        """)

    lobbies = db_mgr.get_lobbies()
    if not lobbies:
        st.warning("No lobbies available for matchmaking.")
        return

    # Configuration Form
    with st.container():
        st.markdown('<div class="sl-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([6, 4])
        with col1:
            sel_lobby = st.selectbox(
                "Select Matchmaking Lobby:",
                options=lobbies,
                format_func=lambda l: f"Lobby #{l['LobbyID']} – {l['GameTitle']} (Host: {l['HostName']}, Status: {l['Status']}, {l['ParticipantCount']}/5)",
                key="mm_lobby_select",
            )
        with col2:
            min_rep = st.slider(
                "Minimum Player Reputation Score:",
                min_value=0.0,
                max_value=5.0,
                value=3.5,
                step=0.1,
                key="mm_min_rep_slider",
            )

        lobby_id = sel_lobby["LobbyID"]
        game_id = sel_lobby["GameID"]
        host_id = sel_lobby["HostID"]

        # Fetch host profile
        host_profiles = db_mgr.get_profiles(game_id=game_id, user_id=host_id)
        host_profile = host_profiles[0] if host_profiles else None

        if host_profile:
            hv = host_profile.get("PlaystyleVector", [0.5, 0.5, 0.5])
            st.markdown(f"""
                <div style="background: #F1F5F9; border-radius: 8px; padding: 12px 16px; margin: 12px 0; font-size: 0.9rem; color: #334155;">
                    <strong>Host Profile ({sel_lobby['HostName']}):</strong> 
                    Playstyle Vector: Aggression: <code>{hv[0]}</code> | Teamwork: <code>{hv[1]}</code> | Objective: <code>{hv[2]}</code> | Reputation: ⭐ <strong>{host_profile['ReputationScore']}</strong>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"Host '{sel_lobby['HostName']}' does not have an active profile registered for {sel_lobby['GameTitle']}.")

        btn_find = st.button("🔍 Find Compatible Players (sp_find_match)", key="btn_execute_mm", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Show results
    if btn_find or st.session_state.get(f"ran_mm_{lobby_id}"):
        st.session_state[f"ran_mm_{lobby_id}"] = True
        try:
            matches = db_mgr.find_match(lobby_id=lobby_id, min_rep=min_rep)
        except Exception as e:
            st.error(f"Error executing sp_find_match: {e}")
            return

        if not matches:
            st.info(f"No players found with Reputation >= {min_rep:.2f} who are not already in this lobby. Try lowering the minimum reputation.")
            return

        st.markdown(f"### Top {len(matches)} Recommended Teammates for Lobby #{lobby_id}")

        for idx, match in enumerate(matches, start=1):
            cand_uid = match["UserID"]
            cand_name = match["Username"]
            cand_rep = float(match["ReputationScore"])
            dist = float(match["playstyle_distance"])
            cv = match.get("PlaystyleVector", [0.5, 0.5, 0.5])
            hv = match.get("HostVector", host_profile.get("PlaystyleVector", [0.5, 0.5, 0.5]) if host_profile else [0.5, 0.5, 0.5])

            # Similarity Percentage: max theoretical distance in 3D unit cube is sqrt(3) ~ 1.732
            max_dist = 1.732
            similarity_pct = max(0, min(100, int((1.0 - (dist / max_dist)) * 100)))

            with st.container():
                st.markdown(f"""
                    <div class="sl-card" style="margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <div>
                                <span style="font-size: 1.15rem; font-weight: 700; color: #1A1B2F;">#{idx} {cand_name}</span>
                                <span style="margin-left: 10px; color: #64748B; font-size: 0.85rem;">User ID: {cand_uid}</span>
                            </div>
                            <div style="display: flex; gap: 12px; align-items: center;">
                                <span style="background: #ECFDF5; color: #065F46; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;">
                                    {similarity_pct}% Compatibility
                                </span>
                                <span style="background: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                                    ⭐ {cand_rep:.2f}
                                </span>
                            </div>
                        </div>
                        <div style="margin-bottom: 12px; font-size: 0.9rem; color: #475569;">
                            <strong>3D Euclidean Distance (fn_playstyle_dist):</strong> <code>{dist:.3f}</code> (lower is closer)
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Vector comparison columns
                v_col1, v_col2 = st.columns([7, 3])
                with v_col1:
                    df_vec = pd.DataFrame({
                        "Dimension": ["Aggression", "Teamwork", "Objective Focus"],
                        f"Candidate ({cand_name})": [cv[0], cv[1], cv[2]],
                        f"Host ({sel_lobby['HostName']})": [hv[0], hv[1], hv[2]],
                    })
                    st.dataframe(df_vec, hide_index=True, use_container_width=True)

                with v_col2:
                    st.write("")
                    # Action: Add recommended player to lobby
                    rec_role = st.selectbox(
                        "Assign Squad Role:",
                        options=["Duelist", "Sentinel", "Controller", "Initiator", "Support", "Flex"],
                        key=f"mm_role_{lobby_id}_{cand_uid}",
                    )
                    if st.button(f"➕ Add {cand_name} to Lobby", key=f"btn_add_cand_{lobby_id}_{cand_uid}", use_container_width=True):
                        try:
                            res = db_mgr.join_lobby(
                                lobby_id=lobby_id,
                                user_id=cand_uid,
                                squad_role=rec_role,
                            )
                            mongo.log_activity(
                                user_id=cand_uid,
                                username=cand_name,
                                action="LOBBY_JOINED",
                                description=f"Recruited into Lobby #{lobby_id} via Vector Matchmaking as {rec_role}.",
                                metadata={"lobby_id": lobby_id, "recruited_by": current_user["Username"]},
                            )
                            st.success(f"Successfully added {cand_name} to Lobby #{lobby_id}!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Cannot add player: {ex}")
