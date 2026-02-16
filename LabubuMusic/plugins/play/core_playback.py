import random
import string

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from MattoMusic import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from MattoMusic.core.stream_call import Samar
from MattoMusic.utils import seconds_to_min, time_to_seconds
from MattoMusic.utils.channelplay import get_channeplayCB
from MattoMusic.utils.decorators.language import languageCB
from MattoMusic.utils.decorators.play import PlayWrapper
from MattoMusic.utils.formatters import formats
from MattoMusic.utils.inline import (
    botplaylist_markup, livestream_markup, playlist_markup,
    slider_markup, track_markup,
)
from MattoMusic.utils.logger import play_logs
from MattoMusic.utils.stream.stream import stream
from config import BANNED_USERS, lyrical

@app.on_message(
    filters.command(["play", "vplay", "cplay", "cvplay", "playforce", "vplayforce", "cplayforce", "cvplayforce"])
    & filters.group & ~BANNED_USERS
)
@PlayWrapper
async def initiate_playback_command(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):
    status_msg = await message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])
    
    p_id = None
    is_slider = None
    p_type = None
    is_spotify = None
    u_id = message.from_user.id
    u_name = message.from_user.first_name
    
    tg_audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    tg_video = (message.reply_to_message.video or message.reply_to_message.document) if message.reply_to_message else None
    
    if tg_audio:
        if tg_audio.file_size > 104857600:
            return await status_msg.edit_text(_["play_5"])
            
        if tg_audio.duration > config.DURATION_LIMIT:
            return await status_msg.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, app.mention))
            
        f_path = await Telegram.get_filepath(audio=tg_audio)
        if await Telegram.download(_, message, status_msg, f_path):
            m_link = await Telegram.get_link(message)
            f_name = await Telegram.get_filename(tg_audio, audio=True)
            t_dur = await Telegram.get_duration(tg_audio, f_path)
            track_info = {"title": f_name, "link": m_link, "path": f_path, "dur": t_dur}

            try:
                await stream(_, status_msg, u_id, track_info, chat_id, u_name, message.chat.id, streamtype="telegram", forceplay=fplay)
            except Exception as err:
                err_type = type(err).__name__
                return await status_msg.edit_text(err if err_type == "AssistantErr" else _["general_2"].format(err_type))
            return await status_msg.delete()
        return

    elif tg_video:
        if message.reply_to_message.document:
            try:
                ext_chk = tg_video.file_name.split(".")[-1]
                if ext_chk.lower() not in formats:
                    return await status_msg.edit_text(_["play_7"].format(f"{' | '.join(formats)}"))
            except Exception:
                return await status_msg.edit_text(_["play_7"].format(f"{' | '.join(formats)}"))
                
        if tg_video.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
            return await status_msg.edit_text(_["play_8"])
            
        f_path = await Telegram.get_filepath(video=tg_video)
        if await Telegram.download(_, message, status_msg, f_path):
            m_link = await Telegram.get_link(message)
            f_name = await Telegram.get_filename(tg_video)
            t_dur = await Telegram.get_duration(tg_video, f_path)
            track_info = {"title": f_name, "link": m_link, "path": f_path, "dur": t_dur}
            
            try:
                await stream(_, status_msg, u_id, track_info, chat_id, u_name, message.chat.id, video=True, streamtype="telegram", forceplay=fplay)
            except Exception as err:
                err_type = type(err).__name__
                return await status_msg.edit_text(err if err_type == "AssistantErr" else _["general_2"].format(err_type))
            return await status_msg.delete()
        return

    elif url:
        if await YouTube.exists(url):
            if "playlist" in url:
                try: track_info = await YouTube.playlist(url, config.PLAYLIST_FETCH_LIMIT, message.from_user.id)
                except Exception: return await status_msg.edit_text(_["play_3"])
                
                streamtype = "playlist"
                p_type = "yt"
                p_id = url.split("=")[1].split("&")[0] if "&" in url else url.split("=")[1]
                t_img = config.PLAYLIST_IMG_URL
                t_cap = _["play_9"]
            else:
                try: track_info, t_id = await YouTube.track(url)
                except Exception: return await status_msg.edit_text(_["play_3"])
                
                streamtype = "youtube"
                t_img = track_info["thumb"]
                t_cap = _["play_10"].format(track_info["title"], track_info["duration_min"])
                
        elif await Spotify.valid(url):
            is_spotify = True
            if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
                return await status_msg.edit_text("» sᴘᴏᴛɪғʏ ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ʏᴇᴛ.\n\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
                
            if "track" in url:
                try: track_info, t_id = await Spotify.track(url)
                except Exception: return await status_msg.edit_text(_["play_3"])
                streamtype = "youtube"
                t_img = track_info["thumb"]
                t_cap = _["play_10"].format(track_info["title"], track_info["duration_min"])
            elif "playlist" in url:
                try: track_info, p_id = await Spotify.playlist(url)
                except Exception: return await status_msg.edit_text(_["play_3"])
                streamtype, p_type = "playlist", "spplay"
                t_img, t_cap = config.SPOTIFY_PLAYLIST_IMG_URL, _["play_11"].format(app.mention, message.from_user.mention)
            elif "album" in url:
                try: track_info, p_id = await Spotify.album(url)
                except Exception: return await status_msg.edit_text(_["play_3"])
                streamtype, p_type = "playlist", "spalbum"
                t_img, t_cap = config.SPOTIFY_ALBUM_IMG_URL, _["play_11"].format(app.mention, message.from_user.mention)
            elif "artist" in url:
                try: track_info, p_id = await Spotify.artist(url)
                except Exception: return await status_msg.edit_text(_["play_3"])
                streamtype, p_type = "playlist", "spartist"
                t_img, t_cap = config.SPOTIFY_ARTIST_IMG_URL, _["play_11"].format(message.from_user.first_name)
            else:
                return await status_msg.edit_text(_["play_15"])
                
        elif await Apple.valid(url):
            if "album" in url:
                try: track_info, t_id = await Apple.track(url)
                except Exception: return await status_msg.edit_text(_["play_3"])
                streamtype, t_img = "youtube", track_info["thumb"]
                t_cap = _["play_10"].format(track_info["title"], track_info["duration_min"])
            elif "playlist" in url:
                is_spotify = True
                try: track_info, p_id = await Apple.playlist(url)
                except Exception: return await status_msg.edit_text(_["play_3"])
                streamtype, p_type = "playlist", "apple"
                t_cap, t_img = _["play_12"].format(app.mention, message.from_user.mention), url
            else:
                return await status_msg.edit_text(_["play_3"])
                
        elif await Resso.valid(url):
            try: track_info, t_id = await Resso.track(url)
            except Exception: return await status_msg.edit_text(_["play_3"])
            streamtype, t_img = "youtube", track_info["thumb"]
            t_cap = _["play_10"].format(track_info["title"], track_info["duration_min"])
            
        elif await SoundCloud.valid(url):
            try: track_info, track_path = await SoundCloud.download(url)
            except Exception: return await status_msg.edit_text(_["play_3"])
            
            if track_info["duration_sec"] > config.DURATION_LIMIT:
                return await status_msg.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, app.mention))
                
            try:
                await stream(_, status_msg, u_id, track_info, chat_id, u_name, message.chat.id, streamtype="soundcloud", forceplay=fplay)
            except Exception as err:
                err_type = type(err).__name__
                return await status_msg.edit_text(err if err_type == "AssistantErr" else _["general_2"].format(err_type))
            return await status_msg.delete()
            
        else:
            try: await Samar.stream_call(url)
            except NoActiveGroupCall:
                await status_msg.edit_text(_["black_9"])
                return await app.send_message(chat_id=config.LOG_GROUP_ID, text=_["play_17"])
            except Exception as err:
                return await status_msg.edit_text(_["general_2"].format(type(err).__name__))
                
            await status_msg.edit_text(_["str_2"])
            try:
                await stream(_, status_msg, message.from_user.id, url, chat_id, message.from_user.first_name, message.chat.id, video=video, streamtype="index", forceplay=fplay)
            except Exception as err:
                err_type = type(err).__name__
                return await status_msg.edit_text(err if err_type == "AssistantErr" else _["general_2"].format(err_type))
            return await play_logs(message, streamtype="M3u8 or Index Link")
            
    else:
        if len(message.command) < 2:
            return await status_msg.edit_text(_["play_18"], reply_markup=InlineKeyboardMarkup(botplaylist_markup(_)))
            
        is_slider = True
        q_term = message.text.split(None, 1)[1].replace("-v", "")
        
        try: track_info, t_id = await YouTube.track(q_term)
        except Exception: return await status_msg.edit_text(_["play_3"])
        streamtype = "youtube"

    if str(playmode) == "Direct":
        if not p_type:
            if track_info["duration_min"]:
                if time_to_seconds(track_info["duration_min"]) > config.DURATION_LIMIT:
                    return await status_msg.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, app.mention))
            else:
                btns = livestream_markup(_, t_id, u_id, "v" if video else "a", "c" if channel else "g", "f" if fplay else "d")
                return await status_msg.edit_text(_["play_13"], reply_markup=InlineKeyboardMarkup(btns))
                
        try:
            await stream(_, status_msg, u_id, track_info, chat_id, u_name, message.chat.id, video=video, streamtype=streamtype, spotify=is_spotify, forceplay=fplay)
        except Exception as err:
            err_type = type(err).__name__
            return await status_msg.edit_text(err if err_type == "AssistantErr" else _["general_2"].format(err_type))
            
        await status_msg.delete()
        return await play_logs(message, streamtype=streamtype)
    else:
        if p_type:
            r_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
            lyrical[r_hash] = p_id
            btns = playlist_markup(_, r_hash, message.from_user.id, p_type, "c" if channel else "g", "f" if fplay else "d")
            
            await status_msg.delete()
            await message.reply_photo(photo=t_img, caption=t_cap, reply_markup=InlineKeyboardMarkup(btns))
            return await play_logs(message, streamtype=f"Playlist : {p_type}")
        else:
            if is_slider:
                btns = slider_markup(_, t_id, message.from_user.id, q_term, 0, "c" if channel else "g", "f" if fplay else "d")
                await status_msg.delete()
                await message.reply_photo(photo=track_info["thumb"], caption=_["play_10"].format(track_info["title"].title(), track_info["duration_min"]), reply_markup=InlineKeyboardMarkup(btns))
                return await play_logs(message, streamtype=f"Searched on Youtube")
            else:
                btns = track_markup(_, t_id, message.from_user.id, "c" if channel else "g", "f" if fplay else "d")
                await status_msg.delete()
                await message.reply_photo(photo=t_img, caption=t_cap, reply_markup=InlineKeyboardMarkup(btns))
                return await play_logs(message, streamtype=f"URL Searched Inline")

@app.on_callback_query(filters.regex("MusicStream") & ~BANNED_USERS)
@languageCB
async def music_playback_callback(client, query, _):
    cb_data = query.data.strip().split(None, 1)[1]
    v_id, u_id, mode_val, c_play, f_play = cb_data.split("|")
    
    if query.from_user.id != int(u_id):
        try: return await query.answer(_["playcb_1"], show_alert=True)
        except Exception: return
        
    try: target_chat, target_channel = await get_channeplayCB(_, c_play, query)
    except Exception: return
    
    i_name = query.from_user.first_name
    try:
        await query.message.delete()
        await query.answer()
    except Exception: pass
    
    status_msg = await query.message.reply_text(_["play_2"].format(target_channel) if target_channel else _["play_1"])
    
    try: track_info, t_id = await YouTube.track(v_id, True)
    except Exception: return await status_msg.edit_text(_["play_3"])
    
    if track_info["duration_min"]:
        if time_to_seconds(track_info["duration_min"]) > config.DURATION_LIMIT:
            return await status_msg.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, app.mention))
    else:
        btns = livestream_markup(_, t_id, query.from_user.id, mode_val, "c" if c_play == "c" else "g", "f" if f_play else "d")
        return await status_msg.edit_text(_["play_13"], reply_markup=InlineKeyboardMarkup(btns))
        
    v_mode = True if mode_val == "v" else None
    f_mode = True if f_play == "f" else None
    
    try:
        await stream(_, status_msg, query.from_user.id, track_info, target_chat, i_name, query.message.chat.id, v_mode, streamtype="youtube", forceplay=f_mode)
    except Exception as err:
        err_type = type(err).__name__
        return await status_msg.edit_text(err if err_type == "AssistantErr" else _["general_2"].format(err_type))
        
    return await status_msg.delete()

@app.on_callback_query(filters.regex("AnonymousAdmin") & ~BANNED_USERS)
async def verify_anonymous_admin(client, query):
    try:
        await query.answer("» ʀᴇᴠᴇʀᴛ ʙᴀᴄᴋ ᴛᴏ ᴜsᴇʀ ᴀᴄᴄᴏᴜɴᴛ :\n\nᴏᴘᴇɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs.\n-> ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs\n-> ᴄʟɪᴄᴋ ᴏɴ ʏᴏᴜʀ ɴᴀᴍᴇ\n-> ᴜɴᴄʜᴇᴄᴋ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs.", show_alert=True)
    except Exception: pass

@app.on_callback_query(filters.regex("SamarPlaylists") & ~BANNED_USERS)
@languageCB
async def process_playlist_playback(client, query, _):
    cb_data = query.data.strip().split(None, 1)[1]
    v_id, u_id, p_type, mode_val, c_play, f_play = cb_data.split("|")
    
    if query.from_user.id != int(u_id):
        try: return await query.answer(_["playcb_1"], show_alert=True)
        except Exception: return
        
    try: target_chat, target_channel = await get_channeplayCB(_, c_play, query)
    except Exception: return
    
    i_name = query.from_user.first_name
    await query.message.delete()
    try: await query.answer()
    except Exception: pass
    
    status_msg = await query.message.reply_text(_["play_2"].format(target_channel) if target_channel else _["play_1"])
    v_id = lyrical.get(v_id)
    v_mode = True if mode_val == "v" else None
    f_mode = True if f_play == "f" else None
    is_sp = True
    
    if p_type == "yt":
        is_sp = False
        try: results_list = await YouTube.playlist(v_id, config.PLAYLIST_FETCH_LIMIT, query.from_user.id, True)
        except Exception: return await status_msg.edit_text(_["play_3"])
    elif p_type == "spplay":
        try: results_list, _ = await Spotify.playlist(v_id)
        except Exception: return await status_msg.edit_text(_["play_3"])
    elif p_type == "spalbum":
        try: results_list, _ = await Spotify.album(v_id)
        except Exception: return await status_msg.edit_text(_["play_3"])
    elif p_type == "spartist":
        try: results_list, _ = await Spotify.artist(v_id)
        except Exception: return await status_msg.edit_text(_["play_3"])
    elif p_type == "apple":
        try: results_list, _ = await Apple.playlist(v_id, True)
        except Exception: return await status_msg.edit_text(_["play_3"])
        
    try:
        await stream(_, status_msg, u_id, results_list, target_chat, i_name, query.message.chat.id, v_mode, streamtype="playlist", spotify=is_sp, forceplay=f_mode)
    except Exception as err:
        err_type = type(err).__name__
        return await status_msg.edit_text(err if err_type == "AssistantErr" else _["general_2"].format(err_type))
        
    return await status_msg.delete()

@app.on_callback_query(filters.regex("slider") & ~BANNED_USERS)
@languageCB
async def handle_slider_interaction(client, query, _):
    cb_data = query.data.strip().split(None, 1)[1]
    action_type, r_type, s_query, u_id, c_play, f_play = cb_data.split("|")
    
    if query.from_user.id != int(u_id):
        try: return await query.answer(_["playcb_1"], show_alert=True)
        except Exception: return
        
    action_type = str(action_type)
    r_type = int(r_type)
    
    if action_type == "F":
        q_idx = 0 if r_type == 9 else r_type + 1
    elif action_type == "B":
        q_idx = 9 if r_type == 0 else r_type - 1
        
    try: await query.answer(_["playcb_2"])
    except Exception: pass
    
    t_title, t_dur, t_thumb, t_vid = await YouTube.slider(s_query, q_idx)
    btns = slider_markup(_, t_vid, u_id, s_query, q_idx, c_play, f_play)
    
    new_media = InputMediaPhoto(media=t_thumb, caption=_["play_10"].format(t_title.title(), t_dur))
    return await query.edit_message_media(media=new_media, reply_markup=InlineKeyboardMarkup(btns))