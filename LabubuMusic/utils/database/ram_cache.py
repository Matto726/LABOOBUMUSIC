import json
import os
from pytgcalls.types.input_stream.quality import AudioQuality, VideoQuality
from MattoMusic.core.db_setup import mongodb

db_channel = mongodb.cplaymode
db_commands = mongodb.commands
db_clean = mongodb.cleanmode
db_playmode = mongodb.playmode
db_playtype = mongodb.playtypedb
db_lang = mongodb.language
db_auth = mongodb.adminauth
db_video = mongodb.Champuvideocalls
db_onoff = mongodb.onoffper
db_autoend = mongodb.autoend
db_notes = mongodb.notes
db_filters = mongodb.filters

cache_loop = {}
cache_playtype = {}
cache_playmode = {}
cache_channelconnect = {}
cache_lang = {}
cache_pause = {}
cache_mute = {}
cache_active_audio = []
cache_active_video = []
cache_nonadmin = {}
cache_vlimit = []
cache_maintenance = []
cache_autoend = {}
cache_welcome_msgs = {"welcome": {}, "goodbye": {}}

AUDIO_CFG_PATH = "audio_bitrate.json"
VIDEO_CFG_PATH = "video_bitrate.json"

def load_json_cache(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as file_obj:
            return json.load(file_obj)
    return {}

def flush_json_cache(filepath, dict_data):
    with open(filepath, "w") as file_obj:
        json.dump(dict_data, file_obj, indent=4)

mem_audio_cfg = load_json_cache(AUDIO_CFG_PATH)
mem_video_cfg = load_json_cache(VIDEO_CFG_PATH)

async def record_audio_bitrate(c_id: int, bit_val: str):
    mem_audio_cfg[str(c_id)] = bit_val
    flush_json_cache(AUDIO_CFG_PATH, mem_audio_cfg)

async def record_video_bitrate(c_id: int, bit_val: str):
    mem_video_cfg[str(c_id)] = bit_val
    flush_json_cache(VIDEO_CFG_PATH, mem_video_cfg)

async def fetch_audio_bitrate_str(c_id: int) -> str:
    return mem_audio_cfg.get(str(c_id), "HIGH")

async def fetch_video_bitrate_str(c_id: int) -> str:
    return mem_video_cfg.get(str(c_id), "HD_720p")

async def fetch_audio_quality(c_id: int):
    qual_map = {
        "STUDIO": AudioQuality.STUDIO,
        "HIGH": AudioQuality.HIGH,
        "MEDIUM": AudioQuality.MEDIUM,
        "LOW": AudioQuality.LOW,
    }
    current_mode = mem_audio_cfg.get(str(c_id), "MEDIUM")
    return qual_map.get(current_mode, AudioQuality.MEDIUM)

async def fetch_video_quality(c_id: int):
    qual_map = {
        "UHD_4K": VideoQuality.UHD_4K,
        "QHD_2K": VideoQuality.QHD_2K,
        "FHD_1080p": VideoQuality.FHD_1080p,
        "HD_720p": VideoQuality.HD_720p,
        "SD_480p": VideoQuality.SD_480p,
        "SD_360p": VideoQuality.SD_360p,
    }
    current_mode = mem_video_cfg.get(str(c_id), "SD_480p")
    return qual_map.get(current_mode, VideoQuality.SD_480p)