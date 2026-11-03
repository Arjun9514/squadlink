-- ============================================================
-- File: reset_demo.sql
-- Contents: Reset demo changes back to clean baseline seed state
-- ============================================================

USE `squadlink`;

-- 1. Remove demo participants added during testing (ParticipantID > 11)
DELETE FROM `lobby_participants` WHERE `ParticipantID` > 11;
ALTER TABLE `lobby_participants` AUTO_INCREMENT = 12;

-- 2. Reset Lobby statuses back to initial seed state
UPDATE `matchmaking_lobby` SET `Status` = 'open' WHERE `LobbyID` IN (1, 4);
UPDATE `matchmaking_lobby` SET `Status` = 'in_progress' WHERE `LobbyID` = 2;
UPDATE `matchmaking_lobby` SET `Status` = 'completed' WHERE `LobbyID` = 3;

-- 3. Reset Ready_Status for Lobby 2 & 3 participants if modified by sp_close_lobby
UPDATE `lobby_participants` SET `Ready_Status` = 1 WHERE `ParticipantID` IN (1, 3, 7, 8, 9);
UPDATE `lobby_participants` SET `Ready_Status` = 0 WHERE `ParticipantID` IN (2, 4, 5, 6, 10, 11);

-- 4. Revert priya's role if changed to moderator during demo trigger test
UPDATE `user_account` SET `Role` = 'player' WHERE `UserID` = 3;

-- 5. Clean up extra feedback and audit log entries created during demo
DELETE FROM `player_feedback` WHERE `FeedbackID` > 13;
ALTER TABLE `player_feedback` AUTO_INCREMENT = 14;

DELETE FROM `security_audit_log` WHERE `LogID` > 6;
ALTER TABLE `security_audit_log` AUTO_INCREMENT = 7;

-- 6. Recalculate ReputationScores across all profiles
UPDATE `player_profile` pp
SET pp.`ReputationScore` = fn_avg_rating(pp.`UserID`)
WHERE pp.`UserID` IN (SELECT DISTINCT `ReviewedUserID` FROM `player_feedback`);

SELECT 'SquadLink demo state reset complete!' AS status;