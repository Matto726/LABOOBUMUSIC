import asyncio
import time
import psutil

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from MattoMusic import YouTube, app
from MattoMusic.core.stream_call import Samar
from MattoMusic.misc import SUDOERS, db
from MattoMusic.utils import bot_sys_stats
from MattoMusic.utils.database import (
    get_active_chats, get_lang, get_upvote_count, is_active_chat,
    is_music_playing, is_nonadmin_chat, music_off, music_on, set_loop,
)
from MattoMusic.utils.decorators.language import languageCB
from MattoMusic.utils.formatters import seconds_to_min
from MattoMusic.utils.inline import close_markup, stream_markup, stream_markup_timer
from MattoMusic.utils.inline.help import help_pannel_page1, help_pannel_page2, help_pannel_page3, help_pannel_page4
from MattoMusic.utils.inline.start import about_panel, owner_panel
from MattoMusic.utils.stream.autoclear import auto_clean
from MattoMusic.utils.thumbnails import gen_thumb

from config import (
    BANNED_USERS, SOUNCLOUD_IMG_URL, STREAM_IMG_URL, TELEGRAM_AUDIO_URL,
    TELEGRAM_VIDEO_URL, adminlist, confirmer, votemode, SUPPORT_GROUP
)
from strings import get_string
import config

active_checkers = {}
active_upvoters = {}

def format_readable_time(seconds: int) -> str:
    count = 0
    p_time = ""
    t_vals = []
    t_suffixes = ["s", "m", "h", "d"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and result == 0:
            break
        t_vals.append(int(result))
        seconds = int(remainder)

    for i in range(len(t_vals)):
        p_time = f"{t_vals[i]}{t_suffixes[i]} {p_time}"
    return p_time.strip()

@app.on_callback_query(filters.regex("help_page_1"))
async def display_help_p1(client, query: CallbackQuery):
    lang_code = (await get_lang(query.message.chat.id)) if query.message.chat else "en"
    _ = get_string(lang_code)

    await query.message.edit_caption(
        caption=_["help_1"].format(SUPPORT_GROUP),
        reply_markup=help_pannel_page1(_, START=True)
    )

@app.on_callback_query(filters.regex("fork_repo"))
async def fork_repository_cb(client, query: CallbackQuery):
    await query.message.edit_text(
        text=(
            "✨ <b>ʙᴜɪʟᴅ Yᴏᴜʀ Oᴡɴ ᴍᴜsɪᴄ ʙᴏᴛ 🎧</b>\n\n"
            "🚀 ʀᴇᴀᴅʏ ᴛᴏ ʟᴀᴜɴᴄʜ ʏᴏᴜʀ ᴏᴡɴ ʙᴏᴛ?\n"
            "ғᴏʀᴋ ᴛʜᴇ ʀᴇᴘᴏ ᴀɴᴅ ᴅᴇᴘʟᴏʏ ɪɴ sᴇᴄᴏɴᴅs.\n\n"
            "🔧 <b>Cᴜsᴛᴏᴍɪᴢᴇ ɪᴛ. Dᴇᴘʟᴏʏ ɪᴛ. Vɪʙᴇ ᴡɪᴛʜ ɪᴛ 🔥</b>"
        ),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🚀 Fᴏʀᴋ Rᴇᴘᴏ", url="https://github.com/Matto726/LabubuMusic/fork"),
                    InlineKeyboardButton("⚡ Hᴇʀᴏᴋᴜ Dᴇᴘʟᴏʏ", url="https://dashboard.heroku.com/new?template=https://github.com/Matto726/LabubuMusic")
                ],
                [InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="settingsback_helper")]
            ]
        )
    )

@app.on_callback_query(filters.regex("about_page") & ~BANNED_USERS)
async def fetch_about_cb(client, query: CallbackQuery):
    try:
        _ = get_string("en")
        await query.answer()
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(about_panel(_)))
    except Exception as e:
        await query.answer(f"❌ Error: {e}", show_alert=True)

@app.on_callback_query(filters.regex("owner_page") & ~BANNED_USERS)
async def fetch_owner_cb(client, query: CallbackQuery):
    try:
        _ = get_string("en")
        await query.answer()
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(owner_panel(_)))
    except Exception as e:
        await query.answer(f"❌ Error: {e}", show_alert=True)

@app.on_callback_query(filters.regex("ping_status"))
async def display_ping_status(client, query: CallbackQuery):
    loader = await query.message.reply_text("🔄 ᴘɪɴɢɪɴɢ...")
    start_t = time.time()
    
    try:
        await Samar.ping()
    except Exception:
        pass
        
    ping_val = round((time.time() - start_t) * 1000)

    try:
        sys_up, sys_cpu, sys_ram, sys_disk = await bot_sys_stats()
    except Exception:
        sys_up = "Unknown"
        sys_cpu = psutil.cpu_percent()
        sys_ram = psutil.virtual_memory().percent
        sys_disk = psutil.disk_usage('/').percent

    color_ind = "🟢" if ping_val < 100 else "🟡" if ping_val < 300 else "🔴"

    status_txt = (
        f"📡 ᴘɪɴɢ: {ping_val}ms {color_ind}\n"
        f"⏱ ᴜᴘᴛɪᴍᴇ: {sys_up}\n"
        f"💾 ᴅɪꜱᴋ: {sys_disk}%\n"
        f"📈 ᴍᴇᴍᴏʀʏ: {sys_ram}%\n"
        f"🖥 ᴄᴘᴜ: {sys_cpu}%"
    )

    await loader.edit_text(status_txt)
    await asyncio.sleep(8)
    await loader.delete()

@app.on_callback_query(filters.regex("help_page_2"))
async def display_help_p2(client, query: CallbackQuery):
    lang_code = (await get_lang(query.message.chat.id)) if query.message.chat else "en"
    _ = get_string(lang_code)
    await query.message.edit_caption(caption=_["help_1"].format(SUPPORT_GROUP), reply_markup=help_pannel_page2(_, START=True))

@app.on_callback_query(filters.regex("help_page_3"))
async def display_help_p3(client, query: CallbackQuery):
    lang_code = (await get_lang(query.message.chat.id)) if query.message.chat else "en"
    _ = get_string(lang_code)
    await query.message.edit_caption(caption=_["help_1"].format(SUPPORT_GROUP), reply_markup=help_pannel_page3(_, START=True))

@app.on_callback_query(filters.regex("help_page_4"))
async def display_help_p4(client, query: CallbackQuery):
    lang_code = (await get_lang(query.message.chat.id)) if query.message.chat else "en"
    _ = get_string(lang_code)
    await query.message.edit_caption(caption=_["help_1"].format(SUPPORT_GROUP), reply_markup=help_pannel_page4(_, START=True))

@app.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def handle_admin_callbacks(client, query: CallbackQuery, _):
    cb_data = query.data.strip()
    action_req = cb_data.split(None, 1)[1]
    cmd, target_chat = action_req.split("|")
    cb_counter = None
    
    if "_" in str(target_chat):
        parts = target_chat.split("_")
        target_chat = parts[0]
        cb_counter = parts[1]
    
    chat_id = int(target_chat)
    
    if not await is_active_chat(chat_id):
        return await query.answer(_["general_5"], show_alert=True)
    
    user_mention = query.from_user.mention
    
    if cmd == "UpVote":
        if chat_id not in votemode: votemode[chat_id] = {}
        if chat_id not in active_upvoters: active_upvoters[chat_id] = {}

        if not (active_upvoters[chat_id]).get(query.message.id):
            active_upvoters[chat_id][query.message.id] = []
        if not (votemode[chat_id]).get(query.message.id):
            votemode[chat_id][query.message.id] = 0

        if query.from_user.id in active_upvoters[chat_id][query.message.id]:
            (active_upvoters[chat_id][query.message.id]).remove(query.from_user.id)
            votemode[chat_id][query.message.id] -= 1
        else:
            (active_upvoters[chat_id][query.message.id]).append(query.from_user.id)
            votemode[chat_id][query.message.id] += 1
        
        req_upvotes = await get_upvote_count(chat_id)
        current_upvotes = int(votemode[chat_id][query.message.id])
        
        if current_upvotes >= req_upvotes:
            votemode[chat_id][query.message.id] = req_upvotes
            try:
                verified_vid = confirmer[chat_id][query.message.id]
                current_stream = db[chat_id][0]
            except Exception:
                return await query.edit_message_text("ғᴀɪʟᴇᴅ.")
            
            try:
                if current_stream["vidid"] != verified_vid["vidid"] or current_stream["file"] != verified_vid["file"]:
                    return await query.edit_message_text(_["admin_35"])
            except Exception:
                return await query.edit_message_text(_["admin_36"])
            
            try:
                await query.edit_message_text(_["admin_37"].format(req_upvotes))
            except Exception:
                pass
            
            cmd = cb_counter
            user_mention = "ᴜᴘᴠᴏᴛᴇs"
        else:
            if query.from_user.id in active_upvoters[chat_id][query.message.id]:
                await query.answer(_["admin_38"], show_alert=True)
            else:
                await query.answer(_["admin_39"], show_alert=True)
            
            btn_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=f"👍 {current_upvotes}", callback_data=f"ADMIN  UpVote|{chat_id}_{cb_counter}")]])
            await query.answer(_["admin_40"], show_alert=True)
            return await query.edit_message_reply_markup(reply_markup=btn_markup)
            
    else:
        is_regular = await is_nonadmin_chat(query.message.chat.id)
        if not is_regular:
            if query.from_user.id not in SUDOERS:
                chat_admins = adminlist.get(query.message.chat.id)
                if not chat_admins:
                    return await query.answer(_["admin_13"], show_alert=True)
                elif query.from_user.id not in chat_admins:
                    return await query.answer(_["admin_14"], show_alert=True)
    
    if cmd == "Pause":
        if not await is_music_playing(chat_id):
            return await query.answer(_["admin_1"], show_alert=True)
        await query.answer()
        await music_off(chat_id)
        await Samar.pause_stream(chat_id)
        await query.message.reply_text(_["admin_2"].format(user_mention), reply_markup=close_markup(_))
    
    elif cmd == "Resume":
        if await is_music_playing(chat_id):
            return await query.answer(_["admin_3"], show_alert=True)
        await query.answer()
        await music_on(chat_id)
        await Samar.resume_stream(chat_id)
        await query.message.reply_text(_["admin_4"].format(user_mention), reply_markup=close_markup(_))
    
    elif cmd in ["Stop", "End"]:
        await query.answer()
        await Samar.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        await query.message.reply_text(_["admin_5"].format(user_mention), reply_markup=close_markup(_))
        await query.message.delete()
    
    elif cmd in ["Skip", "Replay"]:
        q_data = db.get(chat_id)
        if not q_data:
            return await query.answer("No music in queue!", show_alert=True)
        
        if cmd == "Skip":
            msg_txt = f"➻ sᴛʀᴇᴀᴍ sᴋɪᴩᴩᴇᴅ 🎄\n│ \n└ʙʏ : {user_mention} 🥀"
            try:
                pop_item = q_data.pop(0)
                if pop_item: await auto_clean(pop_item)
                
                if not q_data:
                    await query.edit_message_text(msg_txt)
                    await query.message.reply_text(text=_["admin_6"].format(user_mention, query.message.chat.title), reply_markup=close_markup(_))
                    try: return await Samar.stop_stream(chat_id)
                    except: return
            except Exception:
                try:
                    await query.edit_message_text(msg_txt)
                    await query.message.reply_text(text=_["admin_6"].format(user_mention, query.message.chat.title), reply_markup=close_markup(_))
                    return await Samar.stop_stream(chat_id)
                except: return
        else:
            msg_txt = f"➻ sᴛʀᴇᴀᴍ ʀᴇ-ᴘʟᴀʏᴇᴅ 🎄\n│ \n└ʙʏ : {user_mention} 🥀"
        
        await query.answer()
        if not q_data:
            return await query.edit_message_text("Queue is empty!")
        
        next_file = q_data[0]["file"]
        next_title = (q_data[0]["title"]).title()
        next_user = q_data[0]["by"]
        next_dur = q_data[0]["dur"]
        s_type = q_data[0]["streamtype"]
        v_id = q_data[0]["vidid"]
        is_vid = True if str(s_type) == "video" else None
        
        db[chat_id][0]["played"] = 0
        if (q_data[0]).get("old_dur"):
            db[chat_id][0]["dur"] = q_data[0]["old_dur"]
            db[chat_id][0]["seconds"] = q_data[0]["old_second"]
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0
        
        if "live_" in next_file:
            success, link_url = await YouTube.video(v_id, True)
            if success == 0:
                return await query.message.reply_text(text=_["admin_7"].format(next_title), reply_markup=close_markup(_))
            try: thumb_img = await YouTube.thumbnail(v_id, True)
            except Exception: thumb_img = None
            
            try: await Samar.skip_stream(chat_id, link_url, video=is_vid, image=thumb_img)
            except Exception: return await query.message.reply_text(_["call_6"])
            
            btn = stream_markup(_, chat_id)
            img = await gen_thumb(v_id)
            run_msg = await query.message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{v_id}", next_title[:23], next_dur, next_user),
                reply_markup=InlineKeyboardMarkup(btn),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "tg"
            await query.edit_message_text(msg_txt, reply_markup=close_markup(_))
        
        elif "vid_" in next_file:
            load_msg = await query.message.reply_text(_["call_7"], disable_web_page_preview=True)
            try:
                dl_path, _ = await YouTube.download(v_id, load_msg, videoid=True, video=is_vid)
            except Exception:
                return await load_msg.edit_text(_["call_6"])
            
            try: thumb_img = await YouTube.thumbnail(v_id, True)
            except Exception: thumb_img = None
            
            try: await Samar.skip_stream(chat_id, dl_path, video=is_vid, image=thumb_img)
            except Exception: return await load_msg.edit_text(_["call_6"])
            
            btn = stream_markup(_, chat_id)
            img = await gen_thumb(v_id)
            run_msg = await query.message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{v_id}", next_title[:23], next_dur, next_user),
                reply_markup=InlineKeyboardMarkup(btn),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "stream"
            await query.edit_message_text(msg_txt, reply_markup=close_markup(_))
            await load_msg.delete()
        
        elif "index_" in next_file:
            try: await Samar.skip_stream(chat_id, v_id, video=is_vid)
            except Exception: return await query.message.reply_text(_["call_6"])
            
            btn = stream_markup(_, chat_id)
            run_msg = await query.message.reply_photo(
                photo=STREAM_IMG_URL,
                caption=_["stream_2"].format(next_user),
                reply_markup=InlineKeyboardMarkup(btn),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "tg"
            await query.edit_message_text(msg_txt, reply_markup=close_markup(_))
        
        else:
            if v_id in ["telegram", "soundcloud"]: thumb_img = None
            else:
                try: thumb_img = await YouTube.thumbnail(v_id, True)
                except Exception: thumb_img = None
            
            try: await Samar.skip_stream(chat_id, next_file, video=is_vid, image=thumb_img)
            except Exception: return await query.message.reply_text(_["call_6"])
            
            if v_id == "telegram":
                btn = stream_markup(_, chat_id)
                run_msg = await query.message.reply_photo(
                    photo=TELEGRAM_AUDIO_URL if str(s_type) == "audio" else TELEGRAM_VIDEO_URL,
                    caption=_["stream_1"].format(config.SUPPORT_GROUP, next_title[:23], next_dur, next_user),
                    reply_markup=InlineKeyboardMarkup(btn),
                )
                db[chat_id][0]["mystic"] = run_msg
                db[chat_id][0]["markup"] = "tg"
            elif v_id == "soundcloud":
                btn = stream_markup(_, chat_id)
                run_msg = await query.message.reply_photo(
                    photo=SOUNCLOUD_IMG_URL if str(s_type) == "audio" else TELEGRAM_VIDEO_URL,
                    caption=_["stream_1"].format(config.SUPPORT_GROUP, next_title[:23], next_dur, next_user),
                    reply_markup=InlineKeyboardMarkup(btn),
                )
                db[chat_id][0]["mystic"] = run_msg
                db[chat_id][0]["markup"] = "tg"
            else:
                btn = stream_markup(_, chat_id)
                img = await gen_thumb(v_id)
                run_msg = await query.message.reply_photo(
                    photo=img,
                    caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{v_id}", next_title[:23], next_dur, next_user),
                    reply_markup=InlineKeyboardMarkup(btn),
                )
                db[chat_id][0]["mystic"] = run_msg
                db[chat_id][0]["markup"] = "stream"
            
            await query.edit_message_text(msg_txt, reply_markup=close_markup(_))

async def process_markup_timer():
    while True:
        try:
            await asyncio.sleep(7)
            active_sessions = await get_active_chats()
            for c_id in active_sessions:
                try:
                    if not await is_music_playing(c_id): continue
                    play_data = db.get(c_id)
                    if not play_data or int(play_data[0]["seconds"]) == 0: continue
                    
                    try: msg_obj = play_data[0]["mystic"]
                    except Exception: continue
                    
                    if active_checkers.get(c_id, {}).get(msg_obj.id) is False: continue
                    
                    lang_c = await get_lang(c_id) if c_id else "en"
                    _ = get_string(lang_c)
                    
                    try:
                        timer_btns = stream_markup_timer(_, c_id, seconds_to_min(play_data[0]["played"]), play_data[0]["dur"])
                        await msg_obj.edit_reply_markup(reply_markup=InlineKeyboardMarkup(timer_btns))
                    except Exception: continue
                except Exception: continue
        except Exception: continue

asyncio.create_task(process_markup_timer())