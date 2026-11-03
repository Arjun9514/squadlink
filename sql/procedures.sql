-- ============================================================
-- File: procedures.sql
-- Contents: Lobby Stored Procedures (sp_join_lobby, sp_find_match, sp_close_lobby)
-- ============================================================

USE `squadlink`;

DROP PROCEDURE IF EXISTS `sp_join_lobby`;
DROP PROCEDURE IF EXISTS `sp_find_match`;
DROP PROCEDURE IF EXISTS `sp_close_lobby`;

DELIMITER $$

-- 1. Join an open lobby with transaction handling
CREATE PROCEDURE `sp_join_lobby`(
    IN p_lobby INT, 
    IN p_user INT, 
    IN p_role VARCHAR(30)
)
BEGIN
    DECLARE v_status VARCHAR(20) DEFAULT NULL;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    SELECT Status INTO v_status FROM Matchmaking_Lobby WHERE LobbyID = p_lobby FOR UPDATE;
    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lobby not found';
    END IF;
    INSERT INTO Lobby_Participants (LobbyID, UserID, Squad_Role, Ready_Status)
    VALUES (p_lobby, p_user, p_role, FALSE);
    COMMIT;

    SELECT CONCAT('User ', p_user, ' joined lobby ', p_lobby) AS result;
END$$

-- 2. Find matching players for a lobby using Euclidean playstyle vector distance and reputation
CREATE PROCEDURE `sp_find_match`(
    IN p_lobby INT, 
    IN p_min_rep DECIMAL(3,2)
)
BEGIN
    SELECT u.UserID, u.Username, pp.ReputationScore,
           fn_playstyle_dist(pp.PlaystyleVector, hp.PlaystyleVector) AS playstyle_distance
    FROM Matchmaking_Lobby l
    JOIN Player_Profile hp ON hp.UserID = l.HostID AND hp.GameID = l.GameID
    JOIN Player_Profile pp ON pp.GameID = l.GameID AND pp.UserID <> l.HostID
    JOIN User_Account u    ON u.UserID = pp.UserID
    WHERE l.LobbyID = p_lobby
      AND pp.ReputationScore >= p_min_rep
      AND pp.UserID NOT IN (SELECT UserID FROM Lobby_Participants WHERE LobbyID = p_lobby)
    ORDER BY playstyle_distance ASC, pp.ReputationScore DESC
    LIMIT 5;
END$$

-- 3. Close/complete a lobby, reset participant ready status, and write an audit log
CREATE PROCEDURE `sp_close_lobby`(
    IN p_lobby INT
)
BEGIN
    DECLARE v_status VARCHAR(20) DEFAULT NULL;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    SELECT Status INTO v_status FROM Matchmaking_Lobby WHERE LobbyID = p_lobby FOR UPDATE;
    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lobby not found';
    END IF;
    UPDATE Matchmaking_Lobby SET Status = 'completed' WHERE LobbyID = p_lobby;
    UPDATE Lobby_Participants SET Ready_Status = FALSE WHERE LobbyID = p_lobby;
    INSERT INTO Security_Audit_Log (TargetUserID, Action_Type)
    SELECT HostID, CONCAT('LOBBY_COMPLETED: ', p_lobby) FROM Matchmaking_Lobby WHERE LobbyID = p_lobby;
    COMMIT;
END$$

DELIMITER ;