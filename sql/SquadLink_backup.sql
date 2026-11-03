-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: squadlink
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `squadlink`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `squadlink` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `squadlink`;

--
-- Table structure for table `game_metadata`
--

DROP TABLE IF EXISTS `game_metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `game_metadata` (
  `GameID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(100) NOT NULL,
  `Genre` varchar(50) NOT NULL,
  PRIMARY KEY (`GameID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_metadata`
--

LOCK TABLES `game_metadata` WRITE;
/*!40000 ALTER TABLE `game_metadata` DISABLE KEYS */;
INSERT INTO `game_metadata` VALUES (1,'Valorant','Tactical Shooter'),(2,'Apex Legends','Battle Royale'),(3,'Dota 2','MOBA'),(4,'Rocket League','Sports'),(5,'Overwatch 2','FPS');
/*!40000 ALTER TABLE `game_metadata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lobby_participants`
--

DROP TABLE IF EXISTS `lobby_participants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lobby_participants` (
  `ParticipantID` int NOT NULL AUTO_INCREMENT,
  `LobbyID` int NOT NULL,
  `UserID` int NOT NULL,
  `Squad_Role` varchar(30) DEFAULT NULL,
  `Ready_Status` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ParticipantID`),
  UNIQUE KEY `uq_lp` (`LobbyID`,`UserID`),
  KEY `fk_lp_user` (`UserID`),
  CONSTRAINT `fk_lp_lobby` FOREIGN KEY (`LobbyID`) REFERENCES `matchmaking_lobby` (`LobbyID`),
  CONSTRAINT `fk_lp_user` FOREIGN KEY (`UserID`) REFERENCES `user_account` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lobby_participants`
--

LOCK TABLES `lobby_participants` WRITE;
/*!40000 ALTER TABLE `lobby_participants` DISABLE KEYS */;
INSERT INTO `lobby_participants` VALUES (1,1,1,'Duelist',1),(2,1,2,'Sentinel',0),(3,1,3,'Controller',1),(4,2,2,'Fragger',0),(5,2,1,'Support',0),(6,2,7,'Scout',0),(7,3,3,'Shotcaller',1),(8,3,5,'Support',1),(9,3,7,'Carry',1),(10,4,5,'Initiator',0),(11,4,6,'Controller',0),(12,1,4,'Duelist',0),(13,1,5,'Sentinel',0),(14,4,1,'Duelist',0);
/*!40000 ALTER TABLE `lobby_participants` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_part_bi` BEFORE INSERT ON `lobby_participants` FOR EACH ROW BEGIN
    DECLARE v_status VARCHAR(20) DEFAULT NULL;
    SELECT Status INTO v_status FROM Matchmaking_Lobby WHERE LobbyID = NEW.LobbyID;
    IF v_status IS NOT NULL AND v_status <> 'open' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lobby is not open for joining';
    END IF;
    IF fn_lobby_size(NEW.LobbyID) >= 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Lobby is full';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_part_ai` AFTER INSERT ON `lobby_participants` FOR EACH ROW BEGIN
    IF fn_lobby_size(NEW.LobbyID) >= 5 THEN
        UPDATE Matchmaking_Lobby SET Status = 'full' WHERE LobbyID = NEW.LobbyID;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `matchmaking_lobby`
--

DROP TABLE IF EXISTS `matchmaking_lobby`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matchmaking_lobby` (
  `LobbyID` int NOT NULL AUTO_INCREMENT,
  `HostID` int NOT NULL,
  `GameID` int NOT NULL,
  `Status` varchar(20) NOT NULL DEFAULT 'open',
  PRIMARY KEY (`LobbyID`),
  KEY `fk_ml_host` (`HostID`),
  KEY `fk_ml_game` (`GameID`),
  CONSTRAINT `fk_ml_game` FOREIGN KEY (`GameID`) REFERENCES `game_metadata` (`GameID`),
  CONSTRAINT `fk_ml_host` FOREIGN KEY (`HostID`) REFERENCES `user_account` (`UserID`),
  CONSTRAINT `chk_status` CHECK ((`Status` in (_utf8mb4'open',_utf8mb4'full',_utf8mb4'in_progress',_utf8mb4'completed')))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `matchmaking_lobby`
--

LOCK TABLES `matchmaking_lobby` WRITE;
/*!40000 ALTER TABLE `matchmaking_lobby` DISABLE KEYS */;
INSERT INTO `matchmaking_lobby` VALUES (1,1,1,'full'),(2,2,2,'completed'),(3,3,3,'completed'),(4,5,1,'open');
/*!40000 ALTER TABLE `matchmaking_lobby` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_connections`
--

DROP TABLE IF EXISTS `player_connections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_connections` (
  `ConnectionID` int NOT NULL AUTO_INCREMENT,
  `RequesterID` int NOT NULL,
  `ReceiverID` int NOT NULL,
  `Connection_Type` varchar(20) NOT NULL,
  PRIMARY KEY (`ConnectionID`),
  KEY `fk_pc_req` (`RequesterID`),
  KEY `fk_pc_rec` (`ReceiverID`),
  CONSTRAINT `fk_pc_rec` FOREIGN KEY (`ReceiverID`) REFERENCES `user_account` (`UserID`),
  CONSTRAINT `fk_pc_req` FOREIGN KEY (`RequesterID`) REFERENCES `user_account` (`UserID`),
  CONSTRAINT `chk_ctype` CHECK ((`Connection_Type` in (_utf8mb4'friend',_utf8mb4'follow',_utf8mb4'block'))),
  CONSTRAINT `chk_selfc` CHECK ((`RequesterID` <> `ReceiverID`))
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_connections`
--

LOCK TABLES `player_connections` WRITE;
/*!40000 ALTER TABLE `player_connections` DISABLE KEYS */;
INSERT INTO `player_connections` VALUES (1,1,2,'friend'),(2,3,1,'friend'),(3,4,1,'block'),(4,5,3,'friend'),(5,7,8,'follow'),(6,6,2,'follow'),(7,8,7,'friend');
/*!40000 ALTER TABLE `player_connections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_feedback`
--

DROP TABLE IF EXISTS `player_feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_feedback` (
  `FeedbackID` int NOT NULL AUTO_INCREMENT,
  `ReviewerID` int NOT NULL,
  `ReviewedUserID` int NOT NULL,
  `Score` int NOT NULL,
  PRIMARY KEY (`FeedbackID`),
  KEY `fk_pf_reviewer` (`ReviewerID`),
  KEY `fk_pf_reviewed` (`ReviewedUserID`),
  CONSTRAINT `fk_pf_reviewed` FOREIGN KEY (`ReviewedUserID`) REFERENCES `user_account` (`UserID`),
  CONSTRAINT `fk_pf_reviewer` FOREIGN KEY (`ReviewerID`) REFERENCES `user_account` (`UserID`),
  CONSTRAINT `chk_score` CHECK ((`Score` between 1 and 5)),
  CONSTRAINT `chk_selffb` CHECK ((`ReviewerID` <> `ReviewedUserID`))
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_feedback`
--

LOCK TABLES `player_feedback` WRITE;
/*!40000 ALTER TABLE `player_feedback` DISABLE KEYS */;
INSERT INTO `player_feedback` VALUES (1,1,2,5),(2,3,2,4),(3,2,1,4),(4,5,1,5),(5,1,3,5),(6,2,3,4),(7,4,5,3),(8,6,4,2),(9,5,4,3),(10,7,8,4),(11,8,7,5),(12,3,6,4),(13,4,2,5);
/*!40000 ALTER TABLE `player_feedback` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_feedback_bi` BEFORE INSERT ON `player_feedback` FOR EACH ROW BEGIN
    IF NEW.ReviewerID = NEW.ReviewedUserID THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A user cannot review themselves';
    END IF;
    IF NEW.Score < 1 OR NEW.Score > 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Score must be between 1 and 5';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_feedback_ai` AFTER INSERT ON `player_feedback` FOR EACH ROW BEGIN
    UPDATE Player_Profile
    SET ReputationScore = fn_avg_rating(NEW.ReviewedUserID)
    WHERE UserID = NEW.ReviewedUserID;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `player_profile`
--

DROP TABLE IF EXISTS `player_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_profile` (
  `ProfileID` int NOT NULL AUTO_INCREMENT,
  `UserID` int NOT NULL,
  `GameID` int NOT NULL,
  `PlaystyleVector` json NOT NULL,
  `ReputationScore` decimal(3,2) NOT NULL DEFAULT '0.00',
  `Telemetry_Data` json DEFAULT NULL,
  PRIMARY KEY (`ProfileID`),
  UNIQUE KEY `uq_pp` (`UserID`,`GameID`),
  KEY `fk_pp_game` (`GameID`),
  CONSTRAINT `fk_pp_game` FOREIGN KEY (`GameID`) REFERENCES `game_metadata` (`GameID`),
  CONSTRAINT `fk_pp_user` FOREIGN KEY (`UserID`) REFERENCES `user_account` (`UserID`),
  CONSTRAINT `chk_rep` CHECK ((`ReputationScore` between 0 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_profile`
--

LOCK TABLES `player_profile` WRITE;
/*!40000 ALTER TABLE `player_profile` DISABLE KEYS */;
INSERT INTO `player_profile` VALUES (1,1,1,'[0.8, 0.6, 0.5]',4.50,'{\"kd\": 1.4, \"matches\": 120, \"win_rate\": 0.56}'),(2,2,1,'[0.7, 0.7, 0.6]',4.67,'{\"kd\": 1.2, \"matches\": 95, \"win_rate\": 0.52}'),(3,3,1,'[0.3, 0.9, 0.8]',4.50,'{\"kd\": 0.9, \"matches\": 210, \"win_rate\": 0.61}'),(4,4,1,'[0.9, 0.3, 0.4]',2.50,'{\"kd\": 1.8, \"matches\": 60, \"win_rate\": 0.44}'),(5,5,1,'[0.4, 0.8, 0.7]',3.00,'{\"kd\": 1.0, \"matches\": 150, \"win_rate\": 0.55}'),(6,6,1,'[0.6, 0.5, 0.9]',4.00,'{\"kd\": 1.1, \"matches\": 180, \"win_rate\": 0.58}'),(7,1,2,'[0.7, 0.5, 0.4]',4.50,'{\"kd\": 1.3, \"matches\": 80, \"win_rate\": 0.5}'),(8,2,2,'[0.6, 0.6, 0.5]',4.67,'{\"kd\": 1.1, \"matches\": 70, \"win_rate\": 0.49}'),(9,7,2,'[0.8, 0.4, 0.3]',5.00,'{\"kd\": 1.6, \"matches\": 55, \"win_rate\": 0.47}'),(10,8,2,'[0.5, 0.7, 0.6]',4.00,'{\"kd\": 1.0, \"matches\": 90, \"win_rate\": 0.53}'),(11,3,3,'[0.2, 0.8, 0.9]',4.50,'{\"gpm\": 420, \"matches\": 300, \"win_rate\": 0.57}'),(12,5,3,'[0.4, 0.7, 0.8]',3.00,'{\"gpm\": 380, \"matches\": 140, \"win_rate\": 0.51}'),(13,7,3,'[0.5, 0.6, 0.7]',5.00,'{\"gpm\": 400, \"matches\": 110, \"win_rate\": 0.54}'),(14,6,4,'[0.7, 0.8, 0.5]',4.00,'{\"goals\": 310, \"matches\": 200, \"win_rate\": 0.6}'),(15,8,4,'[0.6, 0.6, 0.6]',4.00,'{\"goals\": 190, \"matches\": 130, \"win_rate\": 0.52}');
/*!40000 ALTER TABLE `player_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `security_audit_log`
--

DROP TABLE IF EXISTS `security_audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `security_audit_log` (
  `LogID` int NOT NULL AUTO_INCREMENT,
  `TargetUserID` int NOT NULL,
  `Action_Type` varchar(100) NOT NULL,
  `Log_Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`LogID`),
  KEY `fk_sal_user` (`TargetUserID`),
  CONSTRAINT `fk_sal_user` FOREIGN KEY (`TargetUserID`) REFERENCES `user_account` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `security_audit_log`
--

LOCK TABLES `security_audit_log` WRITE;
/*!40000 ALTER TABLE `security_audit_log` DISABLE KEYS */;
INSERT INTO `security_audit_log` VALUES (1,1,'LOGIN','2026-10-02 18:28:01'),(2,2,'LOGIN','2026-10-02 18:28:01'),(3,4,'FAILED_LOGIN','2026-10-02 18:28:01'),(4,4,'FAILED_LOGIN','2026-10-02 18:28:01'),(5,6,'PASSWORD_RESET','2026-10-02 18:28:01'),(6,9,'ROLE_CHANGE: player -> moderator','2026-10-02 18:28:01'),(7,3,'ROLE_CHANGE: player -> moderator','2026-10-02 18:39:56'),(8,2,'LOBBY_COMPLETED: 2','2026-10-02 18:41:31');
/*!40000 ALTER TABLE `security_audit_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_account`
--

DROP TABLE IF EXISTS `user_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_account` (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `Username` varchar(50) NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `Role` varchar(20) NOT NULL DEFAULT 'player',
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `Username` (`Username`),
  CONSTRAINT `chk_role` CHECK ((`Role` in (_utf8mb4'player',_utf8mb4'moderator',_utf8mb4'admin')))
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_account`
--

LOCK TABLES `user_account` WRITE;
/*!40000 ALTER TABLE `user_account` DISABLE KEYS */;
INSERT INTO `user_account` VALUES (1,'rahul','f0238f6dc401055f97761133158d1eca21d14fb453bf5b8d90efd7f39373743f','player'),(2,'arjun','26a95b1e69c92f1cfb0381fd379d80526ecd9c368d3a7baa9be6c24b61a25e71','player'),(3,'priya','bdcd8f14a7b9cee0c191985e3e1b7d9e47cbdfa92b2df68b91cbd7828a21e35b','moderator'),(4,'karthik','9e53246d7a8e55d7583534e123bbf30837f2bf85b8394a05f1c368e64b5e6f6a','player'),(5,'sneha','1a97f616bc859e058a244fb7a75abe1e8510e913cc72479e67962281343df008','player'),(6,'vikram','37185d3e31a5c2cc4af7ad13021b03588ae52971b870a36adb1ce925a49d0e45','player'),(7,'ananya','eaf2b4285d739aa8830455af01f3299fbc4eb5e03301411fe2a3b1962b342d9c','player'),(8,'rohan','a4232054c2fc1ff21e8d911d0669df5e636562b9da8c14ecaa8fddc0f92e070c','player'),(9,'meera','ccf694e32b137ad43360c322f40c79421925260d6ec9e871998670083bd9beab','moderator'),(10,'admin1','7676aaafb027c825bd9abab78b234070e702752f625b752e55e55b48e607e358','admin');
/*!40000 ALTER TABLE `user_account` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_user_au` AFTER UPDATE ON `user_account` FOR EACH ROW BEGIN
    IF OLD.Role <> NEW.Role THEN
        INSERT INTO Security_Audit_Log (TargetUserID, Action_Type)
        VALUES (NEW.UserID, CONCAT('ROLE_CHANGE: ', OLD.Role, ' -> ', NEW.Role));
    END IF;
    IF OLD.PasswordHash <> NEW.PasswordHash THEN
        INSERT INTO Security_Audit_Log (TargetUserID, Action_Type)
        VALUES (NEW.UserID, 'PASSWORD_CHANGE');
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Dumping events for database 'squadlink'
--

--
-- Dumping routines for database 'squadlink'
--
/*!50003 DROP FUNCTION IF EXISTS `fn_avg_rating` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_avg_rating`(p_user INT) RETURNS decimal(3,2)
    READS SQL DATA
BEGIN
    DECLARE v_avg DECIMAL(3,2);
    SELECT IFNULL(ROUND(AVG(Score),2),0) INTO v_avg
    FROM Player_Feedback WHERE ReviewedUserID = p_user;
    RETURN v_avg;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `fn_lobby_size` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_lobby_size`(p_lobby INT) RETURNS int
    READS SQL DATA
BEGIN
    DECLARE v_cnt INT;
    SELECT COUNT(*) INTO v_cnt FROM Lobby_Participants WHERE LobbyID = p_lobby;
    RETURN v_cnt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `fn_playstyle_dist` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_playstyle_dist`(v1 JSON, v2 JSON) RETURNS decimal(6,3)
    DETERMINISTIC
BEGIN
    RETURN ROUND(SQRT(
        POW(CAST(JSON_EXTRACT(v1,'$[0]') AS DECIMAL(4,2)) - CAST(JSON_EXTRACT(v2,'$[0]') AS DECIMAL(4,2)), 2) +
        POW(CAST(JSON_EXTRACT(v1,'$[1]') AS DECIMAL(4,2)) - CAST(JSON_EXTRACT(v2,'$[1]') AS DECIMAL(4,2)), 2) +
        POW(CAST(JSON_EXTRACT(v1,'$[2]') AS DECIMAL(4,2)) - CAST(JSON_EXTRACT(v2,'$[2]') AS DECIMAL(4,2)), 2)
    ), 3);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_close_lobby` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_close_lobby`(IN p_lobby INT)
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
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_find_match` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_find_match`(IN p_lobby INT, IN p_min_rep DECIMAL(3,2))
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
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_join_lobby` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_join_lobby`(IN p_lobby INT, IN p_user INT, IN p_role VARCHAR(30))
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
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-02  2:41:08
