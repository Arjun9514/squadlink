
# SquadLink – Database Module (`sql`)

## Overview

Relational database implementation for **SquadLink** (MySQL 8.0), a vector-driven player matchmaking platform. It supports multi-game player profiles with 3D JSON playstyle vectors, automated reputation scoring, lobby capacity management, and security audit logging.

## Database Schema (`DDL.sql` & `DML.sql`)

1. **`user_account`** (`UserID`, `Username`, `PasswordHash`, `Role`)
2. **`game_metadata`** (`GameID`, `Title`, `Genre`)
3. **`player_profile`** (`ProfileID`, `UserID`, `GameID`, `PlaystyleVector`, `ReputationScore`, `Telemetry_Data`)
4. **`matchmaking_lobby`** (`LobbyID`, `HostID`, `GameID`, `Status`)
5. **`lobby_participants`** (`ParticipantID`, `LobbyID`, `UserID`, `Squad_Role`, `Ready_Status`)
6. **`player_connections`** (`ConnectionID`, `RequesterID`, `ReceiverID`, `Connection_Type`)
7. **`player_feedback`** (`FeedbackID`, `ReviewerID`, `ReviewedUserID`, `Score`)
8. **`security_audit_log`** (`LogID`, `TargetUserID`, `Action_Type`, `Log_Timestamp`)

## Stored Procedures (`procedures.sql`)

* **`sp_join_lobby(p_lobby, p_user, p_role)`**: Transactionally adds a user to an open lobby with row-level locking (`FOR UPDATE`).
* **`sp_find_match(p_lobby, p_min_rep)`**: Recommends up to 5 compatible players for a lobby ranked by Euclidean playstyle distance (`fn_playstyle_dist`) and `ReputationScore`.
* **`sp_close_lobby(p_lobby)`**: Marks a lobby as `completed`, resets participant ready statuses, and records `LOBBY_COMPLETED` in `security_audit_log`.

## Stored Functions (`functions.sql`)

* **`fn_avg_rating(p_user)`**: Computes the rounded average feedback score for a user from `player_feedback`.
* **`fn_lobby_size(p_lobby)`**: Counts current participants in a given lobby.
* **`fn_playstyle_dist(v1, v2)`**: Computes the 3D Euclidean distance between two JSON `PlaystyleVector` arrays (`$[0]`, `$[1]`, `$[2]`).

## Triggers (`triggers.sql`)

* **`trg_feedback_bi`**: Validates feedback before insert (prevents self-reviews and enforces score between 1 and 5).
* **`trg_feedback_ai`**: Automatically recalculates and updates `player_profile.ReputationScore` via `fn_avg_rating` after new feedback is inserted.
* **`trg_user_au`**: Logs `ROLE_CHANGE` and `PASSWORD_CHANGE` events into `security_audit_log` whenever `user_account` is updated.
* **`trg_part_bi`**: Blocks joining if the lobby status is not `'open'` or if `fn_lobby_size(NEW.LobbyID) >= 5`.
* **`trg_part_ai`**: Automatically updates `matchmaking_lobby.Status` to `'full'` once the 5th participant joins.

## Execution Screenshots

### DDL & Tables

* Database Creation: `screenshots/ddl/create database.png`
* All Tables: `screenshots/ddl/tables/tables.png`
* Table Schemas:
  * `screenshots/ddl/tables/user_account.png`
  * `screenshots/ddl/tables/player_profile.png`
  * `screenshots/ddl/tables/game_metadata.png`
  * `screenshots/ddl/tables/matchmaking_lobby.png`
  * `screenshots/ddl/tables/lobby_participants.png`
  * `screenshots/ddl/tables/player_connections.png`
  * `screenshots/ddl/tables/player_feedback.png`
  * `screenshots/ddl/tables/security_audit_log.png`

### DML (Seed Data)

* `screenshots/dml/user_account.png`
* `screenshots/dml/player_profile.png`
* `screenshots/dml/game_metadata.png`
* `screenshots/dml/matchmaking_lobby.png`
* `screenshots/dml/lobby_participants.png`
* `screenshots/dml/player_connections.png`
* `screenshots/dml/player_feedback.png`
* `screenshots/dml/security_audit_log.png`

### Functions, Procedures, Triggers & Nested Queries

* Functions:
  * `screenshots/ddl/functions/functions.png`
  * `screenshots/ddl/functions/fn_avg_rating.png`
  * `screenshots/ddl/functions/fn_lobby_size.png`
  * `screenshots/ddl/functions/fn_playstyle_dist.png`
* Stored Procedures:
  * `screenshots/sp_join_lobby.png`
  * `screenshots/sp_find_match.png`
* Audit Log Trigger Output: `screenshots/audit logs.png`
* Nested Queries:
  * `screenshots/ddl/nested query 1.png`
  * `screenshots/ddl/nested query 2.png`
