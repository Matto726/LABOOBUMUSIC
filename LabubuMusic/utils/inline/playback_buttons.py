import math
from pyrogram.types import InlineKeyboardButton
from MattoMusic.utils.formatters import time_to_seconds
from config import SUPPORT_GROUP

def track_markup(_, videoid, user_id, channel, fplay):
    return [
        [
            InlineKeyboardButton(text=_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}"),
            InlineKeyboardButton(text=_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}")
        ],
    ]

def stream_markup_timer(_, chat_id, played, dur):
    try:
        played_sec = time_to_seconds(played)
        total_sec = time_to_seconds(dur)
        pct = (played_sec / total_sec) * 100
        bar = "{0}{1}".format(
            "".join(["▰" for i in range(math.floor(pct / 10))]),
            "".join(["▱" for i in range(10 - math.floor(pct / 10))]),
        )
    except Exception:
        bar = "▰▰▰▰▰▰▰▰▰▰"
        
    return [
        [
            InlineKeyboardButton(text=f"{played} {bar} {dur}", callback_data="GetTimer")
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="〶", callback_data=f"ADMIN Shuffle|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Loop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]

def stream_markup(_, chat_id):
    return [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]

def telegram_markup(_, chat_id):
    return [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]

def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [
            InlineKeyboardButton(text=_["P_B_3"], callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}"),
        ],
    ]

def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    return [
        [
            InlineKeyboardButton(text=_["P_B_1"], callback_data=f"SamarPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"),
            InlineKeyboardButton(text=_["P_B_2"], callback_data=f"SamarPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {videoid}|{user_id}"),
        ],
    ]

def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    short_query = f"{query[:20]}"
    return [
        [
            InlineKeyboardButton(text=_["P_B_1"], callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}"),
            InlineKeyboardButton(text=_["P_B_2"], callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(text="◁", callback_data=f"slider B|{query_type}|{short_query}|{user_id}|{channel}|{fplay}"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {short_query}|{user_id}"),
            InlineKeyboardButton(text="▷", callback_data=f"slider F|{query_type}|{short_query}|{user_id}|{channel}|{fplay}"),
        ],
    ]