# SquadLink – MongoDB integration

This version adds two MongoDB-backed features to the existing Streamlit + MySQL application:

1. **Gameplay Telemetry** – manually record match sessions, flexible performance metrics, playstyle indicators and an event entry. Browse match history and view an aggregate performance summary.
2. **Player Activity Feed** – record and filter important application actions: lobby creation, lobby joining, lobby completion, player ratings, match telemetry submissions and role changes.

MySQL remains the source of truth for accounts, games, lobbies, feedback, reputation and relationships. MongoDB stores supplementary documents and refers to MySQL records using their existing integer IDs. No existing MySQL table, trigger, stored procedure or SQL script needs to be changed.

## 1. Install MongoDB on Windows

The simplest setup for a local college-project demo is MongoDB Community Server on the same computer as Streamlit.

1. Download **MongoDB Community Server** for Windows from: https://www.mongodb.com/try/download/community
2. Select the current stable release, Windows x64, and the MSI package.
3. Run the installer. Choose **Complete**.
4. Keep **Install MongoDB as a Service** enabled. The default service name is normally `MongoDB`.
5. MongoDB Compass is optional, but useful for viewing the collections visually. Install it if offered.
6. After installation, open PowerShell and check the service:

```powershell
Get-Service MongoDB
```

If it is stopped, start it from an Administrator PowerShell:

```powershell
Start-Service MongoDB
```

The default local MongoDB connection is `mongodb://localhost:27017`.

### Verify the server

If MongoDB Shell (`mongosh`) is installed, run:

```powershell
mongosh "mongodb://localhost:27017"
```

At the shell prompt:

```javascript
 db.runCommand({ ping: 1 })
```

A successful response contains `ok: 1`. Exit with `exit`.

If `mongosh` is not installed, the application itself will test the connection when either MongoDB tab is opened.

## 2. Install the Python dependency

Open PowerShell or Command Prompt in the folder containing `app.py` and `requirements.txt`:

```powershell
py -m pip install -r requirements.txt
```

This installs `pymongo` in addition to the existing Streamlit, MySQL connector and pandas dependencies. If you use a virtual environment, activate it before running the command.

## 3. Configure the connection (optional)

By default, the app connects to:

- URI: `mongodb://localhost:27017`
- Database: `squadlink_nosql`

You can override these using environment variables. In PowerShell, for the current terminal session:

```powershell
$env:SQUADLINK_MONGO_URI = "mongodb://localhost:27017"
$env:SQUADLINK_MONGO_DB = "squadlink_nosql"
```

For MongoDB Atlas, set `SQUADLINK_MONGO_URI` to your Atlas connection string. URL-encode special characters in the database password. Do not commit credentials or an Atlas URI containing a password to GitHub.

## 4. Run SquadLink

Start the app exactly as before, from the project folder:

```powershell
py -m streamlit run app.py
```

Connect to MySQL through the existing login screen. MongoDB is connected lazily when you open **Gameplay Telemetry** or **Activity Feed**. If MongoDB is unavailable, the original MySQL features continue to work; the MongoDB tabs display a connection error instead of stopping the entire app.

## 5. How to demonstrate Gameplay Telemetry

1. Open **Gameplay Telemetry**.
2. Choose an existing player and game (these are read from MySQL).
3. Optionally associate the session with an existing lobby.
4. Enter duration, result, kills, deaths, assists, accuracy and damage.
5. Set the three playstyle indicators and enter a short event description.
6. Click **Save match to MongoDB**.
7. The session appears in Match History. Change the player/game filters to explore the data.
8. The Player Performance Summary is calculated by a MongoDB aggregation pipeline.

The demo form is a manual telemetry entry. It does not connect to or collect data from a real game. This keeps the project self-contained and makes it easy to demonstrate.

## 6. How to demonstrate Player Activity Feed

1. Perform an action in the app: create a lobby, join a lobby, submit a rating, record telemetry or change a role.
2. Open **Activity Feed**.
3. Filter by player or action type.
4. The newest events appear first.

The feed starts collecting events after this updated version is running. It does not backfill actions that happened before MongoDB integration.

## 7. MongoDB data model

Database: `squadlink_nosql`

### `game_sessions`

A document represents one player's recorded match session. It contains:

- `user_id`, `username`: references to the MySQL account.
- `game_id`, `game_title`: references to the MySQL game.
- `lobby_id`: optional MySQL lobby reference.
- `duration_minutes`, `played_at`.
- `result`: outcome and win flag.
- `performance`: kills, deaths, assists, accuracy and damage dealt.
- `playstyle`: aggression, teamwork and objective-focus values.
- `events`: an array of event objects. This can grow to contain different event shapes for different game genres.
- `source`: identifies the manual Streamlit entry path.

### `player_activity`

A document represents one action in the application. It contains:

- `user_id`, `username`.
- `action`: an action code such as `LOBBY_JOINED`.
- `description`: human-readable event text.
- `metadata`: a flexible object containing relevant IDs or action-specific fields.
- `created_at`: UTC timestamp.

Indexes are created automatically for player/time, game/time and action/time lookups.

## 8. Troubleshooting

**MongoDB is unavailable / connection refused**

- Check `Get-Service MongoDB`.
- Start it using `Start-Service MongoDB` in Administrator PowerShell.
- Confirm the URI is correct. Local default: `mongodb://localhost:27017`.
- If using Atlas, check network access/IP allowlisting and database-user credentials.

**`ModuleNotFoundError: No module named 'pymongo'`**

Run `py -m pip install pymongo` (or reinstall all dependencies with `py -m pip install -r requirements.txt`) using the same Python interpreter that runs Streamlit.

**MongoDB tabs show no records**

This is expected until you save a match or perform a new activity after installing this version. Existing MySQL records are not automatically copied into MongoDB.

**MySQL features work but MongoDB features do not**

That is intentional fault isolation: MongoDB is supplementary. Check the MongoDB service and URI; the MySQL database is not modified by this integration.

## 9. Files added/changed

- `mongo_store.py` – MongoDB connection, indexes, inserts, filters and aggregation.
- `app.py` – two new tabs and activity logging after successful MySQL actions.
- `requirements.txt` – adds `pymongo`.
- `MONGODB_INTEGRATION.md` – this setup and demonstration guide.
