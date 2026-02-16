import asyncio
import os
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery, InputMediaPhoto

import config
from MattoMusic import app
from MattoMusic.misc import db
from MattoMusic.utils import SamarBin, get_channeplayCB, seconds_to_min
from MattoMusic.utils.database import get_cmode, is_active_chat, is_music_playing
from MattoMusic.utils.decorators.language import language, languageCB
from MattoMusic.utils.inline import queue_back_markup, queue_markup
from config import BANNED_USERS

ui_queue_tracker = {}

def get_track_thumb(vid_id):
    local_path = f"cache/{vid_id}.png"
    return local_path if os.path.isfile(local_path) else config.YOUTUBE_IMG_URL

def calculate_duration(play_list):
    track_path = play_list[0]["file"]
    if "index_" in track_path or "live_" in track_path:
        return "Unknown"
    
    total_sec = int(play_list[0]["seconds"])
    return "Unknown" if total_sec == 0 else play_list[0]["dur"]

@app.on_callback_query(filters.regex("GetTimer") & ~BANNED_USERS)
@languageCB
async def track_timer_cb(client, query: CallbackQuery, _):
    cb_args = query.data.split(None, 1)[1]
    v_id, c_play = cb_args.split("|")
    
    try: target_chat, _ = await get_channeplayCB(_, c_play, query)
    except Exception: return
    
    if not await is_active_chat(target_chat):
        return await query.answer(_["general_5"], show_alert=True)
        
    play_data = db.get(target_chat)
    if not play_data:
        return await query.answer(_["queue_2"], show_alert=True)
        
    try: await query.answer()
    except Exception: pass
    
    if str(play_data[0]["vidid"]) != str(v_id):
        return await query.answer(_["queue_1"], show_alert=True)
        
    track_dur = calculate_duration(play_data)
    ui_queue_tracker[v_id] = True
    
    btn_markup = queue_markup(_, track_dur, c_play, v_id, seconds_to_min(play_data[0]["played"]), play_data[0]["dur"])
    new_media = InputMediaPhoto(media=get_track_thumb(v_id), caption=_["queue_3"].format(play_data[0]["title"], play_data[0]["played"], play_data[0]["dur"]))
    
    menu_msg = await query.edit_message_media(media=new_media, reply_markup=btn_markup)
    
    if track_dur != "Unknown":
        try:
            while db[target_chat][0]["vidid"] == v_id:
                await asyncio.sleep(5)
                if await is_active_chat(target_chat) and ui_queue_tracker.get(v_id):
                    if await is_music_playing(target_chat):
                        try:
                            live_btns = queue_markup(_, track_dur, c_play, v_id, seconds_to_min(db[target_chat][0]["played"]), db[target_chat][0]["dur"])
                            await menu_msg.edit_reply_markup(reply_markup=live_btns)
                        except FloodWait: pass
                    else: pass
                else: break
        except Exception: return

@app.on_callback_query(filters.regex("GetQueued") & ~BANNED_USERS)
@languageCB
async def get_queue_list_cb(client, query: CallbackQuery, _):
    cb_args = query.data.split(None, 1)[1]
    c_play = cb_args.split("|")[0]
    
    try: target_chat, _ = await get_channeplayCB(_, c_play, query)
    except Exception: return
    
    if not await is_active_chat(target_chat):
        return await query.answer(_["general_5"], show_alert=True)
        
    play_data = db.get(target_chat)
    if not play_data:
        return await query.answer(_["queue_2"], show_alert=True)
        
    try: await query.answer()
    except Exception: pass
    
    q_text = _["queue_4"]
    for i, track in enumerate(play_data[1:21], 1):
        q_text += f"{i}. {track['title']} | {track['dur']} | By {track['by']}\n\n"
        
    btn_markup = queue_back_markup(_, c_play)
    await query.edit_message_text(q_text, reply_markup=btn_markup)