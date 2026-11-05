"""Gameplay Telemetry view matching gameplay_telemetry.png & player_performance_summary.png."""

import streamlit as st
import pandas as pd
import altair as alt
from mongo_helper import get_mongo_helper
from styles import render_metric_card


def render_telemetry_view():
    """Render Gameplay Telemetry and Performance Summary view."""
    db_mgr = st.session_state.db_manager
    mongo = get_mongo_helper()
    users = db_mgr.get_users()
    games = db_mgr.get_games()
    lobbies = db_mgr.get_lobbies()

    st.markdown("""
        <div class="sl-card-title">Gameplay telemetry</div>
        <div class="sl-card-subtitle">Record flexible per-match statistics in MongoDB. MySQL continues to own player and game identities.</div>
    """, unsafe_allow_html=True)

    # 1. Match Recording Form Card
    with st.container():
        st.markdown('<div class="sl-card">', unsafe_allow_html=True)

        st.markdown("<h4 style='margin-bottom: 12px; color: #1E293B;'>Match details</h4>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            sel_player = st.selectbox(
                "Player",
                options=users,
                format_func=lambda u: u["Username"],
                key="telem_player_select",
            )
        with col2:
            sel_game = st.selectbox(
                "Game",
                options=games,
                format_func=lambda g: g["Title"],
                key="telem_game_select",
            )
        with col3:
            lobby_opts = [{"LobbyID": 0, "label": "No lobby"}] + [
                {"LobbyID": l["LobbyID"], "label": f"Lobby #{l['LobbyID']} ({l['GameTitle']})"}
                for l in lobbies
            ]
            sel_lobby = st.selectbox(
                "Lobby (optional)",
                options=lobby_opts,
                format_func=lambda l: l["label"],
                key="telem_lobby_select",
            )

        col4, col5, col6 = st.columns(3)
        with col4:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=24, step=1, key="telem_duration")
        with col5:
            result_str = st.selectbox("Result", options=["Win", "Loss", "Draw"], key="telem_result")
        with col6:
            notable_event = st.selectbox("Notable event", options=["kill", "assist", "clutch", "ace", "objective_capture"], key="telem_notable_event")

        st.markdown("<h4 style='margin: 18px 0 12px 0; color: #1E293B;'>Performance statistics</h4>", unsafe_allow_html=True)
        stat1, stat2, stat3, stat4 = st.columns(4)
        with stat1:
            kills = st.number_input("Kills", min_value=0, max_value=200, value=15, step=1, key="telem_kills")
        with stat2:
            deaths = st.number_input("Deaths", min_value=0, max_value=200, value=9, step=1, key="telem_deaths")
        with stat3:
            assists = st.number_input("Assists", min_value=0, max_value=200, value=9, step=1, key="telem_assists")
        with stat4:
            accuracy = st.number_input("Accuracy (%)", min_value=0.0, max_value=100.0, value=77.0, step=0.5, key="telem_acc")

        damage = st.number_input("Damage dealt", min_value=0, max_value=100000, value=3400, step=50, key="telem_damage")

        st.markdown("<h4 style='margin: 18px 0 12px 0; color: #1E293B;'>Playstyle indicators (0–1)</h4>", unsafe_allow_html=True)
        p1, p2, p3 = st.columns(3)
        with p1:
            aggression = st.slider("Aggression", 0.0, 1.0, 0.95, 0.05, key="telem_agg")
        with p2:
            teamwork = st.slider("Teamwork", 0.0, 1.0, 0.40, 0.05, key="telem_team")
        with p3:
            obj_focus = st.slider("Objective focus", 0.0, 1.0, 0.90, 0.05, key="telem_obj")

        st.markdown("<h4 style='margin: 18px 0 12px 0; color: #1E293B;'>Event description</h4>", unsafe_allow_html=True)
        event_desc = st.text_input("Event description", value="Played a match", label_visibility="collapsed", key="telem_event_desc")

        st.write("")
        if st.button("Save match to MongoDB", key="btn_save_mongo", use_container_width=False):
            doc = {
                "user_id": sel_player["UserID"],
                "username": sel_player["Username"],
                "game_id": sel_game["GameID"],
                "game_title": sel_game["Title"],
                "lobby_id": sel_lobby["LobbyID"] if sel_lobby["LobbyID"] != 0 else None,
                "duration_minutes": int(duration),
                "result": {"outcome": result_str.lower(), "win": (result_str.lower() == "win")},
                "performance": {
                    "kills": int(kills),
                    "deaths": int(deaths),
                    "assists": int(assists),
                    "accuracy": float(accuracy),
                    "damage": int(damage),
                },
                "playstyle": {
                    "aggression": round(float(aggression), 2),
                    "teamwork": round(float(teamwork), 2),
                    "objective_focus": round(float(obj_focus), 2),
                },
                "events": [{"type": notable_event, "description": event_desc}],
                "source": "streamlit_manual_entry",
            }
            session_id = mongo.log_session(doc)
            # Log activity feed event
            mongo.log_activity(
                user_id=sel_player["UserID"],
                username=sel_player["Username"],
                action="MATCH_RECORDED",
                description=f"Recorded a {result_str.lower()} in {sel_game['Title']}.",
                metadata={"session_id": str(session_id), "game_title": sel_game["Title"], "kills": kills, "result": result_str},
            )
            st.session_state["last_saved_session_id"] = session_id
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("last_saved_session_id"):
        sid = st.session_state["last_saved_session_id"]
        st.success(f"Match telemetry saved. Session ID: {sid}")

    st.write("---")

    # 2. Player Performance Summary Section
    st.markdown("""
        <div class="sl-card-title">Player performance summary</div>
    """, unsafe_allow_html=True)

    s_col1, s_col2 = st.columns(2)
    with s_col1:
        p_summary_opts = [{"UserID": None, "Username": "All players"}] + users
        sel_summary_player = st.selectbox(
            "Player summary",
            options=p_summary_opts,
            format_func=lambda u: u["Username"],
            key="summary_player_select",
        )
    with s_col2:
        g_summary_opts = [{"GameID": None, "Title": "All games"}] + games
        sel_summary_game = st.selectbox(
            "Game summary",
            options=g_summary_opts,
            format_func=lambda g: g["Title"],
            key="summary_game_select",
        )

    # Aggregation Pipeline
    summary_data = mongo.get_session_summary(
        user_id=sel_summary_player["UserID"],
        game_id=sel_summary_game["GameID"],
    )

    # Metric Cards Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(render_metric_card("Matches", summary_data.get("matches", 0)), unsafe_allow_html=True)
    with m2:
        st.markdown(render_metric_card("Wins", summary_data.get("wins", 0)), unsafe_allow_html=True)
    with m3:
        st.markdown(render_metric_card("K/D", f"{summary_data.get('kd', 0.0):.2f}"), unsafe_allow_html=True)
    with m4:
        st.markdown(render_metric_card("Win rate", f"{summary_data.get('win_rate', 0.0):.1f}%"), unsafe_allow_html=True)
    with m5:
        st.markdown(render_metric_card("Avg. accuracy", f"{summary_data.get('avg_accuracy', 0.0):.1f}%"), unsafe_allow_html=True)

    st.markdown(f"""
        <div style="color: #64748B; font-size: 0.9rem; margin: 12px 0 24px 0;">
            Total recorded playtime: {summary_data.get('total_minutes', 0)} minutes. Statistics are calculated using a MongoDB aggregation pipeline.
        </div>
    """, unsafe_allow_html=True)

    # Match History Filters & Table
    h_col1, h_col2 = st.columns(2)
    with h_col1:
        sel_hist_player = st.selectbox(
            "Match history player",
            options=p_summary_opts,
            format_func=lambda u: u["Username"],
            key="hist_player_select",
        )
    with h_col2:
        sel_hist_game = st.selectbox(
            "Match history game",
            options=g_summary_opts,
            format_func=lambda g: g["Title"],
            key="hist_game_select",
        )

    sessions = mongo.get_sessions(
        user_id=sel_hist_player["UserID"],
        game_id=sel_hist_game["GameID"],
    )

    if not sessions:
        st.info("No recorded matches found for the selected filters.")
    else:
        hist_rows = []
        for s in sessions:
            p_date = s.get("played_at")
            if hasattr(p_date, "strftime"):
                date_str = p_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                date_str = str(p_date)[:19]

            perf = s.get("performance", {})
            hist_rows.append({
                "Date": date_str,
                "Player": s.get("username", "Unknown"),
                "Game": s.get("game_title", "Unknown"),
                "Result": s.get("result", {}).get("outcome", "-"),
                "Kills": perf.get("kills", 0),
                "Deaths": perf.get("deaths", 0),
                "Assists": perf.get("assists", 0),
                "Accuracy %": perf.get("accuracy", 0),
                "Duration min": s.get("duration_minutes", 0),
            })

        df_hist = pd.DataFrame(hist_rows)
        st.dataframe(df_hist, hide_index=True, use_container_width=True)

        # Kills chart
        st.markdown("<h4 style='margin-top: 24px; color: #1E293B;'>Total kills in the displayed match history</h4>", unsafe_allow_html=True)
        chart_data = df_hist.groupby("Player")["Kills"].sum().reset_index()

        chart = alt.Chart(chart_data).mark_bar(color="#0066CC", size=50).encode(
            x=alt.X("Player:N", sort=None, axis=alt.Axis(labelAngle=-90)),
            y=alt.Y("Kills:Q", title="Total Kills"),
            tooltip=["Player", "Kills"],
        ).properties(
            height=300
        )
        st.altair_chart(chart, use_container_width=True)
