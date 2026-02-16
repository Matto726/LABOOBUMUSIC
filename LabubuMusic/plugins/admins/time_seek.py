from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import YouTube, app
from MattoMusic.core.stream_call import Samar
from MattoMusic.misc import db
from MattoMusic.utils import AdminRightsCheck, seconds_to_min
from MattoMusic.utils.inline import close_markup
from config import BANNED_USERS

@app.on_message(filters.command(["seek", "cseek", "seekback", "cseekback"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def seek_timeline(cli, message: Message, _, chat_id):
    if len(message.command) == 1:
        return await message.reply_text(_["admin_20"])
        
    seek_query = message.text.split(None, 1)[1].strip()
    if not seek_query.isnumeric():
        return await message.reply_text(_["admin_21"])
        
    q_data = db.get(chat_id)
    if not q_data:
        return await message.reply_text(_["queue_2"])
        
    total_seconds = int(q_data[0]["seconds"])
    if total_seconds == 0:
        return await message.reply_text(_["admin_22"])
        
    path_file = q_data[0]["file"]
    played_time = int(q_data[0]["played"])
    skip_time = int(seek_query)
    full_duration = q_data[0]["dur"]
    
    is_backward = message.command[0][-2] == "c"
    
    if is_backward:
        if (played_time - skip_time) <= 10:
            return await message.reply_text(
                text=_["admin_23"].format(seconds_to_min(played_time), full_duration),
                reply_markup=close_markup(_),
            )
        target_seek = played_time - skip_time + 1
    else:
        if (total_seconds - (played_time + skip_time)) <= 10:
            return await message.reply_text(
                text=_["admin_23"].format(seconds_to_min(played_time), full_duration),
                reply_markup=close_markup(_),
            )
        target_seek = played_time + skip_time + 1
        
    alert_msg = await message.reply_text(_["admin_24"])
    
    if "vid_" in path_file:
        status, path_file = await YouTube.video(q_data[0]["vidid"], True)
        if status == 0:
            return await message.reply_text(_["admin_22"])
            
    speed_file = (q_data[0]).get("speed_path")
    if speed_file:
        path_file = speed_file
    if "index_" in path_file:
        path_file = q_data[0]["vidid"]
        
    try:
        await Samar.seek_stream(
            chat_id,
            path_file,
            seconds_to_min(target_seek),
            full_duration,
            q_data[0]["streamtype"],
        )
    except Exception:
        return await alert_msg.edit_text(_["admin_26"], reply_markup=close_markup(_))
        
    if is_backward:
        db[chat_id][0]["played"] -= skip_time
    else:
        db[chat_id][0]["played"] += skip_time
        
    await alert_msg.edit_text(
        text=_["admin_25"].format(seconds_to_min(target_seek), message.from_user.mention),
        reply_markup=close_markup(_),
    )