from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.core.stream_call import Samar
from MattoMusic.misc import SUDOERS, db
from MattoMusic.utils import AdminRightsCheck
from MattoMusic.utils.database import is_active_chat, is_nonadmin_chat
from MattoMusic.utils.decorators.language import languageCB
from MattoMusic.utils.inline import close_markup, speed_markup
from config import BANNED_USERS, adminlist

speed_trackers = []

@app.on_message(filters.command(["cspeed", "speed", "cslow", "slow", "playback", "cplayback"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def adjust_playback_speed(cli, message: Message, _, chat_id):
    q_data = db.get(chat_id)
    if not q_data:
        return await message.reply_text(_["queue_2"])
        
    t_seconds = int(q_data[0]["seconds"])
    if t_seconds == 0:
        return await message.reply_text(_["admin_27"])
        
    p_file = q_data[0]["file"]
    if "downloads" not in p_file:
        return await message.reply_text(_["admin_27"])
        
    s_markup = speed_markup(_, chat_id)
    return await message.reply_text(
        text=_["admin_28"].format(app.mention),
        reply_markup=s_markup,
    )


@app.on_callback_query(filters.regex("SpeedUP") & ~BANNED_USERS)
@languageCB
async def speed_callback_handler(client, query, _):
    cb_data = query.data.strip().split(None, 1)[1]
    t_chat, new_speed = cb_data.split("|")
    c_id = int(t_chat)
    
    if not await is_active_chat(c_id):
        return await query.answer(_["general_5"], show_alert=True)
        
    is_regular = await is_nonadmin_chat(query.message.chat.id)
    if not is_regular:
        if query.from_user.id not in SUDOERS:
            c_admins = adminlist.get(query.message.chat.id)
            if not c_admins:
                return await query.answer(_["admin_13"], show_alert=True)
            elif query.from_user.id not in c_admins:
                return await query.answer(_["admin_14"], show_alert=True)
                
    q_data = db.get(c_id)
    if not q_data:
        return await query.answer(_["queue_2"], show_alert=True)
        
    if int(q_data[0]["seconds"]) == 0:
        return await query.answer(_["admin_27"], show_alert=True)
        
    if "downloads" not in q_data[0]["file"]:
        return await query.answer(_["admin_27"], show_alert=True)
        
    c_speed = q_data[0].get("speed")
    if c_speed and str(c_speed) == str(new_speed):
        if str(new_speed) == "1.0":
            return await query.answer(_["admin_29"], show_alert=True)
    elif not c_speed and str(new_speed) == "1.0":
        return await query.answer(_["admin_29"], show_alert=True)
        
    if c_id in speed_trackers:
        return await query.answer(_["admin_30"], show_alert=True)
    else:
        speed_trackers.append(c_id)
        
    try: await query.answer(_["admin_31"])
    except Exception: pass
    
    status_msg = await query.edit_message_text(text=_["admin_32"].format(query.from_user.mention))
    
    try:
        await Samar.speedup_stream(c_id, q_data[0]["file"], new_speed, q_data)
    except Exception:
        if c_id in speed_trackers: speed_trackers.remove(c_id)
        return await status_msg.edit_text(_["admin_33"], reply_markup=close_markup(_))
        
    if c_id in speed_trackers: speed_trackers.remove(c_id)
    
    await status_msg.edit_text(
        text=_["admin_34"].format(new_speed, query.from_user.mention),
        reply_markup=close_markup(_)
    )