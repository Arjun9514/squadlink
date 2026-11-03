-- ============================================================
-- File: functions.sql
-- Contents: Rating, lobby size and playstyle distance functions
-- ============================================================

USE `squadlink`;

DROP FUNCTION IF EXISTS `fn_avg_rating`;
DROP FUNCTION IF EXISTS `fn_lobby_size`;
DROP FUNCTION IF EXISTS `fn_playstyle_dist`;

DELIMITER $$

-- 1. Calculate average feedback score for a user
CREATE FUNCTION `fn_avg_rating`(p_user INT) 
RETURNS DECIMAL(3,2)
READS SQL DATA
BEGIN
    DECLARE v_avg DECIMAL(3,2);
    SELECT IFNULL(ROUND(AVG(Score),2),0) INTO v_avg
    FROM Player_Feedback WHERE ReviewedUserID = p_user;
    RETURN v_avg;
END$$

-- 2. Get current participant count in a lobby
CREATE FUNCTION `fn_lobby_size`(p_lobby INT) 
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_cnt INT;
    SELECT COUNT(*) INTO v_cnt FROM Lobby_Participants WHERE LobbyID = p_lobby;
    RETURN v_cnt;
END$$

-- 3. Compute Euclidean distance between two 3D JSON PlaystyleVectors
CREATE FUNCTION `fn_playstyle_dist`(v1 JSON, v2 JSON) 
RETURNS DECIMAL(6,3)
DETERMINISTIC
BEGIN
    RETURN ROUND(SQRT(
        POW(CAST(JSON_EXTRACT(v1,'$[0]') AS DECIMAL(4,2)) - CAST(JSON_EXTRACT(v2,'$[0]') AS DECIMAL(4,2)), 2) +
        POW(CAST(JSON_EXTRACT(v1,'$[1]') AS DECIMAL(4,2)) - CAST(JSON_EXTRACT(v2,'$[1]') AS DECIMAL(4,2)), 2) +
        POW(CAST(JSON_EXTRACT(v1,'$[2]') AS DECIMAL(4,2)) - CAST(JSON_EXTRACT(v2,'$[2]') AS DECIMAL(4,2)), 2)
    ), 3);
END$$

DELIMITER ;