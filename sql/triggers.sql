-- ============================================================
-- File: triggers.sql
-- Contents: Validation, audit and lobby triggers
-- ============================================================

USE `squadlink`;

DROP TRIGGER IF EXISTS `trg_feedback_bi`;
DROP TRIGGER IF EXISTS `trg_feedback_ai`;
DROP TRIGGER IF EXISTS `trg_user_au`;
DROP TRIGGER IF EXISTS `trg_part_bi`;
DROP TRIGGER IF EXISTS `trg_part_ai`;

DELIMITER $$

-- 1. Validate feedback before insert (no self-review, score between 1 and 5)
CREATE TRIGGER `trg_feedback_bi` 
BEFORE INSERT ON `player_feedback` 
FOR EACH ROW 
BEGIN
    IF NEW.ReviewerID = NEW.ReviewedUserID THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A user cannot review themselves';
    END IF;
    IF NEW.Score < 1 OR NEW.Score > 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Score must be between 1 and 5';
    END IF;
END$$

-- 2. Auto-update ReputationScore in Player_Profile after new feedback is inserted
CREATE TRIGGER `trg_feedback_ai` 
AFTER INSERT ON `player_feedback` 
FOR EACH ROW 
BEGIN
    UPDATE Player_Profile
    SET ReputationScore = fn_avg_rating(NEW.ReviewedUserID)
    WHERE UserID = NEW.ReviewedUserID;
END$$

-- 3. Audit role changes and password changes on user_account
CREATE TRIGGER `trg_user_au` 
AFTER UPDATE ON `user_account` 
FOR EACH ROW 
BEGIN
    IF OLD.Role <> NEW.Role THEN
        INSERT INTO Security_Audit_Log (TargetUserID, Action_Type)
        VALUES (NEW.UserID, CONCAT('ROLE_CHANGE: ', OLD.Role, ' -> ', NEW.Role));
    END IF;
    IF OLD.PasswordHash <> NEW.PasswordHash THEN
        INSERT INTO Security_Audit_Log (TargetUserID, Action_Type)
        VALUES (NEW.UserID, 'PASSWORD_CHANGE');
    END IF;
END$$

-- 4. Guard lobby capacity (< 5) and open status before participant joins
CREATE TRIGGER `trg_part_bi` 
BEFORE INSERT ON `lobby_participants` 
FOR EACH ROW 
BEGIN
    DECLARE v_status VARCHAR(20) DEFAULT NULL;
    SELECT Status INTO v_status FROM Matchmaking_Lobby WHERE LobbyID = NEW.LobbyID;
    IF v_status IS NOT NULL AND v_status <> 'open' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lobby is not open for joining';
    END IF;
    IF fn_lobby_size(NEW.LobbyID) >= 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lobby is full';
    END IF;
END$$

-- 5. Automatically mark lobby as 'full' when 5th participant joins
CREATE TRIGGER `trg_part_ai` 
AFTER INSERT ON `lobby_participants` 
FOR EACH ROW 
BEGIN
    IF fn_lobby_size(NEW.LobbyID) >= 5 THEN
        UPDATE Matchmaking_Lobby SET Status = 'full' WHERE LobbyID = NEW.LobbyID;
    END IF;
END$$

DELIMITER ;