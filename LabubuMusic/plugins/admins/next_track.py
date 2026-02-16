from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

import config
from MattoMusic import YouTube, app
from MattoMusic.core.stream_call import Samar
from MattoMusic.misc import db
from MattoMusic.utils.database import get_loop
from MattoMusic.utils.decorators import AdminRightsCheck
from MattoMusic.utils.inline import close_markup, stream_markup
from MattoMusic.utils.stream.autoclear import auto_clean
from MattoMusic.utils.thumbnails import gen_thumb
from config import BANNED_USERS

@app.on_message(filters.command(["skip", "cskip", "next", "cnext"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def skip_current_track(cli, message: Message, _, chat_id):
    if len(message.command) >= 2:
        loop_setting = await get_loop(chat_id)
        if loop_setting != 0:
            return await message.reply_text(_["admin_8"])
            
        skip_count = message.text.split(None, 1)[1].strip()
        if skip_count.isnumeric():
            skip_count = int(skip_count)
            q_list = db.get(chat_id)
            if q_list:
                list_size = len(q_list)
                if list_size > 2:
                    list_size -= 1
                    if 1 <= skip_count <= list_size:
                        for _ in range(skip_count):
                            try:
                                pop_item = q_list.pop(0)
                            except Exception:
                                return await message.reply_text(_["admin_12"])
                            if pop_item:
                                await auto_clean(pop_item)
                            if not q_list:
                                try:
                                    await message.reply_text(
                                        text=_["admin_6"].format(message.from_user.mention, message.chat.title),
                                        reply_markup=close_markup(_),
                                    )
                                    await Samar.stop_stream(chat_id)
                                except Exception: return
                                break
                    else:
                        return await message.reply_text(_["admin_11"].format(list_size))
                else:
                    return await message.reply_text(_["admin_10"])
            else:
                return await message.reply_text(_["queue_2"])
        else:
            return await message.reply_text(_["admin_9"])
    else:
        q_list = db.get(chat_id)
        try:
            pop_item = q_list.pop(0)
            if pop_item:
                await auto_clean(pop_item)
            if not q_list:
                await message.reply_text(
                    text=_["admin_6"].format(message.from_user.mention, message.chat.title),
                    reply_markup=close_markup(_),
                )
                try: return await Samar.stop_stream(chat_id)
                except Exception: return
        except Exception:
            try:
                await message.reply_text(
                    text=_["admin_6"].format(message.from_user.mention, message.chat.title),
                    reply_markup=close_markup(_),
                )
                return await Samar.stop_stream(chat_id)
            except Exception: return

    next_file = q_list[0]["file"]
    next_title = (q_list[0]["title"]).title()
    next_user = q_list[0]["by"]
    stream_t = q_list[0]["streamtype"]
    v_id = q_list[0]["vidid"]
    is_vid = True if str(stream_t) == "video" else None
    
    db[chat_id][0]["played"] = 0
    if q_list[0].get("old_dur"):
        db[chat_id][0]["dur"] = q_list[0]["old_dur"]
        db[chat_id][0]["seconds"] = q_list[0]["old_second"]
        db[chat_id][0]["speed_path"] = None
        db[chat_id][0]["speed"] = 1.0
        
    if "live_" in next_file:
        success, vid_url = await YouTube.video(v_id, True)
        if success == 0:
            return await message.reply_text(_["admin_7"].format(next_title))
        try: t_img = await YouTube.thumbnail(v_id, True)
        except Exception: t_img = None
        
        try: await Samar.skip_stream(chat_id, vid_url, video=is_vid, image=t_img)
        except Exception: return await message.reply_text(_["call_6"])
        
        btn = stream_markup(_, chat_id)
        img = await gen_thumb(v_id)
        run_msg = await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{v_id}", next_title[:23], q_list[0]["dur"], next_user),
            reply_markup=InlineKeyboardMarkup(btn),
        )
        db[chat_id][0]["mystic"] = run_msg
        db[chat_id][0]["markup"] = "tg"
        
    elif "vid_" in next_file:
        load_msg = await message.reply_text(_["call_7"], disable_web_page_preview=True)
        try: file_path, _ = await YouTube.download(v_id, load_msg, videoid=True, video=is_vid)
        except Exception: return await load_msg.edit_text(_["call_6"])
        
        try: t_img = await YouTube.thumbnail(v_id, True)
        except Exception: t_img = None
        
        try: await Samar.skip_stream(chat_id, file_path, video=is_vid, image=t_img)
        except Exception: return await load_msg.edit_text(_["call_6"])
        
        btn = stream_markup(_, chat_id)
        img = await gen_thumb(v_id)
        run_msg = await message.reply_photo(
            photo=img,
            caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{v_id}", next_title[:23], q_list[0]["dur"], next_user),
            reply_markup=InlineKeyboardMarkup(btn),
        )
        db[chat_id][0]["mystic"] = run_msg
        db[chat_id][0]["markup"] = "stream"
        await load_msg.delete()
        
    elif "index_" in next_file:
        try: await Samar.skip_stream(chat_id, v_id, video=is_vid)
        except Exception: return await message.reply_text(_["call_6"])
        
        btn = stream_markup(_, chat_id)
        run_msg = await message.reply_photo(
            photo=config.STREAM_IMG_URL,
            caption=_["stream_2"].format(next_user),
            reply_markup=InlineKeyboardMarkup(btn),
        )
        db[chat_id][0]["mystic"] = run_msg
        db[chat_id][0]["markup"] = "tg"
        
    else:
        if v_id in ["telegram", "soundcloud"]: t_img = None
        else:
            try: t_img = await YouTube.thumbnail(v_id, True)
            except Exception: t_img = None
            
        try: await Samar.skip_stream(chat_id, next_file, video=is_vid, image=t_img)
        except Exception: return await message.reply_text(_["call_6"])
        
        if v_id == "telegram":
            btn = stream_markup(_, chat_id)
            run_msg = await message.reply_photo(
                photo=config.TELEGRAM_AUDIO_URL if str(stream_t) == "audio" else config.TELEGRAM_VIDEO_URL,
                caption=_["stream_1"].format(config.SUPPORT_GROUP, next_title[:23], q_list[0]["dur"], next_user),
                reply_markup=InlineKeyboardMarkup(btn),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "tg"
        elif v_id == "soundcloud":
            btn = stream_markup(_, chat_id)
            run_msg = await message.reply_photo(
                photo=config.SOUNCLOUD_IMG_URL if str(stream_t) == "audio" else config.TELEGRAM_VIDEO_URL,
                caption=_["stream_1"].format(config.SUPPORT_GROUP, next_title[:23], q_list[0]["dur"], next_user),
                reply_markup=InlineKeyboardMarkup(btn),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "tg"
        else:
            btn = stream_markup(_, chat_id)
            img = await gen_thumb(v_id)
            run_msg = await message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{v_id}", next_title[:23], q_list[0]["dur"], next_user),
                reply_markup=InlineKeyboardMarkup(btn),
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "stream"