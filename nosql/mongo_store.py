"""MongoDB persistence helpers for SquadLink.

MySQL remains authoritative for users, games and lobbies. MongoDB stores
flexible gameplay session documents and an append-only activity feed.
"""
import os
from datetime import datetime, timezone
from functools import lru_cache

from pymongo import MongoClient, DESCENDING
from pymongo.errors import PyMongoError


@lru_cache(maxsize=4)
def _client(uri: str):
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    return client


def get_db():
    uri = os.getenv("SQUADLINK_MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("SQUADLINK_MONGO_DB", "squadlink_nosql")
    return _client(uri)[db_name]


def ensure_indexes(db):
    """Create indexes used by the application's common filters/sorts."""
    db.game_sessions.create_index([("user_id", 1), ("played_at", DESCENDING)])
    db.game_sessions.create_index([("game_id", 1), ("played_at", DESCENDING)])
    db.player_activity.create_index([("user_id", 1), ("created_at", DESCENDING)])
    db.player_activity.create_index([("created_at", DESCENDING)])
    db.player_activity.create_index([("action", 1), ("created_at", DESCENDING)])


def record_activity(user_id, username, action, description, metadata=None):
    db = get_db()
    return db.player_activity.insert_one({
        "user_id": int(user_id),
        "username": str(username),
        "action": str(action),
        "description": str(description),
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc),
    })


def record_session(document):
    db = get_db()
    payload = dict(document)
    payload["played_at"] = datetime.now(timezone.utc)
    result = db.game_sessions.insert_one(payload)
    return result.inserted_id


def get_sessions(user_id=None, game_id=None, limit=100):
    db = get_db()
    filters = {}
    if user_id is not None:
        filters["user_id"] = int(user_id)
    if game_id is not None:
        filters["game_id"] = int(game_id)
    return list(db.game_sessions.find(filters).sort("played_at", DESCENDING).limit(int(limit)))


def get_activity(user_id=None, action=None, limit=100):
    db = get_db()
    filters = {}
    if user_id is not None:
        filters["user_id"] = int(user_id)
    if action and action != "All actions":
        filters["action"] = action
    return list(db.player_activity.find(filters).sort("created_at", DESCENDING).limit(int(limit)))


def session_summary(user_id=None, game_id=None):
    """Aggregate session count, wins, K/D and average accuracy in MongoDB."""
    match = {}
    if user_id is not None:
        match["user_id"] = int(user_id)
    if game_id is not None:
        match["game_id"] = int(game_id)
    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": None,
            "matches": {"$sum": 1},
            "wins": {"$sum": {"$cond": ["$result.win", 1, 0]}},
            "kills": {"$sum": "$performance.kills"},
            "deaths": {"$sum": "$performance.deaths"},
            "avg_accuracy": {"$avg": "$performance.accuracy"},
            "total_minutes": {"$sum": "$duration_minutes"},
        }},
    ]
    rows = list(get_db().game_sessions.aggregate(pipeline))
    if not rows:
        return {"matches": 0, "wins": 0, "kills": 0, "deaths": 0,
                "avg_accuracy": 0, "total_minutes": 0, "kd": 0, "win_rate": 0}
    row = rows[0]
    deaths = row.get("deaths", 0) or 0
    kills = row.get("kills", 0) or 0
    matches = row.get("matches", 0) or 0
    row["kd"] = round(kills / max(deaths, 1), 2)
    row["win_rate"] = round((row.get("wins", 0) / matches) * 100, 1) if matches else 0
    row["avg_accuracy"] = round(row.get("avg_accuracy", 0) or 0, 1)
    row.pop("_id", None)
    return row
