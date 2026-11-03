CREATE DATABASE IF NOT EXISTS squadlink;
USE squadlink;

CREATE TABLE user_account (
    UserID INT NOT NULL AUTO_INCREMENT,
    Username VARCHAR(50) NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role VARCHAR(20) NOT NULL DEFAULT 'player',
    PRIMARY KEY (UserID),
    UNIQUE KEY Username (Username),
    CONSTRAINT chk_role CHECK (Role IN ('player', 'moderator', 'admin'))
);

CREATE TABLE game_metadata (
    GameID INT NOT NULL AUTO_INCREMENT,
    Title VARCHAR(100) NOT NULL,
    Genre VARCHAR(50) NOT NULL,
    PRIMARY KEY (GameID)
);

CREATE TABLE matchmaking_lobby (
    LobbyID INT NOT NULL AUTO_INCREMENT,
    HostID INT NOT NULL,
    GameID INT NOT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT 'open',
    PRIMARY KEY (LobbyID),
    KEY fk_ml_host (HostID),
    KEY fk_ml_game (GameID),
    CONSTRAINT fk_ml_game FOREIGN KEY (GameID) REFERENCES game_metadata (GameID),
    CONSTRAINT fk_ml_host FOREIGN KEY (HostID) REFERENCES user_account (UserID),
    CONSTRAINT chk_status CHECK (Status IN ('open', 'full', 'in_progress', 'completed'))
);

CREATE TABLE player_profile (
    ProfileID INT NOT NULL AUTO_INCREMENT,
    UserID INT NOT NULL,
    GameID INT NOT NULL,
    PlaystyleVector JSON NOT NULL,
    ReputationScore DECIMAL(3,2) NOT NULL DEFAULT '0.00',
    Telemetry_Data JSON DEFAULT NULL,
    PRIMARY KEY (ProfileID),
    UNIQUE KEY uq_pp (UserID, GameID),
    KEY fk_pp_game (GameID),
    CONSTRAINT fk_pp_game FOREIGN KEY (GameID) REFERENCES game_metadata (GameID),
    CONSTRAINT fk_pp_user FOREIGN KEY (UserID) REFERENCES user_account (UserID),
    CONSTRAINT chk_rep CHECK (ReputationScore BETWEEN 0 AND 5)
);

CREATE TABLE security_audit_log (
    LogID INT NOT NULL AUTO_INCREMENT,
    TargetUserID INT NOT NULL,
    Action_Type VARCHAR(100) NOT NULL,
    Log_Timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (LogID),
    KEY fk_sal_user (TargetUserID),
    CONSTRAINT fk_sal_user FOREIGN KEY (TargetUserID) REFERENCES user_account (UserID)
);

CREATE TABLE player_connections (
    ConnectionID INT NOT NULL AUTO_INCREMENT,
    RequesterID INT NOT NULL,
    ReceiverID INT NOT NULL,
    Connection_Type VARCHAR(20) NOT NULL,
    PRIMARY KEY (ConnectionID),
    KEY fk_pc_req (RequesterID),
    KEY fk_pc_rec (ReceiverID),
    CONSTRAINT fk_pc_rec FOREIGN KEY (ReceiverID) REFERENCES user_account (UserID),
    CONSTRAINT fk_pc_req FOREIGN KEY (RequesterID) REFERENCES user_account (UserID),
    CONSTRAINT chk_ctype CHECK (Connection_Type IN ('friend', 'follow', 'block')),
    CONSTRAINT chk_selfc CHECK (RequesterID <> ReceiverID)
);

CREATE TABLE player_feedback (
    FeedbackID INT NOT NULL AUTO_INCREMENT,
    ReviewerID INT NOT NULL,
    ReviewedUserID INT NOT NULL,
    Score INT NOT NULL,
    PRIMARY KEY (FeedbackID),
    KEY fk_pf_reviewer (ReviewerID),
    KEY fk_pf_reviewed (ReviewedUserID),
    CONSTRAINT fk_pf_reviewed FOREIGN KEY (ReviewedUserID) REFERENCES user_account (UserID),
    CONSTRAINT fk_pf_reviewer FOREIGN KEY (ReviewerID) REFERENCES user_account (UserID),
    CONSTRAINT chk_score CHECK (Score BETWEEN 1 AND 5),
    CONSTRAINT chk_selffb CHECK (ReviewerID <> ReviewedUserID)
);

CREATE TABLE lobby_participants (
    ParticipantID INT NOT NULL AUTO_INCREMENT,
    LobbyID INT NOT NULL,
    UserID INT NOT NULL,
    Squad_Role VARCHAR(30) DEFAULT NULL,
    Ready_Status TINYINT(1) NOT NULL DEFAULT '0',
    PRIMARY KEY (ParticipantID),
    UNIQUE KEY uq_lp (LobbyID, UserID),
    KEY fk_lp_user (UserID),
    CONSTRAINT fk_lp_lobby FOREIGN KEY (LobbyID) REFERENCES matchmaking_lobby (LobbyID),
    CONSTRAINT fk_lp_user FOREIGN KEY (UserID) REFERENCES user_account (UserID)
);
