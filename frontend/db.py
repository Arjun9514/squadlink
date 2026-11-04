"""SquadLink Database Management Layer.

Supports dual modes:
1. Live MySQL Database (executing real tables, procedures, triggers, functions)
2. Standalone Demo Mode (in-memory database reproducing exact DML seed data,
   procedures, triggers, and Euclidean vector distance calculations)
"""

import json
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    mysql = None
    MySQLError = Exception


# ==============================================================================
# Seed Data Definitions (from sql/DML.sql)
# ==============================================================================

SEED_USERS = [
    {"UserID": 1, "Username": "rahul", "PasswordHash": "f0238f6dc401055f97761133158d1eca21d14fb453bf5b8d90efd7f39373743f", "Role": "player"},
    {"UserID": 2, "Username": "arjun", "PasswordHash": "26a95b1e69c92f1cfb0381fd379d80526ecd9c368d3a7baa9be6c24b61a25e71", "Role": "player"},
    {"UserID": 3, "Username": "priya", "PasswordHash": "bdcd8f14a7b9cee0c191985e3e1b7d9e47cbdfa92b2df68b91cbd7828a21e35b", "Role": "moderator"},
    {"UserID": 4, "Username": "karthik", "PasswordHash": "9e53246d7a8e55d7583534e123bbf30837f2bf85b8394a05f1c368e64b5e6f6a", "Role": "player"},
    {"UserID": 5, "Username": "sneha", "PasswordHash": "1a97f616bc859e058a244fb7a75abe1e8510e913cc72479e67962281343df008", "Role": "player"},
    {"UserID": 6, "Username": "vikram", "PasswordHash": "37185d1e31a5c2cc4af7ad13021b03588ae52971b870a36adb1ce925a49d0e45", "Role": "player"},
    {"UserID": 7, "Username": "ananya", "PasswordHash": "eaf2b4285d739aa8830455af01f3299fbc4eb5e03301411fe2a3b1962b342d9c", "Role": "player"},
    {"UserID": 8, "Username": "rohan", "PasswordHash": "a4232054c2fc1ff21e8d911d0669df5e636562b9da8c14ecaa8fddc0f92e070c", "Role": "player"},
    {"UserID": 9, "Username": "meera", "PasswordHash": "ccf694e32b137ad43360c322f40c79421925260d6ec9e871998670083bd9beab", "Role": "moderator"},
    {"UserID": 10, "Username": "admin1", "PasswordHash": "7676aaafb027c825bd9abab78b234070e702752f625b752e55e55b48e607e358", "Role": "admin"},
]

SEED_GAMES = [
    {"GameID": 1, "Title": "Valorant", "Genre": "Tactical Shooter"},
    {"GameID": 2, "Title": "Apex Legends", "Genre": "Battle Royale"},
    {"GameID": 3, "Title": "Dota 2", "Genre": "MOBA"},
    {"GameID": 4, "Title": "Rocket League", "Genre": "Sports"},
    {"GameID": 5, "Title": "Overwatch 2", "Genre": "FPS"},
]

SEED_LOBBIES = [
    {"LobbyID": 1, "HostID": 1, "GameID": 1, "Status": "full"},
    {"LobbyID": 2, "HostID": 2, "GameID": 2, "Status": "completed"},
    {"LobbyID": 3, "HostID": 3, "GameID": 3, "Status": "completed"},
    {"LobbyID": 4, "HostID": 5, "GameID": 1, "Status": "open"},
]

SEED_PROFILES = [
    {"ProfileID": 1, "UserID": 1, "GameID": 1, "PlaystyleVector": [0.8, 0.6, 0.5], "ReputationScore": 4.50, "Telemetry_Data": {"kd": 1.4, "matches": 120, "win_rate": 0.56}},
    {"ProfileID": 2, "UserID": 2, "GameID": 1, "PlaystyleVector": [0.7, 0.7, 0.6], "ReputationScore": 4.67, "Telemetry_Data": {"kd": 1.2, "matches": 95, "win_rate": 0.52}},
    {"ProfileID": 3, "UserID": 3, "GameID": 1, "PlaystyleVector": [0.3, 0.9, 0.8], "ReputationScore": 4.50, "Telemetry_Data": {"kd": 0.9, "matches": 210, "win_rate": 0.61}},
    {"ProfileID": 4, "UserID": 4, "GameID": 1, "PlaystyleVector": [0.9, 0.3, 0.4], "ReputationScore": 2.50, "Telemetry_Data": {"kd": 1.8, "matches": 60, "win_rate": 0.44}},
    {"ProfileID": 5, "UserID": 5, "GameID": 1, "PlaystyleVector": [0.4, 0.8, 0.7], "ReputationScore": 3.00, "Telemetry_Data": {"kd": 1.0, "matches": 150, "win_rate": 0.55}},
    {"ProfileID": 6, "UserID": 6, "GameID": 1, "PlaystyleVector": [0.6, 0.5, 0.9], "ReputationScore": 4.00, "Telemetry_Data": {"kd": 1.1, "matches": 180, "win_rate": 0.58}},
    {"ProfileID": 7, "UserID": 1, "GameID": 2, "PlaystyleVector": [0.7, 0.5, 0.4], "ReputationScore": 4.50, "Telemetry_Data": {"kd": 1.3, "matches": 80, "win_rate": 0.5}},
    {"ProfileID": 8, "UserID": 2, "GameID": 2, "PlaystyleVector": [0.6, 0.6, 0.5], "ReputationScore": 4.67, "Telemetry_Data": {"kd": 1.1, "matches": 70, "win_rate": 0.49}},
    {"ProfileID": 9, "UserID": 7, "GameID": 2, "PlaystyleVector": [0.8, 0.4, 0.3], "ReputationScore": 5.00, "Telemetry_Data": {"kd": 1.6, "matches": 55, "win_rate": 0.47}},
    {"ProfileID": 10, "UserID": 8, "GameID": 2, "PlaystyleVector": [0.5, 0.7, 0.6], "ReputationScore": 4.00, "Telemetry_Data": {"kd": 1.0, "matches": 90, "win_rate": 0.53}},
    {"ProfileID": 11, "UserID": 3, "GameID": 3, "PlaystyleVector": [0.2, 0.8, 0.9], "ReputationScore": 4.50, "Telemetry_Data": {"gpm": 420, "matches": 300, "win_rate": 0.57}},
    {"ProfileID": 12, "UserID": 5, "GameID": 3, "PlaystyleVector": [0.4, 0.7, 0.8], "ReputationScore": 3.00, "Telemetry_Data": {"gpm": 380, "matches": 140, "win_rate": 0.51}},
    {"ProfileID": 13, "UserID": 7, "GameID": 3, "PlaystyleVector": [0.5, 0.6, 0.7], "ReputationScore": 5.00, "Telemetry_Data": {"gpm": 400, "matches": 110, "win_rate": 0.54}},
    {"ProfileID": 14, "UserID": 6, "GameID": 4, "PlaystyleVector": [0.7, 0.8, 0.5], "ReputationScore": 4.00, "Telemetry_Data": {"goals": 310, "matches": 200, "win_rate": 0.6}},
    {"ProfileID": 15, "UserID": 8, "GameID": 4, "PlaystyleVector": [0.6, 0.6, 0.6], "ReputationScore": 4.00, "Telemetry_Data": {"goals": 190, "matches": 130, "win_rate": 0.52}},
]

SEED_PARTICIPANTS = [
    {"ParticipantID": 1, "LobbyID": 1, "UserID": 1, "Squad_Role": "Duelist", "Ready_Status": 1},
    {"ParticipantID": 2, "LobbyID": 1, "UserID": 2, "Squad_Role": "Sentinel", "Ready_Status": 0},
    {"ParticipantID": 3, "LobbyID": 1, "UserID": 3, "Squad_Role": "Controller", "Ready_Status": 1},
    {"ParticipantID": 4, "LobbyID": 2, "UserID": 2, "Squad_Role": "Fragger", "Ready_Status": 0},
    {"ParticipantID": 5, "LobbyID": 2, "UserID": 1, "Squad_Role": "Support", "Ready_Status": 0},
    {"ParticipantID": 6, "LobbyID": 2, "UserID": 7, "Squad_Role": "Scout", "Ready_Status": 0},
    {"ParticipantID": 7, "LobbyID": 3, "UserID": 3, "Squad_Role": "Shotcaller", "Ready_Status": 1},
    {"ParticipantID": 8, "LobbyID": 3, "UserID": 5, "Squad_Role": "Support", "Ready_Status": 1},
    {"ParticipantID": 9, "LobbyID": 3, "UserID": 7, "Squad_Role": "Carry", "Ready_Status": 1},
    {"ParticipantID": 10, "LobbyID": 4, "UserID": 5, "Squad_Role": "Initiator", "Ready_Status": 0},
    {"ParticipantID": 11, "LobbyID": 4, "UserID": 6, "Squad_Role": "Controller", "Ready_Status": 0},
    {"ParticipantID": 12, "LobbyID": 1, "UserID": 4, "Squad_Role": "Duelist", "Ready_Status": 0},
    {"ParticipantID": 13, "LobbyID": 1, "UserID": 5, "Squad_Role": "Sentinel", "Ready_Status": 0},
    {"ParticipantID": 14, "LobbyID": 4, "UserID": 1, "Squad_Role": "Duelist", "Ready_Status": 0},
]

SEED_FEEDBACK = [
    {"FeedbackID": 1, "ReviewerID": 1, "ReviewedUserID": 2, "Score": 5},
    {"FeedbackID": 2, "ReviewerID": 3, "ReviewedUserID": 2, "Score": 4},
    {"FeedbackID": 3, "ReviewerID": 2, "ReviewedUserID": 1, "Score": 4},
    {"FeedbackID": 4, "ReviewerID": 5, "ReviewedUserID": 1, "Score": 5},
    {"FeedbackID": 5, "ReviewerID": 1, "ReviewedUserID": 3, "Score": 5},
    {"FeedbackID": 6, "ReviewerID": 2, "ReviewedUserID": 3, "Score": 4},
    {"FeedbackID": 7, "ReviewerID": 4, "ReviewedUserID": 5, "Score": 3},
    {"FeedbackID": 8, "ReviewerID": 6, "ReviewedUserID": 4, "Score": 2},
    {"FeedbackID": 9, "ReviewerID": 5, "ReviewedUserID": 4, "Score": 3},
    {"FeedbackID": 10, "ReviewerID": 7, "ReviewedUserID": 8, "Score": 4},
    {"FeedbackID": 11, "ReviewerID": 8, "ReviewedUserID": 7, "Score": 5},
    {"FeedbackID": 12, "ReviewerID": 3, "ReviewedUserID": 6, "Score": 4},
    {"FeedbackID": 13, "ReviewerID": 4, "ReviewedUserID": 2, "Score": 5},
]

SEED_CONNECTIONS = [
    {"ConnectionID": 1, "RequesterID": 1, "ReceiverID": 2, "Connection_Type": "friend"},
    {"ConnectionID": 2, "RequesterID": 3, "ReceiverID": 1, "Connection_Type": "friend"},
    {"ConnectionID": 3, "RequesterID": 4, "ReceiverID": 1, "Connection_Type": "block"},
    {"ConnectionID": 4, "RequesterID": 5, "ReceiverID": 3, "Connection_Type": "friend"},
    {"ConnectionID": 5, "RequesterID": 7, "ReceiverID": 8, "Connection_Type": "follow"},
    {"ConnectionID": 6, "RequesterID": 6, "ReceiverID": 2, "Connection_Type": "follow"},
    {"ConnectionID": 7, "RequesterID": 8, "ReceiverID": 7, "Connection_Type": "friend"},
]

SEED_AUDIT_LOGS = [
    {"LogID": 1, "TargetUserID": 1, "Action_Type": "LOGIN", "Log_Timestamp": "2026-10-02 18:28:01"},
    {"LogID": 2, "TargetUserID": 2, "Action_Type": "LOGIN", "Log_Timestamp": "2026-10-02 18:28:01"},
    {"LogID": 3, "TargetUserID": 4, "Action_Type": "FAILED_LOGIN", "Log_Timestamp": "2026-10-02 18:28:01"},
    {"LogID": 4, "TargetUserID": 4, "Action_Type": "FAILED_LOGIN", "Log_Timestamp": "2026-10-02 18:28:01"},
    {"LogID": 5, "TargetUserID": 6, "Action_Type": "PASSWORD_RESET", "Log_Timestamp": "2026-10-02 18:28:01"},
    {"LogID": 6, "TargetUserID": 9, "Action_Type": "ROLE_CHANGE: player -> moderator", "Log_Timestamp": "2026-10-02 18:28:01"},
    {"LogID": 7, "TargetUserID": 3, "Action_Type": "ROLE_CHANGE: player -> moderator", "Log_Timestamp": "2026-10-02 18:39:56"},
    {"LogID": 8, "TargetUserID": 2, "Action_Type": "LOBBY_COMPLETED: 2", "Log_Timestamp": "2026-10-02 18:41:31"},
]


# ==============================================================================
# Helper Math: fn_playstyle_dist
# ==============================================================================

def fn_playstyle_dist(v1: List[float], v2: List[float]) -> float:
    """Compute 3D Euclidean distance between two playstyle vectors.
    
    Equivalent to SQL fn_playstyle_dist(v1, v2).
    """
    if not v1 or not v2 or len(v1) < 3 or len(v2) < 3:
        return 0.0
    dist = math.sqrt(
        (float(v1[0]) - float(v2[0])) ** 2 +
        (float(v1[1]) - float(v2[1])) ** 2 +
        (float(v1[2]) - float(v2[2])) ** 2
    )
    return round(dist, 3)


# ==============================================================================
# In-Memory Database Engine for Mock/Demo Mode
# ==============================================================================

class InMemoryDatabase:
    """In-memory relational engine replicating SquadLink DDL, DML, triggers & procedures."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Restore pristine baseline seed state (sql/reset_demo.sql equivalent)."""
        import copy
        self.users = copy.deepcopy(SEED_USERS)
        self.games = copy.deepcopy(SEED_GAMES)
        self.lobbies = copy.deepcopy(SEED_LOBBIES)
        self.profiles = copy.deepcopy(SEED_PROFILES)
        self.participants = copy.deepcopy(SEED_PARTICIPANTS)
        self.feedback = copy.deepcopy(SEED_FEEDBACK)
        self.connections = copy.deepcopy(SEED_CONNECTIONS)
        self.audit_logs = copy.deepcopy(SEED_AUDIT_LOGS)

    # --- Stored Functions ---

    def fn_avg_rating(self, user_id: int) -> float:
        scores = [f["Score"] for f in self.feedback if f["ReviewedUserID"] == user_id]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)

    def fn_lobby_size(self, lobby_id: int) -> int:
        return sum(1 for p in self.participants if p["LobbyID"] == lobby_id)

    # --- Stored Procedures & Triggers ---

    def sp_join_lobby(self, lobby_id: int, user_id: int, squad_role: str) -> str:
        """Transactionally join a lobby with trigger validations."""
        lobby = next((l for l in self.lobbies if l["LobbyID"] == lobby_id), None)
        if not lobby:
            raise ValueError(f"Lobby not found: {lobby_id}")

        # Trigger trg_part_bi checks:
        if lobby["Status"] != "open":
            raise ValueError("Lobby is not open for joining")
        if self.fn_lobby_size(lobby_id) >= 5:
            raise ValueError("Lobby is full")

        # Unique key check:
        if any(p["LobbyID"] == lobby_id and p["UserID"] == user_id for p in self.participants):
            raise ValueError("User already in this lobby")

        new_id = max([p["ParticipantID"] for p in self.participants], default=0) + 1
        self.participants.append({
            "ParticipantID": new_id,
            "LobbyID": lobby_id,
            "UserID": user_id,
            "Squad_Role": squad_role,
            "Ready_Status": 0,
        })

        # Trigger trg_part_ai check:
        if self.fn_lobby_size(lobby_id) >= 5:
            lobby["Status"] = "full"

        return f"User {user_id} joined lobby {lobby_id}"

    def sp_find_match(self, lobby_id: int, min_rep: float) -> List[Dict[str, Any]]:
        """Recommends up to 5 compatible players ranked by Euclidean distance."""
        lobby = next((l for l in self.lobbies if l["LobbyID"] == lobby_id), None)
        if not lobby:
            raise ValueError("Lobby not found")

        host_profile = next(
            (p for p in self.profiles if p["UserID"] == lobby["HostID"] and p["GameID"] == lobby["GameID"]),
            None
        )
        if not host_profile:
            return []

        lobby_user_ids = {p["UserID"] for p in self.participants if p["LobbyID"] == lobby_id}

        candidates = []
        for p in self.profiles:
            if p["GameID"] == lobby["GameID"] and p["UserID"] != lobby["HostID"]:
                if p["UserID"] not in lobby_user_ids and p["ReputationScore"] >= min_rep:
                    user = next((u for u in self.users if u["UserID"] == p["UserID"]), None)
                    if user:
                        dist = fn_playstyle_dist(p["PlaystyleVector"], host_profile["PlaystyleVector"])
                        candidates.append({
                            "UserID": user["UserID"],
                            "Username": user["Username"],
                            "ReputationScore": float(p["ReputationScore"]),
                            "playstyle_distance": dist,
                            "PlaystyleVector": p["PlaystyleVector"],
                            "HostVector": host_profile["PlaystyleVector"],
                        })

        candidates.sort(key=lambda x: (x["playstyle_distance"], -x["ReputationScore"]))
        return candidates[:5]

    def sp_close_lobby(self, lobby_id: int):
        """Close/complete a lobby, reset ready status, write audit log."""
        lobby = next((l for l in self.lobbies if l["LobbyID"] == lobby_id), None)
        if not lobby:
            raise ValueError("Lobby not found")

        lobby["Status"] = "completed"
        for p in self.participants:
            if p["LobbyID"] == lobby_id:
                p["Ready_Status"] = 0

        log_id = max([a["LogID"] for a in self.audit_logs], default=0) + 1
        self.audit_logs.append({
            "LogID": log_id,
            "TargetUserID": lobby["HostID"],
            "Action_Type": f"LOBBY_COMPLETED: {lobby_id}",
            "Log_Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    def submit_feedback(self, reviewer_id: int, reviewed_user_id: int, score: int):
        """Insert feedback with trigger validations."""
        # Trigger trg_feedback_bi:
        if reviewer_id == reviewed_user_id:
            raise ValueError("A user cannot review themselves")
        if score < 1 or score > 5:
            raise ValueError("Score must be between 1 and 5")

        new_id = max([f["FeedbackID"] for f in self.feedback], default=0) + 1
        self.feedback.append({
            "FeedbackID": new_id,
            "ReviewerID": reviewer_id,
            "ReviewedUserID": reviewed_user_id,
            "Score": score,
        })

        # Trigger trg_feedback_ai:
        new_avg = self.fn_avg_rating(reviewed_user_id)
        for p in self.profiles:
            if p["UserID"] == reviewed_user_id:
                p["ReputationScore"] = new_avg

    def update_user_role(self, user_id: int, new_role: str):
        """Update user role and log trigger trg_user_au."""
        user = next((u for u in self.users if u["UserID"] == user_id), None)
        if not user:
            raise ValueError("User not found")
        old_role = user["Role"]
        if old_role != new_role:
            user["Role"] = new_role
            log_id = max([a["LogID"] for a in self.audit_logs], default=0) + 1
            self.audit_logs.append({
                "LogID": log_id,
                "TargetUserID": user_id,
                "Action_Type": f"ROLE_CHANGE: {old_role} -> {new_role}",
                "Log_Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

    def run_nested_query_1(self) -> List[Dict[str, Any]]:
        """Nested Query 1: Players whose ReputationScore is strictly above overall platform avg."""
        if not self.profiles:
            return []
        avg_rep = sum(p["ReputationScore"] for p in self.profiles) / len(self.profiles)
        results = []
        for p in self.profiles:
            if p["ReputationScore"] > avg_rep:
                user = next((u for u in self.users if u["UserID"] == p["UserID"]), {})
                game = next((g for g in self.games if g["GameID"] == p["GameID"]), {})
                results.append({
                    "UserID": p["UserID"],
                    "Username": user.get("Username", "Unknown"),
                    "Game": game.get("Title", "Unknown"),
                    "ReputationScore": p["ReputationScore"],
                    "PlaystyleVector": p["PlaystyleVector"],
                })
        results.sort(key=lambda x: (-x["ReputationScore"], x["Username"]))
        return results

    def run_nested_query_2(self) -> List[Dict[str, Any]]:
        """Nested Query 2: Users in Valorant lobbies with max feedback score of 5."""
        val_game = next((g for g in self.games if g["Title"] == "Valorant"), None)
        if not val_game:
            return []
        val_lobbies = {l["LobbyID"] for l in self.lobbies if l["GameID"] == val_game["GameID"]}
        val_participants = {p["UserID"] for p in self.participants if p["LobbyID"] in val_lobbies}
        five_star_users = {f["ReviewedUserID"] for f in self.feedback if f["Score"] == 5}

        matching_ids = val_participants.intersection(five_star_users)
        results = []
        for uid in matching_ids:
            u = next((usr for usr in self.users if usr["UserID"] == uid), None)
            if u:
                results.append({
                    "UserID": u["UserID"],
                    "Username": u["Username"],
                    "Role": u["Role"],
                    "Avg_Feedback_Score": self.fn_avg_rating(u["UserID"]),
                })
        return results


# ==============================================================================
# SquadLink DB Manager (Connecting to MySQL or In-Memory)
# ==============================================================================

class DatabaseManager:
    """Manages database connection and query execution for SquadLink."""

    def __init__(self):
        self.is_connected = False
        self.use_mock = True
        self.connection_info = "Demo Mode (Mock Database)"
        self.mock_db = InMemoryDatabase()
        self.connection = None

    def connect(self, host="localhost", port=3306, user="root", password="", database="squadlink") -> Tuple[bool, str]:
        """Attempt connection to real MySQL server."""
        if not mysql:
            self.use_mock = True
            self.is_connected = True
            self.connection_info = "Demo Mode (mysql-connector not available)"
            return True, "Running in Demo Mode"

        try:
            self.connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                autocommit=True,
                connect_timeout=3,
            )
            self.is_connected = True
            self.use_mock = False
            self.connection_info = f"{user}@{host} / {database}"
            return True, "Connected to MySQL database!"
        except Exception as e:
            # Fall back to mock mode gracefully
            self.use_mock = True
            self.is_connected = True
            self.connection_info = f"{user}@{host} / {database} (Demo Fallback)"
            return False, f"Could not connect to MySQL ({str(e)}). Enabled Demo Mode."

    def enable_demo_mode(self):
        """Explicitly switch to Demo Mode."""
        self.use_mock = True
        self.is_connected = True
        self.connection_info = "Demo Mode (In-Memory Database)"

    # --- Data Retrieval API ---

    def get_users(self) -> List[Dict[str, Any]]:
        if self.use_mock:
            return self.mock_db.users
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT UserID, Username, Role FROM user_account ORDER BY UserID")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_games(self) -> List[Dict[str, Any]]:
        if self.use_mock:
            return self.mock_db.games
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT GameID, Title, Genre FROM game_metadata ORDER BY GameID")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_lobbies(self, game_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            res = []
            for l in self.mock_db.lobbies:
                if game_id and l["GameID"] != game_id:
                    continue
                if status and status != "All" and l["Status"] != status:
                    continue
                host = next((u for u in self.mock_db.users if u["UserID"] == l["HostID"]), {})
                game = next((g for g in self.mock_db.games if g["GameID"] == l["GameID"]), {})
                size = self.mock_db.fn_lobby_size(l["LobbyID"])
                res.append({
                    **l,
                    "HostName": host.get("Username", "Unknown"),
                    "GameTitle": game.get("Title", "Unknown"),
                    "Genre": game.get("Genre", "Unknown"),
                    "ParticipantCount": size,
                })
            return res

        cursor = self.connection.cursor(dictionary=True)
        query = """
            SELECT ml.LobbyID, ml.HostID, ml.GameID, ml.Status,
                   u.Username AS HostName, gm.Title AS GameTitle, gm.Genre,
                   fn_lobby_size(ml.LobbyID) AS ParticipantCount
            FROM matchmaking_lobby ml
            JOIN user_account u ON u.UserID = ml.HostID
            JOIN game_metadata gm ON gm.GameID = ml.GameID
            WHERE 1=1
        """
        params = []
        if game_id:
            query += " AND ml.GameID = %s"
            params.append(game_id)
        if status and status != "All":
            query += " AND ml.Status = %s"
            params.append(status)
        query += " ORDER BY ml.LobbyID DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_lobby_participants(self, lobby_id: int) -> List[Dict[str, Any]]:
        if self.use_mock:
            parts = [p for p in self.mock_db.participants if p["LobbyID"] == lobby_id]
            res = []
            for p in parts:
                user = next((u for u in self.mock_db.users if u["UserID"] == p["UserID"]), {})
                res.append({**p, "Username": user.get("Username", "Unknown")})
            return res

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT lp.ParticipantID, lp.LobbyID, lp.UserID, lp.Squad_Role, lp.Ready_Status,
                   u.Username
            FROM lobby_participants lp
            JOIN user_account u ON u.UserID = lp.UserID
            WHERE lp.LobbyID = %s
            ORDER BY lp.ParticipantID
        """, (lobby_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def create_lobby(self, host_id: int, game_id: int, host_role: str = "Duelist") -> int:
        if self.use_mock:
            new_id = max([l["LobbyID"] for l in self.mock_db.lobbies], default=0) + 1
            self.mock_db.lobbies.append({
                "LobbyID": new_id,
                "HostID": host_id,
                "GameID": game_id,
                "Status": "open",
            })
            # Host joins automatically
            self.mock_db.sp_join_lobby(new_id, host_id, host_role)
            return new_id

        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO matchmaking_lobby (HostID, GameID, Status) VALUES (%s, %s, 'open')",
            (host_id, game_id)
        )
        lobby_id = cursor.lastrowid
        cursor.callproc("sp_join_lobby", (lobby_id, host_id, host_role))
        cursor.close()
        return lobby_id

    def join_lobby(self, lobby_id: int, user_id: int, squad_role: str) -> str:
        if self.use_mock:
            return self.mock_db.sp_join_lobby(lobby_id, user_id, squad_role)
        cursor = self.connection.cursor()
        cursor.callproc("sp_join_lobby", (lobby_id, user_id, squad_role))
        cursor.close()
        return f"User {user_id} joined lobby {lobby_id}"

    def close_lobby(self, lobby_id: int):
        if self.use_mock:
            return self.mock_db.sp_close_lobby(lobby_id)
        cursor = self.connection.cursor()
        cursor.callproc("sp_close_lobby", (lobby_id,))
        cursor.close()

    def update_participant_ready(self, participant_id: int, ready_status: int):
        if self.use_mock:
            for p in self.mock_db.participants:
                if p["ParticipantID"] == participant_id:
                    p["Ready_Status"] = ready_status
            return
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE lobby_participants SET Ready_Status = %s WHERE ParticipantID = %s",
            (ready_status, participant_id)
        )
        cursor.close()

    def update_lobby_status(self, lobby_id: int, new_status: str):
        if self.use_mock:
            for l in self.mock_db.lobbies:
                if l["LobbyID"] == lobby_id:
                    l["Status"] = new_status
            return
        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE matchmaking_lobby SET Status = %s WHERE LobbyID = %s",
            (new_status, lobby_id)
        )
        cursor.close()

    def find_match(self, lobby_id: int, min_rep: float) -> List[Dict[str, Any]]:
        if self.use_mock:
            return self.mock_db.sp_find_match(lobby_id, min_rep)

        cursor = self.connection.cursor(dictionary=True)
        cursor.callproc("sp_find_match", (lobby_id, min_rep))
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())
        cursor.close()

        # Augment with playstyle vector if needed
        for r in results:
            if "PlaystyleVector" not in r:
                r["PlaystyleVector"] = [0.5, 0.5, 0.5]
        return results

    def get_profiles(self, game_id: Optional[int] = None, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            res = []
            for p in self.mock_db.profiles:
                if game_id and p["GameID"] != game_id:
                    continue
                if user_id and p["UserID"] != user_id:
                    continue
                u = next((usr for usr in self.mock_db.users if usr["UserID"] == p["UserID"]), {})
                g = next((gm for gm in self.mock_db.games if gm["GameID"] == p["GameID"]), {})
                res.append({
                    **p,
                    "Username": u.get("Username", "Unknown"),
                    "Role": u.get("Role", "player"),
                    "GameTitle": g.get("Title", "Unknown"),
                    "Genre": g.get("Genre", "Unknown"),
                })
            return res

        cursor = self.connection.cursor(dictionary=True)
        query = """
            SELECT pp.ProfileID, pp.UserID, pp.GameID, pp.PlaystyleVector, pp.ReputationScore, pp.Telemetry_Data,
                   u.Username, u.Role, gm.Title AS GameTitle, gm.Genre
            FROM player_profile pp
            JOIN user_account u ON u.UserID = pp.UserID
            JOIN game_metadata gm ON gm.GameID = pp.GameID
            WHERE 1=1
        """
        params = []
        if game_id:
            query += " AND pp.GameID = %s"
            params.append(game_id)
        if user_id:
            query += " AND pp.UserID = %s"
            params.append(user_id)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        for r in rows:
            if isinstance(r["PlaystyleVector"], str):
                r["PlaystyleVector"] = json.loads(r["PlaystyleVector"])
            if isinstance(r["Telemetry_Data"], str):
                r["Telemetry_Data"] = json.loads(r["Telemetry_Data"])
        return rows

    def save_profile(self, user_id: int, game_id: int, playstyle_vector: List[float], telemetry: Optional[Dict] = None):
        if self.use_mock:
            existing = next((p for p in self.mock_db.profiles if p["UserID"] == user_id and p["GameID"] == game_id), None)
            if existing:
                existing["PlaystyleVector"] = playstyle_vector
                if telemetry:
                    existing["Telemetry_Data"] = telemetry
            else:
                new_id = max([p["ProfileID"] for p in self.mock_db.profiles], default=0) + 1
                self.mock_db.profiles.append({
                    "ProfileID": new_id,
                    "UserID": user_id,
                    "GameID": game_id,
                    "PlaystyleVector": playstyle_vector,
                    "ReputationScore": self.mock_db.fn_avg_rating(user_id),
                    "Telemetry_Data": telemetry or {},
                })
            return

        cursor = self.connection.cursor()
        query = """
            INSERT INTO player_profile (UserID, GameID, PlaystyleVector, ReputationScore, Telemetry_Data)
            VALUES (%s, %s, %s, fn_avg_rating(%s), %s)
            ON DUPLICATE KEY UPDATE PlaystyleVector = VALUES(PlaystyleVector), Telemetry_Data = VALUES(Telemetry_Data)
        """
        cursor.execute(query, (user_id, game_id, json.dumps(playstyle_vector), user_id, json.dumps(telemetry or {})))
        cursor.close()

    def submit_feedback(self, reviewer_id: int, reviewed_user_id: int, score: int):
        if self.use_mock:
            return self.mock_db.submit_feedback(reviewer_id, reviewed_user_id, score)

        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO player_feedback (ReviewerID, ReviewedUserID, Score) VALUES (%s, %s, %s)",
            (reviewer_id, reviewed_user_id, score)
        )
        cursor.close()

    def get_feedback(self, reviewed_user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            res = []
            for f in self.mock_db.feedback:
                if reviewed_user_id and f["ReviewedUserID"] != reviewed_user_id:
                    continue
                rev = next((u for u in self.mock_db.users if u["UserID"] == f["ReviewerID"]), {})
                target = next((u for u in self.mock_db.users if u["UserID"] == f["ReviewedUserID"]), {})
                res.append({
                    **f,
                    "ReviewerName": rev.get("Username", "Unknown"),
                    "ReviewedName": target.get("Username", "Unknown"),
                })
            return res

        cursor = self.connection.cursor(dictionary=True)
        query = """
            SELECT pf.FeedbackID, pf.ReviewerID, pf.ReviewedUserID, pf.Score,
                   u1.Username AS ReviewerName, u2.Username AS ReviewedName
            FROM player_feedback pf
            JOIN user_account u1 ON u1.UserID = pf.ReviewerID
            JOIN user_account u2 ON u2.UserID = pf.ReviewedUserID
            WHERE 1=1
        """
        params = []
        if reviewed_user_id:
            query += " AND pf.ReviewedUserID = %s"
            params.append(reviewed_user_id)
        query += " ORDER BY pf.FeedbackID DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_connections(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            res = []
            for c in self.mock_db.connections:
                if user_id and c["RequesterID"] != user_id and c["ReceiverID"] != user_id:
                    continue
                req = next((u for u in self.mock_db.users if u["UserID"] == c["RequesterID"]), {})
                rec = next((u for u in self.mock_db.users if u["UserID"] == c["ReceiverID"]), {})
                res.append({
                    **c,
                    "RequesterName": req.get("Username", "Unknown"),
                    "ReceiverName": rec.get("Username", "Unknown"),
                })
            return res

        cursor = self.connection.cursor(dictionary=True)
        query = """
            SELECT pc.ConnectionID, pc.RequesterID, pc.ReceiverID, pc.Connection_Type,
                   u1.Username AS RequesterName, u2.Username AS ReceiverName
            FROM player_connections pc
            JOIN user_account u1 ON u1.UserID = pc.RequesterID
            JOIN user_account u2 ON u2.UserID = pc.ReceiverID
            WHERE 1=1
        """
        params = []
        if user_id:
            query += " AND (pc.RequesterID = %s OR pc.ReceiverID = %s)"
            params.extend([user_id, user_id])
        query += " ORDER BY pc.ConnectionID DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def add_connection(self, requester_id: int, receiver_id: int, conn_type: str):
        if requester_id == receiver_id:
            raise ValueError("A user cannot connect with themselves")

        if self.use_mock:
            new_id = max([c["ConnectionID"] for c in self.mock_db.connections], default=0) + 1
            self.mock_db.connections.append({
                "ConnectionID": new_id,
                "RequesterID": requester_id,
                "ReceiverID": receiver_id,
                "Connection_Type": conn_type,
            })
            return

        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO player_connections (RequesterID, ReceiverID, Connection_Type) VALUES (%s, %s, %s)",
            (requester_id, receiver_id, conn_type)
        )
        cursor.close()

    def get_audit_logs(self, target_user: Optional[int] = None) -> List[Dict[str, Any]]:
        if self.use_mock:
            res = []
            for a in reversed(self.mock_db.audit_logs):
                if target_user and a["TargetUserID"] != target_user:
                    continue
                u = next((usr for usr in self.mock_db.users if usr["UserID"] == a["TargetUserID"]), {})
                res.append({
                    **a,
                    "Username": u.get("Username", "Unknown"),
                })
            return res

        cursor = self.connection.cursor(dictionary=True)
        query = """
            SELECT sal.LogID, sal.TargetUserID, sal.Action_Type, sal.Log_Timestamp,
                   u.Username
            FROM security_audit_log sal
            JOIN user_account u ON u.UserID = sal.TargetUserID
            WHERE 1=1
        """
        params = []
        if target_user:
            query += " AND sal.TargetUserID = %s"
            params.append(target_user)
        query += " ORDER BY sal.LogID DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def update_user_role(self, user_id: int, new_role: str):
        if self.use_mock:
            return self.mock_db.update_user_role(user_id, new_role)

        cursor = self.connection.cursor()
        cursor.execute("UPDATE user_account SET Role = %s WHERE UserID = %s", (new_role, user_id))
        cursor.close()

    def run_nested_query_1(self) -> List[Dict[str, Any]]:
        if self.use_mock:
            return self.mock_db.run_nested_query_1()

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                u.UserID,
                u.Username,
                gm.Title AS Game,
                pp.ReputationScore,
                pp.PlaystyleVector
            FROM player_profile pp
            JOIN user_account u ON u.UserID = pp.UserID
            JOIN game_metadata gm ON gm.GameID = pp.GameID
            WHERE pp.ReputationScore > (
                SELECT AVG(ReputationScore) 
                FROM player_profile
            )
            ORDER BY pp.ReputationScore DESC, u.Username ASC;
        """)
        rows = cursor.fetchall()
        cursor.close()
        for r in rows:
            if isinstance(r["PlaystyleVector"], str):
                r["PlaystyleVector"] = json.loads(r["PlaystyleVector"])
        return rows

    def run_nested_query_2(self) -> List[Dict[str, Any]]:
        if self.use_mock:
            return self.mock_db.run_nested_query_2()

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                u.UserID,
                u.Username,
                u.Role,
                fn_avg_rating(u.UserID) AS Avg_Feedback_Score
            FROM user_account u
            WHERE u.UserID IN (
                SELECT lp.UserID
                FROM lobby_participants lp
                JOIN matchmaking_lobby ml ON ml.LobbyID = lp.LobbyID
                WHERE ml.GameID = (
                    SELECT GameID FROM game_metadata WHERE Title = 'Valorant'
                )
            )
            AND u.UserID IN (
                SELECT ReviewedUserID
                FROM player_feedback
                WHERE Score = 5
            );
        """)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def reset_demo_state(self):
        """Reset state back to clean baseline."""
        if self.use_mock:
            self.mock_db.reset()
            return "Demo database reset to initial seed state!"

        # Live MySQL reset logic executing reset_demo.sql
        cursor = self.connection.cursor()
        reset_statements = [
            "DELETE FROM `lobby_participants` WHERE `ParticipantID` > 11",
            "UPDATE `matchmaking_lobby` SET `Status` = 'open' WHERE `LobbyID` IN (1, 4)",
            "UPDATE `matchmaking_lobby` SET `Status` = 'in_progress' WHERE `LobbyID` = 2",
            "UPDATE `matchmaking_lobby` SET `Status` = 'completed' WHERE `LobbyID` = 3",
            "UPDATE `lobby_participants` SET `Ready_Status` = 1 WHERE `ParticipantID` IN (1, 3, 7, 8, 9)",
            "UPDATE `lobby_participants` SET `Ready_Status` = 0 WHERE `ParticipantID` IN (2, 4, 5, 6, 10, 11)",
            "UPDATE `user_account` SET `Role` = 'player' WHERE `UserID` = 3",
            "DELETE FROM `player_feedback` WHERE `FeedbackID` > 13",
            "DELETE FROM `security_audit_log` WHERE `LogID` > 6",
            """UPDATE `player_profile` pp
               SET pp.`ReputationScore` = fn_avg_rating(pp.`UserID`)
               WHERE pp.`UserID` IN (SELECT DISTINCT `ReviewedUserID` FROM `player_feedback`)""",
        ]
        for stmt in reset_statements:
            try:
                cursor.execute(stmt)
            except Exception:
                pass
        cursor.close()
        return "MySQL database reset to initial seed state!"
