"""SquadLink Frontend Configuration and Constants."""

APP_TITLE = "SquadLink"
APP_SUBTITLE = "Vector-Driven Player Matchmaking & Telemetry Platform"
APP_ICON = "🎮"

# Brand Theme Colors
COLOR_PRIMARY = "#E63956"
COLOR_PRIMARY_HOVER = "#D81B60"
COLOR_PRIMARY_LIGHT = "#FFF0F3"
COLOR_BACKGROUND = "#F7F8FC"
COLOR_CARD_BG = "#FFFFFF"
COLOR_TEXT_MAIN = "#1A1B2F"
COLOR_TEXT_MUTED = "#6B7280"
COLOR_BORDER = "#E5E7EB"

# Default Database Settings
DEFAULT_MYSQL_HOST = "localhost"
DEFAULT_MYSQL_PORT = 3306
DEFAULT_MYSQL_USER = "root"
DEFAULT_MYSQL_DB = "squadlink"
DEFAULT_MONGO_URI = "mongodb://localhost:27017"
DEFAULT_MONGO_DB = "squadlink_nosql"

# Game Metadata Defaults
DEFAULT_GAMES = [
    {"GameID": 1, "Title": "Valorant", "Genre": "Tactical Shooter"},
    {"GameID": 2, "Title": "Apex Legends", "Genre": "Battle Royale"},
    {"GameID": 3, "Title": "Dota 2", "Genre": "MOBA"},
    {"GameID": 4, "Title": "Rocket League", "Genre": "Sports"},
    {"GameID": 5, "Title": "Overwatch 2", "Genre": "FPS"},
]

# Squad Roles by Game / Generic
SQUAD_ROLES = [
    "Duelist",
    "Sentinel",
    "Controller",
    "Initiator",
    "Support",
    "Fragger",
    "Shotcaller",
    "Carry",
    "Scout",
    "Flex",
]

NAVIGATION_TABS = [
    "Lobbies",
    "Join a lobby",
    "Find a match",
    "Ratings",
    "Players",
    "Gameplay Telemetry",
    "Activity Feed",
    "Admin",
]
