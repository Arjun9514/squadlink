# SquadLink – NoSQL (MongoDB) part
Gameplay telemetry and player activity feed stored in MongoDB.

- `mongo_store.py` – MongoDB helper module (imported by the frontend's `app.py`)
- `cleanup_mongodb.py` – cleanup utility
- `MONGODB_INTEGRATION.md` – setup and design notes
- `screenshots/` – telemetry / activity feed / summary outputs

Requires `pymongo`. Default URI: `mongodb://localhost:27017`.
