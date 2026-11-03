"""SquadLink front end (Streamlit + MySQL).

A login screen opens first. After a successful connection it is replaced by the app.

Every screen calls something that already exists in the database:
  Lobbies      -> fn_lobby_size, sp_close_lobby
  Join a lobby -> sp_join_lobby, triggers trg_part_bi / trg_part_ai
  Find a match -> sp_find_match, fn_playstyle_dist
  Feedback     -> trg_feedback_bi / trg_feedback_ai, fn_avg_rating
  Players      -> player_profile (reputation + telemetry JSON)
  Admin        -> trg_user_au (role change -> security_audit_log)
"""
import html
import os
from datetime import datetime

import mysql.connector
import pandas as pd
import streamlit as st

from mongo_store import (
    get_db, ensure_indexes, record_activity, record_session,
    get_sessions, get_activity, session_summary,
)

LOBBY_CAPACITY = 5  # matches the limit enforced in trg_part_bi
STATUS_LABEL = {
    "open": "Open",
    "full": "Full",
    "in_progress": "In progress",
    "completed": "Completed",
}

st.set_page_config(page_title="SquadLink", layout="wide", initial_sidebar_state="collapsed")

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=DM+Sans:wght@400;500;600&display=swap');
:root{--ink:#231F3D;--muted:#6E6A8A;--line:#DAD5EA;--card:#FFFFFF;--accent:#E23E6B;--open:#12A594;--full:#C97B10;--prog:#5B6CFF;--done:#8A87A3;}
.stApp{font-family:'DM Sans',sans-serif;color:var(--ink);}
.stApp h1,.stApp h2,.stApp h3{font-family:'Bricolage Grotesque',sans-serif;letter-spacing:-0.01em;color:var(--ink);}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none;}
#MainMenu,footer{visibility:hidden;}
[data-testid="stHeader"]{background:transparent;}
.block-container{max-width:1080px;padding-top:2.2rem;padding-bottom:4rem;}
.brand{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.7rem;letter-spacing:-0.02em;display:flex;align-items:center;}
.brand.big{font-size:3.2rem;justify-content:center;}
.mark{display:inline-flex;gap:4px;margin-right:.7rem;}
.mark i{width:10px;height:10px;border-radius:50%;background:var(--accent);display:block;box-sizing:border-box;}
.mark i:last-child{background:transparent;border:2px solid var(--accent);}
.brand.big .mark i{width:14px;height:14px;}
.hero{text-align:center;margin:2.2rem 0 1.6rem;}
.hero p{color:var(--muted);font-size:1.12rem;margin:.5rem 0 0;}
.who{color:var(--muted);font-size:.85rem;text-align:right;margin-bottom:.3rem;}
[data-testid="stForm"]{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:1.5rem 1.6rem 1.2rem;box-shadow:0 14px 34px -20px rgba(35,31,61,.45);}
.stButton>button,.stFormSubmitButton>button{background:var(--accent);color:#fff;border:0;border-radius:10px;font-weight:600;padding:.5rem 1.2rem;}
.stButton>button:hover,.stFormSubmitButton>button:hover{background:#C92F5A;color:#fff;}
.stButton>button:disabled{background:#CFCBDD;color:#fff;}
.st-key-logout button{background:transparent;color:var(--ink);border:1px solid var(--line);float:right;}
.st-key-logout button:hover{background:#fff;color:var(--accent);border-color:var(--accent);}
button[data-baseweb="tab"]{font-weight:600;color:var(--muted);}
button[data-baseweb="tab"][aria-selected="true"]{color:var(--accent);}
[data-baseweb="tab-highlight"]{background:var(--accent);}
[data-baseweb="input"],[data-baseweb="select"]>div{border-radius:10px;}
[data-testid="stAlert"]{border-radius:12px;}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:.8rem 1rem;}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:.4rem 0 1.4rem;}
.stat{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:.9rem 1.1rem;}
.stat b{display:block;font-family:'Bricolage Grotesque',sans-serif;font-size:2rem;line-height:1.1;}
.stat span{color:var(--muted);font-size:.85rem;}
.lgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px;margin:.2rem 0 1.4rem;}
.lcard{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--c);border-radius:14px;padding:1rem 1.1rem;}
.lcard.s-open{--c:var(--open);}
.lcard.s-full{--c:var(--full);}
.lcard.s-in_progress{--c:var(--prog);}
.lcard.s-completed{--c:var(--done);}
.lhead{display:flex;justify-content:space-between;align-items:center;}
.lid{color:var(--muted);font-size:.85rem;font-weight:600;}
.pill{font-size:.75rem;font-weight:600;padding:.15rem .65rem;border-radius:99px;background:var(--c);color:#fff;}
.lgame{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:1.3rem;margin:.55rem 0 .1rem;}
.lmeta{color:var(--muted);font-size:.85rem;}
.dots{display:flex;gap:6px;margin:.85rem 0 .35rem;}
.dot{width:14px;height:14px;border-radius:50%;border:2px solid var(--c);box-sizing:border-box;}
.dot.on{background:var(--c);}
.lcount{font-size:.82rem;color:var(--muted);}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:.4rem 0 1rem;}
.chip{background:var(--card);border:1px solid var(--line);border-radius:99px;padding:.35rem .85rem;font-size:.9rem;}
.chip em{color:var(--muted);font-style:normal;margin-left:.5rem;}
.chip.ready{border-color:var(--open);box-shadow:inset 0 0 0 1px var(--open);}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

BRAND_MARK = '<span class="mark"><i></i><i></i><i></i><i></i><i></i></span>'


def esc(value):
    return html.escape("" if value is None else str(value))


# ---------------------------------------------------------------- database helpers
def get_conn():
    cfg = st.session_state["cfg"]
    return mysql.connector.connect(
        host=cfg["host"], port=cfg["port"], user=cfg["user"],
        password=cfg["password"], database=cfg["database"], autocommit=True,
    )


def query(sql, params=None):
    """Run a SELECT and return a DataFrame."""
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return pd.DataFrame(cur.fetchall())
    finally:
        conn.close()


def execute(sql, params=None):
    """Run an INSERT/UPDATE/DELETE and return the affected row count."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        return cur.rowcount
    finally:
        conn.close()


def call(proc, args):
    """Call a stored procedure; return its result sets as DataFrames."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.callproc(proc, args)
        return [
            pd.DataFrame(res.fetchall(), columns=res.column_names)
            for res in cur.stored_results()
        ]
    finally:
        conn.close()


def create_lobby(host_id, game_id, role):
    """Insert a lobby and its host as the first player, all or nothing."""
    conn = get_conn()
    try:
        conn.autocommit = False
        cur = conn.cursor()
        cur.execute("INSERT INTO matchmaking_lobby (HostID, GameID) VALUES (%s, %s)", (host_id, game_id))
        lobby_id = cur.lastrowid
        cur.execute(
            "INSERT INTO lobby_participants (LobbyID, UserID, Squad_Role) VALUES (%s, %s, %s)",
            (lobby_id, host_id, role),
        )
        conn.commit()
        return lobby_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def live(fn, seconds=5):
    """Re-run fn on a timer so its output stays current (needs a Streamlit with st.fragment)."""
    fragment = getattr(st, "fragment", None)
    return fragment(run_every=seconds)(fn) if fragment else fn


def explain(err):
    """Turn a MySQL error into a sentence the user can act on."""
    errno = getattr(err, "errno", None)
    if errno == 1062:
        return "That player is already in this lobby."
    if errno == 3819:
        return "The database rejected that value (a table rule was broken)."
    if errno == 1045:
        return "Wrong user or password."
    if errno == 2003:
        return "Can't reach the MySQL server. Check that it is running and the host and port are right."
    if errno == 1049:
        return "That database doesn't exist on this server."
    return getattr(err, "msg", None) or str(err)


def show(df, **kwargs):
    """Full-width table without the index (works across Streamlit versions)."""
    try:
        st.dataframe(df, hide_index=True, width="stretch", **kwargs)
    except Exception:
        st.dataframe(df, hide_index=True, use_container_width=True, **kwargs)


def mongo_status():
    """Connect lazily; MongoDB being unavailable must not break MySQL features."""
    try:
        db = get_db()
        ensure_indexes(db)
        return db, None
    except Exception as err:
        return None, str(err)


def log_activity(user_id, username, action, description, metadata=None):
    """Best-effort activity logging; do not undo a successful MySQL operation."""
    try:
        record_activity(user_id, username, action, description, metadata)
        return None
    except Exception as err:
        return str(err)


def mongo_docs_frame(docs):
    """Convert MongoDB documents to a display-friendly DataFrame."""
    rows = []
    for doc in docs:
        row = dict(doc)
        row["Mongo ID"] = str(row.pop("_id", ""))
        for key in ("created_at", "played_at"):
            if key in row and row[key] is not None:
                row[key] = row[key].astimezone().strftime("%Y-%m-%d %H:%M:%S") if row[key].tzinfo else row[key].strftime("%Y-%m-%d %H:%M:%S")
        rows.append(row)
    return pd.DataFrame(rows)


def floatify(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = df[c].astype(float)
    return df


# ---------------------------------------------------------------- login
def login_view():
    st.markdown(
        f'<div class="hero"><div class="brand big">{BRAND_MARK}SquadLink</div>'
        "<p>Find a squad that plays like you.</p></div>",
        unsafe_allow_html=True,
    )
    _, middle, _ = st.columns([1, 1.5, 1])
    with middle:
        with st.form("login"):
            st.subheader("Connect to your database")
            user = st.text_input("MySQL user", os.getenv("SQUADLINK_USER", "root"))
            password = st.text_input("Password", os.getenv("SQUADLINK_PASSWORD", ""), type="password")
            with st.expander("Server settings"):
                host = st.text_input("Host", os.getenv("SQUADLINK_HOST", "localhost"))
                port = st.number_input("Port", value=int(os.getenv("SQUADLINK_PORT", "3306")), step=1)
                database = st.text_input("Database", os.getenv("SQUADLINK_DB", "squadlink"))
            go = st.form_submit_button("Connect")

        if go:
            cfg = {
                "host": host.strip(), "port": int(port), "user": user.strip(),
                "password": password, "database": database.strip(),
            }
            error = None
            with st.spinner("Connecting..."):
                try:
                    mysql.connector.connect(**cfg).close()
                except mysql.connector.Error as e:
                    error = explain(e)
            if error:
                st.error(f"Could not connect. {error}")
            else:
                st.session_state["cfg"] = cfg
                st.rerun()


if "cfg" not in st.session_state:
    login_view()
    st.stop()

cfg = st.session_state["cfg"]

# ---------------------------------------------------------------- top bar
bar_left, bar_right = st.columns([5, 2])
bar_left.markdown(f'<div class="brand">{BRAND_MARK}SquadLink</div>', unsafe_allow_html=True)
with bar_right:
    st.markdown(
        f'<div class="who">{esc(cfg["user"])}@{esc(cfg["host"])} / {esc(cfg["database"])}</div>',
        unsafe_allow_html=True,
    )
    if st.button("Log out", key="logout"):
        del st.session_state["cfg"]
        st.rerun()

try:
    query("SELECT 1")
except mysql.connector.Error as e:
    st.error(f"Lost the database connection. {explain(e)}")
    st.info("Use Log out and sign in again.")
    st.stop()


# ---------------------------------------------------------------- lookups
def users():
    return query("SELECT UserID, Username FROM user_account ORDER BY Username")


def lobbies():
    return query(
        """
        SELECT l.LobbyID, g.Title AS Game, h.Username AS Host, l.Status,
               fn_lobby_size(l.LobbyID) AS Players
        FROM matchmaking_lobby l
        JOIN game_metadata g ON g.GameID = l.GameID
        JOIN user_account h ON h.UserID = l.HostID
        ORDER BY l.LobbyID
        """
    )


def lobby_label(row):
    return f"Lobby {row.LobbyID} - {row.Game} - {row.Status} ({int(row.Players)}/{LOBBY_CAPACITY})"


def participants(lobby_id):
    return query(
        """
        SELECT u.Username AS Player, p.Squad_Role AS Role,
               IF(p.Ready_Status, 'Ready', 'Not ready') AS Ready
        FROM lobby_participants p
        JOIN user_account u ON u.UserID = p.UserID
        WHERE p.LobbyID = %s
        ORDER BY p.ParticipantID
        """,
        (lobby_id,),
    )


def reputation_of(user_id):
    df = query("SELECT ReputationScore FROM player_profile WHERE UserID = %s LIMIT 1", (user_id,))
    return float(df.iloc[0, 0]) if not df.empty else None


# ---------------------------------------------------------------- html pieces
def lobby_card(r):
    status = r.Status
    players = int(r.Players)
    dots = "".join(
        f'<span class="dot{" on" if i < players else ""}"></span>' for i in range(LOBBY_CAPACITY)
    )
    return (
        f'<div class="lcard s-{esc(status)}">'
        f'<div class="lhead"><span class="lid">Lobby {int(r.LobbyID)}</span>'
        f'<span class="pill">{esc(STATUS_LABEL.get(status, status))}</span></div>'
        f'<div class="lgame">{esc(r.Game)}</div>'
        f'<div class="lmeta">Hosted by {esc(r.Host)}</div>'
        f'<div class="dots">{dots}</div>'
        f'<div class="lcount">{players} of {LOBBY_CAPACITY} players</div></div>'
    )


def chips(df):
    if df.empty:
        return '<div class="lmeta">No players in this lobby yet.</div>'
    out = []
    for r in df.itertuples():
        cls = "chip ready" if r.Ready == "Ready" else "chip"
        out.append(f'<span class="{cls}"><b>{esc(r.Player)}</b><em>{esc(r.Role or "no role")}</em></span>')
    return '<div class="chips">' + "".join(out) + "</div>"


# ---------------------------------------------------------------- tabs
tab_lobbies, tab_join, tab_match, tab_feedback, tab_players, tab_telemetry, tab_activity, tab_admin = st.tabs(
    ["Lobbies", "Join a lobby", "Find a match", "Ratings", "Players", "Gameplay Telemetry", "Activity Feed", "Admin"]
)

# ---------------------------------------------------------------- Lobbies
with tab_lobbies:
    with st.expander("Create a lobby"):
        games_df = query("SELECT GameID, Title FROM game_metadata ORDER BY Title")
        roles_df = query(
            "SELECT DISTINCT Squad_Role FROM lobby_participants WHERE Squad_Role IS NOT NULL ORDER BY Squad_Role"
        )
        hosts_df = users()
        if games_df.empty or roles_df.empty or hosts_df.empty:
            st.warning("The database needs at least one game, one user and one squad role.")
        else:
            host_opts = {r.Username: int(r.UserID) for r in hosts_df.itertuples()}
            game_opts = {r.Title: int(r.GameID) for r in games_df.itertuples()}
            with st.form("create_lobby_form"):
                col_a, col_b, col_c = st.columns(3)
                host = col_a.selectbox("Host", list(host_opts))
                game = col_b.selectbox("Game", list(game_opts))
                host_role = col_c.selectbox("Host's squad role", roles_df["Squad_Role"].tolist())
                go = st.form_submit_button("Create lobby")
            if go:
                try:
                    new_id = create_lobby(host_opts[host], game_opts[game], host_role)
                    mongo_warning = log_activity(host_opts[host], host, "LOBBY_CREATED", f"Created lobby {new_id} for {game}.", {"lobby_id": new_id, "game_id": game_opts[game]})
                    st.success(f"Lobby {new_id} created. {host} is hosting and has joined it.")
                    if mongo_warning:
                        st.warning(f"Lobby was created in MySQL, but its MongoDB activity entry was not saved: {mongo_warning}")
                except mysql.connector.Error as e:
                    st.error(explain(e))

    def lobby_board():
        lob = lobbies()
        open_count = int((lob["Status"] == "open").sum()) if not lob.empty else 0
        st.markdown(
            '<div class="stats">'
            f'<div class="stat"><b>{len(lob)}</b><span>Lobbies</span></div>'
            f'<div class="stat"><b>{open_count}</b><span>Open to join</span></div>'
            f'<div class="stat"><b>{len(users())}</b><span>Registered players</span></div>'
            "</div>",
            unsafe_allow_html=True,
        )

        if lob.empty:
            st.info("No lobbies yet. Create the first one above.")
            return

        st.markdown(
            '<div class="lgrid">' + "".join(lobby_card(r) for r in lob.itertuples()) + "</div>",
            unsafe_allow_html=True,
        )

        ids = [int(r.LobbyID) for r in lob.itertuples()]
        labels = {int(r.LobbyID): lobby_label(r) for r in lob.itertuples()}
        lobby_id = st.selectbox("See who is in", ids, format_func=lambda i: labels[i], key="lob_pick")
        st.markdown(chips(participants(lobby_id)), unsafe_allow_html=True)
        st.caption("A green outline means the player is ready.")

        with st.expander("Close this lobby"):
            st.write(
                "Marks the lobby completed and adds a LOBBY_COMPLETED entry to the audit log. "
                "This is saved permanently."
            )
            sure = st.checkbox("I want to close this lobby", key="close_sure")
            if st.button("Close lobby", disabled=not sure, key="close_btn"):
                try:
                    call("sp_close_lobby", (lobby_id,))
                    host_row = query("SELECT u.UserID, u.Username FROM matchmaking_lobby l JOIN user_account u ON u.UserID=l.HostID WHERE l.LobbyID=%s", (lobby_id,))
                    if not host_row.empty:
                        log_activity(int(host_row.iloc[0]["UserID"]), host_row.iloc[0]["Username"], "LOBBY_COMPLETED", f"Completed lobby {lobby_id}.", {"lobby_id": int(lobby_id)})
                    st.success(f"Lobby {lobby_id} closed.")
                    st.rerun()
                except mysql.connector.Error as e:
                    st.error(explain(e))

        st.caption(f"Refreshes every 5 seconds. Last updated {datetime.now().strftime('%H:%M:%S')}.")

    live(lobby_board)()

# ---------------------------------------------------------------- Join
with tab_join:
    st.subheader("Join a lobby")
    st.caption(
        "Pick any lobby, including full or closed ones. The database decides whether the join is allowed."
    )
    u = users()
    lob = lobbies()
    roles = query(
        "SELECT DISTINCT Squad_Role FROM lobby_participants WHERE Squad_Role IS NOT NULL ORDER BY Squad_Role"
    )

    if u.empty or lob.empty or roles.empty:
        st.warning("The database needs at least one user, one lobby and one role.")
    else:
        user_opts = {r.Username: int(r.UserID) for r in u.itertuples()}
        lob_labels = {int(r.LobbyID): lobby_label(r) for r in lob.itertuples()}
        with st.form("join_form"):
            who = st.selectbox("Player", list(user_opts))
            lobby_id = st.selectbox("Lobby", list(lob_labels), format_func=lambda i: lob_labels[i])
            role = st.selectbox("Squad role", roles["Squad_Role"].tolist())
            go = st.form_submit_button("Join lobby")
        if go:
            try:
                frames = call("sp_join_lobby", (lobby_id, user_opts[who], role))
                msg = frames[0].iloc[0, 0] if frames and not frames[0].empty else "Joined."
                log_activity(user_opts[who], who, "LOBBY_JOINED", f"Joined lobby {lobby_id}.", {"lobby_id": int(lobby_id), "role": role})
                st.success(msg)
            except mysql.connector.Error as e:
                st.error(explain(e))
            status = query(
                "SELECT Status, fn_lobby_size(LobbyID) AS Players FROM matchmaking_lobby WHERE LobbyID = %s",
                (lobby_id,),
            )
            if not status.empty:
                st.write(
                    f"Lobby {lobby_id} is now **{STATUS_LABEL.get(status.iloc[0]['Status'], status.iloc[0]['Status'])}** "
                    f"with {int(status.iloc[0]['Players'])} of {LOBBY_CAPACITY} players."
                )
            st.markdown(chips(participants(lobby_id)), unsafe_allow_html=True)

# ---------------------------------------------------------------- Match
with tab_match:
    st.subheader("Find players for a lobby")
    st.caption("Players above your minimum reputation, closest playstyle first.")
    lob = lobbies()
    if lob.empty:
        st.warning("No lobbies found.")
    else:
        lob_labels = {int(r.LobbyID): lobby_label(r) for r in lob.itertuples()}
        with st.form("match_form"):
            match_lobby = st.selectbox(
                "Lobby", list(lob_labels), format_func=lambda i: lob_labels[i], key="match_lobby"
            )
            min_rep = st.slider("Minimum reputation", 0.0, 5.0, 3.0, 0.1)
            go = st.form_submit_button("Find players")
        if go:
            try:
                frames = call("sp_find_match", (match_lobby, round(min_rep, 2)))
                df = frames[0] if frames else pd.DataFrame()
                if df.empty:
                    st.info("No players meet that reputation. Lower the minimum and try again.")
                else:
                    df = floatify(df, ["ReputationScore", "playstyle_distance"])
                    show(
                        df,
                        column_config={
                            "ReputationScore": st.column_config.ProgressColumn(
                                "Reputation", min_value=0.0, max_value=5.0, format="%.2f"
                            ),
                            "playstyle_distance": st.column_config.NumberColumn(
                                "Playstyle distance", format="%.3f"
                            ),
                        },
                    )
                    if {"Username", "playstyle_distance"} <= set(df.columns):
                        st.caption("Playstyle distance. Shorter bars are closer matches.")
                        st.bar_chart(df.set_index("Username")["playstyle_distance"], color="#E23E6B")
            except mysql.connector.Error as e:
                st.error(explain(e))

    st.divider()
    st.subheader("Compare two profiles")
    profiles = query(
        """
        SELECT p.ProfileID, u.Username, g.Title
        FROM player_profile p
        JOIN user_account u ON u.UserID = p.UserID
        JOIN game_metadata g ON g.GameID = p.GameID
        ORDER BY u.Username, g.Title
        """
    )
    if len(profiles) >= 2:
        prof_opts = {f"{r.Username} ({r.Title})": int(r.ProfileID) for r in profiles.itertuples()}
        names = list(prof_opts)
        col_a, col_b = st.columns(2)
        a = col_a.selectbox("First profile", names, index=0, key="cmp_a")
        b = col_b.selectbox("Second profile", names, index=1, key="cmp_b")
        dist = query(
            """
            SELECT fn_playstyle_dist(a.PlaystyleVector, b.PlaystyleVector) AS d
            FROM player_profile a, player_profile b
            WHERE a.ProfileID = %s AND b.ProfileID = %s
            """,
            (prof_opts[a], prof_opts[b]),
        )
        if not dist.empty and dist.iloc[0, 0] is not None:
            st.metric("Playstyle distance", f"{float(dist.iloc[0, 0]):.3f}")
            st.caption("0 means identical playstyles.")

# ---------------------------------------------------------------- Feedback
with tab_feedback:
    st.subheader("Rate a teammate")
    st.caption("A new score recalculates the rated player's reputation automatically.")
    u = users()
    if len(u) < 2:
        st.warning("The database needs at least two users.")
    else:
        user_opts = {r.Username: int(r.UserID) for r in u.itertuples()}
        names = list(user_opts)
        with st.form("fb_form"):
            col_a, col_b = st.columns(2)
            reviewer = col_a.selectbox("Your account", names, index=0)
            reviewed = col_b.selectbox("Player you are rating", names, index=1)
            score = st.slider("Score", 1, 5, 4)
            go = st.form_submit_button("Submit rating")
        if go:
            before = reputation_of(user_opts[reviewed])
            try:
                execute(
                    "INSERT INTO player_feedback (ReviewerID, ReviewedUserID, Score) VALUES (%s, %s, %s)",
                    (user_opts[reviewer], user_opts[reviewed], score),
                )
                after = reputation_of(user_opts[reviewed])
                log_activity(user_opts[reviewer], reviewer, "PLAYER_RATED", f"Rated {reviewed} {score}/5.", {"reviewed_user_id": user_opts[reviewed], "score": int(score)})
                st.success("Rating saved.")
                if before is not None and after is not None:
                    st.metric(f"{reviewed}'s reputation", f"{after:.2f}", f"{after - before:+.2f}")
            except mysql.connector.Error as e:
                st.error(explain(e))

    def ratings_board():
        st.subheader("Player ratings")
        board = query(
            """
            SELECT u.Username, ROUND(AVG(f.Score), 2) AS AvgRating, COUNT(f.FeedbackID) AS Ratings
            FROM user_account u
            LEFT JOIN player_feedback f ON f.ReviewedUserID = u.UserID
            GROUP BY u.UserID, u.Username
            ORDER BY AvgRating DESC, Ratings DESC, u.Username
            """
        )
        board = floatify(board, ["AvgRating"])
        show(
            board,
            column_config={
                "AvgRating": st.column_config.ProgressColumn(
                    "Average rating", min_value=0.0, max_value=5.0, format="%.2f"
                ),
                "Ratings": st.column_config.NumberColumn("Ratings received", format="%d"),
            },
        )

        st.subheader("Latest ratings")
        show(
            query(
                """
                SELECT f.FeedbackID, r.Username AS Reviewer, t.Username AS Rated, f.Score
                FROM player_feedback f
                JOIN user_account r ON r.UserID = f.ReviewerID
                JOIN user_account t ON t.UserID = f.ReviewedUserID
                ORDER BY f.FeedbackID DESC
                LIMIT 10
                """
            )
        )
        st.caption(f"Refreshes every 5 seconds. Last updated {datetime.now().strftime('%H:%M:%S')}.")

    # Re-run just this block every 5 seconds so new ratings appear without a page reload.
    # Older Streamlit versions have no st.fragment, so the board then updates on each action.
    _fragment = getattr(st, "fragment", None)
    if _fragment is not None:
        ratings_board = _fragment(run_every=5)(ratings_board)
    ratings_board()

# ---------------------------------------------------------------- Players
with tab_players:
    st.subheader("Player reputation")
    games = query("SELECT Title FROM game_metadata ORDER BY Title")["Title"].tolist()
    game = st.selectbox("Game", ["All games"] + games, key="players_game")
    sql = """
        SELECT u.Username, g.Title AS Game, p.ReputationScore AS Reputation,
               CAST(JSON_UNQUOTE(JSON_EXTRACT(p.Telemetry_Data, '$.kd')) AS DECIMAL(5,2)) AS KD,
               CAST(JSON_UNQUOTE(JSON_EXTRACT(p.Telemetry_Data, '$.matches')) AS UNSIGNED) AS Matches,
               CAST(JSON_UNQUOTE(JSON_EXTRACT(p.Telemetry_Data, '$.win_rate')) AS DECIMAL(4,2)) AS WinRate
        FROM player_profile p
        JOIN user_account u ON u.UserID = p.UserID
        JOIN game_metadata g ON g.GameID = p.GameID
    """
    params = ()
    if game != "All games":
        sql += " WHERE g.Title = %s"
        params = (game,)
    sql += " ORDER BY p.ReputationScore DESC, u.Username"
    players = floatify(query(sql, params), ["Reputation", "KD", "WinRate"])
    show(
        players,
        column_config={
            "Reputation": st.column_config.ProgressColumn(
                "Reputation", min_value=0.0, max_value=5.0, format="%.2f"
            ),
            "KD": st.column_config.NumberColumn("K/D", format="%.2f"),
            "WinRate": st.column_config.NumberColumn("Win rate", format="%.2f"),
        },
    )

# ---------------------------------------------------------------- Gameplay Telemetry (MongoDB)
with tab_telemetry:
    st.subheader("Gameplay telemetry")
    st.caption("Record flexible per-match statistics in MongoDB. MySQL continues to own player and game identities.")
    db, mongo_error = mongo_status()
    if mongo_error:
        st.error(f"MongoDB is unavailable: {mongo_error}")
        st.info("Start MongoDB and check SQUADLINK_MONGO_URI. Your existing MySQL features remain available.")
    else:
        u = users()
        g = query("SELECT GameID, Title FROM game_metadata ORDER BY Title")
        lob = query("SELECT LobbyID FROM matchmaking_lobby ORDER BY LobbyID DESC")
        if u.empty or g.empty:
            st.warning("Add at least one MySQL user and one game before recording telemetry.")
        else:
            user_opts = {r.Username: int(r.UserID) for r in u.itertuples()}
            game_opts = {r.Title: int(r.GameID) for r in g.itertuples()}
            lobby_values = [None] + [int(x) for x in lob["LobbyID"].tolist()]
            with st.form("telemetry_form"):
                st.markdown("**Match details**")
                c1, c2, c3 = st.columns(3)
                player_name = c1.selectbox("Player", list(user_opts), key="telemetry_player")
                game_name = c2.selectbox("Game", list(game_opts), key="telemetry_game")
                lobby_id = c3.selectbox("Lobby (optional)", lobby_values, format_func=lambda x: "No lobby" if x is None else f"Lobby {x}")
                c1, c2, c3 = st.columns(3)
                duration = c1.number_input("Duration (minutes)", min_value=1, max_value=600, value=30)
                result = c2.selectbox("Result", ["Win", "Loss", "Draw"])
                event_type = c3.selectbox("Notable event", ["kill", "assist", "objective", "death", "teamwork", "other"])
                st.markdown("**Performance statistics**")
                c1, c2, c3, c4 = st.columns(4)
                kills = c1.number_input("Kills", min_value=0, max_value=500, value=10)
                deaths = c2.number_input("Deaths", min_value=0, max_value=500, value=4)
                assists = c3.number_input("Assists", min_value=0, max_value=500, value=6)
                accuracy = c4.number_input("Accuracy (%)", min_value=0.0, max_value=100.0, value=72.5, step=0.5)
                damage = st.number_input("Damage dealt", min_value=0, max_value=1000000, value=2500)
                st.markdown("**Playstyle indicators (0–1)**")
                c1, c2, c3 = st.columns(3)
                aggression = c1.slider("Aggression", 0.0, 1.0, 0.5, 0.05)
                teamwork = c2.slider("Teamwork", 0.0, 1.0, 0.7, 0.05)
                objective_focus = c3.slider("Objective focus", 0.0, 1.0, 0.6, 0.05)
                event_note = st.text_input("Event description", value="Played a match")
                submitted = st.form_submit_button("Save match to MongoDB")
            if submitted:
                doc = {
                    "user_id": user_opts[player_name], "username": player_name,
                    "game_id": game_opts[game_name], "game_title": game_name,
                    "lobby_id": int(lobby_id) if lobby_id is not None else None,
                    "duration_minutes": int(duration),
                    "result": {"outcome": result.lower(), "win": result == "Win"},
                    "performance": {"kills": int(kills), "deaths": int(deaths), "assists": int(assists), "accuracy": float(accuracy), "damage_dealt": int(damage)},
                    "playstyle": {"aggression": float(aggression), "teamwork": float(teamwork), "objective_focus": float(objective_focus)},
                    "events": [{"type": event_type, "description": event_note.strip(), "occurred_at": datetime.now()}],
                    "source": "streamlit_manual_entry",
                }
                try:
                    inserted_id = record_session(doc)
                    log_activity(user_opts[player_name], player_name, "MATCH_RECORDED", f"Recorded a {result.lower()} in {game_name}.", {"session_id": str(inserted_id), "game_id": game_opts[game_name]})
                    st.success(f"Match telemetry saved. Session ID: {inserted_id}")
                except Exception as err:
                    st.error(f"Could not save match telemetry: {err}")

        st.divider()
        st.subheader("Player performance summary")
        if not u.empty and not g.empty:
            c1, c2 = st.columns(2)
            summary_player = c1.selectbox("Player summary", ["All players"] + list(user_opts), key="summary_player")
            summary_game = c2.selectbox("Game summary", ["All games"] + list(game_opts), key="summary_game")
            summary = session_summary(None if summary_player == "All players" else user_opts[summary_player], None if summary_game == "All games" else game_opts[summary_game])
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Matches", summary["matches"])
            m2.metric("Wins", summary["wins"])
            m3.metric("K/D", f"{summary['kd']:.2f}")
            m4.metric("Win rate", f"{summary['win_rate']:.1f}%")
            m5.metric("Avg. accuracy", f"{summary['avg_accuracy']:.1f}%")
            st.caption(f"Total recorded playtime: {summary['total_minutes']} minutes. Statistics are calculated using a MongoDB aggregation pipeline.")

            session_player = st.selectbox("Match history player", ["All players"] + list(user_opts), key="history_player")
            session_game = st.selectbox("Match history game", ["All games"] + list(game_opts), key="history_game")
            docs = get_sessions(None if session_player == "All players" else user_opts[session_player], None if session_game == "All games" else game_opts[session_game], 100)
            if docs:
                history_rows = []
                for d in docs:
                    perf = d.get("performance", {})
                    history_rows.append({"Date": d.get("played_at"), "Player": d.get("username"), "Game": d.get("game_title"), "Result": d.get("result", {}).get("outcome", "-"), "Kills": perf.get("kills", 0), "Deaths": perf.get("deaths", 0), "Assists": perf.get("assists", 0), "Accuracy %": perf.get("accuracy", 0), "Duration min": d.get("duration_minutes", 0)})
                history = pd.DataFrame(history_rows)
                history["Date"] = pd.to_datetime(history["Date"], utc=True).dt.tz_convert(None)
                show(history)
                chart_data = history.groupby("Player")["Kills"].sum().sort_values(ascending=False)
                if not chart_data.empty:
                    st.caption("Total kills in the displayed match history")
                    st.bar_chart(chart_data)
            else:
                st.info("No match sessions found. Save a match above to populate this section.")

# ---------------------------------------------------------------- Player Activity Feed (MongoDB)
with tab_activity:
    st.subheader("Player activity feed")
    st.caption("A MongoDB-backed timeline of important actions across SquadLink.")
    db, mongo_error = mongo_status()
    if mongo_error:
        st.error(f"MongoDB is unavailable: {mongo_error}")
    else:
        u = users()
        user_map = {r.Username: int(r.UserID) for r in u.itertuples()} if not u.empty else {}
        c1, c2 = st.columns(2)
        selected_user = c1.selectbox("Player", ["Everyone"] + list(user_map), key="activity_player")
        action_filter = c2.selectbox("Activity type", ["All actions", "LOBBY_CREATED", "LOBBY_JOINED", "LOBBY_COMPLETED", "PLAYER_RATED", "MATCH_RECORDED", "ROLE_CHANGED"], key="activity_action")
        activities = get_activity(None if selected_user == "Everyone" else user_map[selected_user], action_filter, 100)
        if activities:
            activity_rows = []
            for item in activities:
                activity_rows.append({"Time": item.get("created_at"), "Player": item.get("username"), "Action": item.get("action"), "Description": item.get("description")})
            activity_df = pd.DataFrame(activity_rows)
            activity_df["Time"] = pd.to_datetime(activity_df["Time"], utc=True).dt.tz_convert(None)
            show(activity_df)
            st.caption(f"Showing {len(activity_df)} most recent matching activities (maximum 100).")
        else:
            st.info("No activity has been recorded yet. Create/join a lobby, submit a rating or record match telemetry.")

# ---------------------------------------------------------------- Admin
with tab_admin:
    st.subheader("Change a user's role")
    st.caption("Role changes are written to the security audit log by a trigger.")
    u = users()
    if not u.empty:
        user_opts = {r.Username: int(r.UserID) for r in u.itertuples()}
        with st.form("role_form"):
            col_a, col_b = st.columns(2)
            who = col_a.selectbox("User", list(user_opts), key="role_user")
            new_role = col_b.selectbox("New role", ["player", "moderator", "admin"])
            go = st.form_submit_button("Change role")
        if go:
            try:
                execute("UPDATE user_account SET Role = %s WHERE UserID = %s", (new_role, user_opts[who]))
                log_activity(user_opts[who], who, "ROLE_CHANGED", f"Account role changed to {new_role}.", {"new_role": new_role})
                st.success(f"{who} is now {new_role}.")
            except mysql.connector.Error as e:
                st.error(explain(e))

    def audit_log():
        st.subheader("Security audit log")

        logs = query(
            """
            SELECT l.LogID,
                u.Username AS Account,
                l.Action_Type AS Action,
                l.Log_Timestamp AS Time
            FROM security_audit_log l
            JOIN user_account u ON u.UserID = l.TargetUserID
            ORDER BY l.LogID DESC
            LIMIT 15
            """
        )

        show(logs)

        st.caption(
            f"Refreshes every 5 seconds. "
            f"Last updated {datetime.now().strftime('%H:%M:%S')}."
        )


    live(audit_log)()