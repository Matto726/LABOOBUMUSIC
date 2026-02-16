import os
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "Matto726")
BOT_USERNAME = os.getenv("BOT_USERNAME", "MattoMusicBot")

MONGO_DB_URI = os.getenv("MONGO_DB_URI", "")
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", "0"))
HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME", "")
HEROKU_API_KEY = os.getenv("HEROKU_API_KEY", "")

UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "https://github.com/Matto726/LabubuMusic")
UPSTREAM_BRANCH = os.getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = os.getenv("GIT_TOKEN", None)

SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/Laboobubots")
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/laboobusupportbot")
INSTAGRAM = os.getenv("INSTAGRAM", "https://instagram.com")
YOUTUBE = os.getenv("YOUTUBE", "https://youtube.com")
GITHUB = os.getenv("GITHUB", "https://github.com/Matto726")
DONATE = os.getenv("DONATE", "https://t.me/laboobusupportbot")
START_IMG_URL = os.getenv("START_IMG_URL", "https://files.catbox.moe/7q8bfg.jpg")

PING_IMG_URL = os.getenv("PING_IMG_URL", "https://files.catbox.moe/eehxb4.jpg")
PLAYLIST_IMG_URL = os.getenv("PLAYLIST_IMG_URL", "https://files.catbox.moe/eehxb4.jpg")
STATS_IMG_URL = os.getenv("STATS_IMG_URL", "https://files.catbox.moe/eehxb4.jpg")
TELEGRAM_AUDIO_URL = os.getenv("TELEGRAM_AUDIO_URL", "https://files.catbox.moe/eehxb4.jpg")
TELEGRAM_VIDEO_URL = os.getenv("TELEGRAM_VIDEO_URL", "https://files.catbox.moe/eehxb4.jpg")
STREAM_IMG_URL = os.getenv("STREAM_IMG_URL", "https://files.catbox.moe/eehxb4.jpg")
SOUNCLOUD_IMG_URL = os.getenv("SOUNCLOUD_IMG_URL", "https://files.catbox.moe/eehxb4.jpg")
YOUTUBE_IMG_URL = os.getenv("YOUTUBE_IMG_URL", "https://files.catbox.moe/eehxb4.jpg")
SPOTIFY_ARTIST_IMG_URL = os.getenv("SPOTIFY_ARTIST_IMG_URL", "https://files.catbox.moe/eehxb4.jpg")
SPOTIFY_ALBUM_IMG_URL = os.getenv("SPOTIFY_ALBUM_IMG_URL", "https://files.catbox.moe/eehxb4.jpg")
SPOTIFY_PLAYLIST_IMG_URL = os.getenv("SPOTIFY_PLAYLIST_IMG_URL", "https://files.catbox.moe/eehxb4.jpg")

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

TEMP_DB_FOLDER = "tempdb"

def time_to_seconds(time_str):
    time_parts = time_str.split(":")
    if len(time_parts) == 3:
        return int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
    elif len(time_parts) == 2:
        return int(time_parts[0]) * 60 + int(time_parts[1])
    return int(time_parts[0])

DURATION_LIMIT_MIN = "600"
DURATION_LIMIT = time_to_seconds(DURATION_LIMIT_MIN)

STRING1 = os.getenv("STRING_SESSION", None)
STRING2 = os.getenv("STRING_SESSION2", None)
STRING3 = os.getenv("STRING_SESSION3", None)
STRING4 = os.getenv("STRING_SESSION4", None)
STRING5 = os.getenv("STRING_SESSION5", None)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", None)

PLAYLIST_FETCH_LIMIT = int(os.getenv("PLAYLIST_FETCH_LIMIT", 25))
TG_AUDIO_FILESIZE_LIMIT = int(os.getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(os.getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

PRIVACY_LINK = os.getenv("PRIVACY_LINK", "https://telegra.ph/Privacy-Policy-for-ShrutiMusic-11-26")