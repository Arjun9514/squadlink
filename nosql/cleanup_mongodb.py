#!/usr/bin/env python3
"""Safely preview or remove SquadLink test sessions and linked activity entries.

Dry-run (no changes):
  py cleanup_mongodb.py --user-id 10 --from 2026-11-02T17:50:00Z --to 2026-11-02T18:05:00Z

Execute after reviewing the preview:
  py cleanup_mongodb.py --user-id 10 --from 2026-11-02T17:50:00Z --to 2026-11-02T18:05:00Z --execute

Optional environment variables:
  MONGODB_URI       mongodb://localhost:27017 (default)
  MONGODB_DATABASE  squadlink_nosql (default)
"""

import argparse
import os
import sys
from datetime import datetime, timezone

try:
    from pymongo import MongoClient
except ImportError:
    print("Missing dependency: pymongo. Install with: py -m pip install pymongo")
    sys.exit(1)


def parse_iso_datetime(value: str) -> datetime:
    """Parse ISO-8601 timestamp and require an explicit timezone."""
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid timestamp {value!r}; use e.g. 2026-11-02T17:50:00Z"
        ) from exc
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("Timestamp needs a timezone; append Z for UTC.")
    return parsed.astimezone(timezone.utc)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preview or remove SquadLink test sessions and their linked activity entries."
    )
    parser.add_argument("--user-id", required=True, type=int, help="Numeric SquadLink user ID to target")
    parser.add_argument("--from", dest="start", required=True, type=parse_iso_datetime,
                        help="Inclusive start timestamp, e.g. 2026-11-02T17:50:00Z")
    parser.add_argument("--to", dest="end", required=True, type=parse_iso_datetime,
                        help="Exclusive end timestamp, e.g. 2026-11-02T18:05:00Z")
    parser.add_argument("--execute", action="store_true",
                        help="Actually delete after showing a preview and requesting confirmation")
    args = parser.parse_args()

    if args.start >= args.end:
        parser.error("--from must be earlier than --to")

    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    database_name = os.getenv("MONGODB_DATABASE", "squadlink_nosql")
    client = None

    print(f"Database: {database_name}")
    print(f"User ID: {args.user_id}")
    print(f"UTC window: [{args.start.isoformat()}, {args.end.isoformat()})")
    print("Only source='streamlit_manual_entry' sessions are considered.\n")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client[database_name]

        session_filter = {
            "user_id": args.user_id,
            "source": "streamlit_manual_entry",
            "played_at": {"$gte": args.start, "$lt": args.end},
        }
        sessions = list(db.game_sessions.find(
            session_filter,
            {"_id": 1, "username": 1, "game_title": 1, "played_at": 1, "performance": 1},
        ).sort("played_at", 1))

        if not sessions:
            print("No matching sessions found. Nothing to delete.")
            return 0

        session_ids = [str(doc["_id"]) for doc in sessions]
        activity_filter = {
            "user_id": args.user_id,
            "action": "MATCH_RECORDED",
            "metadata.session_id": {"$in": session_ids},
        }
        activities = list(db.player_activity.find(
            activity_filter,
            {"_id": 1, "username": 1, "description": 1, "created_at": 1},
        ).sort("created_at", 1))

        print(f"Gameplay sessions matched: {len(sessions)}")
        for doc in sessions:
            stats = doc.get("performance", {})
            print(
                f"  session={doc['_id']} | player={doc.get('username', '?')} | "
                f"game={doc.get('game_title', '?')} | played_at={doc.get('played_at')} | "
                f"K/D={stats.get('kills', '?')}/{stats.get('deaths', '?')}"
            )

        print(f"\nLinked activity entries matched: {len(activities)}")
        for doc in activities:
            print(f"  activity={doc['_id']} | {doc.get('description', '')}")

        if not args.execute:
            print("\nDRY RUN: no data was changed.")
            print("Review this list, then rerun the same command with --execute to delete.")
            return 0

        print("\nThis permanently deletes only the sessions and their linked MATCH_RECORDED entries above.")
        expected = f"DELETE {len(sessions)}"
        if input(f"Type exactly '{expected}' to continue: ").strip() != expected:
            print("Confirmation did not match. Nothing was deleted.")
            return 2

        # Delete only activity documents linked to the exact session IDs above.
        activity_result = db.player_activity.delete_many(activity_filter)
        session_result = db.game_sessions.delete_many(
            {"_id": {"$in": [doc["_id"] for doc in sessions]}}
        )
        print("\nCleanup complete.")
        print(f"Sessions deleted: {session_result.deleted_count}")
        print(f"Linked activity entries deleted: {activity_result.deleted_count}")
        print("Other MongoDB documents, collections, indexes, and MySQL data were not touched.")
        return 0

    except Exception as exc:
        print(f"\nMongoDB cleanup failed: {exc}")
        return 1
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())
