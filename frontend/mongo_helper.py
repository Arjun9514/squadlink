"""MongoDB connection and fallback helper for SquadLink Frontend."""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

# Attempt importing mongo_store from nosql
try:
    import mongo_store
except ImportError:
    try:
        from nosql import mongo_store
    except ImportError:
        mongo_store = None


class MongoHelper:
    """Safely interfaces with MongoDB or provides in-memory fallback for activity & telemetry."""

    def __init__(self):
        self.is_connected = False
        self._fallback_sessions = [
            {
                "_id": "6ae8d0e4c336e212cdc0e60e",
                "user_id": 7,
                "username": "ananya",
                "game_id": 2,
                "game_title": "Apex Legends",
                "lobby_id": None,
                "duration_minutes": 24,
                "result": {"outcome": "win", "win": True},
                "performance": {"kills": 15, "deaths": 9, "assists": 9, "accuracy": 77.0, "damage": 3400},
                "playstyle": {"aggression": 0.95, "teamwork": 0.40, "objective_focus": 0.90},
                "events": [{"type": "kill", "description": "Played a match"}],
                "played_at": datetime(2026, 11, 2, 18, 5, 24, tzinfo=timezone.utc),
                "source": "streamlit_manual_entry",
            },
            {
                "_id": "6ae8d0e4c336e212cdc0e60f",
                "user_id": 4,
                "username": "karthik",
                "game_id": 2,
                "game_title": "Apex Legends",
                "lobby_id": None,
                "duration_minutes": 27,
                "result": {"outcome": "win", "win": True},
                "performance": {"kills": 24, "deaths": 11, "assists": 5, "accuracy": 88.0, "damage": 4200},
                "playstyle": {"aggression": 0.90, "teamwork": 0.35, "objective_focus": 0.85},
                "events": [{"type": "kill", "description": "Played a match"}],
                "played_at": datetime(2026, 11, 2, 18, 7, 10, tzinfo=timezone.utc),
                "source": "streamlit_manual_entry",
            },
        ]
        self._fallback_activities = [
            {
                "user_id": 4,
                "username": "karthik",
                "action": "MATCH_RECORDED",
                "description": "Recorded a win in Apex Legends.",
                "created_at": datetime(2026, 11, 2, 18, 7, 10, tzinfo=timezone.utc),
            },
            {
                "user_id": 7,
                "username": "ananya",
                "action": "MATCH_RECORDED",
                "description": "Recorded a win in Apex Legends.",
                "created_at": datetime(2026, 11, 2, 18, 5, 24, tzinfo=timezone.utc),
            },
        ]
        self.check_connection()

    def check_connection(self) -> bool:
        if not mongo_store:
            self.is_connected = False
            return False
        try:
            db = mongo_store.get_db()
            mongo_store.ensure_indexes(db)
            self.is_connected = True
            return True
        except Exception:
            self.is_connected = False
            return False

    def log_activity(self, user_id: int, username: str, action: str, description: str, metadata: Optional[Dict] = None):
        """Record an activity event to MongoDB or in-memory timeline."""
        if self.check_connection():
            try:
                mongo_store.record_activity(user_id, username, action, description, metadata)
                return
            except Exception:
                pass
        # Fallback in-memory
        self._fallback_activities.insert(0, {
            "user_id": int(user_id),
            "username": str(username),
            "action": str(action),
            "description": str(description),
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc),
        })

    def get_activities(self, user_id: Optional[int] = None, action: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if self.check_connection():
            try:
                return mongo_store.get_activity(user_id=user_id, action=action, limit=limit)
            except Exception:
                pass
        # Fallback
        res = self._fallback_activities
        if user_id is not None:
            res = [a for a in res if a["user_id"] == user_id]
        if action and action != "All actions":
            res = [a for a in res if a["action"] == action]
        return res[:limit]

    def log_session(self, document: Dict[str, Any]) -> str:
        """Save match session to MongoDB or fallback."""
        if self.check_connection():
            try:
                obj_id = mongo_store.record_session(document)
                return str(obj_id)
            except Exception:
                pass
        # Fallback
        import uuid
        session_id = uuid.uuid4().hex[:24]
        doc = dict(document)
        doc["_id"] = session_id
        doc["played_at"] = datetime.now(timezone.utc)
        self._fallback_sessions.insert(0, doc)
        return session_id

    def get_sessions(self, user_id: Optional[int] = None, game_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if self.check_connection():
            try:
                return mongo_store.get_sessions(user_id=user_id, game_id=game_id, limit=limit)
            except Exception:
                pass
        res = self._fallback_sessions
        if user_id is not None:
            res = [s for s in res if s.get("user_id") == user_id]
        if game_id is not None:
            res = [s for s in res if s.get("game_id") == game_id]
        return res[:limit]

    def get_session_summary(self, user_id: Optional[int] = None, game_id: Optional[int] = None) -> Dict[str, Any]:
        if self.check_connection():
            try:
                return mongo_store.session_summary(user_id=user_id, game_id=game_id)
            except Exception:
                pass
        # Fallback aggregation pipeline
        sessions = self.get_sessions(user_id=user_id, game_id=game_id)
        if not sessions:
            return {"matches": 0, "wins": 0, "kills": 0, "deaths": 0, "avg_accuracy": 0, "total_minutes": 0, "kd": 0.0, "win_rate": 0.0}
        matches = len(sessions)
        wins = sum(1 for s in sessions if s.get("result", {}).get("win"))
        kills = sum(s.get("performance", {}).get("kills", 0) for s in sessions)
        deaths = sum(s.get("performance", {}).get("deaths", 0) for s in sessions)
        accuracies = [s.get("performance", {}).get("accuracy", 0) for s in sessions if "accuracy" in s.get("performance", {})]
        avg_acc = round(sum(accuracies) / len(accuracies), 1) if accuracies else 0.0
        total_min = sum(s.get("duration_minutes", 0) for s in sessions)
        kd = round(kills / max(deaths, 1), 2)
        win_rate = round((wins / matches) * 100, 1) if matches else 0.0
        return {
            "matches": matches,
            "wins": wins,
            "kills": kills,
            "deaths": deaths,
            "avg_accuracy": avg_acc,
            "total_minutes": total_min,
            "kd": kd,
            "win_rate": win_rate,
        }


# Singleton instance
_mongo_helper = None

def get_mongo_helper() -> MongoHelper:
    global _mongo_helper
    if _mongo_helper is None:
        _mongo_helper = MongoHelper()
    return _mongo_helper
