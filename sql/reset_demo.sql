-- Puts squadlink back to the seeded state after you have tried the app.
-- sp_join_lobby and sp_close_lobby commit, so their changes stay until you run this.
-- Run it in MySQL Workbench or: mysql -u root -p < reset_demo.sql
USE squadlink;

-- Seed rows are lobby_participants 1-14, player_feedback 1-13, security_audit_log 1-8.
DELETE FROM lobby_participants WHERE ParticipantID > 14;
DELETE FROM player_feedback WHERE FeedbackID > 13;

-- Lobbies created in the app (seed lobbies are 1-4). Their players are already gone from the line above.
DELETE FROM matchmaking_lobby WHERE LobbyID > 4;

-- Lobby status as seeded.
UPDATE matchmaking_lobby SET Status = 'full' WHERE LobbyID = 1;
UPDATE matchmaking_lobby SET Status = 'completed' WHERE LobbyID IN (2, 3);
UPDATE matchmaking_lobby SET Status = 'open' WHERE LobbyID = 4;

-- Reputation is the average of the scores a user has received.
UPDATE player_profile
SET ReputationScore = fn_avg_rating(UserID)
WHERE UserID IN (SELECT ReviewedUserID FROM player_feedback);

-- Roles as seeded (admin1, user 10, is left alone).
UPDATE user_account SET Role = 'player' WHERE UserID IN (1, 2, 4, 5, 6, 7, 8);
UPDATE user_account SET Role = 'moderator' WHERE UserID IN (3, 9);

-- The role updates above fire trg_user_au, so clear the audit log last.
DELETE FROM security_audit_log WHERE LogID > 8;

-- Check: lobby 4 open with 3 players, 14 participants, 13 feedback rows, 8 audit rows.
SELECT LobbyID, Status, fn_lobby_size(LobbyID) AS Players FROM matchmaking_lobby;
SELECT (SELECT COUNT(*) FROM lobby_participants) AS participants,
       (SELECT COUNT(*) FROM player_feedback) AS feedback,
       (SELECT COUNT(*) FROM security_audit_log) AS audit_rows;

-- Reset AUTO_INCREMENT counters to the next seeded ID.
ALTER TABLE user_account AUTO_INCREMENT = 11;
ALTER TABLE game_metadata AUTO_INCREMENT = 6;
ALTER TABLE player_profile AUTO_INCREMENT = 16;
ALTER TABLE matchmaking_lobby AUTO_INCREMENT = 5;
ALTER TABLE lobby_participants AUTO_INCREMENT = 15;
ALTER TABLE player_feedback AUTO_INCREMENT = 14;
ALTER TABLE player_connections AUTO_INCREMENT = 8;
ALTER TABLE security_audit_log AUTO_INCREMENT = 9;