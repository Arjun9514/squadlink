USE squadlink;

INSERT INTO user_account (UserID, Username, PasswordHash, Role) VALUES
(1,'rahul','f0238f6dc401055f97761133158d1eca21d14fb453bf5b8d90efd7f39373743f','player'),
(2,'arjun','26a95b1e69c92f1cfb0381fd379d80526ecd9c368d3a7baa9be6c24b61a25e71','player'),
(3,'priya','bdcd8f14a7b9cee0c191985e3e1b7d9e47cbdfa92b2df68b91cbd7828a21e35b','moderator'),
(4,'karthik','9e53246d7a8e55d7583534e123bbf30837f2bf85b8394a05f1c368e64b5e6f6a','player'),
(5,'sneha','1a97f616bc859e058a244fb7a75abe1e8510e913cc72479e67962281343df008','player'),
(6,'vikram','37185d1e31a5c2cc4af7ad13021b03588ae52971b870a36adb1ce925a49d0e45','player'),
(7,'ananya','eaf2b4285d739aa8830455af01f3299fbc4eb5e03301411fe2a3b1962b342d9c','player'),
(8,'rohan','a4232054c2fc1ff21e8d911d0669df5e636562b9da8c14ecaa8fddc0f92e070c','player'),
(9,'meera','ccf694e32b137ad43360c322f40c79421925260d6ec9e871998670083bd9beab','moderator'),
(10,'admin1','7676aaafb027c825bd9abab78b234070e702752f625b752e55e55b48e607e358','admin');

INSERT INTO game_metadata VALUES
(1,'Valorant','Tactical Shooter'),
(2,'Apex Legends','Battle Royale'),
(3,'Dota 2','MOBA'),
(4,'Rocket League','Sports'),
(5,'Overwatch 2','FPS');

INSERT INTO matchmaking_lobby VALUES
(1,1,1,'full'),
(2,2,2,'completed'),
(3,3,3,'completed'),
(4,5,1,'open');

INSERT INTO player_profile VALUES
(1,1,1,'[0.8, 0.6, 0.5]',4.50,'{"kd": 1.4, "matches": 120, "win_rate": 0.56}'),
(2,2,1,'[0.7, 0.7, 0.6]',4.67,'{"kd": 1.2, "matches": 95, "win_rate": 0.52}'),
(3,3,1,'[0.3, 0.9, 0.8]',4.50,'{"kd": 0.9, "matches": 210, "win_rate": 0.61}'),
(4,4,1,'[0.9, 0.3, 0.4]',2.50,'{"kd": 1.8, "matches": 60, "win_rate": 0.44}'),
(5,5,1,'[0.4, 0.8, 0.7]',3.00,'{"kd": 1.0, "matches": 150, "win_rate": 0.55}'),
(6,6,1,'[0.6, 0.5, 0.9]',4.00,'{"kd": 1.1, "matches": 180, "win_rate": 0.58}'),
(7,1,2,'[0.7, 0.5, 0.4]',4.50,'{"kd": 1.3, "matches": 80, "win_rate": 0.5}'),
(8,2,2,'[0.6, 0.6, 0.5]',4.67,'{"kd": 1.1, "matches": 70, "win_rate": 0.49}'),
(9,7,2,'[0.8, 0.4, 0.3]',5.00,'{"kd": 1.6, "matches": 55, "win_rate": 0.47}'),
(10,8,2,'[0.5, 0.7, 0.6]',4.00,'{"kd": 1.0, "matches": 90, "win_rate": 0.53}'),
(11,3,3,'[0.2, 0.8, 0.9]',4.50,'{"gpm": 420, "matches": 300, "win_rate": 0.57}'),
(12,5,3,'[0.4, 0.7, 0.8]',3.00,'{"gpm": 380, "matches": 140, "win_rate": 0.51}'),
(13,7,3,'[0.5, 0.6, 0.7]',5.00,'{"gpm": 400, "matches": 110, "win_rate": 0.54}'),
(14,6,4,'[0.7, 0.8, 0.5]',4.00,'{"goals": 310, "matches": 200, "win_rate": 0.6}'),
(15,8,4,'[0.6, 0.6, 0.6]',4.00,'{"goals": 190, "matches": 130, "win_rate": 0.52}');

INSERT INTO security_audit_log VALUES
(1,1,'LOGIN','2026-10-02 18:28:01'),
(2,2,'LOGIN','2026-10-02 18:28:01'),
(3,4,'FAILED_LOGIN','2026-10-02 18:28:01'),
(4,4,'FAILED_LOGIN','2026-10-02 18:28:01'),
(5,6,'PASSWORD_RESET','2026-10-02 18:28:01'),
(6,9,'ROLE_CHANGE: player -> moderator','2026-10-02 18:28:01'),
(7,3,'ROLE_CHANGE: player -> moderator','2026-10-02 18:39:56'),
(8,2,'LOBBY_COMPLETED: 2','2026-10-02 18:41:31');

INSERT INTO player_connections VALUES
(1,1,2,'friend'),
(2,3,1,'friend'),
(3,4,1,'block'),
(4,5,3,'friend'),
(5,7,8,'follow'),
(6,6,2,'follow'),
(7,8,7,'friend');

INSERT INTO player_feedback VALUES
(1,1,2,5),
(2,3,2,4),
(3,2,1,4),
(4,5,1,5),
(5,1,3,5),
(6,2,3,4),
(7,4,5,3),
(8,6,4,2),
(9,5,4,3),
(10,7,8,4),
(11,8,7,5),
(12,3,6,4),
(13,4,2,5);

INSERT INTO lobby_participants VALUES
(1,1,1,'Duelist',1),
(2,1,2,'Sentinel',0),
(3,1,3,'Controller',1),
(4,2,2,'Fragger',0),
(5,2,1,'Support',0),
(6,2,7,'Scout',0),
(7,3,3,'Shotcaller',1),
(8,3,5,'Support',1),
(9,3,7,'Carry',1),
(10,4,5,'Initiator',0),
(11,4,6,'Controller',0),
(12,1,4,'Duelist',0),
(13,1,5,'Sentinel',0),
(14,4,1,'Duelist',0);
