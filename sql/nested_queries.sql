-- ============================================================
-- File: nested_queries.sql
-- Contents: Nested queries on SquadLink schema
-- ============================================================

USE `squadlink`;

-- Nested Query 1: Players whose ReputationScore is strictly above the overall platform average
SELECT 
    u.UserID,
    u.Username,
    gm.Title AS Game,
    pp.ReputationScore,
    pp.PlaystyleVector
FROM Player_Profile pp
JOIN User_Account u ON u.UserID = pp.UserID
JOIN Game_Metadata gm ON gm.GameID = pp.GameID
WHERE pp.ReputationScore > (
    SELECT AVG(ReputationScore) 
    FROM Player_Profile
)
ORDER BY pp.ReputationScore DESC, u.Username ASC;

-- Nested Query 2: Find users who have participated in lobbies for 'Valorant' 
-- and have received a max feedback score of 5 from any reviewer
SELECT 
    u.UserID,
    u.Username,
    u.Role,
    fn_avg_rating(u.UserID) AS Avg_Feedback_Score
FROM User_Account u
WHERE u.UserID IN (
    SELECT lp.UserID
    FROM Lobby_Participants lp
    JOIN Matchmaking_Lobby ml ON ml.LobbyID = lp.LobbyID
    WHERE ml.GameID = (
        SELECT GameID FROM Game_Metadata WHERE Title = 'Valorant'
    )
)
AND u.UserID IN (
    SELECT ReviewedUserID
    FROM Player_Feedback
    WHERE Score = 5
);