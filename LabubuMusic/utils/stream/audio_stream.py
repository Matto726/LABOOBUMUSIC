import os
from random import randint
from typing import Union
from pyrogram.types import InlineKeyboardMarkup

import config
from MattoMusic import Carbon, YouTube, app
from MattoMusic.core.stream_call import Samar
from MattoMusic.misc import db
from MattoMusic.utils.database import add_active_video_chat, is_active_chat
from MattoMusic.utils.exceptions import AssistantErr
from MattoMusic.utils.inline import aq_markup, close_markup, stream_markup
from MattoMusic.utils.pastebin import SamarBin
from MattoMusic.utils.stream.manage_queue import add_to_queue, add_to_queue_index
from MattoMusic.utils.thumbnails import gen_thumb

async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
):
    is_video_mode = True if video else None
    is_force_play = True if forceplay else None

    if streamtype == "playlist":
        total_added = 0
        msg_text = ""
        for track in result:
            if total_added == config.PLAYLIST_FETCH_LIMIT:
                break
            
            track_vidid = track["vidid"]
            track_title = track["title"].title()
            track_dur = track["duration_min"]
            
            try:
                await add_to_queue(
                    chat_id, original_chat_id, f"vid_{track_vidid}", track_title, track_dur, user_name, track_vidid, user_id, "audio" if not is_video_mode else "video", forceplay=is_force_play
                )
                total_added += 1
                msg_text += f"{total_added}. {track_title[:25]}\n"
            except Exception:
                continue
        
        if not msg_text:
            return await mystic.edit_text(_["play_3"])
            
        paste_url = await SamarBin(msg_text)
        target_link = paste_url if spotify else f"https://youtube.com/watch?v={result[0]['vidid']}"
        
        button = aq_markup(_, chat_id)
        run_msg = await app.send_photo(
            original_chat_id,
            photo=config.PLAYLIST_IMG_URL if spotify else result[0]["thumb"],
            caption=_["play_19"].format(total_added, target_link),
            reply_markup=InlineKeyboardMarkup(button),
        )
        
        if not await is_active_chat(chat_id):
            if not is_force_play:
                db[chat_id] = []
            await Samar.join_call(
                chat_id, original_chat_id, f"vid_{result[0]['vidid']}", video=is_video_mode
            )
            if is_video_mode:
                await add_active_video_chat(chat_id)
        
        db[chat_id][0]["mystic"] = run_msg
        db[chat_id][0]["markup"] = "tg"
        await mystic.delete()
        
    elif streamtype == "youtube":
        track_link = result["link"]
        track_vidid = result["vidid"]
        track_title = result["title"].title()
        track_dur = result["duration_min"]
        track_thumb = result["thumb"]
        
        status_msg = await mystic.edit_text(_["play_4"])
        
        active_status = await is_active_chat(chat_id)
        if not active_status:
            if not is_force_play:
                db[chat_id] = []
            await Samar.join_call(chat_id, original_chat_id, track_link, video=is_video_mode, image=track_thumb)
            await add_to_queue(chat_id, original_chat_id, f"vid_{track_vidid}", track_title, track_dur, user_name, track_vidid, user_id, "video" if is_video_mode else "audio")
            
            if is_video_mode:
                await add_active_video_chat(chat_id)
                
            btn_markup = stream_markup(_, chat_id)
            gen_img = await gen_thumb(track_vidid)
            
            run_msg = await app.send_photo(
                original_chat_id,
                photo=gen_img,
                caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{track_vidid}", track_title[:23], track_dur, user_name),
                reply_markup=InlineKeyboardMarkup(btn_markup),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "stream"
            await status_msg.delete()
        else:
            await add_to_queue(chat_id, original_chat_id, f"vid_{track_vidid}", track_title, track_dur, user_name, track_vidid, user_id, "video" if is_video_mode else "audio", forceplay=is_force_play)
            
            pos = len(db.get(chat_id)) - 1
            btn_markup = aq_markup(_, chat_id)
            
            await status_msg.edit_text(
                _["queue_4"].format(pos, track_title[:27], track_dur, user_name),
                reply_markup=InlineKeyboardMarkup(btn_markup),
            )

    elif streamtype == "soundcloud":
        track_path = result["filepath"]
        track_title = result["title"]
        track_dur = result["duration_min"]
        
        active_status = await is_active_chat(chat_id)
        if not active_status:
            if not is_force_play:
                db[chat_id] = []
            await Samar.join_call(chat_id, original_chat_id, track_path, video=is_video_mode)
            await add_to_queue(chat_id, original_chat_id, track_path, track_title, track_dur, user_name, "soundcloud", user_id, "audio")
            
            if is_video_mode:
                await add_active_video_chat(chat_id)
                
            btn_markup = stream_markup(_, chat_id)
            run_msg = await app.send_photo(
                original_chat_id,
                photo=config.SOUNCLOUD_IMG_URL,
                caption=_["stream_1"].format(config.SUPPORT_GROUP, track_title[:23], track_dur, user_name),
                reply_markup=InlineKeyboardMarkup(btn_markup),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "tg"
            await mystic.delete()
        else:
            await add_to_queue(chat_id, original_chat_id, track_path, track_title, track_dur, user_name, "soundcloud", user_id, "audio", forceplay=is_force_play)
            
            pos = len(db.get(chat_id)) - 1
            btn_markup = aq_markup(_, chat_id)
            
            await mystic.edit_text(
                _["queue_4"].format(pos, track_title[:27], track_dur, user_name),
                reply_markup=InlineKeyboardMarkup(btn_markup),
            )
            
    elif streamtype == "telegram":
        track_path = result["path"]
        track_title = result["title"]
        track_dur = result["dur"]
        track_link = result["link"]
        
        active_status = await is_active_chat(chat_id)
        if not active_status:
            if not is_force_play:
                db[chat_id] = []
            await Samar.join_call(chat_id, original_chat_id, track_path, video=is_video_mode)
            await add_to_queue(chat_id, original_chat_id, track_path, track_title, track_dur, user_name, "telegram", user_id, "video" if is_video_mode else "audio")
            
            if is_video_mode:
                await add_active_video_chat(chat_id)
                
            btn_markup = stream_markup(_, chat_id)
            run_msg = await app.send_photo(
                original_chat_id,
                photo=config.TELEGRAM_VIDEO_URL if is_video_mode else config.TELEGRAM_AUDIO_URL,
                caption=_["stream_1"].format(track_link, track_title[:23], track_dur, user_name),
                reply_markup=InlineKeyboardMarkup(btn_markup),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "tg"
            await mystic.delete()
        else:
            await add_to_queue(chat_id, original_chat_id, track_path, track_title, track_dur, user_name, "telegram", user_id, "video" if is_video_mode else "audio", forceplay=is_force_play)
            
            pos = len(db.get(chat_id)) - 1
            btn_markup = aq_markup(_, chat_id)
            
            await mystic.edit_text(
                _["queue_4"].format(pos, track_title[:27], track_dur, user_name),
                reply_markup=InlineKeyboardMarkup(btn_markup),
            )
            
    elif streamtype == "live":
        track_link = result["link"]
        track_vidid = result["vidid"]
        track_title = result["title"].title()
        track_dur = "Live Stream"
        track_thumb = result["thumb"]
        
        active_status = await is_active_chat(chat_id)
        if not active_status:
            if not is_force_play:
                db[chat_id] = []
            await Samar.join_call(chat_id, original_chat_id, track_link, video=is_video_mode, image=track_thumb)
            await add_to_queue(chat_id, original_chat_id, f"live_{track_vidid}", track_title, track_dur, user_name, track_vidid, user_id, "video" if is_video_mode else "audio")
            
            if is_video_mode:
                await add_active_video_chat(chat_id)
                
            btn_markup = stream_markup(_, chat_id)
            gen_img = await gen_thumb(track_vidid)
            
            run_msg = await app.send_photo(
                original_chat_id,
                photo=gen_img,
                caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{track_vidid}", track_title[:23], track_dur, user_name),
                reply_markup=InlineKeyboardMarkup(btn_markup),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "tg"
            await mystic.delete()
        else:
            await add_to_queue(chat_id, original_chat_id, f"live_{track_vidid}", track_title, track_dur, user_name, track_vidid, user_id, "video" if is_video_mode else "audio", forceplay=is_force_play)
            
            pos = len(db.get(chat_id)) - 1
            btn_markup = aq_markup(_, chat_id)
            
            await mystic.edit_text(
                _["queue_4"].format(pos, track_title[:27], track_dur, user_name),
                reply_markup=InlineKeyboardMarkup(btn_markup),
            )

    elif streamtype == "index":
        track_link = result
        track_title = "Index or M3u8 Link"
        track_dur = "Unknown"
        
        active_status = await is_active_chat(chat_id)
        if not active_status:
            if not is_force_play:
                db[chat_id] = []
            await Samar.join_call(chat_id, original_chat_id, track_link, video=is_video_mode)
            await add_to_queue_index(chat_id, original_chat_id, "index_url", track_title, track_dur, user_name, track_link, "video" if is_video_mode else "audio", forceplay=is_force_play)
            
            if is_video_mode:
                await add_active_video_chat(chat_id)
                
            btn_markup = stream_markup(_, chat_id)
            
            run_msg = await app.send_photo(
                original_chat_id,
                photo=config.STREAM_IMG_URL,
                caption=_["stream_2"].format(user_name),
                reply_markup=InlineKeyboardMarkup(btn_markup),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "tg"
            await mystic.delete()
        else:
            await add_to_queue_index(chat_id, original_chat_id, "index_url", track_title, track_dur, user_name, track_link, "video" if is_video_mode else "audio", forceplay=is_force_play)
            
            pos = len(db.get(chat_id)) - 1
            btn_markup = aq_markup(_, chat_id)
            
            await mystic.edit_text(
                _["queue_4"].format(pos, track_title[:27], track_dur, user_name),
                reply_markup=InlineKeyboardMarkup(btn_markup),
            )