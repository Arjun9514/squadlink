# SquadLink front end

## Run it
```
pip install -r requirements.txt
streamlit run app.py
```
It opens in the browser on a login screen. Enter your MySQL user and password (host, port and database are under Server settings). The login disappears once you are connected. To prefill the password, set it first:
- PowerShell: `$env:SQUADLINK_PASSWORD="yourpassword"`
- Command Prompt: `set SQUADLINK_PASSWORD=yourpassword`

## What each tab uses
| Tab | Database objects |
|---|---|
| Lobbies | fn_lobby_size, sp_close_lobby, creating a lobby (inserts the lobby and its host; trg_part_bi checks the join) |
| Join a lobby | sp_join_lobby, trg_part_bi, trg_part_ai |
| Find a match | sp_find_match, fn_playstyle_dist |
| Ratings | trg_feedback_bi, trg_feedback_ai, fn_avg_rating |
| Players | player_profile, JSON telemetry |
| Admin | trg_user_au, security_audit_log |

## Screenshots for the report
1. Lobbies tab, then pick lobby 4 to show its players.
2. Join a lobby: join lobby 1 (rejected, "Lobby is not open for joining").
3. Join a lobby: add two players to lobby 4 and show it turn full.
4. Find a match: lobby 4, minimum reputation 3.0, with the chart.
5. Ratings: rate yourself (rejected), then rate someone else and show the reputation change.
6. Admin: change a role and show the new audit log row.

Joins and lobby closes are saved permanently. Run `reset_demo.sql` afterwards to restore the seeded data.