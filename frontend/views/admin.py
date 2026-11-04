"""Admin View: Security audit logs, role management, nested analytical queries, and demo reset."""

import streamlit as st
import pandas as pd
from mongo_helper import get_mongo_helper


def render_admin_view():
    """Render the Admin & Security Audit view."""
    db_mgr = st.session_state.db_manager
    mongo = get_mongo_helper()
    users = db_mgr.get_users()
    current_user_id = st.session_state.get("current_user_id", 1)
    current_user = next((u for u in users if u["UserID"] == current_user_id), {"Role": "player"})

    st.markdown("""
        <div class="sl-card-title">Platform Administration & Analytics</div>
        <div class="sl-card-subtitle">Inspect trigger-driven security audit logs, manage player roles, execute nested SQL queries, and manage demo resets.</div>
    """, unsafe_allow_html=True)

    tab_audit, tab_roles, tab_queries, tab_reset = st.tabs([
        "🛡️ Security Audit Logs",
        "🔑 Role Management",
        "📊 Analytical Nested Queries",
        "🔄 Database Demo Reset",
    ])

    # 1. Security Audit Logs
    with tab_audit:
        st.info("💡 **Trigger-Driven Auditing:** Events such as `ROLE_CHANGE` and `PASSWORD_CHANGE` are captured by trigger `trg_user_au`. `LOBBY_COMPLETED` is captured by procedure `sp_close_lobby`.")

        col1, col2 = st.columns(2)
        with col1:
            u_opts = [{"UserID": None, "Username": "All Target Users"}] + users
            sel_target = st.selectbox(
                "Filter by Target User:",
                options=u_opts,
                format_func=lambda u: u["Username"],
                key="audit_target_filter",
            )
        with col2:
            st.write("")
            st.write("")
            if st.button("🔄 Refresh Audit Logs", key="btn_refresh_audit", use_container_width=True):
                st.rerun()

        logs = db_mgr.get_audit_logs(target_user=sel_target["UserID"])
        if not logs:
            st.info("No security audit logs found.")
        else:
            df_logs = pd.DataFrame(logs)[["LogID", "Username", "Action_Type", "Log_Timestamp"]]
            df_logs.columns = ["Log ID", "Target User", "Action Description", "Timestamp"]
            st.dataframe(df_logs, hide_index=True, use_container_width=True)

    # 2. Role Management (triggers trg_user_au)
    with tab_roles:
        st.markdown('<div class="sl-card">', unsafe_allow_html=True)
        st.markdown("<strong>Update User Account Role:</strong>", unsafe_allow_html=True)
        st.write("Updating a role executes `UPDATE user_account SET Role = ...` which fires trigger `trg_user_au`.")

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            sel_u_for_role = st.selectbox(
                "Select User:",
                options=users,
                format_func=lambda u: f"{u['Username']} (Current: {u['Role']})",
                key="role_user_select",
            )
        with r_col2:
            new_role = st.selectbox(
                "Assign New Role:",
                options=["player", "moderator", "admin"],
                index=["player", "moderator", "admin"].index(sel_u_for_role["Role"]) if sel_u_for_role["Role"] in ["player", "moderator", "admin"] else 0,
                key="role_new_select",
            )

        if st.button("Apply Role Change", key="btn_apply_role", use_container_width=True):
            try:
                old_role = sel_u_for_role["Role"]
                db_mgr.update_user_role(sel_u_for_role["UserID"], new_role)
                mongo.log_activity(
                    user_id=sel_u_for_role["UserID"],
                    username=sel_u_for_role["Username"],
                    action="ROLE_CHANGED",
                    description=f"Role changed from {old_role} to {new_role}.",
                    metadata={"old_role": old_role, "new_role": new_role},
                )
                st.success(f"Updated {sel_u_for_role['Username']} to {new_role}! Audit log recorded via trg_user_au.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update role: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Analytical Nested Queries
    with tab_queries:
        st.markdown("### Nested Query 1: Players Above Platform Average Reputation")
        st.code("""
SELECT u.UserID, u.Username, gm.Title AS Game, pp.ReputationScore, pp.PlaystyleVector
FROM Player_Profile pp
JOIN User_Account u ON u.UserID = pp.UserID
JOIN Game_Metadata gm ON gm.GameID = pp.GameID
WHERE pp.ReputationScore > (SELECT AVG(ReputationScore) FROM Player_Profile)
ORDER BY pp.ReputationScore DESC, u.Username ASC;
        """, language="sql")

        q1_results = db_mgr.run_nested_query_1()
        if q1_results:
            st.dataframe(pd.DataFrame(q1_results), hide_index=True, use_container_width=True)
        else:
            st.info("No matching records found for Query 1.")

        st.write("---")

        st.markdown("### Nested Query 2: Users in Valorant Lobbies with 5-Star Feedback")
        st.code("""
SELECT u.UserID, u.Username, u.Role, fn_avg_rating(u.UserID) AS Avg_Feedback_Score
FROM User_Account u
WHERE u.UserID IN (
    SELECT lp.UserID FROM Lobby_Participants lp
    JOIN Matchmaking_Lobby ml ON ml.LobbyID = lp.LobbyID
    WHERE ml.GameID = (SELECT GameID FROM Game_Metadata WHERE Title = 'Valorant')
)
AND u.UserID IN (
    SELECT ReviewedUserID FROM Player_Feedback WHERE Score = 5
);
        """, language="sql")

        q2_results = db_mgr.run_nested_query_2()
        if q2_results:
            st.dataframe(pd.DataFrame(q2_results), hide_index=True, use_container_width=True)
        else:
            st.info("No matching records found for Query 2.")

    # 4. Database Demo Reset
    with tab_reset:
        st.markdown('<div class="sl-card">', unsafe_allow_html=True)
        st.markdown("<h4 style='color: #DC2626;'>Reset Database to Seed State</h4>", unsafe_allow_html=True)
        st.write("This utility runs the script `sql/reset_demo.sql` to revert demo changes back to the clean baseline state.")

        st.markdown("""
        **What gets restored:**
        - Removes test participants added during demo (`ParticipantID > 11`)
        - Resets lobby statuses (`Lobby 1 & 4 -> 'open'`, `Lobby 2 -> 'in_progress'`, `Lobby 3 -> 'completed'`)
        - Resets participant `Ready_Status`
        - Reverts modified roles to original baseline
        - Cleans up demo feedback and audit logs
        - Recalculates reputation scores across all profiles using `fn_avg_rating`
        """)

        if st.button("⚠️ Reset Demo Database State", key="btn_reset_db", use_container_width=True):
            try:
                res_msg = db_mgr.reset_demo_state()
                st.success(f"Status: {res_msg}")
                st.rerun()
            except Exception as e:
                st.error(f"Reset failed: {e}")

        st.markdown('</div>', unsafe_allow_html=True)
