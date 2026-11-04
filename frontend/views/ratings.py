"""Player Ratings & Feedback view: trg_feedback_bi, trg_feedback_ai & fn_avg_rating."""

import streamlit as st
import pandas as pd
from mongo_helper import get_mongo_helper


def render_ratings_view():
    """Render the Ratings and Feedback interface."""
    db_mgr = st.session_state.db_manager
    mongo = get_mongo_helper()
    current_user_id = st.session_state.get("current_user_id", 1)
    users = {u["UserID"]: u for u in db_mgr.get_users()}
    current_user = users.get(current_user_id, {"Username": "player", "Role": "player"})

    st.markdown("""
        <div class="sl-card-title">Player Ratings & Feedback</div>
        <div class="sl-card-subtitle">Submit post-match player reviews and explore community reputation scores.</div>
    """, unsafe_allow_html=True)

    st.info(
        "💡 **Database Trigger Automation:**\n"
        "- `trg_feedback_bi` validates that users cannot review themselves and that score is between 1 and 5.\n"
        "- `trg_feedback_ai` automatically triggers `fn_avg_rating(NEW.ReviewedUserID)` and updates `player_profile.ReputationScore` across all games."
    )

    # Submission Form Card
    with st.container():
        st.markdown('<div class="sl-card">', unsafe_allow_html=True)
        st.markdown("<strong>Submit Player Rating:</strong>", unsafe_allow_html=True)

        r_col1, r_col2, r_col3 = st.columns([4, 4, 2])
        with r_col1:
            all_users = db_mgr.get_users()
            sel_reviewer_id = st.selectbox(
                "Reviewer (Posting as):",
                options=[u["UserID"] for u in all_users],
                format_func=lambda uid: users[uid]["Username"],
                index=[u["UserID"] for u in all_users].index(current_user_id) if current_user_id in [u["UserID"] for u in all_users] else 0,
                key="rating_reviewer_select",
            )
        with r_col2:
            target_candidates = [u["UserID"] for u in all_users if u["UserID"] != sel_reviewer_id]
            sel_target_id = st.selectbox(
                "Reviewed Player:",
                options=target_candidates,
                format_func=lambda uid: users[uid]["Username"],
                key="rating_target_select",
            )
        with r_col3:
            sel_score = st.selectbox(
                "Rating (1 to 5 Stars):",
                options=[5, 4, 3, 2, 1],
                format_func=lambda s: f"{'⭐' * s} ({s}/5)",
                key="rating_score_select",
            )

        if st.button("⭐ Submit Rating (INSERT INTO player_feedback)", key="btn_submit_feedback", use_container_width=True):
            try:
                db_mgr.submit_feedback(
                    reviewer_id=sel_reviewer_id,
                    reviewed_user_id=sel_target_id,
                    score=sel_score,
                )
                rev_name = users[sel_reviewer_id]["Username"]
                target_name = users[sel_target_id]["Username"]

                mongo.log_activity(
                    user_id=sel_reviewer_id,
                    username=rev_name,
                    action="FEEDBACK_SUBMITTED",
                    description=f"Submitted a {sel_score}-star rating for {target_name}.",
                    metadata={"reviewer_id": sel_reviewer_id, "target_user_id": sel_target_id, "score": sel_score},
                )
                st.success(f"Feedback recorded! Trigger `trg_feedback_ai` updated {target_name}'s reputation score.")
                st.rerun()
            except Exception as e:
                st.error(f"Rating submission failed: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

    # Leaderboard & Feedback History
    tab_board, tab_history = st.tabs(["🏆 Reputation Leaderboard", "📜 Recent Feedback History"])

    with tab_board:
        profiles = db_mgr.get_profiles()
        # Group by user for overall reputation
        user_rep_map = {}
        for p in profiles:
            uid = p["UserID"]
            user_rep_map[uid] = max(user_rep_map.get(uid, 0.0), float(p["ReputationScore"]))

        ranked_users = sorted(user_rep_map.items(), key=lambda x: -x[1])
        leaderboard_data = []
        for rank, (uid, score) in enumerate(ranked_users, start=1):
            u = users.get(uid, {"Username": "Unknown", "Role": "player"})
            leaderboard_data.append({
                "Rank": f"#{rank}",
                "Player": u["Username"],
                "Role": u["Role"],
                "Reputation Score": f"⭐ {score:.2f} / 5.00",
            })
        st.dataframe(pd.DataFrame(leaderboard_data), hide_index=True, use_container_width=True)

    with tab_history:
        feedback_list = db_mgr.get_feedback()
        if not feedback_list:
            st.info("No feedback entries recorded yet.")
        else:
            history_data = []
            for f in feedback_list:
                history_data.append({
                    "Feedback ID": f["FeedbackID"],
                    "Reviewer": f["ReviewerName"],
                    "Reviewed Player": f["ReviewedName"],
                    "Score": f"{'⭐' * f['Score']} ({f['Score']})",
                })
            st.dataframe(pd.DataFrame(history_data), hide_index=True, use_container_width=True)
